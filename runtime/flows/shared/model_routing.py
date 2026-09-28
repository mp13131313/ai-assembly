"""Which model runs each LLM step — one place for both pipelines.

Reads `<repo>/model_routing.json`. Call sites ask for their step:

    cfg = step_config("runtime.researcher.extraction")
    client.messages.stream(model=cfg.model, **({"thinking": ...} if cfg.thinking_on else {}),
                           **cfg.output_config_kwargs(), ...)

Legacy per-step env vars (docs/LLM_CALL_INVENTORY.md §5) still override the
file, so documented run commands keep working. Empty env values count as
unset (the Claude Code shell pre-sets some vars to "").

Unsafe combinations raise `ModelRoutingError` instead of reaching the API:
thinking "off" on a model that can't disable it, no explicit effort on a
model whose default effort isn't "high" (which would silently lower quality),
or a validator ladder rung that isn't an OpenAI or Google model (ladders are
cross-model checks of Claude output — a Claude rung would be same-family).
Ladder call sites route each rung by `model_vendor(model)`, not by position.

This file is duplicated byte-for-byte at personas/flows/shared/model_routing.py
— the two pipelines have separate venvs and don't import each other (same
pattern as project_root.py). A test in each suite checks the copies match.
"""
from __future__ import annotations

import json
import os
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path
from typing import Any

CONFIG_PATH = Path(__file__).resolve().parents[3] / "model_routing.json"

_EFFORTS = {"low", "medium", "high", "xhigh", "max"}
_OFF = {"0", "false", "off", "no"}
_LADDER_VENDORS = {"openai", "google"}  # what the validator ladder call sites can call

# step (or step prefix ending in ".") -> legacy model env vars, first set wins.
_MODEL_ENV: dict[str, tuple[str, ...]] = {
    "runtime.transcription.speaker_id": ("TRANSCRIPTION_SPEAKER_ID_MODEL", "CLAUDE_MODEL"),
    "runtime.transcription.cleaning": ("TRANSCRIPTION_CLAUDE_MODEL", "CLAUDE_MODEL"),
    "runtime.researcher.": ("RESEARCHER_CLAUDE_MODEL", "CLAUDE_MODEL"),
    "runtime.provocateur.": ("PROVOCATEUR_CLAUDE_MODEL", "CLAUDE_MODEL"),
    "runtime.voice.step1": ("VOICE_MODEL", "CLAUDE_MODEL"),
    "runtime.voice.step2": ("VOICE_MODEL", "CLAUDE_MODEL"),
    "runtime.voice.step3": ("VOICE_MODEL", "CLAUDE_MODEL"),
    "runtime.voice.continuity": ("VOICE_CONTINUITY_MODEL",),
    "runtime.voice.step2_validation": ("VOICE_STEP2_VALIDATION_MODEL",),
    "runtime.synthesis_router": ("SYNTHESIS_ROUTER_MODEL",),
    "runtime.editor.dossier": ("EDITOR_MODEL", "CLAUDE_MODEL"),
    "personas.pass_1a_perplexity": ("PERPLEXITY_MODEL",),
    "personas.pass_1b_gemini": ("GEMINI_MODEL",),
}
# step (or prefix) -> legacy thinking on/off env var.
_THINKING_ENV: dict[str, str] = {
    "runtime.researcher.": "RESEARCHER_THINKING",
    "runtime.provocateur.": "PROVOCATEUR_THINKING",
    "runtime.voice.step1": "VOICE_THINKING",
    "runtime.voice.step2": "VOICE_THINKING",
    "runtime.voice.step3": "VOICE_THINKING",
    "runtime.voice.continuity": "VOICE_CONTINUITY_THINKING",
    "runtime.editor.dossier": "EDITOR_THINKING",
}
# step -> legacy comma-separated ladder env var.
_LADDER_ENV: dict[str, str] = {
    "runtime.voice.step1_validation": "VOICE_VALIDATION_MODELS",
}


class ModelRoutingError(ValueError):
    """model_routing.json (or an env override) asks for an unsafe/unknown setup."""


@dataclass(frozen=True)
class StepConfig:
    step: str
    label: str
    model: str
    vendor: str
    thinking: str | None          # "adaptive" | "off"; None for non-Anthropic steps
    effort: str | None            # None = don't send, model default applies
    sampling_params: bool         # False = model rejects temperature/top_p/top_k
    ladder: tuple[str, ...] = ()  # cross-vendor fallback order (validators)
    fallback: StepConfig | None = None

    @property
    def thinking_on(self) -> bool:
        return self.thinking == "adaptive"

    def output_config_kwargs(self) -> dict[str, Any]:
        """`{"output_config": {"effort": ...}}` when an effort is set, else {}."""
        return {"output_config": {"effort": self.effort}} if self.effort else {}


def _env(name: str) -> str | None:
    value = os.environ.get(name, "").strip()
    return value or None


def _lookup(table: dict[str, Any], step: str) -> Any:
    if step in table:
        return table[step]
    for key, value in table.items():
        if key.endswith(".") and step.startswith(key):
            return value
    return None


@lru_cache(maxsize=None)
def _load(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        data = json.load(f)
    for step, raw in data["steps"].items():  # validate the file as written
        _build(step, raw, data["models"])
    return data


def _build(step: str, raw: dict[str, Any], models: dict[str, Any],
           model: str | None = None, thinking: str | None = None,
           ladder: tuple[str, ...] | None = None) -> StepConfig:
    model = model or raw["model"]
    ladder = ladder if ladder is not None else tuple(raw.get("ladder", ()))
    for m in (model, *ladder):
        if m not in models:
            raise ModelRoutingError(
                f"{step}: model {m!r} is not listed under 'models' in model_routing.json "
                f"— add it with its rules first.")
    for m in ladder:
        if models[m]["vendor"] not in _LADDER_VENDORS:
            raise ModelRoutingError(
                f"{step}: ladder rung {m!r} is a {models[m]['vendor']} model — validator "
                f"ladders take only {sorted(_LADDER_VENDORS)} models (cross-model check).")
    spec = models[model]
    effort = raw.get("effort")
    if spec["vendor"] == "anthropic":
        thinking = thinking or raw.get("thinking") or "adaptive"
        if thinking not in ("adaptive", "off"):
            raise ModelRoutingError(f"{step}: thinking must be 'adaptive' or 'off', got {thinking!r}.")
        if thinking == "off" and not spec["thinking_can_disable"]:
            raise ModelRoutingError(
                f"{step}: {model} cannot run with thinking off — use 'adaptive' with a low effort.")
        if effort is not None and effort not in _EFFORTS:
            raise ModelRoutingError(f"{step}: effort must be one of {sorted(_EFFORTS)} or null, got {effort!r}.")
        if effort is None and spec["default_effort"] != "high":
            raise ModelRoutingError(
                f"{step}: {model} defaults to effort '{spec['default_effort']}' (lower than the "
                f"'high' these steps were tuned on) — set effort explicitly.")
    else:
        thinking = None
    fallback = raw.get("fallback")
    return StepConfig(
        step=step,
        label=raw.get("label", step),
        model=model,
        vendor=spec["vendor"],
        thinking=thinking,
        effort=effort,
        sampling_params=spec.get("sampling_params", True),
        ladder=ladder,
        fallback=_build(f"{step}.fallback", fallback, models) if fallback else None,
    )


def step_config(step: str, *, path: Path | None = None) -> StepConfig:
    """The effective model setup for `step`: model_routing.json + legacy env overrides."""
    data = _load(path or CONFIG_PATH)
    if step not in data["steps"]:
        raise ModelRoutingError(f"Unknown step {step!r} — add it to model_routing.json.")
    model = None
    for name in _lookup(_MODEL_ENV, step) or ():
        model = _env(name)
        if model:
            break
    thinking = None
    thinking_env = _lookup(_THINKING_ENV, step)
    if thinking_env and _env(thinking_env) is not None:
        thinking = "off" if _env(thinking_env).lower() in _OFF else "adaptive"
    ladder = None
    ladder_env = _lookup(_LADDER_ENV, step)
    if ladder_env and _env(ladder_env) is not None:
        ladder = tuple(m.strip() for m in _env(ladder_env).split(",") if m.strip())
        model = model or ladder[0]
    return _build(step, data["steps"][step], data["models"], model, thinking, ladder)


def model_vendor(model: str, *, path: Path | None = None) -> str:
    """The vendor of a model listed in model_routing.json ("anthropic", "openai", "google", …)."""
    models = _load(path or CONFIG_PATH)["models"]
    if model not in models:
        raise ModelRoutingError(f"model {model!r} is not listed under 'models' in model_routing.json.")
    return models[model]["vendor"]


def all_steps(*, path: Path | None = None) -> dict[str, StepConfig]:
    """Every step's effective setup (for an overview page / audits)."""
    data = _load(path or CONFIG_PATH)
    return {step: step_config(step, path=path) for step in data["steps"]}
