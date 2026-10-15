"""The batches feature: the structural check of ``batches.yaml`` beside the backlog.

``check`` applies ``batch_check.py``'s structural rules to every batch that is not closed or
superseded. The composition check (members queued and unclaimed) runs only when a batch is named
on ``batch_check.py``'s command line, because a running batch's members are active or complete. A
repository without a batches file has nothing to check.
"""

from __future__ import annotations

import batch_check
import paths


def check(config: paths.Config) -> list[str]:
    return batch_check.problems(config)
