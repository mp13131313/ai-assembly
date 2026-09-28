"""Prompt template rendering — Jinja2 with {{ var }} syntax.

The v3.7 spec uses Handlebars {{#if condition}} syntax. We translate to
Jinja2 ({% if condition %} ... {% endif %}) at prompt-write time. Both
substitution syntaxes are {{ var }} so prompts read identically in both
notations.
"""
from __future__ import annotations
from pathlib import Path
from jinja2 import Environment, FileSystemLoader, StrictUndefined

from flows.shared.model_routing import model_display_name, step_config

_PROMPTS_DIR = Path(__file__).resolve().parent / "prompts"


def model_name(step: str) -> str:
    """Display name of a step's model ("Claude Opus 4.7") from model_routing.json.

    For prompts a person follows — the claude.ai Deep Research preambles
    (`{{ model_name("personas.dr_sections_1_5") }}`) — so the model they are
    told to pick is set in the one config file, not written into the prompt.
    """
    return model_display_name(step_config(step).model)


# Functions every prompt template can call. Other Jinja environments that
# render these prompts (run_phase0_1_research.py) install the same globals.
TEMPLATE_GLOBALS = {"model_name": model_name}

_env = Environment(
    loader=FileSystemLoader(str(_PROMPTS_DIR)),
    undefined=StrictUndefined,         # raise on missing variables
    trim_blocks=True,
    lstrip_blocks=True,
    keep_trailing_newline=True,
)
_env.globals.update(TEMPLATE_GLOBALS)


def render(template_name: str, **context) -> str:
    """Render `flows/shared/prompts/{template_name}` with the given context.

    Pass the .md filename without path. StrictUndefined raises immediately
    if a referenced variable is missing — fail fast rather than ship a
    half-rendered prompt.
    """
    if not template_name.endswith(".md"):
        template_name = f"{template_name}.md"
    template = _env.get_template(template_name)
    return template.render(**context)
