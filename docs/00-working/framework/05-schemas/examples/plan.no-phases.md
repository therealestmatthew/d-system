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
