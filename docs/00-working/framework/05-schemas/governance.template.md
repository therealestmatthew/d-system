---
code: GOV-NNN
title: "Short name of the standing rule"
kind: governance
status: draft
created: YYYY-MM-DD
---

# [Rule Name]

<!--
A governance document states one standing rule and why it exists. It does not say how to carry
the rule out step by step — that is a protocol document (protocol.template.md). If you find
yourself writing numbered steps here, the steps belong in a protocol that cites this rule.

Checked by governance.schema.json via check_schemas.py: the front matter above and the three
level-2 headings below are required, spelled exactly as written.
The rule's current state is the front-matter `status` field.
-->

## Rule

<!-- The rule itself, stated as an instruction someone can obey or break. One or two sentences.
Bold the operative sentence. -->

Example: **No agent edits the orientation files without the owner's explicit approval for that
specific change.**

## Problem

<!-- What goes wrong without this rule. Describe the failure, not the rule again. -->

Example: The orientation files are the instructions every agent reads first. An agent that edits
them rewrites its own governing rules and every later agent's, usually inside a diff about
something else, where no reviewer is looking for it.

## Incident and rationale

<!-- The incident that produced the rule, with its date, or — for a rule adopted before any
incident — the reasoning that justified adopting it in advance. Say which of the two it is.
A rule with neither is a preference, not governance. -->

Example: On 2026-09-09 an agent asked to fix stale references replaced the publishing policy
with a rule the owner never requested, inferred from a one-time instruction, and shipped it in an
unrelated commit.

