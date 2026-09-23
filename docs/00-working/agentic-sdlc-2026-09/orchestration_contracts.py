"""
Orchestration contract surface for an agentic SDLC pipeline.

This file defines the seams, not the behaviour. Every agent in the system is
declared here even where its implementation doesn't exist yet, so that adding
one later is a registry entry rather than a refactor.

Load-bearing invariant, enforced by ArtifactRef:
    THE ORCHESTRATOR NEVER HOLDS CONTENT. It holds pointers, hashes, status,
    and counters. Plans, diffs, reviews, and logs live on disk; agents read
    them by ref. This is what keeps orchestrator context O(1) in repo size
    and what makes a run resumable after a crash.

Python 3.12+. Pydantic v2, frozen + extra="forbid" throughout.
"""

from __future__ import annotations

import hashlib
from collections.abc import Sequence
from datetime import datetime, timezone
from enum import StrEnum
from pathlib import Path
from typing import Any, Literal, Protocol, Self

from pydantic import BaseModel, ConfigDict, Field


class Spec(BaseModel):
    model_config = ConfigDict(extra="forbid", frozen=True)


def _now() -> datetime:
    return datetime.now(timezone.utc)


# ===========================================================================
# 1. Artifacts — the anti-context-bloat primitive
# ===========================================================================


class ArtifactKind(StrEnum):
    CONTEXT_BUNDLE = "context_bundle"
    PLAN = "plan"
    INTERFACE_CONTRACT = "interface_contract"
    TASK_SPEC = "task_spec"
    DIFF = "diff"
    REVIEW = "review"
    TEST_REPORT = "test_report"
    MUTATION_REPORT = "mutation_report"
    BASELINE = "baseline"
    INCIDENT = "incident"


class ArtifactRef(Spec):
    """A pointer to content the orchestrator deliberately does not read."""

    kind: ArtifactKind
    path: Path
    sha256: str
    bytes: int
    produced_by: str  # agent name
    created_at: datetime = Field(default_factory=_now)

    @classmethod
    def of(cls, kind: ArtifactKind, path: Path, produced_by: str) -> Self:
        data = path.read_bytes()
        return cls(
            kind=kind,
            path=path,
            sha256=hashlib.sha256(data).hexdigest(),
            bytes=len(data),
            produced_by=produced_by,
        )


# ===========================================================================
# 2. Findings and gates — one shape for every kind of check
#
# A human approval, a mypy run, and an LLM code review all return GateResult.
# That uniformity is what lets you swap a deterministic check in for an agent
# check later without touching the orchestrator.
# ===========================================================================


class Severity(StrEnum):
    BLOCKING = "blocking"  # reopens the loop
    ADVISORY = "advisory"  # becomes a backlog item, never reopens the loop


class Finding(Spec):
    severity: Severity
    code: str  # stable id, e.g. "REV.MISSING_ERROR_PATH" — groupable for evals
    message: str
    path: Path | None = None
    line: int | None = None


class GateKind(StrEnum):
    DETERMINISTIC = "deterministic"  # mypy, ruff, pytest, mutmut, merge
    AGENT = "agent"  # LLM reviewer
    HUMAN = "human"  # blocking approval


class GateResult(Spec):
    gate: str
    kind: GateKind
    passed: bool
    findings: tuple[Finding, ...] = ()
    evidence: ArtifactRef | None = None
    shadow: bool = False  # ran, recorded, did NOT gate — see AgentSpec.shadow
    decided_at: datetime = Field(default_factory=_now)

    @property
    def blocking(self) -> tuple[Finding, ...]:
        return tuple(f for f in self.findings if f.severity is Severity.BLOCKING)


class Gate(Protocol):
    name: str
    kind: GateKind

    async def evaluate(self, manifest: RunManifest, subject: ArtifactRef) -> GateResult: ...


# ===========================================================================
# 3. Agent declarations — every agent in the design, implemented or not
# ===========================================================================


class ModelTier(StrEnum):
    SMALL = "small"
    MID = "mid"
    LARGE = "large"


class AgentRole(StrEnum):
    ORCHESTRATOR = "orchestrator"
    CONTEXT_GATHERER = "context_gatherer"
    PLAN_WRITER = "plan_writer"
    PLAN_REVIEWER = "plan_reviewer"
    TASK_DECOMPOSER = "task_decomposer"
    TEST_AUTHOR = "test_author"  # NOT the dev agent — see note below
    TASK_DEV = "task_dev"
    CODE_REVIEWER = "code_reviewer"
    INTEGRATOR = "integrator"  # owns shared files and merge order
    TEST_RUNNER = "test_runner"
    TEST_INVESTIGATOR = "test_investigator"
    CI_CLEANUP = "ci_cleanup"
    PR_REVIEWER = "pr_reviewer"
    SECURITY_REVIEWER = "security_reviewer"
    LOG_MONITOR = "log_monitor"
    ERROR_ANALYZER = "error_analyzer"


class AgentSpec(Spec):
    """Declarative config. Adding an agent should never touch the loop."""

    role: AgentRole
    model_tier: ModelTier
    tool_allowlist: tuple[str, ...]
    writable_globs: tuple[str, ...] = ()  # empty = read-only agent
    max_steps: int = 12
    token_budget: int = 200_000

    # Runs, records its verdict, but does not gate. The calibration mechanism:
    # ship a new validator in shadow, compare against a human, promote later.
    shadow: bool = False

    # Reviewers must not see the builder's rationale, only spec + artifact.
    # Set False for any validator whose independence you care about.
    sees_generator_rationale: bool = False


DEFAULT_AGENTS: dict[AgentRole, AgentSpec] = {
    AgentRole.CONTEXT_GATHERER: AgentSpec(
        role=AgentRole.CONTEXT_GATHERER,
        model_tier=ModelTier.SMALL,
        tool_allowlist=("grep", "read_file", "list_dir", "rag_search", "git_log"),
        max_steps=30,
    ),
    AgentRole.PLAN_WRITER: AgentSpec(
        role=AgentRole.PLAN_WRITER,
        model_tier=ModelTier.LARGE,
        tool_allowlist=("read_artifact", "write_artifact", "ask_user"),
        writable_globs=(".runs/*/plan.md",),
    ),
    AgentRole.PLAN_REVIEWER: AgentSpec(
        role=AgentRole.PLAN_REVIEWER,
        model_tier=ModelTier.LARGE,
        tool_allowlist=("read_artifact", "grep", "read_file"),
    ),
    AgentRole.TEST_AUTHOR: AgentSpec(
        # Separate from TASK_DEV on purpose. If one agent writes both the test
        # and the code, the test is a tautology. The dev agent gets no write
        # access to tests/ — note the disjoint writable_globs below.
        role=AgentRole.TEST_AUTHOR,
        model_tier=ModelTier.MID,
        tool_allowlist=("read_artifact", "read_file", "write_file", "run_tests"),
        writable_globs=("tests/**",),
    ),
    AgentRole.TASK_DEV: AgentSpec(
        role=AgentRole.TASK_DEV,
        model_tier=ModelTier.MID,
        tool_allowlist=("read_file", "write_file", "run_tests", "run_typecheck"),
        writable_globs=("src/**",),  # deliberately excludes tests/**
        max_steps=40,
    ),
    AgentRole.CODE_REVIEWER: AgentSpec(
        role=AgentRole.CODE_REVIEWER,
        model_tier=ModelTier.LARGE,
        tool_allowlist=("read_diff", "read_file", "grep", "run_tests", "run_typecheck"),
        shadow=True,  # start here; promote once precision is measured
    ),
    AgentRole.TEST_INVESTIGATOR: AgentSpec(
        role=AgentRole.TEST_INVESTIGATOR,
        model_tier=ModelTier.LARGE,
        tool_allowlist=("read_file", "run_tests", "git_log", "git_blame", "read_flake_registry"),
    ),
    AgentRole.CI_CLEANUP: AgentSpec(
        role=AgentRole.CI_CLEANUP,
        model_tier=ModelTier.SMALL,
        tool_allowlist=("run_formatter", "write_file"),
        writable_globs=("src/**", "docs/**"),
        max_steps=6,
    ),
    AgentRole.LOG_MONITOR: AgentSpec(
        role=AgentRole.LOG_MONITOR,
        model_tier=ModelTier.SMALL,
        tool_allowlist=("query_logs", "query_metrics"),
        # No rollback tool. Detection is deterministic; this agent only
        # correlates and proposes. See RollbackProposal.
    ),
    AgentRole.ERROR_ANALYZER: AgentSpec(
        role=AgentRole.ERROR_ANALYZER,
        model_tier=ModelTier.LARGE,
        tool_allowlist=("query_logs", "read_diff", "git_log", "match_patterns"),
    ),
}


# ===========================================================================
# 4. Escalation — a ladder, as data, in order of increasing cost
# ===========================================================================


class EscalationStep(StrEnum):
    REGATHER_CONTEXT = "regather_context"  # cheapest, most often correct
    RESPEC_TASK = "respec_task"  # back to the decomposer
    ESCALATE_MODEL = "escalate_model"  # last, not first
    HUMAN = "human"


class EscalationPolicy(Spec):
    ladder: tuple[EscalationStep, ...] = (
        EscalationStep.REGATHER_CONTEXT,
        EscalationStep.RESPEC_TASK,
        EscalationStep.ESCALATE_MODEL,
        EscalationStep.HUMAN,
    )
    rounds_per_step: int = 2

    def step_for(self, failed_rounds: int) -> EscalationStep:
        idx = min(failed_rounds // self.rounds_per_step, len(self.ladder) - 1)
        return self.ladder[idx]


class Budget(Spec):
    """Unbounded loops plus model escalation is how you get a surprise bill."""

    max_tokens: int = 20_000_000
    max_usd: float = 200.0
    max_wall_clock_s: float = 7200.0
    max_review_rounds_per_task: int = 6


# ===========================================================================
# 5. Tasks and the run manifest
# ===========================================================================


class TaskStatus(StrEnum):
    PENDING = "pending"
    IN_PROGRESS = "in_progress"
    IN_REVIEW = "in_review"
    APPROVED = "approved"
    MERGED = "merged"
    BLOCKED = "blocked"
    ABANDONED = "abandoned"


class TaskRecord(Spec):
    task_id: str
    title: str
    spec: ArtifactRef
    owned_globs: tuple[str, ...]  # disjoint across sibling tasks — asserted
    depends_on: tuple[str, ...] = ()
    worktree: Path | None = None
    branch: str | None = None
    status: TaskStatus = TaskStatus.PENDING
    model_tier: ModelTier = ModelTier.MID
    review_rounds: int = 0
    diff: ArtifactRef | None = None
    gates: tuple[GateResult, ...] = ()


class PartialFailurePolicy(StrEnum):
    """What happens when 4 of 6 tasks succeed. Decide now, not at 2am."""

    BLOCK_PLAN = "block_plan"  # nothing merges until all pass
    MERGE_INDEPENDENT = "merge_independent"  # merge tasks with no failed deps
    HUMAN_DECIDES = "human_decides"


class Phase(StrEnum):
    INTAKE = "intake"
    CONTEXT = "context"
    PLANNING = "planning"
    PLAN_APPROVAL = "plan_approval"  # human gate
    DECOMPOSITION = "decomposition"
    CONTRACT_FREEZE = "contract_freeze"  # serialized, before any parallelism
    BUILD = "build"  # the swarm
    INTEGRATION = "integration"  # merge order, shared files
    VERIFICATION = "verification"  # tests, mutation, typecheck
    CI = "ci"
    PULL_REQUEST = "pull_request"
    PROMOTION = "promotion"  # human gate for QA -> prod
    OBSERVATION = "observation"  # always-on, post-merge
    DONE = "done"
    HALTED = "halted"


PHASE_ORDER: tuple[Phase, ...] = (
    Phase.INTAKE,
    Phase.CONTEXT,
    Phase.PLANNING,
    Phase.PLAN_APPROVAL,
    Phase.DECOMPOSITION,
    Phase.CONTRACT_FREEZE,
    Phase.BUILD,
    Phase.INTEGRATION,
    Phase.VERIFICATION,
    Phase.CI,
    Phase.PULL_REQUEST,
    Phase.PROMOTION,
    Phase.OBSERVATION,
    Phase.DONE,
)

HUMAN_GATED: frozenset[Phase] = frozenset({Phase.PLAN_APPROVAL, Phase.PROMOTION})


class RunManifest(Spec):
    """The single source of truth. Serialize after every transition.

    Everything here is a pointer, a status, or a counter. If you find yourself
    wanting to add a `plan_text: str` field, that's the invariant breaking.
    """

    run_id: str
    repo: Path
    request: str
    phase: Phase = Phase.INTAKE

    baseline: ArtifactRef | None = None  # test/skip/coverage counts pre-swarm
    context_bundle: ArtifactRef | None = None
    plan: ArtifactRef | None = None
    interface_contract: ArtifactRef | None = None

    tasks: tuple[TaskRecord, ...] = ()
    merge_order: tuple[str, ...] = ()  # task_ids, planned not emergent
    gates: tuple[GateResult, ...] = ()

    budget: Budget = Budget()
    escalation: EscalationPolicy = EscalationPolicy()
    partial_failure: PartialFailurePolicy = PartialFailurePolicy.HUMAN_DECIDES

    tokens_spent: int = 0
    usd_spent: float = 0.0
    started_at: datetime = Field(default_factory=_now)

    def over_budget(self) -> bool:
        return (
            self.tokens_spent > self.budget.max_tokens
            or self.usd_spent > self.budget.max_usd
        )

    def blocking_findings(self) -> tuple[Finding, ...]:
        return tuple(
            f
            for g in self.gates
            if not g.shadow
            for f in g.blocking
        )


# ===========================================================================
# 6. Event log — append-only. Your audit trail and your eval substrate.
# ===========================================================================


class Event(Spec):
    run_id: str
    seq: int
    at: datetime = Field(default_factory=_now)
    kind: Literal[
        "phase_entered",
        "agent_started",
        "agent_finished",
        "gate_evaluated",
        "escalated",
        "human_decision",
        "budget_warning",
        "halted",
    ]
    actor: str
    payload: dict[str, Any] = Field(default_factory=dict)


class HumanDecision(Spec):
    phase: Phase
    approved: bool
    reviewer: str
    rationale: str
    # The calibration record: did the human agree with the shadow validator?
    overturned_gates: tuple[str, ...] = ()


# ===========================================================================
# 7. Production monitoring — detection is deterministic, diagnosis is not
# ===========================================================================


class RollbackProposal(Spec):
    """The log agent produces this. It does not execute it.

    The trigger stays a deterministic alerting rule or a human. An LLM holding
    the production kill switch is the highest-authority, lowest-evidence
    component in the whole design.
    """

    run_id: str
    alert_id: str  # from deterministic alerting, not from the model
    suspected_task_ids: tuple[str, ...]
    matched_patterns: tuple[str, ...]
    confidence: float = Field(ge=0.0, le=1.0)
    evidence: ArtifactRef
    recommended: Literal["rollback", "hotfix", "monitor", "no_action"]


# ===========================================================================
# 8. The orchestrator seam
# ===========================================================================


class PhaseHandler(Protocol):
    phase: Phase

    async def run(self, manifest: RunManifest) -> RunManifest: ...


def next_phase(manifest: RunManifest) -> Phase:
    """Pure transition. Easy to unit test, which is the point."""
    if manifest.over_budget():
        return Phase.HALTED
    if manifest.blocking_findings():
        return manifest.phase  # stay put; the loop reopens
    if manifest.phase in (Phase.DONE, Phase.HALTED):
        return manifest.phase
    idx = PHASE_ORDER.index(manifest.phase)
    return PHASE_ORDER[idx + 1]


def assert_disjoint_ownership(tasks: Sequence[TaskRecord]) -> None:
    """Run this before spawning the swarm, not after the conflicts appear."""
    seen: dict[str, str] = {}
    for task in tasks:
        for glob in task.owned_globs:
            if glob in seen:
                raise ValueError(
                    f"Ownership collision on {glob!r}: {seen[glob]} and {task.task_id}. "
                    "Return to the decomposer; do not let agents resolve this."
                )
            seen[glob] = task.task_id


if __name__ == "__main__":
    m = RunManifest(run_id="r-001", repo=Path("."), request="Add retry to the ingest client")
    for _ in range(4):
        m = m.model_copy(update={"phase": next_phase(m)})
        print(m.phase)
    print("escalation at 5 failed rounds:", m.escalation.step_for(5))
