---
id: aws-step-functions
kind: entity
title: AWS Step Functions
author: <handle>
created: '2026-10-14'
updated: '2026-10-14'
status: active
tags:
- aws
- reasoning-core
sources:
- ARCH-002
- Figure 4
---

AWS Step Functions is the orchestrator, and the orchestrator is code. It assembles context for each agent, applies the gates on every hop (ingress gate, a hop gate after every agent, egress gate) and applies the escalation rules. Pass 1 runs when the case opens; Pass 2 runs on each proposed determination.
