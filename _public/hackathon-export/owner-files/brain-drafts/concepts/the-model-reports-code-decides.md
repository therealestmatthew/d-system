---
id: the-model-reports-code-decides
kind: concept
title: The model reports; code decides
author: <handle>
created: '2026-10-14'
updated: '2026-10-14'
status: active
tags:
- principle
- reasoning-core
links:
- aws-step-functions
- case-synthesis-agent
- statutory-application-agent
- bidirectional-flagging-agent
- notice-drafting-agent
sources:
- ARCH-002
- Figure 4
---

Figure 4 states the rule: "The model reports. Code decides."

The four Claude agents produce outputs. Code controls everything else: the orchestrator (AWS Step Functions) assembles context, applies the escalation rules, and runs the gates, which are also code: an ingress gate, a hop gate after every agent, and an egress gate. Only validated agent outputs become case state.
