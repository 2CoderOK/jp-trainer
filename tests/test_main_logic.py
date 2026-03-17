"""Tests for pure logic functions in jptrainer.main.

NoteDisplay and Sampler (which require Tk / audio hardware) are kept out of
scope here. Only functions that can be exercised without a running GUI are
covered: _resolve_ports and Trainer.generate_path.
"""

from pathlib import Path
from unittest.mock import patch

import pytest

import jptrainer.main as main_mod
from jptrainer.settings import AppSettings
from jptrainer.theory import TheoryItem


# ── _resolve_ports ────────────────────────────────────────────────────────────


class TestResolvePorts:
    def test_empty_midi_ports_returns_empty(self):
        settings = AppSettings(midi_ports=[])
        assert main_mod._resolve_ports(settings) == []

    def test_all_ports_unavailable_returns_empty(self):
        settings = AppSettings(midi_ports=["Ghost Port"])
        with patch("jptrainer.main.mido.get_input_names", return_value=[]):
            result = main_mod._resolve_ports(settings)
        assert result == []

    def test_available_ports_all_returned(self):
        settings = AppSettings(midi_ports=["Piano", "Controller"])
        with patch(
            "jptrainer.main.mido.get_input_names",
            return_value=["Piano", "Controller", "Other"],
        ):
            result = main_mod._resolve_ports(settings)
        assert result == ["Piano", "Controller"]

    def test_only_selected_ports_returned_not_all_available(self):
        settings = AppSettings(midi_ports=["Piano"])
        with patch(
            "jptrainer.main.mido.get_input_names", return_value=["Piano", "Controller"]
        ):
            result = main_mod._resolve_ports(settings)
        assert result == ["Piano"]

    def test_partial_availability_returns_subset(self):
        settings = AppSettings(midi_ports=["A", "B", "C"])
        with patch("jptrainer.main.mido.get_input_names", return_value=["A", "C"]):
            result = main_mod._resolve_ports(settings)
        assert result == ["A", "C"]

    def test_preserves_selection_order(self):
        """Order follows midi_ports list, not the order ports appear in the system."""
        settings = AppSettings(midi_ports=["B", "A"])
        with patch("jptrainer.main.mido.get_input_names", return_value=["A", "B"]):
            result = main_mod._resolve_ports(settings)
        assert result == ["B", "A"]


# ── Trainer.generate_path ─────────────────────────────────────────────────────

# generate_path references only the t_item argument (not self), so we call it
# as an unbound method passing None as the receiver.


def _generate_path(t_item):
    return main_mod.Trainer.generate_path(None, t_item)


class TestGeneratePath:
    def test_mode_prefix_is_03(self):
        path = _generate_path(TheoryItem(type="Mode", scale_id=0, id=0))
        assert str(path).startswith("03")

    def test_chord_prefix_is_04(self):
        path = _generate_path(TheoryItem(type="Chord", scale_id=0, id=0))
        assert str(path).startswith("04")

    def test_returns_path_object(self):
        path = _generate_path(TheoryItem(type="Mode", scale_id=0, id=0))
        assert isinstance(path, Path)

    def test_scale_subfolder_is_scale_id_plus_one(self):
        # scale_id=5 → subfolder "06"
        path = _generate_path(TheoryItem(type="Chord", scale_id=5, id=0))
        parts = Path(path).parts
        assert parts[1] == "06"

    def test_filename_encodes_type_scale_id_and_item_id(self):
        # type=Mode(03), scale_id=2, id=1 → filename "030201"
        path = _generate_path(TheoryItem(type="Mode", scale_id=2, id=1))
        assert Path(path).parts[2] == "030201"

    def test_known_mode_path_structure(self):
        # Mode, scale_id=0, id=0 → 03/01/030000
        path = _generate_path(TheoryItem(type="Mode", scale_id=0, id=0))
        parts = Path(path).parts
        assert parts == ("03", "01", "030000")

    def test_known_chord_path_structure(self):
        # Chord, scale_id=11, id=3 → 04/12/041103
        path = _generate_path(TheoryItem(type="Chord", scale_id=11, id=3))
        parts = Path(path).parts
        assert parts == ("04", "12", "041103")

    def test_dict_input_supported(self):
        """generate_path also accepts plain dicts."""
        path = _generate_path({"type": "Chord", "scale_id": 0, "id": 0})
        assert str(path).startswith("04")

    def test_different_scale_ids_produce_different_paths(self):
        p0 = _generate_path(TheoryItem(type="Chord", scale_id=0, id=0))
        p1 = _generate_path(TheoryItem(type="Chord", scale_id=1, id=0))
        assert p0 != p1
