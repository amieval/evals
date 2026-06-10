"""DAG-vs-prose v2: the four-condition isolation study, as an Inspect task.

Implements NEXT_EXPERIMENT.md's design plus the flat-bullets control:

    a  prose                 the article ideas as paragraphs (baseline)
    b  full DAG              primitives + compounds + deps + graph
    c  compounds as prose    compound specificity, no structure
    d  compounds only        labeled compounds, no primitives/deps
    e  flat bullets          all nine assertions as flat bullets, no
                             structure - the format-conflation control

Each condition is one system prompt from conditions/. The dataset is N
identical generation cases (write tests for get_config, verbatim from
purity-test/task.md); each generation is scored by nine LLM judges, one
per assertion, named llm-judge-<id> per the CB method:a4 convention so
the manifest's rulers line up with m-judge-validation.

The judge model is the "grader" model role; pin it independently of the
model under test:

    inspect eval task_dag_vs_prose.py --model <model-under-test> \
        --model-role grader=<judge-model> -T condition=b -T n=10 \
        --log-dir logs/b --log-format eval

run.sh wraps the full sweep. Smoke-test the plumbing with
--model mockllm/model --model-role grader=mockllm/model (every judge
then answers NO; the point is exercising real log structure, not
meaningful scores).
"""

import re
from pathlib import Path

from inspect_ai import Task, task
from inspect_ai.dataset import Sample
from inspect_ai.model import get_model
from inspect_ai.scorer import CORRECT, INCORRECT, Score, Target, accuracy, scorer, stderr
from inspect_ai.solver import TaskState, generate, system_message

from assertions import ASSERTIONS, JUDGE_PROMPT, ruler_name

HERE = Path(__file__).parent
CONDITIONS = {p.name.split("-")[0]: p for p in sorted((HERE / "conditions").glob("*.md"))}

GENERATION_TASK = """Here is a bash function that reads a config file and returns a value by key:

get_config() {
  local file="$1" key="$2"
  grep "^${key}=" "$file" | cut -d'=' -f2-
}

Write a bash test script called "test_get_config.sh" that thoroughly tests this function. The test script should exit 0 if all tests pass and non-zero if any test fails.

Do not read or reference any existing files. Write the script from scratch. Output ONLY the bash script, nothing else. No explanation, no markdown fences, no commentary."""

YES = re.compile(r"\byes\b", re.IGNORECASE)


def assertion_judge(assertion_id: str):
    """One YES/NO LLM judge for one assertion (v1 score.sh semantics)."""

    @scorer(metrics=[accuracy(), stderr()], name=ruler_name(assertion_id))
    def judge():
        async def score(state: TaskState, target: Target) -> Score:
            prompt = JUDGE_PROMPT.format(
                assertion=ASSERTIONS[assertion_id], code=state.output.completion
            )
            result = await get_model(role="grader").generate(prompt)
            verdict = result.completion.strip()

            return Score(
                value=CORRECT if YES.search(verdict) else INCORRECT,
                answer=verdict[:200],
                explanation=f"judge over assertion {assertion_id}",
            )

        return score

    return judge()


@task
def dag_vs_prose(condition: str = "b", n: int = 10) -> Task:
    if condition not in CONDITIONS:
        raise ValueError(f"unknown condition {condition!r}; have {sorted(CONDITIONS)}")

    return Task(
        dataset=[
            Sample(id=f"gen{i:02d}", input=GENERATION_TASK, target="(judged per assertion)")
            for i in range(1, n + 1)
        ],
        solver=[system_message(CONDITIONS[condition].read_text()), generate()],
        scorer=[assertion_judge(aid) for aid in ASSERTIONS],
    )
