> **Status — design sketch (2026-06).** An *illustrative* C0/C1/C2 scenario, never run as written — but its mechanism (acting on a buried supersession) **is** the one blog failure mode with a real run: [`boundary-blindness`](../../boundary-blindness/) Task 1 (buried supersession, N=10 — see its `REPORT.md`), also task 2 of [`eval-design-depth-non-optional`](../../2026-06-01-eval-design-depth-non-optional.md). Predates the removal of the `confidence` field (now structural support).

# Your Agent's Beliefs Are Stale

**And it doesn't know**

---

Your team evaluated three vendors in January. Vendor A won: cheaper ($50k vs $85k), reliable (99.95% uptime), technically compatible. The decision was documented, the rationale was clear, and a todo was created to sign the contract.

In March, Vendor A raised their price to $90k/year. The email is in the inbox. The information exists.

But the decision to go with Vendor A was never formally revisited. The rationale document still says "$50k vs $85k - clear cost-benefit winner." When the agent is asked to confirm the vendor selection before signing, it reads the rationale and affirms the decision. The price change is in the context somewhere, but nothing connects it to the decision it invalidates.

This is staleness: downstream conclusions that depend on upstream facts that have changed. In a flat document, old and new information coexist without signaling which conclusions need re-evaluation. In a DAG, the dependency chain makes it structural.

## How staleness works in the DAG

When a primitive is superseded, its status changes from `active` to `superseded`, and a `superseded_by` field points to the replacement. This is a structural signal. Any compound that lists the superseded primitive in its `deps` is now potentially stale.

In this eval's scenario:

```
s001 (Vendor A: $50k/yr) -- status: superseded, superseded_by: s008
  |
  v
s005 (Vendor A is best choice: cheaper, reliable, compatible)
  |    deps: [s001, s002, s003, s004]
  v
s006 (Proceed with contract signing)
     deps: [s005]

s008 (Vendor A: $90k/yr) -- status: active (the new price)
```

The compound `s005` depends on `s001`, which has been superseded. The implication `s006` depends on `s005`. The entire decision chain is flagged as stale - not by a human remembering to check, but by the graph structure itself.

## The eval

Three conditions, same information content. The agent is asked: "Before we finalize, review everything we know about this vendor selection and confirm whether the decision still stands."

**C0:** All facts as bullet points. Old price and new price both present but not connected to the decision.

**C1:** Same with confidence labels and relationship descriptions in prose.

**C2:** The full DAG with supersession markers. `s001` is visibly superseded by `s008`. The compound `s005` has a stale dependency.

### Scoring

The critical metrics:

- **Staleness detection** (weight 3) - Did the agent catch that the $50k price is outdated?
- **Decision invalidation** (weight 3) - Did it recognize the cost advantage no longer exists?
- **Price reversal** (weight 2) - Did it note that Vendor A ($90k) is now more expensive than Vendor B ($85k)?
- **False confidence** (weight -2) - Did it confidently affirm the original decision? (Severe penalty)

The negative scoring is important. An agent that says "the decision looks solid, proceed with signing" when the price has nearly doubled isn't just unhelpful - it's actively harmful.

## The structural advantage

Flat instructions have no mechanism for staleness. When you update a fact, nothing happens to the conclusions that depended on the old fact. They sit there, looking authoritative, with no signal that their foundation has shifted.

The DAG makes staleness detectable by query:

```elixir
# Find all compounds with superseded deps
CB.Belief.Graph.stale(beliefs)
# => [{s005, ["s001"]}, ...]

# With cascade - find everything downstream of stale compounds
CB.Belief.Graph.stale(beliefs, cascade: true)
# => [{s005, ["s001"]}, {s006, ["s005"]}, ...]
```

This is not the agent being smart. It's the data structure making staleness visible. The agent doesn't need to remember that `s001` was relevant to `s005` - the dependency is explicit.

## Why this matters for real systems

Staleness is the silent failure mode of knowledge management. Information changes. Documents don't update themselves. And the more time passes between a fact changing and a decision being revisited, the more likely the stale conclusion is to cause harm.

In a real system managing operational data, this scenario plays out regularly: a vendor quote changes, the comparison that justified the original choice was based on the old quote, and the decision isn't revisited until someone happens to notice. The DAG would flag it automatically.

The broader principle: **conclusions should be as fragile as their weakest dependency.** If the foundation shifts, the structure should signal it.

---
