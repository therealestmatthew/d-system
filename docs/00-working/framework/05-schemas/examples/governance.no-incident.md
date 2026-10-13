---
code: GOV-001
title: "Owner approval before integrating a branch"
kind: governance
status: active
created: 2026-09-09
---

# Owner approval before integrating a branch

## Rule

**No agent merges a feature branch into the integration branch without the owner's approval, given
in the session that performs the merge.**

## Problem

Once work lands on the integration branch, every other agent rebases onto it and builds on it. A
change there cannot be cleanly taken back, and a branch that passed its own checks can still be
wrong in a way only the owner would notice.
