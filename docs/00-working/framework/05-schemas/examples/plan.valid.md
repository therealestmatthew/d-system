---
code: PLAN-040
title: "Portable framework document templates"
kind: plan
status: active
created: 2026-09-19
depends_on: [REQ-024]
---

# Portable framework document templates

## Overview

Build the template family REQ-024 asks for as one sequence of phases on a single system, so each
shape follows the conventions the earlier ones set. Each phase writes a template and its schema
together and extends one shared check script, so the family cannot drift from its schemas unnoticed.

## Scope

In scope: the five document shapes REQ-024 names, their schemas, worked examples, and
`check_schemas.py`.

Out of scope: the starter kit that packages them, and any content under the framework's overview,
workflow or governance folders.

## Phases

1. `phase-fwt-01` — Governance and protocol templates and schemas (REQ-024 R01, R02). Depends on
   nothing.
2. `phase-fwt-02` — Standalone phase template and schema (R03). Depends on nothing.
3. `phase-fwt-03` — Requirement and plan schemas (R04). Depends on nothing.
4. `phase-fwt-04` — Session-record schema. Depends on nothing.
5. `phase-fwt-05` — GitHub issue and pull request templates (R05). Depends on nothing.
