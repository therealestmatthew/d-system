#!/usr/bin/env python3
"""Completion edit: set one phase's status to complete in backlog.yaml and bump `updated`. usage: complete_phase.py <phase-id>"""
import re, sys, datetime as dt
p = 'docs/09-backlog/backlog.yaml'; pid = sys.argv[1]
s = open(p).read()
m = re.search(r'^- id: %s\n(.*?)(?=^- id: |\Z)' % re.escape(pid), s, re.S | re.M)
b = m.group(0)
assert '\n  status: active\n' in b, 'phase is not active'
nb = b.replace('\n  status: active\n', '\n  status: complete\n', 1)
s = s.replace(b, nb, 1)
s = re.sub(r"^updated: '\d{4}-\d{2}-\d{2}'", "updated: '%s'" % dt.date.today().isoformat(), s, count=1, flags=re.M)
open(p, 'w').write(s); print('completed', pid)
