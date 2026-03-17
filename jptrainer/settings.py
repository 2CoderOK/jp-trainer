"""settings.py – App-wide settings with JSON persistence."""

from __future__ import annotations

import json
import logging
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import List

# Settings file lives next to the package (project root)
_SETTINGS_FILE = Path(__file__).parent.parent / "jptrainer.json"

log = logging.getLogger(__name__)


@dataclass
class AppSettings:
    # ── MIDI ──────────────────────────────────────────────────────────────────
    midi_ports: List[str] = field(default_factory=list)
    """Empty list = use all available ports."""

    # ── Sampler ───────────────────────────────────────────────────────────────
    sampler_enabled: bool = True
    ignore_velocity: bool = True
    sustain: bool = False
    polyphony: int = 32
    samples_path: str = "./piano_samples.zip"

    # ── Display ───────────────────────────────────────────────────────────────
    octaves: int = 4
    """Number of octaves shown on the virtual keyboard (1‑7)."""

    debug: bool = False


def load_settings() -> AppSettings:
    """Load settings from *jptrainer.json*; return defaults on any failure."""
    if not _SETTINGS_FILE.exists():
        log.debug("Settings file not found – using defaults (%s)", _SETTINGS_FILE)
        return AppSettings()
    try:
        raw = json.loads(_SETTINGS_FILE.read_text(encoding="utf-8"))
        # Only keep recognised fields so old keys don't crash dataclass
        known = {f for f in AppSettings.__dataclass_fields__}
        filtered = {k: v for k, v in raw.items() if k in known}
        loaded = AppSettings(**filtered)
        loaded.octaves = max(1, min(7, loaded.octaves))
        loaded.polyphony = max(1, min(256, loaded.polyphony))
        return loaded
    except Exception:
        log.exception(
            "Failed to load settings from %s – using defaults", _SETTINGS_FILE
        )
        return AppSettings()


def save_settings(s: AppSettings) -> None:
    """Persist *s* to *jptrainer.json*."""
    try:
        _SETTINGS_FILE.write_text(json.dumps(asdict(s), indent=2), encoding="utf-8")
        log.debug("Settings saved to %s", _SETTINGS_FILE)
    except Exception:
        log.exception("Failed to save settings to %s", _SETTINGS_FILE)
