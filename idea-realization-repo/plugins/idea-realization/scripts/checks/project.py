"""The project feature's check: ``project.yaml`` is valid and the control checkout is its remote.

A repository without ``.idea-realization/project.yaml`` and without ``control_remote`` gets no
report. While ``control_remote`` is unset (``local.yaml``, ``IDEA_REALIZATION_CONTROL_REMOTE``, or
a real ``control.remote`` in ``project.yaml``) the origin comparison is skipped; the rules live in
``project.control_origin``.
"""

from __future__ import annotations

import paths
from project import control_origin

__all__ = ["check"]


def check(config: paths.Config) -> list[str]:
    try:
        problem, _ = control_origin(config)
    except paths.PathError as error:
        return [str(error)]
    return [problem] if problem else []
