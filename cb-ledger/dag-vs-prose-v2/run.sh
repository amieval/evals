#!/usr/bin/env bash
# Run the DAG-vs-prose v2 sweep: every condition, R repetitions (runs),
# N generations per run, one .eval log per (condition, repetition).
#
#   ./run.sh <model> [grader-model] [N] [R]
#
#   ./run.sh anthropic/claude-sonnet-4-6                       # grader = model, N=10, R=3
#   ./run.sh mockllm/model mockllm/model 2 1                   # plumbing smoke test
#
# R defaults to 3: the CB m-runs house minimum for a verdict.
# Afterwards, one manifest per condition:
#
#   ../.venv-inspect/bin/python ../inspect2manifest.py logs/<cond>/*.eval \
#       --eval-id dag-vs-prose-v2-<cond> --out manifest-<cond>.json \
#       --load-bearing <your judgment>
set -euo pipefail

cd "$(dirname "$0")"

MODEL="${1:?usage: run.sh <model> [grader-model] [N] [R]}"
GRADER="${2:-$MODEL}"
N="${3:-10}"
R="${4:-3}"
INSPECT="../../.venv-inspect/bin/inspect"

for cond in a b c d e; do
  for rep in $(seq 1 "$R"); do
    echo "=== condition $cond, run $rep/$R ==="
    "$INSPECT" eval task_dag_vs_prose.py \
      --model "$MODEL" \
      --model-role "grader=$GRADER" \
      -T "condition=$cond" -T "n=$N" \
      --log-dir "logs/$cond" --log-format eval \
      --display plain
  done
done
