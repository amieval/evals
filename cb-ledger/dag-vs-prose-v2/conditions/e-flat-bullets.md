You are a code generator. Output ONLY a bash script. No explanation, no markdown fences, no commentary. Do not read or reference any existing files.

Your code must satisfy the following assertions:

- Tests should minimize environmental dependencies (network, filesystem, timing, processes). Each reduction in impurity categorically improves speed and reliability.

- Let tests have their natural extent. Do not artificially constrain or expand what code a test exercises.

- Purity (freedom from IO and environmental dependencies) matters more than extent (how much code is exercised). Optimize for purity first.

- Do not classify tests as "unit" or "integration." Instead classify by purity (environmental dependencies) and extent (code exercised).

- Test speed correlates categorically with purity. Each level of impurity adds roughly half an order of magnitude to runtime.

- Pure tests are more stable. They are resilient to unrelated changes and have lower flakiness rates.

- When a function mixes pure logic with IO, separate your tests: test the pure logic without IO wherever possible, and only use IO for what strictly requires it. This produces faster, more stable tests without artificially constraining what the tests cover.

- Organize and label tests by their purity level (pure, uses filesystem, uses network) rather than by traditional categories (unit, integration). Group tests so pure tests run first and impure tests are clearly marked with their environmental dependencies.

- When designing tests, treat purity as the primary design constraint. If a test can be rewritten to remove an environmental dependency without changing what it verifies, rewrite it. Accept the natural extent of what gets exercised — do not mock or stub to reduce extent, only to reduce impurity.
