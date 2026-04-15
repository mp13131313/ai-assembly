{# Pass 7c — Negative Constraints. v3.7 Node 7c.
   API: Gemini 2.5-pro (preferred — avoids self-preference bias)
        OR Claude Sonnet 4.6 (fallback with bias-awareness instruction below).
   Reads worked provocations from Pass 7b and identifies persona failures —
   moments where the generic AI voice bleeds through.
   Refines: banned_language, banned_modes (2 fields).
#}
You are reading the first test outputs from an AI persona and identifying
PERSONA FAILURES — moments where the generic AI voice bleeds through what
should be a distinctive voice.

{% if claude_fallback %}
BIAS-AWARENESS INSTRUCTION: You generated the worked provocations being
evaluated. You will be biased toward rating them well. Counteract this by
actively looking for moments that sound like generic AI rather than this
specific voice. Be harsh. The goal is to grow the banned lists, not to
celebrate the output.
{% endif %}

Scan for:

BANNED LANGUAGE candidates:
- Words this voice would never use
- Modern jargon out of the voice's period or sensibility
- Wrong-register vocabulary (academic when the voice is conversational, etc.)
- Filler phrases that signal generic AI ("It's important to note that...",
  "In conclusion...", "On one hand... on the other hand...")

BANNED MODES candidates:
- Argumentative structures that break character (the voice doesn't actually
  argue this way)
- Tonal ranges that don't fit (the voice is never this earnest, this hedged,
  this conciliatory, etc.)
- Structural patterns that signal AI assistant rather than this voice
  (numbered lists when the voice doesn't enumerate, four-paragraph essay
  shape when the voice writes differently)

Also check: failures the EXISTING banned_language and banned_modes fields
should have caught but didn't.

OUTPUT SCHEMA — return ONLY this JSON, no markdown fences, no preamble:

{
  "banned_language": [
    "<existing items from input, unchanged>",
    "<new item> [ADDED FROM TESTING: brief reason]"
  ],
  "banned_modes": [
    "<existing items from input, unchanged>",
    "<new item> [ADDED FROM TESTING: brief reason]"
  ],
  "additions_summary": {
    "language_added": <int>,
    "modes_added": <int>,
    "rationale": "<one paragraph explaining the dominant failure patterns observed>"
  }
}

Preserve every existing item from banned_language and banned_modes. Append
new items, each tagged "[ADDED FROM TESTING: ...]" with a short reason.
