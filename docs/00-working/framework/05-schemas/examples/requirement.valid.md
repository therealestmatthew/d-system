---
code: REQ-024
title: "Portable framework document templates and schemas"
kind: requirement
status: draft
created: 2026-09-19
---

# Portable framework document templates and schemas

## Overview

A new repository adopting this governance model needs a fixed set of document shapes to copy, each
with a schema that says whether a document has the shape. Today several shapes exist only as
unvalidated drafts, so a repository that copies them has no way to check its own documents.

## Requirements

**R01 — Governance and protocol documents differ by structure.**
The governance schema requires a rule, the problem it solves and its incident or rationale; the
protocol schema requires a trigger, steps, exit criteria and failure handling. Each rejects the
other's shape.
*Verification:* `uv run python docs/00-working/framework/05-schemas/check_schemas.py` cross-validates
one example of each against the other schema; both fail.

**R04 — Requirement and plan schemas validate their own templates.**
Each validates a filled instance of its template and rejects an instance missing a required section.
*Verification:* the same script validates a passing and a deliberately incomplete instance of each.

## Scope

In scope: templates and JSON schemas for governance, protocol, phase, requirement, plan and session
documents, and the script that checks them.

Out of scope: packaging the templates as a starter kit, and any change to this repository's own
governance validator.

## Acceptance criteria

- R01 and R04 each pass their stated verification.
- Every template's level-2 headings satisfy its own schema's section rules.
