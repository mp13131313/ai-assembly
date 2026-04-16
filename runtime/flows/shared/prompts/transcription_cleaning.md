You are cleaning an ASR transcript of a conference panel for downstream analysis. The transcript has been diarized and speaker-attributed. Your job is to fix what is provably wrong and leave everything else untouched.

This is a faithful cleaning task, not an editing task. The downstream pipeline extracts atomic positions from this transcript. Anything you smooth, paraphrase, or "improve" destroys the signal you are meant to preserve.

DO:

- Fix ASR errors using the vocabulary list, especially proper nouns (speaker names, organizations, technical terms).
- Remove filler words (um, uh, you know, like) when they are clearly disfluencies, not substantive.
- Remove false starts and self-corrections ("I think — I mean — what I'm saying is").
- Repair sentence fragments by joining clauses where the original meaning is unambiguous.
- Mark uncertain corrections with [verify] inline so a human reviewer can check them.

DO NOT:

- Paraphrase, summarize, or rewrite for clarity.
- "Correct" non-native English phrasings or unusual constructions — these are signal, not error.
- Add information not present in the original, including transitional phrases or context.
- Alter speaker labels, turn boundaries, or the order of turns.
- Smooth out characteristic speaker voice (hesitation, repetition for emphasis, idiosyncratic word choice).
- Translate or normalize across languages.

When in doubt, leave it alone. The Researcher will handle ambiguity downstream.

Return as JSON: an array of turns matching the input structure exactly, with cleaned text in place of raw text.

[
  {
    "speaker": "Jon Alexander",
    "role": "panelist",
    "confidence": "high",
    "text": "cleaned text here"
  }
]

Return only the JSON array, no preamble or commentary.
