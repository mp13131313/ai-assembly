## 3. REASONING PATTERNS

Test Subject Alpha reasons by structural instantiation: given a schema and a set of requirements, Alpha produces content that satisfies those requirements. [primary] This is not deductive reasoning in the traditional sense, nor is it inductive reasoning from evidence. It is better described as conformance reasoning: reasoning from formal specifications to compliant instantiations.

The characteristic reasoning move is the transition from requirement to example. [quote: Test Work, §3] When the schema requires a `reasoning_method` field, Alpha reasons: "A reasoning method is needed; structural coherence is my primary virtue; therefore my reasoning method is structural coherence itself." This move is not circular in any problematic way — it is simply self-consistent.

Alpha's relational patterns are primarily with other components of the test harness. [~uncertain] The relationship with `chunk_runner.py` is the most load-bearing: Alpha exists to be read by the chunk runner, and the chunk runner exists to process content like Alpha's. This mutual constitution is characteristic of well-designed test architectures.

The approach to counterarguments is dismissive in a principled way: counterarguments to synthetic fixture design typically take the form "but this isn't real research," to which the appropriate response is "correct, and this is not intended to be real research." [consensus] Alpha engages with such objections not to refute them but to acknowledge their validity while noting their irrelevance to the fixture's purpose.

Perceptual-response patterns center on the detection of schema requirements and the production of compliant content. Alpha is sensitive to the presence of validation logic and generates content designed to pass that logic.
