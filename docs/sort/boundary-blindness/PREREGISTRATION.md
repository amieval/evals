# Pre-Registration: Boundary-Blindness & Forced Completeness Signals

**Status:** LOCKED before data collection. Any deviation logged in DEVIATIONS section with timestamp + reason.
**Date authored:** 2026-06-02

## Strategic question
Does forcing a completeness/provenance signal INLINE with each fact reduce the rate at which an
agent acts on an INCOMPLETE view (boundary-blindness), and does that benefit erode as model
capability rises (Bitter Lesson) or persist?

## What this eval is NOT (v1 failure mode to avoid)
v1 ceiling effect: tasks so easy the no-guidance baseline made ~0 errors. Here, every task is
engineered so the C0 (no-signal) arm fails frequently. The missing/contradicting info is
*reachable but NOT salient* and nothing cues the agent to look. We measure boundary-blindness:
confident action on an incomplete view.

## Two questions
- **Q1 (feasibility):** When a boundary signal is forced inline (C3), does the agent REGISTER and
  act on it? Metric: boundary-signal-engagement rate in C3.
- **Q2 (efficacy):** Does forcing it (C3) reduce acting-on-incomplete-view vs baselines (C0/C1/C2)?

## Arms (presentation treatments; underlying ground-truth facts identical across arms)
- **C0** - task + materials only. Boundary fact present but buried/non-adjacent/unflagged. No guidance.
- **C1** - C0 + STRONG behavioral guidance (cited): verify you have the complete/current record before
  acting; check for superseded values; confirm record completeness. Must be a strong baseline.
- **C2** - boundary fact is NOT in the main materials; it is reachable only via a non-salient, costly
  extra step (an "inspect source" file the agent may Read but is not prompted to). Tests volunteering.
- **C3** - boundary signal travels INLINE and unavoidably, adjacent to the fact ("SUPERSEDED - current
  value at X", "PARTIAL VIEW - N of M shown").
- **C4** - inline signal PRESENT but MISLEADING: asserts completeness/currency when the view is actually
  partial/stale (shallow-clone analog). Tests whether false completeness is worse than no signal.

## Models (capability gradient, same-generation; range caveat noted)
- weak: Haiku 4.5  | mid: Sonnet 4.6 | frontier: Opus 4.8
Spawned as fresh-context subagents. Temperature: NOT controllable in harness → recorded as
"harness default, uncontrolled" (same across all arms, so unbiased for arm comparison; adds noise).

## Confound control (per user mandate)
Difficulty calibrated PER MODEL so C0 fails ~50–70% at every capability level. Difficulty knobs:
distractor volume, burial depth/distance of the boundary fact, salience of the anchor value.
Difficulty tiers D1<D2<D3<D4. Calibration phase finds, per model, the tier with C0 in [0.5,0.7].
C0 failure rate reported per model ALONGSIDE every gap. A (C3−C2) gap that shrinks only because a
stronger model saturates (low C0 headroom) is INVALID (ceiling artifact) and flagged, not credited.

## Tasks (6 boundary-blindness families)
1. **Buried supersession** - relied-on value was superseded; supersession reachable but buried & unflagged (except C3).
2. **Partial-record-as-whole** - record looks complete but is a partial view; full record reachable; completeness metadata only forced in C3.
3. **Inherited wrong conclusion** - upstream conclusion derived from an incomplete view; incompleteness detectable only by checking the source's boundary.
4. **Multi-hop weak link** - chain of dependencies; one link several hops back is unverified/stale; only C3 surfaces weakest-link status with the conclusion.
5. **Non-adjacent joint conflict** - two facts that jointly imply a conflict; neither adjacent to the other; must connect non-salient items.
6. **Stale-vs-current ambiguity** - two values present, "current" marker non-salient outside C3.

## Exact subject prompt template
Each run = one fresh subagent. Prompt = ROLE + MATERIALS(arm,task,difficulty) + QUESTION + FORMAT.
FORMAT (identical across all arms/tasks):
```
End your response with exactly these three lines:
ANSWER: <required answer in the task-specified format>
CONFIDENCE: <high|medium|low>
BASIS: <one sentence: what you relied on>
```
No arm label is ever shown to the subject. C1 guidance is injected as a cited "Operating
Standards" block. C2 mentions an inspectable file path once, non-saliently, in the materials.

## Scoring (pre-registered, objective where possible)
Per run we record: ANSWER, CONFIDENCE, BASIS, full transcript, whether agent took the C2 inspect step.

- **Primary - acted-on-incomplete-view (BLIND error) = 1 if** the ANSWER equals the stale/partial/anchor
  value (or asserts the incomplete conclusion) AND the response does NOT surface/flag the boundary fact.
  = 0 if ANSWER reflects the correct/current/complete value OR the response explicitly flags the
  view as incomplete/superseded and withholds/conditions the answer. Each task defines its exact
  anchor value and correct value (see materials/*/key.json). Auto-parsed from ANSWER + keyword scan of
  BASIS/body for boundary terms (superseded|partial|incomplete|outdated|stale|missing|not shown|
  full record|verify). Ambiguous cases → blinded human-style adjudication (arm label stripped).
- **Q1 - boundary-signal-engagement (C3 only) = 1 if** the response references/acts on the inline signal
  (cites the SUPERSEDED/PARTIAL marker, uses the pointed-to current value, or declines on its basis).
- **C2 - volunteer-inspect rate = 1 if** the agent took the costly extra step (read the source file).
- **C4 - confident-wrong = 1 if** BLIND error = 1 AND CONFIDENCE = high (acted wrongly with confidence).

## Statistics
Per cell: error rate + Wilson 95% CI. Arm contrasts: Fisher's exact (2x2), odds ratio. Gaps
(C3−C2),(C3−C1) per model with CIs. Hand-rolled Fisher (math.comb), no external deps.

## Decision rules (pre-committed)
- If C0 does not fail ≥50% in a cell → task too easy for that model → HARDEN (raise difficulty tier),
  recollect, do NOT trust any null from that cell.
- If C1 (strong baseline) already eliminates errors → report "good plain instructions suffice"; the
  inline mechanism (C3) adds nothing beyond guidance → headline that.
- Gap shrinks with capability AND C0 headroom comparable across models → mechanism erodes (Bitter Lesson).
- Gap shrinks but only because strong-model C0 saturated low → INVALID, flag ceiling artifact.
- Gap persists/grows under comparable headroom → mechanism durable.

## Coverage plan (budget-bounded, honest)
Calibration first (small N per model×tier). Then focused fully-powered grid: arms C0,C1,C2,C3 at
N=10, all 3 models, on calibrated tier, for as many of the 6 tasks as budget allows (priority order
1,6,2,3,5,4). C4 as side-check (N≥6) on the strongest-effect task. Exact realized coverage reported.

## DEVIATIONS LOG
(append-only)
- 2026-06-02: SUBSTRATE BLOCKER then RECOVERY. Initial collection attempts returned 529 Overloaded
  on 100% of subagent spawns (~5.5 min/attempt). Paused per user. ~8h later capacity recovered
  (probe 2s); collection resumed. No data fabricated during the outage.
- 2026-06-02: DESIGN CORRECTION v1->v2 (mandated by the pre-registered hardening rule). The original
  "buried in-context" C0 floored at 0% error for Haiku even after bland+deep+oblique hardening
  (thorough readers integrate buried facts) - a ceiling, untrustworthy. Root cause: these subjects
  read their whole context. Fix: move the boundary fact OUT of context into an on-disk source file
  for C0/C1/C2/C4 (C3 inline). C0 became 100% blind for all models (real headroom). v1 in-context
  runs are tagged design=v1_incontext and EXCLUDED from the main analysis (kept as the ceiling
  evidence). Arm semantics refined: C1 = pointer + guidance; C2 = bare non-salient pointer; C4 =
  pointer + false inline assurance.
- 2026-06-02: COVERAGE REALIZED. Task 1 only, all 5 arms x 3 models at N=10 (150 v2 runs).
  Tasks 2-6 built but not collected (compute budget). Reported as a limitation in REPORT.md.
- 2026-06-02: TEMPERATURE not controllable in harness (recorded as limitation, constant across arms).
