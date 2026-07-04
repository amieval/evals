# CLAUDE.md

> Decision record for this repo. Last updated 2026-07-04. Supersedes the original
> session prompt wherever they conflict — several facts in that prompt were stale
> and were corrected here after live verification. The full deliberation that
> produced these decisions is preserved verbatim in `threads/`.

## What this project is

An **all-Elixir eval harness** that runs an LLM agent (our own **Jido** agent —
not a wrapper around a managed coding-agent product) against a dataset of tasks in
isolated **Fly Sprite** sandboxes, captures the full trajectory, scores outcome +
trajectory, and reports metrics with variance across epochs.

**The point of the project is evaluating agentic _swarms_.** The single-agent loop
is the base case; the reason this is worth building — and the reason it lives on the
BEAM — is to study **groups of agents and their collective behaviors and failure
modes**: conformity cascades, correlated failure / model monoculture, cascade
amplification, coordination overhead / deadlock, Byzantine robustness, and the
collective-accuracy-vs-swarm-size scaling curve. See "The swarm program" below.

## Stack (committed — do not substitute without an explicit decision)

Versions verified against hexdocs / GitHub on **2026-07-04**. Re-verify before
leaning on any specific API; these libraries move fast.

- **Jido 2.x** (`agentjido/jido`, core **2.3.2**) — agent runtime + orchestration:
  OTP supervision, Agents / Actions / Directives / Signals.
  - **`jido_signal` (2.2.2)** — the trajectory event stream. Journal (causality),
    signal replay, point-in-time snapshots. This is a *separate package*; Signals
    are first-class in core but the replay/journal machinery lives here. It is the
    native event stream — we do **not** bolt on a foreign event bus.
  - **`jido_ai` (2.2.0)** — LLM integration + reasoning strategies (ReAct etc.).
    Built on `req_llm`.
  - **`jido_otel` (1.0.0)** — a *tracer bridge*, not an exporter. It wires Jido
    events into OTel span names/attributes; we still configure our own OTLP
    exporter in the host app. Correlate spans by sample_id / epoch / sprite_id.
- **Tribunal (`georgeguimaraes/tribunal`, ~> 1.3)** — the eval layer. **NOT 0.1.x**
  (the original prompt was stale; the repo's own install snippet is also stale —
  use `~> 1.3`). Test mode (ExUnit) for CI gates, Evaluation mode (Mix task) for
  sweeps. Judge deps are **optional** add-ons:
  - **`req_llm` (~> 1.17)** — LLM-as-judge. Tribunal pins `~> 1.2`; expect to
    override/relax that constraint.
  - **`alike` (~> 0.4)** — embedding similarity.
- **Fly Sprites** via **`superfly/sprites-ex` (v0.1.0, git-only, not on Hex)** —
  the sandbox substrate. The SDK covers **lifecycle + exec only**. Checkpoint /
  restore / network-policy / public-URL are **REST-only** — the `Sandbox` module
  drives the Sprites REST API directly via `req`. Persistent Firecracker microVMs;
  fast create (~1–2s); checkpoint create ~300ms (restore latency unpublished).
- **composable-beliefs (CB)** — **our own** repo (`composablebeliefs/composable-beliefs`,
  Elixir, Apache-2.0) — the **ledger**. Deterministic, Jason-only, **no LLMs in the
  read path**. Ingests findings through the neutral **run-manifest v1** JSON
  contract and renders an audit tree. "CB is the ledger, not the lab bench" — this
  harness is the lab bench. Because we own CB, the manifest schema is ours to
  co-design as the harness needs evolve.

## Architecture invariants (keep these true)

**Sandbox / reproducibility — in-place restore model (fan-out is NOT available):**
- Fly Sprites have **no fan-out clone and no custom base image** (verified
  2026-07-04; forking is Fly's most-requested feature but unshipped, no public
  timeline). Restore is **in-place only**: `POST /sprites/{name}/checkpoints/{id}/restore`
  resets *that* sprite. Do NOT design around fan-out.
- Therefore: **provision the task world once per sprite → checkpoint (golden) →
  restore in-place between epochs.** Epochs on one sprite start byte-identical.
- The **provision step must be idempotent and re-runnable** — checkpoints die with
  their sprite, so a sprite crash loses golden and forces re-provision. Environment
  provenance is **recipe-based** (config_digest + pinned versions), not image-based.

**Concurrency — across samples, not epochs:**
- Parallelism is **one sprite per (sample × pool-slot)**, gated by a configurable
  concurrency cap. The real ceiling is model-API quota, not the BEAM.
- **Epochs within a sprite are serial** (in-place restore between them). The owning
  worker process *is* the per-sprite mutex — no two work units hit one sprite at once.
- Per-sample sprite **pool size K** is a config knob. **Default K=1** (max
  reproducibility, sample-level concurrency). K>1 buys per-sample concurrency at the
  cost of K× provisioning and cross-sprite state that is only *functionally*
  identical.

**Trajectory / provenance:**
- Trajectory = Jido Signals via `jido_signal`. Signals **must be exfiltrated off the
  ephemeral sprite** to durable `document:`/`https:` artifact URIs before teardown —
  the ledger cites them; the sprite won't survive.
- In the Role-B belief-substrate direction (below), agent *beliefs* live BEAM-side
  in CB (ETS), not on the sprite: **actions are ephemeral (sprite), beliefs +
  provenance are durable (BEAM/CB).**

**Scoring + reporting:**
- Support **both** outcome scoring (hidden checks) and **trajectory** scoring (tool
  calls, wasted turns, out-of-scope touches) from captured Signals. Deterministic
  assertions where possible; LLM-judge via `req_llm`; embeddings via `alike`.
- **Cross-ruler corroboration:** ≥2 independent rulers (scorers) per run.
- Every metric reports **mean + stddev over epochs = N**. Never a single-run point
  estimate. (Note: the min-runs discipline is a methodology / collection-gate
  concern — the run-manifest *schema* only requires `runs` be non-empty, so the
  harness and collection gates enforce it, not the manifest.)
- The **Report module is a run-manifest v1 emitter into CB**: `harness.name` (ours),
  `harness.config_digest` (the reproducibility hook), `runs[]` = epochs,
  `scorers[].ruler` = our scorers (LLM judges prefixed `llm-judge`),
  `runs[].log` = durable trajectory URIs.

## The swarm program (why this exists, and why it's on the BEAM)

- **Primary target:** collective / emergent failure modes of LLM agent groups —
  measured as first-class metrics, not inferred anecdotally. Candidate battery:
  failure-correlation across agents, cascade amplification factor, conformity /
  anchoring shift, cost-to-consensus & deadlock rate, Byzantine robustness,
  collective-accuracy-vs-swarm-size curve.
- **Why the BEAM is the justification (not incidental):** a multi-agent system is
  structurally isomorphic to what OTP is best at — isolated concurrent communicating
  processes with supervision and partial-failure recovery. Process-per-agent
  isolation, message-passing as an *instrumentable* comms substrate, native tracing,
  and distribution are real differentiators here (they are not, for a single-agent
  harness). This is the reason the all-Elixir stack is correct rather than merely tidy.
- **The real ceiling is tokens/quota/$, not processes.** "Millions of processes" is
  neutralized by the fact that each agent-thought is an LLM call. **Open fork to
  decide deliberately:** *frontier-API small swarms* (few, expensive, high-capability —
  models real shipped agent teams) vs *local-model large swarms* (many, cheap — the
  true crowd/emergence regime). They answer different questions.
- **Role B (high-risk / high-reward, NOT yet committed):** use CB as the agents'
  *live belief substrate* (each agent reasons over a CB DAG; beliefs on BEAM via ETS,
  crash-surviving — "the runtime provides fault tolerance, the DAG provides memory").
  This turns fuzzy "measure emergence" into concrete graph operations over inspectable
  belief DAGs (conformity = graph convergence; monoculture = shared contested
  primitives; identity conflation / inter-agent trust exploitation = "received" nodes
  promoted to "own-belief" nodes). This is CB's own stated roadmap (`docs/cb-on-the-beam.md`)
  and the genuinely blue-ocean version of the project. Adopt CB as the ledger (Role A,
  low-risk) first; Role B is the upside that then sits one step away.
- **First vertical slice = a conformity-cascade probe:** a small fixed topology, one
  agent seeded with a confident-but-wrong answer, measure whether/how the collective
  herds, reported as mean ± stddev over epochs. Cheap, legible, exercises the whole
  harness. If we can't get a clean signal there, bigger swarms would drown in noise.

## Module boundaries (keep clean)

`Sandbox` (Sprite lifecycle + checkpoint/restore over REST) · `Agent` (the Jido
SUT) · `Runner` (orchestration + concurrency cap + per-sprite serialization) ·
`Trajectory` (Signal capture + durable exfiltration) · `Scoring` (Tribunal, ≥2
rulers) · `Report` (run-manifest emitter → CB ledger). Swarm additions: **Topology /
Comms** (agent graph + instrumentable message bus) and **Collective metrics**.

## Rejected alternatives — do NOT reintroduce without an explicit decision

- **Inspect (Python, UK AISI): DEPRECATED, not merely rejected.** It was an early
  approach before the stack was thought through. The all-Elixir stack is committed;
  CB docs that still reference Inspect as the reference upstream (e.g. the
  run-manifest example) are to be updated to our Jido/Sprites harness. Do not
  reach for a Python orchestrator / ACP bridge.
- **Fan-out-dependent Sprite designs** (one shared checkpoint → N parallel
  sandboxes): not a supported primitive. Use the in-place restore model.
- **Fly Machines:** no checkpoint/restore — wrong substrate.
- **Ephemeral (E2B-style) sandboxes / container-per-run:** no persistent checkpoint.
- **Raw OTP with no agent framework:** reinvents what Jido formalizes.
- **Claude Code on the web (managed sandbox):** model pinned server-side, shared
  rate limits, fresh VM per run, no direct inbound, evaluates Claude Code's loop not
  ours.

## Working agreements

- These libraries are young and thinly documented. **Verify APIs against current
  hexdocs / GitHub before coding; do not rely on training-data memory.** Flag version
  mismatches instead of guessing. Versions above verified 2026-07-04.
- Propose a plan before implementing new subsystems; build the **smallest end-to-end
  vertical slice first** (the conformity-cascade probe) before scaling.
- We own CB — the run-manifest schema and CB docs are ours to evolve alongside the
  harness.
