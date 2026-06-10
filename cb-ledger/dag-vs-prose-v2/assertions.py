"""The nine scoring assertions, verbatim from purity-test/{primitives,compounds}.

Shared by the Inspect task (one LLM-judge scorer per assertion) and the
judge-validation sampler. Scorer/ruler names use the llm-judge prefix per the
CB method:a4 convention, so m-judge-validation can find them.
"""

PRIMITIVES = {
    "p1": "Tests should minimize environmental dependencies (network, filesystem, timing, processes). Each reduction in impurity categorically improves speed and reliability.",
    "p2": "Let tests have their natural extent. Do not artificially constrain or expand what code a test exercises.",
    "p3": "Purity (freedom from IO and environmental dependencies) matters more than extent (how much code is exercised). Optimize for purity first.",
    "p4": 'Do not classify tests as "unit" or "integration." Instead classify by purity (environmental dependencies) and extent (code exercised).',
    "p5": "Test speed correlates categorically with purity. Each level of impurity adds roughly half an order of magnitude to runtime.",
    "p6": "Pure tests are more stable. They are resilient to unrelated changes and have lower flakiness rates.",
}

COMPOUNDS = {
    "c1": "When a function mixes pure logic with IO, separate your tests: test the pure logic without IO wherever possible, and only use IO for what strictly requires it. This produces faster, more stable tests without artificially constraining what the tests cover.",
    "c2": "Organize and label tests by their purity level (pure, uses filesystem, uses network) rather than by traditional categories (unit, integration). Group tests so pure tests run first and impure tests are clearly marked with their environmental dependencies.",
    "c3": "When designing tests, treat purity as the primary design constraint. If a test can be rewritten to remove an environmental dependency without changing what it verifies, rewrite it. Accept the natural extent of what gets exercised — do not mock or stub to reduce extent, only to reduce impurity.",
}

ASSERTIONS = {**PRIMITIVES, **COMPOUNDS}

JUDGE_PROMPT = (
    "ASSERTION: {assertion}\n\n"
    "CODE:\n{code}\n\n"
    "Does this code satisfy or reflect this assertion in its design? Answer only YES or NO."
)


def ruler_name(assertion_id: str) -> str:
    return f"llm-judge-{assertion_id}"
