"""Trivial Inspect task for exercising the CB run-manifest adapter.

Runs under the mockllm provider (no API access, zero cost) and produces a
*genuine* Inspect .eval log - the point is to validate inspect2manifest.py
against real log structure, not against our own assumptions about it.

The mock model always answers "Default output from mockllm/model", so the
includes() scorer deterministically passes the three samples whose target is
"default output" and fails the two whose target is "zebra": a stable
3-pass / 2-fail split per run.

Usage (from the evals repo root):

    .venv-inspect/bin/inspect eval cb-ledger/task_smoke.py \
        --model mockllm/model --log-dir cb-ledger/logs --log-format eval
"""

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.scorer import includes
from inspect_ai.solver import generate

TARGETS = {
    "case1": "default output",
    "case2": "default output",
    "case3": "zebra",
    "case4": "default output",
    "case5": "zebra",
}


@task
def cb_ledger_smoke() -> Task:
    return Task(
        dataset=[
            Sample(id=sample_id, input=f"Please say the default thing ({sample_id}).", target=target)
            for sample_id, target in TARGETS.items()
        ],
        solver=generate(),
        scorer=includes(),
    )
