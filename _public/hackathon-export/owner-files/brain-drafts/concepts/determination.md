---
id: determination
kind: concept
title: Determination
author: <handle>
created: '2026-10-14'
updated: '2026-10-14'
status: active
tags:
- glossary
- unemployment-insurance
sources:
- ARCH-002
- Figure 4
---

General knowledge, not stated in ARCH-002 or Figure 4: a determination is the agency's formal decision on a claim, for example whether a claimant is eligible for benefits.

In this architecture, the orchestrator runs Pass 2 on each proposed determination. The examiner makes the determination; Claude only recommends. Examiner-approved findings sent outbound are advisory and never go to the determination.
