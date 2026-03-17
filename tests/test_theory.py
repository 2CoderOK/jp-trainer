"""Tests for jptrainer.theory – data loading, note generation, and item creation."""

import pytest

from jptrainer.theory import (
    BASIC_CHORDS,
    CHORDS,
    MODES,
    MODES_DESC,
    SCALES,
    Theory,
    TheoryItem,
)


# ── Static config data ────────────────────────────────────────────────────────


class TestConfigData:
    def test_scales_has_12_entries(self):
        assert len(SCALES) == 12

    def test_scales_keyed_0_to_11(self):
        assert set(SCALES.keys()) == set(range(12))

    def test_chords_non_empty(self):
        assert len(CHORDS) > 0

    def test_modes_has_7_entries(self):
        assert len(MODES) == 7

    def test_modes_desc_count_matches_modes(self):
        assert len(MODES_DESC) == len(MODES)

    def test_basic_chords_are_subset_of_chords(self):
        for idx in BASIC_CHORDS:
            assert idx in CHORDS, f"BASIC_CHORDS index {idx} not in CHORDS"

    def test_basic_chords_non_empty(self):
        assert len(BASIC_CHORDS) > 0


# ── Theory._get_notes_for_scale ──────────────────────────────────────────────


class TestGetNotesForScale:
    def setup_method(self):
        self.theory = Theory()

    def test_first_note_equals_start(self):
        notes = self.theory._get_notes_for_scale(36, [2, 2, 1, 2, 2, 2, 1])
        assert notes[0] == 36

    def test_ionian_from_zero(self):
        # W W H W W W H → 2 2 1 2 2 2 1
        notes = self.theory._get_notes_for_scale(0, [2, 2, 1, 2, 2, 2, 1])
        assert notes == [0, 2, 4, 5, 7, 9, 11, 12]

    def test_output_length_is_intervals_plus_one(self):
        intervals = [2, 2, 1, 2, 2, 2, 1]
        notes = self.theory._get_notes_for_scale(0, intervals)
        assert len(notes) == len(intervals) + 1

    def test_empty_intervals_returns_just_root(self):
        notes = self.theory._get_notes_for_scale(60, [])
        assert notes == [60]

    def test_notes_are_cumulative(self):
        notes = self.theory._get_notes_for_scale(0, [1, 2, 3])
        assert notes == [0, 1, 3, 6]


# ── Theory.get_chord ──────────────────────────────────────────────────────────


class TestGetChord:
    def setup_method(self):
        self.theory = Theory()

    def test_returns_theory_item(self):
        assert isinstance(self.theory.get_chord(), TheoryItem)

    def test_type_is_chord(self):
        assert self.theory.get_chord().type == "Chord"

    def test_scale_id_in_valid_range(self):
        item = self.theory.get_chord()
        assert 0 <= item.scale_id <= 11

    def test_scale_matches_scale_id(self):
        item = self.theory.get_chord()
        assert item.scale == SCALES[item.scale_id]

    def test_notes_is_non_empty_list(self):
        notes = self.theory.get_chord().notes
        assert isinstance(notes, list)
        assert len(notes) > 0

    def test_notes_are_integers(self):
        assert all(isinstance(n, int) for n in self.theory.get_chord().notes)

    def test_name_is_known_chord(self):
        assert self.theory.get_chord().name in CHORDS.values()

    def test_chord_id_is_from_basic_chords(self):
        item = self.theory.get_chord()
        assert item.id in BASIC_CHORDS


# ── Theory.get_mode ───────────────────────────────────────────────────────────


class TestGetMode:
    def setup_method(self):
        self.theory = Theory()

    def test_returns_theory_item(self):
        assert isinstance(self.theory.get_mode(), TheoryItem)

    def test_type_is_mode(self):
        assert self.theory.get_mode().type == "Mode"

    def test_scale_id_in_valid_range(self):
        item = self.theory.get_mode()
        assert 0 <= item.scale_id <= 11

    def test_scale_matches_scale_id(self):
        item = self.theory.get_mode()
        assert item.scale == SCALES[item.scale_id]

    def test_notes_is_non_empty_list(self):
        notes = self.theory.get_mode().notes
        assert isinstance(notes, list)
        assert len(notes) > 0

    def test_notes_are_integers(self):
        assert all(isinstance(n, int) for n in self.theory.get_mode().notes)

    def test_desc_is_non_empty_string(self):
        desc = self.theory.get_mode().desc
        assert isinstance(desc, str) and len(desc) > 0

    def test_mode_name_is_known(self):
        assert self.theory.get_mode().name in MODES.values()

    def test_mode_id_in_valid_range(self):
        item = self.theory.get_mode()
        assert 0 <= item.id < len(MODES)


# ── TheoryItem dataclass ──────────────────────────────────────────────────────


class TestTheoryItemDataclass:
    def test_default_construction(self):
        item = TheoryItem()
        assert item.type == ""
        assert item.notes == []
        assert item.scale_id == 0

    def test_notes_default_is_independent_per_instance(self):
        a, b = TheoryItem(), TheoryItem()
        a.notes.append(60)
        assert b.notes == []
