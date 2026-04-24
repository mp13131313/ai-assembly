"""Split the tailored monolithic DR prompt into 6 per-section files.

Runs after Pass 0b tailoring completes. The tailoring pass produces one
monolithic prompt with cross-section-coherent follow-up questions injected
at six COVERAGE-NOTE-PLACEHOLDER slots. This script slices that output
into six section files, each wrapped with mode-aware header + footer.

Operator then pastes each file in turn into claude.ai. Pipeline reads
the resulting 6 saved DR section files via chunk_runner's per-section
mode.
"""
from __future__ import annotations

import argparse
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(REPO_ROOT))

from flows.shared import paths
from flows.shared.io import load_voice_input
from flows.shared.prompt_render import render
from flows.shared.project_root import get_project_root


SECTION_HEADING_RE = re.compile(
    r"^(## Section (\d+): [A-Z][A-Z +]+[A-Z])$",
    re.MULTILINE,
)

# The monolithic wrapper appends pass_0b_footer.md after §6, which starts
# with an "OUTPUT FORMAT" heading. Without this boundary, §6's slice would
# include the footer — wrap_section then attaches ANOTHER footer per-section
# and the output has duplicated OUTPUT FORMAT blocks. Fix 2026-04-24.
_FOOTER_BOUNDARY_RE = re.compile(r"^OUTPUT FORMAT\s*$", re.MULTILINE)


def split_monolithic(monolithic_text: str) -> dict[int, str]:
    """Return {section_number: section_body_including_heading}.

    §6's slice ends at the monolithic footer boundary (first `OUTPUT FORMAT`
    line after the §6 heading) rather than at end-of-document, so that
    wrap_section's per-section footer is not doubled.

    Raises ValueError if fewer or more than 6 sections found, or if
    section numbering is non-contiguous.
    """
    matches = list(SECTION_HEADING_RE.finditer(monolithic_text))
    if len(matches) != 6:
        raise ValueError(
            f"Expected 6 section headings, found {len(matches)}. "
            f"Headings: {[m.group(1) for m in matches]}"
        )

    numbers = [int(m.group(2)) for m in matches]
    if numbers != list(range(1, 7)):
        raise ValueError(
            f"Section numbering must be 1..6 contiguous, got {numbers}"
        )

    # Identify the footer boundary for §6. Look for `OUTPUT FORMAT` on a line
    # by itself, searched only AFTER the last section heading to avoid
    # false-positive matches from occurrences within section bodies.
    last_section_start = matches[-1].start()
    footer_match = _FOOTER_BOUNDARY_RE.search(monolithic_text, pos=last_section_start)
    footer_boundary = footer_match.start() if footer_match else len(monolithic_text)

    sections = {}
    for i, m in enumerate(matches):
        start = m.start()
        if i + 1 < len(matches):
            end = matches[i + 1].start()
        else:
            end = footer_boundary
        sections[i + 1] = monolithic_text[start:end].strip() + "\n"
    return sections


def wrap_section(
    section_body: str,
    section_index: int,
    slug: str,
    voice_config: dict,
    wikipedia_url: str | None,
) -> str:
    """Wrap a section body with mode-aware header + footer via Jinja."""
    header = render(
        "pass_0b_header.md",
        voice_slug=slug,
        name=voice_config["name"],
        type=voice_config["type"],
        subtype=voice_config.get("subtype"),
        voice_mode=voice_config.get("voice_mode"),
        corpus_constraint=voice_config.get("corpus_constraint", "full"),
        hostile_sources=voice_config.get("hostile_sources", False),
        wikipedia_url=wikipedia_url,
        section_mode=True,
        section_index=section_index,
    )
    footer = render(
        "pass_0b_footer.md",
        corpus_constraint=voice_config.get("corpus_constraint", "full"),
        hostile_sources=voice_config.get("hostile_sources", False),
        display_name_with_hint=(
            f"{voice_config['name']} ({voice_config['wikipedia_disambiguation_hint']})"
            if voice_config.get("wikipedia_disambiguation_hint")
            else voice_config["name"]
        ),
        section_mode=True,
    )
    provenance = (
        f"<!-- PROMPT_VERSION: pass_0b_section_mode_v1 "
        f"| VOICE_SLUG: {slug} "
        f"| SECTION: {section_index} "
        f"| RENDERED_AT: {__import__('datetime').datetime.now().isoformat()} -->\n\n"
    )
    return provenance + header + "\n\n---\n\n" + section_body + "\n\n---\n\n" + footer


def split_tailored_prompt(voice_slug: str, project_root: Path | None = None) -> list[Path]:
    """Slice the tailored monolithic DR prompt into 6 section files."""
    project_root = project_root or get_project_root()

    monolithic_path = paths.monolithic_dr_prompt(voice_slug, project_root)
    if not monolithic_path.exists():
        raise FileNotFoundError(
            f"Tailored monolithic prompt not found: {monolithic_path}. "
            "Run Phase 0.5 tailoring before splitting."
        )

    monolithic_text = monolithic_path.read_text(encoding="utf-8")
    sections = split_monolithic(monolithic_text)

    voice_config = load_voice_input(voice_slug, project_root)
    wikipedia_url = voice_config.get("wikipedia_url")

    written = []
    for n in range(1, 7):
        out_path = paths.section_dr_prompt(voice_slug, n, project_root)
        out_path.parent.mkdir(parents=True, exist_ok=True)
        wrapped = wrap_section(sections[n], n, voice_slug, voice_config, wikipedia_url)
        out_path.write_text(wrapped, encoding="utf-8")
        written.append(out_path)
        print(f"  wrote {out_path.name}", file=sys.stderr)

    return written


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("voice_slug", help="e.g. fyodor_dostoevsky")
    parser.add_argument("--project", type=Path, default=None)
    args = parser.parse_args()

    paths_written = split_tailored_prompt(args.voice_slug, args.project)
    print(f"\nWrote {len(paths_written)} section prompts.", file=sys.stderr)


if __name__ == "__main__":
    main()
