# copy.deepcopy no longer required after refactor
from dataclasses import dataclass, field
from secrets import choice
from pathlib import Path
from typing import List, Optional
import json


def _load_config() -> dict:
    """Load theory configuration from theory_config.json next to this file.

    Falls back to embedded defaults if file is missing or invalid.
    """
    cfg_path = Path(__file__).parent / "config" / "theory_config.json"
    if cfg_path.exists():
        try:
            with cfg_path.open("r", encoding="utf-8") as f:
                return json.load(f)
        except Exception:
            pass

    raise FileNotFoundError(
        f"config/theory_config.json not found or failed to load: {cfg_path}"
    )


_CFG = _load_config()

# expose as module-level structures for easy access in other parts of the code
SCALES = {i: name for i, name in enumerate(_CFG.get("SCALES", []))}
SCALES_MIDI = {i: v for i, v in enumerate(_CFG.get("SCALES_MIDI", []))}
CHORDS = {i: name for i, name in enumerate(_CFG.get("CHORDS", []))}
CHORDS_MIDI = {i: lst for i, lst in enumerate(_CFG.get("CHORDS_MIDI", []))}
BASIC_CHORDS = list(_CFG.get("BASIC_CHORDS", []))
MODES = {i: name for i, name in enumerate(_CFG.get("MODES", []))}
MODES_DESC = {i: desc for i, desc in enumerate(_CFG.get("MODES_DESC", []))}
MODES_MIDI = {i: lst for i, lst in enumerate(_CFG.get("MODES_MIDI", []))}
MODES_DIR = {i: d for i, d in enumerate(_CFG.get("MODES_DIR", []))}
CHORD_INVERSIONS = {i: name for i, name in enumerate(_CFG.get("CHORD_INVERSIONS", []))}
BASIC_CHORD_INVERSIONS = list(_CFG.get("BASIC_CHORD_INVERSIONS", []))


@dataclass
class TheoryItem:
    type: str = ""
    name: str = ""
    id: int = 0
    desc: str = ""
    image_path: Optional[str] = None
    audio_path: Optional[str] = None
    scale: str = ""
    dir: str = ""
    notes: List[int] = field(default_factory=list)
    scale_id: int = 0
    dir_id: int = 0


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
        item = TheoryItem()
        item.type = type

        scale_id = choice(list(SCALES.keys()))
        item.scale_id = scale_id
        item.scale = SCALES[scale_id]

        mode_dir = choice(list(MODES_DIR.keys()))
        item.dir_id = mode_dir
        item.dir = MODES_DIR[mode_dir]

        return item

    def _get_notes_for_scale(self, note_start: int, notes: List[int]) -> List[int]:
        """
        Get all notes present in a provided scale
        """
        modified_notes = [note_start]
        for n in notes:
            modified_notes.append(modified_notes[-1] + n)
        return modified_notes

    def get_mode(self) -> TheoryItem:
        """
        Generate a mode to guess
        """
        mode = self._get_common_items("Mode")
        mode_id = choice(list(MODES.keys()))
        mode.id = mode_id
        mode.name = MODES[mode_id]
        mode.desc = MODES_DESC[mode_id]
        mode.notes = self._get_notes_for_scale(mode.scale_id, MODES_MIDI[mode_id])
        return mode

    def get_chord(self) -> TheoryItem:
        """
        Generate a chord to guess
        """
        chord = self._get_common_items("Chord")
        chord_id = choice(BASIC_CHORDS)
        chord.id = chord_id
        chord.name = CHORDS[chord_id]
        chord.desc = CHORDS[chord_id]
        chord.notes = self._get_notes_for_scale(chord.scale_id, CHORDS_MIDI[chord_id])
        return chord
