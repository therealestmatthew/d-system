---
id: amazon-dynamodb
kind: entity
title: Amazon DynamoDB
author: <handle>
created: '2026-10-14'
updated: '2026-10-14'
status: active
tags:
- aws
- data-layer
sources:
- ARCH-002
- Figure 4
---

Amazon DynamoDB holds case state: the validated agent outputs for one case. Each tenant has its own table set. Case state is case-scoped, not claimant-scoped.
