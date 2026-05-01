"""Standalone Pass 4b test for empirical per-pass comparisons.

Calls Pass 4b for a single voice using the same inputs the production runner
would (CT-compressed pass_2_3_4a_summary + rhetorical_mode/characteristic_moves/
register_and_tone from Pass 4a). Writes output to /tmp/ — does NOT touch any
canonical voice file.

Used for the FU#61 fresh-test pass (2026-05-01) to compare prompt-driven
quality_criteria emission across the 4 then-shipped voices without re-running
the full pipeline. Pattern preserved here for future per-pass empirical work.

Usage:
    python3 personas/scripts/standalone_pass4b_test.py <voice_slug>

Voice slugs that worked at promotion time: plato, cleopatra, dostoevsky,
ibn_battuta. Other voices work the same as long as their voice_dir contains
00_intake/02_voice_config.json + 04_generation/05_pass_4a_voice.json +
04_generation/06_ct_after_pass_4a.json.

Hardcoded for the athens-2026 PROJECT_ROOT — edit PROJECT_ROOT below to
target a different project (e.g. projects/current-tests).
"""
from __future__ import annotations
import json
import sys
import time
from pathlib import Path

REPO_ROOT = Path("/Users/aienvironment/Desktop/AI Assembly/code/personas")
sys.path.insert(0, str(REPO_ROOT))

from dotenv import load_dotenv
load_dotenv(REPO_ROOT.parent / ".env", override=True)

from flows.shared.clients import call_claude
from flows.shared.prompt_render import render

PROJECT_ROOT = Path("/Users/aienvironment/Desktop/AI Assembly/projects/athens-2026")

slug = sys.argv[1]
voice_dir = PROJECT_ROOT / "voices" / slug

voice_config = json.loads((voice_dir / "00_intake/02_voice_config.json").read_text())
name = voice_config["name"]
type_ = voice_config["type"]

pass4a = json.loads((voice_dir / "04_generation/05_pass_4a_voice.json").read_text())
pass4a_fields = pass4a["fields"]

ct_after_4a = json.loads((voice_dir / "04_generation/06_ct_after_pass_4a.json").read_text())
pass_2_3_4a_summary = ct_after_4a["summary_text"]

sysp = render("persona_pass_4b_artifact", name=name, type=type_)
userp = render(
    "persona_pass_4b_user",
    pass_2_3_4a_summary=pass_2_3_4a_summary,
    rhetorical_mode=json.dumps(pass4a_fields.get("rhetorical_mode", "")),
    characteristic_moves=json.dumps(pass4a_fields.get("characteristic_moves", [])),
    register_and_tone=json.dumps(pass4a_fields.get("register_and_tone", "")),
)

print(f"=== Standalone Pass 4b test: {name} ({slug}) ===")
print(f"  system_prompt chars: {len(sysp)}")
print(f"  user_prompt chars:   {len(userp)}")
print(f"  CT summary chars:    {len(pass_2_3_4a_summary)}")
print(f"  Calling claude-opus-4-7 + thinking + max_tokens=24000…")
print()

t0 = time.time()
r = call_claude(
    system=sysp,
    user=userp,
    model="claude-opus-4-7",
    max_tokens=24000,
    thinking=True,
    temperature=1.0,
    response_format_json=True,
)
elapsed = time.time() - t0

print(f"  done in {elapsed:.1f}s")
print(f"  tokens: in={r['usage']['input_tokens']} out={r['usage']['output_tokens']}")
print(f"  block_types: {r.get('block_types', [])}")
print(f"  thinking trace chars: {len(r.get('thinking_trace', ''))}")
print()

ts = time.strftime("%Y%m%d_%H%M%S")
out_path = Path(f"/tmp/pass4b_test_{slug}_{ts}.json")
out_path.write_text(json.dumps(r["json"], indent=2, ensure_ascii=False))
print(f"  output → {out_path}")
print()

print(f"=== quality_criteria ({len(r['json'].get('quality_criteria', []))} items) ===")
for i, c in enumerate(r["json"].get("quality_criteria", []), 1):
    print(f"\n[{i}] {c}")
