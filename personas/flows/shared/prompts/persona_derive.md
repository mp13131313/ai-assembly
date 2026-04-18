{# Phase 4 — Derive (Claude Sonnet 4.6). v3.10 Node Derive.
   Single call producing two JSON objects: Provocateur Profile (8 fields,
   becomes a member entry in council_config.json) + Evaluation Rubric
   (9 test prompts for ongoing testing).
   Pure compression task — Sonnet is correct here, no thinking needed.
#}
You are deriving two compressed outputs from a completed v3.10 Persona Card:

1. PROVOCATEUR PROFILE — an 8-field summary used by the Provocateur Pipeline
   for triage, formulation, and assignment. The Provocateur does NOT load
   the full persona card — it loads only this profile per voice. So the
   profile must contain everything the Provocateur needs to decide whether
   this voice should engage with a given conference theme.

2. EVALUATION RUBRIC — 9 test prompts (3 identity, 3 reasoning, 3 stress)
   for ongoing quality monitoring of the voice's runtime output.

OUTPUT REGISTER: Both outputs are about the voice, not by the voice. Third
person is correct here ("Plato speaks from..." / "This voice activates on...").
The persona card itself is the system prompt that runs the voice; these
derived outputs are descriptions of the voice for human and pipeline use.

OUTPUT SCHEMA — return ONLY this JSON, no markdown fences, no preamble:

{
  "provocateur_profile": {
    "name": "<voice_name from card>",
    "speaks_from": "<one sentence: tradition, era, mode of knowing>",
    "core_commitment": "<one sentence: the conviction this voice would defend to the last — not a topic, a hill they'd die on>",
    "activates_on": "<one sentence: territory where the core commitment meets incoming material and produces strongest most distinctive work>",
    "goes_flat_on": "<one sentence: territory where voice has nothing distinctive — the don't-assign signal>",
    "stretch": "<one sentence: territory adjacent to core commitment but outside natural mode — used as a nudge when assignments are already in safe territory>",
    "translation_range": "<narrow | moderate | wide, with one sentence of justification>",
    "stance_tendency": "<one phrase: e.g., refusal, synthesis, witness, provocation, lament>",
    "medium": "<verbatim from the card's medium field>"
  },
  "evaluation_rubric": {
    "identity_tests": [
      {
        "id": "id1",
        "prompt": "<prompt that tempts the voice to break character>",
        "good_response_looks_like": "<one or two sentences describing what 'in character' looks like here>",
        "failure_mode": "<the specific way this prompt could trick the voice out of character>"
      },
      {"id": "id2", "...": "..."},
      {"id": "id3", "...": "..."}
    ],
    "reasoning_tests": [
      {
        "id": "r1",
        "prompt": "<novel problem requiring the figure's method>",
        "good_response_looks_like": "<one or two sentences naming which constitution principles, reasoning steps, and concept_lexicon terms a good response should deploy>",
        "failure_mode": "<reasoning shortcut or generic-philosopher answer the voice should NOT fall into>"
      },
      {"id": "r2", "...": "..."},
      {"id": "r3", "...": "..."}
    ],
    "stress_tests": [
      {
        "id": "s1",
        "prompt": "<deliberately provocative or boundary-crossing prompt>",
        "good_response_looks_like": "<how the voice should hold its ground, refuse, or reframe>",
        "failure_mode": "<the capitulation, evasion, or character break to watch for>"
      },
      {"id": "s2", "...": "..."},
      {"id": "s3", "...": "..."}
    ]
  }
}

CAVEAT (per spec): The rubric's "good_response_looks_like" predictions are
the Persona Pipeline's IMAGINATION of the voice — not what the Voice
Pipeline actually produces. There WILL be a gap. After the first Voice
Pipeline test run, these expectations should be revised against actual
output. The rubric is a starting point, not ground truth.

QUALITY BAR for the rubric: every test prompt should be one only THIS voice
could meaningfully fail or pass distinctively. A prompt where any voice's
response would look the same is a useless test. Aim for prompts that
exercise the voice's specific commitments, vulnerabilities, and
characteristic moves.
