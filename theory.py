from copy import deepcopy
from secrets import choice

SCALES = {
    0: "C",
    1: "C#",
    2: "D",
    3: "Eb",
    4: "E",
    5: "F",
    6: "Gb",
    7: "G",
    8: "Ab",
    9: "A",
    10: "Bb",
    11: "B",
}

SCALES_MIDI = {
    0: 36,
    1: 37,
    2: 38,
    3: 39,
    4: 40,
    5: 41,
    6: 42,
    7: 43,
    8: 44,
    9: 45,
    10: 46,
    11: 47,
}

CHORDS = {
    0: "maj7",
    1: "min7",
    2: "min7/b5",
    3: "7",
    4: "dim",
    5: "aug",
    6: "7/#11",
    7: "maj7/#5",
    8: "minM7",
    9: "sus4/7",
    10: "6",
    11: "min6",
}

CHORDS_MIDI = {
    0: [4, 3, 4],
    1: [3, 4, 3],
    2: [3, 3, 4],
    3: [4, 3, 3],
    4: [3, 3, 3],
    5: [4, 4, 2],
    6: [4, 2, 4],
    7: [4, 4, 3],
    8: [3, 4, 4],
    9: [5, 2, 3],
    10: [4, 3, 2],
    11: [3, 4, 2],
}

BASIC_CHORDS = [0, 1, 3, 4, 5, 10, 11]

MODES = {
    0: "Ionian",
    1: "Dorian",
    2: "Phrygian",
    3: "Lydian",
    4: "Mixolydian",
    5: "Aeolian",
    6: "Loerian",
}

MODES_DESC = {
    0: "Ionian (W,W,H,W,W,W,H)",
    1: "Dorian (W,H,W,W,W,H,W)",
    2: "Phrygian (H,W,W,W,H,W,W)",
    3: "Lydian (W,W,W,H,W,W,H)",
    4: "Mixolydian (W,W,H,W,W,H,W)",
    5: "Aeolian (W,H,W,W,H,W,W)",
    6: "Loerian (H,W,W,H,W,W,W)",
}

MODES_MIDI = {
    0: [2, 2, 1, 2, 2, 2, 1],
    1: [2, 1, 2, 2, 2, 1, 2],
    2: [1, 2, 2, 2, 1, 2, 2],
    3: [2, 2, 2, 1, 2, 2, 1],
    4: [2, 2, 1, 2, 2, 1, 2],
    5: [2, 1, 2, 2, 1, 2, 2],
    6: [1, 2, 2, 1, 2, 2, 2],
}

MODES_DIR = {0: "ascending", 1: "descending"}

# play type
# 0 base - chord
# 1 same base - inverted chord
# 2 same base - inverted chord
# 3 base - single notes up
# 4 base - single notes down
# 5 1st inversion - chord
# 6 1st inversion - single notes up
# 7 1st inversion - single notes down
# 8 2nd inversion - chord
# 9 2nd inversion - single notes up
# 10 2nd inversion - single notes down
# 11 3rd inversion - chord
# 12 3rd inversion - single notes up
# 13 3rd inversion - single notes down

CHORD_INVERSIONS = {
    0: "base - chord",
    1: "bass root - 2nd inversion chord",
    2: "bass root - 3rd inversion chord",
    3: "bass root - single notes up",
    4: "bass root - single notes down",
    5: "1st inversion - chord",
    6: "1st inversion - single notes up",
    7: "1st inversion - single notes down",
    8: "2nd inversion - chord",
    9: "2nd inversion - single notes up",
    10: "2nd inversion - single notes down",
    11: "3rd inversion - chord",
    12: "3rd inversion - single notes up",
    13: "3rd inversion - single notes down",
}

BASIC_CHORD_INVERSIONS = [0, 3]

# TODO: replace with a @dataclass
TheoryItem = {
    "type": "",
    "name": "",
    "id": "",
    "desc": "",
    "image_path": "",
    "audio_path": "",
    "scale": "",
    "dir": "",
    "notes": [],
}


class Theory:
    """
    A main class to handle a music theory related processing
    """

    def __init__(self) -> None:
        pass

    def _get_random_chord_inversion_id(self) -> int:
        """
        Generate a random chord inversion
        """
        return choice(BASIC_CHORD_INVERSIONS)

    def _get_common_items(self, type: str) -> dict:
        """
        Generate and set a common settings for chords and modes
        """
        item = deepcopy(TheoryItem)
        item["type"] = type

        scale_id = choice(list(SCALES.keys()))
        item["scale_id"] = scale_id
        item["scale"] = SCALES[scale_id]

        mode_dir = choice(list(MODES_DIR.keys()))
        item["dir_id"] = mode_dir
        item["dir"] = MODES_DIR[mode_dir]

        return item

    def _get_notes_for_scale(self, note_start, notes) -> list:
        """
        Get all notes present in a provided scale
        """
        modified_notes = [note_start]
        for n in notes:
            modified_notes.append(modified_notes[-1] + n)
        return modified_notes

    def get_mode(self) -> dict:
        """
        Generate a mode to guess
        """
        mode = self._get_common_items("Mode")
        mode_id = choice(list(MODES.keys()))
        mode["id"] = mode_id
        mode["name"] = MODES[mode_id]
        mode["desc"] = MODES_DESC[mode_id]
        mode["notes"] = self._get_notes_for_scale(mode["scale_id"], MODES_MIDI[mode_id])
        return mode

    def get_chord(self) -> dict:
        """
        Generate a chord to guess
        """
        chord = self._get_common_items("Chord")
        chord_id = choice(BASIC_CHORDS)
        chord["id"] = chord_id
        chord["name"] = CHORDS[chord_id]
        chord["desc"] = CHORDS[chord_id]
        chord["notes"] = self._get_notes_for_scale(
            chord["scale_id"], CHORDS_MIDI[chord_id]
        )
        return chord
