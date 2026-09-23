"""The dispatch adapter's interface, and the kill switch's flag file.

PLAN-039.01 section 8: one module owns every agent invocation, binding the role contract
(`phase-irs-03`), checking the kill switch and remaining budget before dispatch, and
recording dispatch and result in the ledger. The real Claude Agent SDK adapter is not built
by this phase -- it needs the role-contract binding and budget accounting this skeleton
does not yet have callers for -- so `Dispatcher` is a `Protocol` that `tick.py` calls
through, and callers (tests today; a later phase's real adapter) supply the implementation.
This is the "stub dispatcher" PLAN-039.01 section 10 names as the testing surface.

**The kill switch ships as a flag file now; its enforcement does not.** `halt` writes
`_working/orchestrator-halt`, `resume_dispatch` removes it -- both verbs the CLI exposes
today, per PLAN-039.01 section 9 ("the verbs ship with the skeleton"). Checking the flag
immediately before every dispatch, so a halt takes effect mid-loop, is `phase-irs-11`'s
enforcement and tests. Outside `data/`, so no rebuild or reset tool can disarm it; gitignored
but under the never-deleted-without-approval protection `_working/` already carries.
"""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Protocol

ROOT = Path(__file__).resolve().parents[2]

#: The kill switch's flag file. Outside data/ so demo_reset.py and rebuild_db.py, which both
#: treat data/ as regenerable, cannot disarm it (PLAN-039.01 section 9).
HALT_FLAG = ROOT / "_working" / "orchestrator-halt"


@dataclass(frozen=True)
class DispatchResult:
    """What a dispatch produced, in the shape `ledger.py` records as a `dispatch_result`."""

    outcome: str
    input_tokens: int = 0
    output_tokens: int = 0


class Dispatcher(Protocol):
    """What `tick.py`'s `advance()` calls to invoke an agent for a run.

    `refs` is the run's own thin-state refs at the moment of dispatch -- never anything
    wider -- and `budget_cap` is the per-dispatch ceiling PLAN-039.01 section 8 requires so a
    single in-flight dispatch's overshoot is bounded.
    """

    def __call__(
        self, *, run_id: str, role: str, refs: dict[str, str], budget_cap: int
    ) -> DispatchResult: ...


def unimplemented_dispatcher(
    *, run_id: str, role: str, refs: dict[str, str], budget_cap: int
) -> DispatchResult:
    """The default `Dispatcher` -- refuses rather than guessing at an SDK binding.

    Deliberately not a real adapter: binding the Claude Agent SDK's role contracts and
    budget accounting into this call is not this phase's scope. Every caller in this
    package's own tests supplies a stub instead.
    """
    raise NotImplementedError(
        "no Dispatcher was supplied -- the real Claude Agent SDK adapter is out of "
        "phase-irs-04's scope; pass a Dispatcher (see src/orchestrator/dispatch.py)"
    )


def halt(flag: Path = HALT_FLAG) -> None:
    """Arm the kill switch. Dispatches in flight finish; nothing new starts once enforced."""
    flag.parent.mkdir(parents=True, exist_ok=True)
    flag.touch()


def resume_dispatch(flag: Path = HALT_FLAG) -> None:
    """Disarm the kill switch."""
    flag.unlink(missing_ok=True)


def is_halted(flag: Path = HALT_FLAG) -> bool:
    return flag.exists()
