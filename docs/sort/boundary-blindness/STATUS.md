# Execution Status - Boundary-Blindness Eval

## 2026-06-02: substrate blocker (RESOLVED)
First collection attempts returned **529 Overloaded** on 100% of subagent spawns (5/5 incl. a
one-token probe, ~5.5 min each to fail). The subagent harness is the only substrate for fresh-
context inference. Paused per user. ~8h later capacity recovered (probe returned in 2s) and
collection proceeded. No data was fabricated during the outage.

| attempt | result | time-to-fail |
|---|---|---|
| smoke + r1..r3 + probe (5) | 529 Overloaded | ~330s each |
| (post-recovery) probe | PROBE-OK | 2s |

## 2026-06-02: design correction v1 -> v2 (the pivotal finding)
The pre-registered "buried supersession in-context" task floored at **0% C0 error** for Haiku even
after bland + deep + oblique hardening: these tool-using subjects read their whole context and
integrate buried facts. That is the v1 ceiling. Root cause -> boundary-blindness is an
**out-of-context** phenomenon. Fix: move the boundary fact into an on-disk source file (reachable by
an extra step) for C0/C1/C2/C4; C3 carries it inline. C0 then = 100% blind for all models (real
headroom). v1 in-context runs are tagged `design=v1_incontext` and excluded from the main analysis.

## Outcome
Task-1 grid fully collected: 5 arms x 3 models x N=10 = 150 v2 runs (+12 v1 ceiling-evidence runs).
Substrate healthy. Headline: forced-inline signal (C3) works (Q1+Q2 positive) but its advantage over
a bare available check (C2) erodes to zero at the frontier (Opus volunteers to inspect 10/10), and
it never beats a strong guidance baseline (C1). See `REPORT.md`. C0 headroom = 100% all models
(collapse is genuine, not a ceiling artifact). Limitation: only Task 1 collected; Tasks 2-6 built,
not run.

## Reproduce
`python3 gen_materials.py <task> <arm> <tier>` renders a subject prompt; spawn fresh agents per
model; append `{run_id,model,task,arm,tier,design:'v2_oob',answer,confidence,basis,body,inspected}`
to `runs/results.jsonl`; `python3 scorer.py` for the full per-cell + gap + Q1 + headroom stats.
