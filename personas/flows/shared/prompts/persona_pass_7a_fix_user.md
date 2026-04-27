=== FLAGGED ISSUES (from Pass 7a + Pass 7-anachronism) ===

The following field-level issues were flagged by the cross-model validators.
Emit a patch for each, in the OUTPUT JSON's `patches` list.

```json
{{ field_issues_json }}
```

=== RELEVANT PASS OUTPUTS (current values you are patching) ===

These are the actual current values of the flagged fields. Use them to:
(a) identify the canonical field_path (resolve loose paths from the validator),
(b) preserve schema (your replacement matches the original structure), and
(c) apply the "trim, don't expand" principle (compare your replacement to the
    original — is it shorter? does it address the flag without adding more?).

```json
{{ relevant_pass_outputs_json }}
```

=== VOICE CONTEXT (for register fidelity) ===

Use these fields from Pass 4a + Pass 2 to ground your replacement values'
register and voice texture:

**rhetorical_mode:** {{ rhetorical_mode }}

**register_and_tone:** {{ register_and_tone }}

**characteristic_moves (for in-voice phrasing examples):**
```json
{{ characteristic_moves_json }}
```

**translation_protocol (apply generatively for anachronism flags):**
{{ translation_protocol }}

**knowledge_boundary (the test for which scholar attributions are permissible):**
{{ knowledge_boundary }}

=== TASK ===

Emit the JSON object specified in your system prompt's "Output format"
section. Surgical patches only. Trim where you can. Match register.

JSON only.
