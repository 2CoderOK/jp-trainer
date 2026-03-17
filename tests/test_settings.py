"""Tests for jptrainer.settings – persistence and field validation."""

import json
from pathlib import Path

import pytest

import jptrainer.settings as _settings_mod
from jptrainer.settings import AppSettings, load_settings, save_settings


@pytest.fixture(autouse=True)
def isolated_settings_file(tmp_path, monkeypatch):
    """Redirect _SETTINGS_FILE to a temp dir so tests never touch the real file."""
    fake_path = tmp_path / "jptrainer.json"
    monkeypatch.setattr(_settings_mod, "_SETTINGS_FILE", fake_path)
    return fake_path


# ── AppSettings defaults ─────────────────────────────────────────────────────


class TestAppSettingsDefaults:
    def test_midi_ports_is_empty_list(self):
        assert AppSettings().midi_ports == []

    def test_octaves_default(self):
        assert AppSettings().octaves == 4

    def test_sampler_enabled_default(self):
        assert AppSettings().sampler_enabled is True

    def test_polyphony_default(self):
        assert AppSettings().polyphony == 32

    def test_sustain_default(self):
        assert AppSettings().sustain is False

    def test_ignore_velocity_default(self):
        assert AppSettings().ignore_velocity is True

    def test_debug_default(self):
        assert AppSettings().debug is False


# ── load_settings ─────────────────────────────────────────────────────────────


class TestLoadSettings:
    def test_missing_file_returns_defaults(self):
        result = load_settings()
        assert isinstance(result, AppSettings)
        assert result.octaves == 4

    def test_valid_json_populates_fields(self, isolated_settings_file):
        isolated_settings_file.write_text(
            json.dumps(
                {"octaves": 3, "sampler_enabled": False, "midi_ports": ["Port A"]}
            ),
            encoding="utf-8",
        )
        result = load_settings()
        assert result.octaves == 3
        assert result.sampler_enabled is False
        assert result.midi_ports == ["Port A"]

    def test_partial_json_uses_defaults_for_missing_fields(
        self, isolated_settings_file
    ):
        isolated_settings_file.write_text(json.dumps({"octaves": 2}), encoding="utf-8")
        result = load_settings()
        assert result.octaves == 2
        assert result.polyphony == 32  # default kept

    def test_unknown_keys_are_ignored(self, isolated_settings_file):
        isolated_settings_file.write_text(
            json.dumps({"octaves": 2, "future_unknown_key": "ignored"}),
            encoding="utf-8",
        )
        result = load_settings()
        assert result.octaves == 2
        assert not hasattr(result, "future_unknown_key")

    def test_octaves_clamped_below_minimum(self, isolated_settings_file):
        isolated_settings_file.write_text(json.dumps({"octaves": 0}), encoding="utf-8")
        assert load_settings().octaves == 1

    def test_octaves_clamped_above_maximum(self, isolated_settings_file):
        isolated_settings_file.write_text(json.dumps({"octaves": 99}), encoding="utf-8")
        assert load_settings().octaves == 7

    def test_polyphony_clamped_below_minimum(self, isolated_settings_file):
        isolated_settings_file.write_text(
            json.dumps({"polyphony": -1}), encoding="utf-8"
        )
        assert load_settings().polyphony == 1

    def test_polyphony_clamped_above_maximum(self, isolated_settings_file):
        isolated_settings_file.write_text(
            json.dumps({"polyphony": 999}), encoding="utf-8"
        )
        assert load_settings().polyphony == 256

    def test_corrupt_json_returns_defaults(self, isolated_settings_file):
        isolated_settings_file.write_text("not { valid json", encoding="utf-8")
        result = load_settings()
        assert isinstance(result, AppSettings)
        assert result.octaves == 4


# ── save_settings ─────────────────────────────────────────────────────────────


class TestSaveSettings:
    def test_creates_file(self, isolated_settings_file):
        save_settings(AppSettings())
        assert isolated_settings_file.exists()

    def test_file_contains_valid_json(self, isolated_settings_file):
        save_settings(AppSettings())
        data = json.loads(isolated_settings_file.read_text(encoding="utf-8"))
        assert "octaves" in data

    def test_round_trip(self, isolated_settings_file):
        original = AppSettings(
            octaves=5,
            sampler_enabled=False,
            midi_ports=["MIDI A", "MIDI B"],
            polyphony=16,
            sustain=True,
        )
        save_settings(original)
        loaded = load_settings()
        assert loaded.octaves == 5
        assert loaded.sampler_enabled is False
        assert loaded.midi_ports == ["MIDI A", "MIDI B"]
        assert loaded.polyphony == 16
        assert loaded.sustain is True

    def test_write_error_does_not_raise(self, monkeypatch):
        """save_settings must log the error, not propagate it."""
        monkeypatch.setattr(
            _settings_mod, "_SETTINGS_FILE", Path("/nonexistent_dir_xyz/settings.json")
        )
        save_settings(AppSettings())  # should not raise
