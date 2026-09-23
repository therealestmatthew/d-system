---
id: mem-proc-never-pass-file-content-through-a-heredoc
title: Never Pass File Content Through a Heredoc
type: procedure
tags: [agentic-systems, ai-tools, automation]
source_model: anthropic/claude-opus-5
project: d-system
created: 2026-09-23
updated: 2026-09-23
confidence: high
related: [mem-proc-pipe-discards-the-exit-code, mem-proc-check-that-cannot-fail, mem-proc-hook-blocked-writes-hand-off-a-candidate]
scope: global
---

## The rule

**Write file content with the host's file-writing or file-editing tool, not through a shell
heredoc.** A heredoc is shell syntax, and the text inside it is only as safe as its terminator is
unique. Text that itself contains shell — a code example, a heredoc of its own, backticks, `$(...)`
— can end the outer heredoc early, and the shell then **executes** whatever follows as commands.

This matters most where it is easiest to reach for a heredoc: editing a document that *documents
shell*, such as a skill, a runbook or an operations document. That is exactly the text most likely
to contain `<<'EOF' ... EOF` itself.

When a heredoc is genuinely the right tool — a short script with no shell inside it — give it a
terminator that cannot occur in the body (`<<'PYEOF'`, not `<<'EOF'`), and keep it short. When the
content is long, or contains any shell at all, write it to a file with the file-writing tool first
and run the file.

## The worked example

**2026-09-23, `phase-part-03`.** An agent edited a skill source file with a Python script passed
through `python3 - <<'EOF'`. The replacement text contained the skill's own example,
`uv run python - "$CORPUS" <<'EOF' ... EOF`. The inner `EOF` line ended the outer heredoc. Python
failed on an unterminated string, and bash went on to run the rest of the text as commands. The
backtick-quoted fragments in the prose, such as `` `manifest.json` `` and
`` `uv run python tools/build_idea_corpus.py --out "$CORPUS"` ``, were command substitutions. The
last one ran for real, with `$CORPUS` unset. It built a full idea corpus, about 4 MB in five files,
into the worktree root, because `--out ""` resolves to the current directory.

Nothing tracked was damaged, only because the stray files landed in the agent's own worktree and
were untracked. The same slip in a directory holding real files, or with a destructive command in
backticks, would have run just as silently. The effective fix was to redo the edit with the
file-editing tool. The skill's example commands also gained a `${CORPUS:?}` guard, so an unset
variable now stops the command instead of defaulting to the current directory.

**A second failure mode, recalled by the owner and not verified from the session above:** a heredoc
carrying a very long file failed and was resolved by switching to the file-writing tool. Whatever
the exact mechanism, the fix is the same: file content goes through the tool built to write files.

## Why this is model-agnostic

Nothing here depends on a particular model or harness. It is a property of POSIX shells: a heredoc
ends at the first line matching its terminator, and unquoted backticks and `$(...)` in the following
text are executed. Any agent that composes shell to write files will reach for a heredoc because it
fits in one command, and will hit this the first time the content contains shell.

It is the same shape as [a pipe discards the exit code](a-pipe-discards-the-exit-code-you-were-guarding-on.md):
a convenience construction quietly changes what the shell does, and nothing reports it. Content is
data, and a heredoc makes it code.
