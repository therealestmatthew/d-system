# Codex capability probe response

## 1. Sub-agents

- **[demonstrated]** I can dispatch sub-agents with separate context using `fork_turns: "none"`. The dispatch returned:

  ```text
  {"task_name":"/root/capability_probe"}
  ```

- **[demonstrated]** The agent spawned its own child. I received only the parent's final report, not either agent's intermediate reasoning:

  ```text
  Child result: NESTED_OK

  PARENT_OK
  ```

- **[demonstrated]** A completed agent can be resumed with its prior context intact. On a follow-up turn, it correctly recalled its child's result:

  ```text
  NESTED_OK

  RESUMED_OK
  ```

- **[demonstrated]** More importantly, an agent interrupted while running can be resumed with its context intact. I gave it `PARTWAY_731`, waited for its readiness message, interrupted it during a 30-second wait, and resumed it:

  ```text
  READY_PARTWAY
  ```

  Interruption result:

  ```text
  {"previous_status":"running"}
  ```

  Resumed result:

  ```text
  PARTWAY_731

  RESUMED_AFTER_INTERRUPT
  ```

- **[documented]** The exact callable agent types exposed to this session are:

  - Built-in: `default`, `explorer`, `worker`
  - Repository-defined: `demo-adversary`, `demo-creator-docs`, `demo-creator-py`, `demo-creator-web`, `demo-orch-content`, `demo-orch-data`, `demo-orch-stage`, `demo-validator-check`, `demo-validator-code`, `demo-validator-web`, `idea-triage`

- **[documented]** The concurrency limit is four agents total, including the coordinator. Therefore this coordinator can have at most three other agents active concurrently. A five-item batch cannot run all five items simultaneously.

- **[documented]** Existing custom agents are defined as TOML files under `.codex/agents/`. Their observed fields include:

  ```toml
  name = "idea-triage"
  description = "..."
  model = "gpt-5.6-luna"
  model_reasoning_effort = "medium"
  sandbox_mode = "workspace-write"
  developer_instructions = "..."
  ```

- **[documented]** I can invoke loaded custom agents by passing their exact name as `agent_type` when dispatching.

- **[uncertain]** I can author another TOML definition during an authorized write task, but I don't know whether a newly created definition is hot-loaded into the current session or requires a new session.

- **[demonstrated]** Default sub-agents can dispatch children.

- **[documented]** Several custom roles say "Spawns no subagents" or prohibit dispatch in their developer instructions.

- **[uncertain]** I don't know whether those prohibitions remove the dispatch tool technically or are instruction-level controls. I did not violate a role's instructions to test that.

- **[documented]** Long prompts are passed in the dispatch's `message` string. Related context may be inherited with `fork_turns: "all"` or a positive number, or excluded with `"none"`.

- **[documented]** A long repository prompt can instead live in a tracked file and be referenced in the dispatch. Under this repository's rules, cross-worktree material belongs in `_tmpagent/` with its claim protocol, not ignored `_working/`.

- **[uncertain]** No maximum dispatch-prompt length is stated in my tool interface. I don't know the hard limit.

## 2. Asking the human a question

- **[documented]** A structured question mechanism exists, but it is available only in Plan mode. It accepts one to three questions per batch.

- **[documented]** Each question supports two or three predefined choices, with one recommended choice first. The client adds a free-form "Other" option.

- **[documented]** The structured mechanism waits for the answer within the active interaction.

- **[documented]** Outside Plan mode, I ask in prose, end my turn, and resume when the human replies.

- **[documented]** I cannot switch myself into Plan mode with any exposed tool.

- **[documented]** The repository's `backlog` skill says to batch up to four structured questions. That does not translate exactly: my mechanism permits at most three.

- **[uncertain]** I did not invoke the structured question mechanism because this session is not in Plan mode, so those properties come from its tool contract rather than a live demonstration.

## 3. Models and cost

- **[documented]** The model IDs selectable for sub-agents in this session are:

  - `gpt-6-astra`
  - `gpt-5.6-sol`
  - `gpt-5.6-terra`
  - `gpt-5.6-luna`
  - `gpt-5.5`

- **[documented]** I can assign a different model to a sub-agent when using `fork_turns: "none"` or a bounded positive history count.

- **[documented]** A full-history fork inherits the parent model and does not accept a model override.

- **[uncertain]** I cannot see the exact backend model identifier currently running this root session.

- **[documented]** Using current public API token pricing as a rough cost ordering:

  | Model | Input / 1M | Output / 1M | Approximate tier |
  |---|---:|---:|---|
  | `gpt-5.6-luna` | $0.20 | $1.20 | Cheapest |
  | `gpt-5.6-terra` | $2 | $12 | Balanced |
  | `gpt-5.6-sol` | $4 | $20 | Flagship |
  | `gpt-5.5` | $5 | $30 | Expensive previous generation |
  | `gpt-6-astra` | $10 | $50 | Most expensive/capable |

  Sources: [current model catalog](https://developers.openai.com/api/docs/models) and [GPT-5.5 model page](https://developers.openai.com/api/docs/models/gpt-5.5).

- **[uncertain]** I don't know whether Codex-session or sub-agent billing maps directly to those public API prices. I cannot see this session's monetary cost.

- **[documented]** I have no exposed exact remaining-context counter.

- **[uncertain]** I therefore cannot reliably stop at a precise percentage such as "10% context remaining." The coordinator would need milestone-based handoffs or externally supplied usage telemetry.

## 4. This repository's configuration

- **[documented]** The contents of `AGENTS.md` were injected into my session context automatically before I opened the file through the shell.

- **[demonstrated]** I subsequently read the file directly, as requested by the probe.

- **[uncertain]** I cannot distinguish whether the host itself read that path at startup or an upstream layer supplied its contents as repository instructions. What I can establish is that I did not need to discover it manually to receive its rules.

- **[documented]** Applicable `AGENTS.md` instructions and the available-skills catalog are supplied at session start. Skill bodies are read only when the skill is invoked or clearly applies.

### `.codex/`

- **[demonstrated]** `.codex/` contains one configuration file and eleven agent definitions—not ten:

  ```text
  .codex/agents/demo-adversary.toml
  .codex/agents/demo-creator-docs.toml
  .codex/agents/demo-creator-py.toml
  .codex/agents/demo-creator-web.toml
  .codex/agents/demo-orch-content.toml
  .codex/agents/demo-orch-data.toml
  .codex/agents/demo-orch-stage.toml
  .codex/agents/demo-validator-check.toml
  .codex/agents/demo-validator-code.toml
  .codex/agents/demo-validator-web.toml
  .codex/agents/idea-triage.toml
  .codex/config.toml
  ```

- **[demonstrated]** There are ten `demo-*` definitions plus `idea-triage`, explaining the count of eleven.

- **[demonstrated]** `.codex/config.toml` configures one Playwright MCP server:

  ```toml
  [mcp_servers.playwright]
  command = "npx"
  args = ["@playwright/mcp@latest"]
  ```

- **[documented]** All eleven agent names appear in my callable `agent_type` registry.

- **[demonstrated]** Ten demo definitions and `config.toml` are locally ignored through `.git/info/exclude`; `idea-triage.toml` is the tracked exception.

### `.agents/`

- **[demonstrated]** `.agents/skills/` contains seven skills:

  ```text
  backlog
  checkpoint
  d-system-overview
  idea
  idea-triage
  log-anti-patterns
  orient
  ```

- **[documented]** These are Markdown `SKILL.md` procedures with YAML front matter containing `name` and `description`.

- **[documented]** All seven are loaded in this session's skill catalog. They can be invoked explicitly by name, such as `$orient`, or automatically when a request clearly matches their description.

- **[documented]** They are skills/procedures, not additional sub-agent types.

### `idea-triage.toml` tracking status

- **[demonstrated]** Exact `git check-ignore` result:

  ```text
  $ git check-ignore -v .codex/agents/idea-triage.toml
  [no output]
  exit 1
  ```

  It is not ignored.

- **[demonstrated]** Exact `git ls-files` result:

  ```text
  $ git ls-files --stage .codex/agents/idea-triage.toml
  100644 9a1ecba48f31ab4b0e55f8f48b7eacdedb8ca075 0	.codex/agents/idea-triage.toml
  ```

  It is tracked.

- **[demonstrated]** The repository remained clean:

  ```text
  ## dev...origin/dev
  ```

  `git diff --stat` produced no output.

## 5. Commands and shell

- **[demonstrated]** I can execute shell commands and successfully ran `sed`, `find`, `rg`, `git status`, `git diff`, `git check-ignore`, and `git ls-files`.

- **[documented]** The shell interface can run `git worktree add`, `git rebase`, `git merge`, and `uv run ...` mechanically.

- **[documented]** This session is sandboxed. Ordinary writes are allowed under `/code/d-system` and `/tmp`; `.git` is exposed read-only, and `/code/d-system-worktrees` is outside the writable roots.

- **[documented]** Consequently, commits, branch operations, rebases, merges, and creation of the mandated sibling worktrees may require an approval escalation.

- **[documented]** Network access is restricted. Fetch, pull, and push may also require escalation.

- **[uncertain]** I did not test remote credentials or pushing because the probe forbids changes. I don't know whether a push would succeed after approval, despite the repository documenting that it should.

- **[documented]** Destructive commands and writes outside the sandbox require explicit approval. I must also honor repository-specific restrictions: no integration into `dev` without owner approval, no unauthorized edits to `AGENTS.md` or `CLAUDE.md`, and no `_private/` access unless directed.

- **[documented]** My closest native equivalent to slash commands is a skill. Codex skills live in `.agents/skills/<name>/SKILL.md` or in the user/plugin skill locations supplied by the host.

- **[documented]** The files in `.claude/commands/` are Claude-specific adapters and are not native Codex slash commands. I can read and follow one as a plain procedure when authorized, but it is not registered as my command.

- **[demonstrated]** I can leave a shell command running and receive a persistent session ID:

  ```json
  {
    "chunk_id": "a47339",
    "wall_time_seconds": 0.251435395,
    "session_id": 32839,
    "original_token_count": 0,
    "output": ""
  }
  ```

  Polling it returned completion:

  ```json
  {
    "chunk_id": "0af8b7",
    "wall_time_seconds": 0.000001112,
    "exit_code": 0,
    "original_token_count": 0,
    "output": ""
  }
  ```

- **[demonstrated]** Completion was not delivered as an unsolicited notification; I had to poll the session.

- **[documented]** Agent work differs: I can wait for agent mailbox updates, and agents can send messages before their final response.

## 6. Honest assessment

### What I would do differently or worse

- **[documented]** I cannot keep five batch items active concurrently; the four-agent total means a coordinator plus at most three active workers.

- **[documented]** I cannot observe exact remaining context, so a protocol depending on a numeric stop threshold cannot be followed literally.

- **[documented]** I have no `maxTurns` or per-agent token-budget control in the dispatch interface. The comment at the top of `idea-triage.toml` explicitly records that Codex cannot enforce Claude's 30-turn cap.

- **[documented]** Structured questions are limited to three at once and Plan mode, while the repository's workflow text assumes batches of up to four.

- **[documented]** Worktree and Git-metadata operations can encounter sandbox approvals even when repository policy already authorizes the action.

- **[documented]** A sub-agent's final answer still enters the coordinator context. Keeping coordinator context small therefore depends on strict short-result contracts, even though intermediate work remains isolated.

### What I would do better

- **[demonstrated]** I can create genuinely context-isolated agents, choose how much history each receives, and receive only their result.

- **[demonstrated]** I can resume both completed and interrupted agents with context intact. The coordinator does not need to repay their reading cost after truncation or interruption.

- **[demonstrated]** Nested dispatch works.

- **[documented]** I can send follow-up instructions to an existing agent, interrupt one, list the live agent tree, and receive intermediate mailbox messages.

- **[documented]** I can assign cheaper or stronger models per isolated dispatch rather than using one model for the entire batch.

- **[documented]** The sandbox and approval system provides an additional mechanical guard around merges, remote access, destructive operations, and out-of-workspace writes.

### Harness-specific assumptions that do not translate cleanly

- **[documented]** `.claude/commands/`, `.claude/skills/`, and `.claude/agents/` are Claude host adapters. Codex natively uses `.agents/skills/` and `.codex/agents/`.

- **[documented]** References to `/session-start`, `/session-close`, and other slash commands are not native invocations here.

- **[documented]** "Ask through the host's structured question capability" needs a Codex-specific qualification: Plan mode only, maximum three questions.

- **[documented]** Any assumption of five parallel workers conflicts with the four-total-agent limit.

- **[documented]** Claude-specific `maxTurns` limits do not translate.

- **[documented]** The mandated sibling worktree location does not fit this session's current writable-root configuration without approval.

- **[documented]** The owner-only `/session-close` restriction remains enforceable as policy, but Codex does not natively expose that repository command anyway.

**Verdict:** **[documented]** I can perform the coordinator job—including isolated delegation, independent validation, adversarial review, real command execution, interrupted-agent resumption, model selection, and owner-gated merging—but the coordinator must schedule at most three active sub-agents, require terse result contracts, replace exact context-budget thresholds with milestone checkpoints, split structured-question batches to three and run decision points in Plan mode, and anticipate approval gates for Git metadata, sibling worktrees, and network access. **[uncertain]** The only capability I cannot promise at all is precise remaining-context measurement; I also cannot promise unattended remote pushes without first testing the runtime's approved network and credentials.
