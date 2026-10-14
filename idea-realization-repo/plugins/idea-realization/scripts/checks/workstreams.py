"""The workstreams feature: its check and the ``workstreams`` command.

``check`` reports every problem in ``<docs_root>/workstreams.yaml`` and in the working phases that
reach into a workstream another developer claimed; the rules live in ``workstreams.problems``. A
repository without the registry has not adopted workstreams and gets no report.

``workstreams`` runs ``workstreams.py`` with the remaining arguments: ``show``, ``claim <id>``,
``release <id>`` or ``check``.
"""

from __future__ import annotations

import paths
from workstreams import COMMANDS, problems

__all__ = ["COMMANDS", "check"]


def check(config: paths.Config) -> list[str]:
    return problems(config)
