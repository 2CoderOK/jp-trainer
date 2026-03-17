import logging
import threading
from contextlib import ExitStack
from pathlib import Path
from typing import Dict, List, Optional

import mido
from pygame import mixer

from .note_display import NoteDisplay
from piano_sampler.main import Sampler
from .settings import AppSettings, load_settings
from .theory import SCALES, Theory


class Trainer:
    """Encapsulates application state and behaviour for the Jazz Piano Trainer."""

    def __init__(
        self,
        settings: AppSettings,
        images_dir: Optional[Path] = None,
    ) -> None:
        self.settings = settings
        # prefer package-local resources when running as a module
        pkg_root = Path(__file__).parent
        self.images_dir = images_dir or (pkg_root / "images")

        mixer.init()
        if settings.sampler_enabled:
            self.sampler = Sampler(
                mixer,
                settings.polyphony,
                settings.ignore_velocity,
                settings.sustain,
                Path(settings.samples_path),
            )
        else:
            self.sampler = None

        self.theory = Theory()

        self.notes_on: List[int] = []
        self.good_notes: List[int] = []
        self.required_notes: List[List[int]] = []
        self.theory_item: Dict = {}

        self.replay_file: Optional[Path] = None
        self.img_path: Optional[Path] = None
        self.answer_text: str = ""
        self.timer: Optional[threading.Timer] = None

        # UI
        self.note_ui = NoteDisplay(self.button_handler, self.replay_handler)
        # Apply initial octave setting once the window is shown
        self.note_ui.window.after(
            100, lambda: self.note_ui.set_octaves(settings.octaves)
        )

    def timer_func(self) -> None:
        """Timer callback that reveals the answer on the UI."""
        if self.img_path and self.answer_text is not None:
            self.note_ui.update_answer(str(self.img_path), self.answer_text)

    def generate_path(self, t_item: Dict) -> Path:
        """Generate a resource path prefix (without extension) for a theory item."""
        # support dataclass or dict-like items
        type_val = (
            getattr(t_item, "type", None)
            if hasattr(t_item, "type")
            else t_item.get("type")
        )
        scale_id = (
            getattr(t_item, "scale_id", None)
            if hasattr(t_item, "scale_id")
            else t_item.get("scale_id")
        )
        item_id = (
            getattr(t_item, "id", None) if hasattr(t_item, "id") else t_item.get("id")
        )
        tp = "03" if type_val == "Mode" else "04"
        # maintain previous file naming pattern
        file_path = f"{tp}/{scale_id + 1:02d}/{tp}{scale_id:02d}{item_id:02d}"
        return Path(file_path)

    def replay_handler(self) -> None:
        """Replay the last played audio for the current question."""
        if self.replay_file and self.replay_file.exists():
            mixer.music.stop()
            mixer.music.play()

    def button_handler(self) -> None:
        """Handle NEXT button: pick a new theory item, update UI and play audio."""
        if self.note_ui.selected_option == "CHORDS":
            self.theory_item = self.theory.get_chord()
        else:
            self.theory_item = self.theory.get_mode()

        notes = (
            getattr(self.theory_item, "notes", None)
            if hasattr(self.theory_item, "notes")
            else self.theory_item.get("notes")
        )
        self.good_notes = [n + i for i in [36, 48, 60, 72] for n in notes]
        self.required_notes = [[n + 36, n + 48, n + 60, n + 72] for n in notes]

        file_path = self.generate_path(self.theory_item)
        # image selection: default placeholder until reveal
        # Construct image path similar to previous naming scheme
        self.img_path = self.images_dir / (str(file_path) + "01.png")

        scale_id = (
            getattr(self.theory_item, "scale_id", None)
            if hasattr(self.theory_item, "scale_id")
            else self.theory_item.get("scale_id")
        )
        q = f"{SCALES[scale_id]}"
        type_val = (
            getattr(self.theory_item, "type", None)
            if hasattr(self.theory_item, "type")
            else self.theory_item.get("type")
        )
        if type_val == "Chord":
            name = (
                getattr(self.theory_item, "name", "")
                if hasattr(self.theory_item, "name")
                else self.theory_item.get("name", "")
            )
            q += f" {name}"
            self.answer_text = q
        else:
            desc = (
                getattr(self.theory_item, "desc", "")
                if hasattr(self.theory_item, "desc")
                else self.theory_item.get("desc", "")
            )
            self.answer_text = q + " " + desc
            # previous code attempted to use a different image; keep same pattern
            self.img_path = Path(str(self.img_path).replace("0.png", "1.png"))

        inv_id = 0  # TODO: support random / chosen inversions
        pkg_root = Path(__file__).parent
        audio_path = pkg_root / "audio" / (str(file_path) + f"{inv_id:02d}.mp3")
        self.replay_file = audio_path
        try:
            mixer.music.load(str(audio_path))
            mixer.music.play()
        except Exception:
            logging.exception("Failed to load/play %s", audio_path)

        self.note_ui.update_question(q)
        self.note_ui.update_answer(str(self.images_dir / "placeholder.png"), "")

        if self.timer:
            self.timer.cancel()
        self.timer = threading.Timer(10.0, self.timer_func)
        self.timer.start()

    def note_handler(self, note: mido.Message) -> None:
        """Callback for incoming MIDI messages from mido.

        Runs in a background thread created by mido; keep work minimal and thread-safe.
        """
        if note.type not in ("note_on", "note_off"):
            return

        note_id = int(note.note) if note.note is not None else -1
        if note.type == "note_on":
            vel = getattr(note, "velocity", 127)
            if self.sampler:
                self.sampler.play(note_id, vel)
            is_green = False
            if note_id in self.good_notes:
                ids_to_remove = []
                for i, req in enumerate(self.required_notes):
                    if note_id in req:
                        ids_to_remove.append(i)
                # remove in reverse order to avoid index shifts
                for i in sorted(ids_to_remove, reverse=True):
                    if 0 <= i < len(self.required_notes):
                        del self.required_notes[i]
                if not self.required_notes:
                    if self.timer:
                        self.timer.cancel()
                    # reveal answer
                    if self.img_path:
                        self.note_ui.update_answer(str(self.img_path), self.answer_text)
                is_green = True
            # update UI
            self.note_ui.add_note(note_id, is_green)
            if note.note not in self.notes_on:
                self.notes_on.append(note.note)
        elif note.type == "note_off":
            if self.sampler:
                self.sampler.stop(note_id)
            self.note_ui.remove_note(note_id)
            if note.note in self.notes_on:
                self.notes_on.remove(note.note)


def _resolve_ports(settings: AppSettings) -> List[str]:
    """Return the list of MIDI port names to open.

    An empty *midi_ports* list means "no ports" – the user has not selected any.
    """
    if not settings.midi_ports:
        return []
    available = mido.get_input_names()
    selected = [p for p in settings.midi_ports if p in available]
    if not selected:
        logging.warning("Configured MIDI ports not available: %s", settings.midi_ports)
    return selected


def main() -> None:
    settings = load_settings()

    logging.basicConfig(
        level=logging.DEBUG if settings.debug else logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
    )

    # ── Build Trainer + UI ────────────────────────────────────────────────────
    trainer = Trainer(settings)

    # Callback called by the Settings dialog when Apply is clicked
    def on_settings_applied(new_settings: AppSettings) -> None:
        """Hot-reload: recreate sampler, close MIDI ports, re-open with new settings."""
        nonlocal active_stack, settings
        settings = new_settings
        trainer.settings = new_settings

        # ── Recreate sampler with new parameters ──────────────────────────────
        if trainer.sampler is not None:
            try:
                trainer.sampler.stop_all()
            except Exception:
                pass
            trainer.sampler = None

        if new_settings.sampler_enabled:
            try:
                trainer.sampler = Sampler(
                    mixer,
                    new_settings.polyphony,
                    new_settings.ignore_velocity,
                    new_settings.sustain,
                    Path(new_settings.samples_path),
                )
            except Exception:
                logging.exception("Failed to create Sampler with new settings")

        # ── Restart MIDI connections ───────────────────────────────────────────
        try:
            active_stack.close()
        except Exception:
            pass
        _start_midi(new_settings)

        # ── Apply display settings live ───────────────────────────────────────
        trainer.note_ui.set_octaves(new_settings.octaves)

    trainer.note_ui.set_open_settings(
        lambda: _open_settings_dialog(
            trainer.note_ui.window, settings, on_settings_applied
        )
    )

    # ── Open MIDI ports ───────────────────────────────────────────────────────
    active_stack: ExitStack = ExitStack()

    def _start_midi(cfg: AppSettings) -> None:
        nonlocal active_stack
        active_stack = ExitStack()
        ports = _resolve_ports(cfg)
        if not ports:
            if not cfg.midi_ports:
                trainer.note_ui.set_status("No MIDI ports selected – open ⚙ Settings")
            else:
                trainer.note_ui.set_status(
                    "Configured MIDI ports not available – check ⚙ Settings"
                )
            logging.warning("No MIDI ports to open.")
            return
        try:
            inputs = [
                active_stack.enter_context(
                    mido.open_input(name, callback=trainer.note_handler)
                )
                for name in ports
            ]
            logging.info("Opened %d MIDI input(s): %s", len(inputs), ports)
            summary = ", ".join(ports) if len(ports) <= 2 else f"{len(ports)} ports"
            trainer.note_ui.set_status(f"MIDI active · {summary}")
        except Exception:
            logging.exception("Failed to open MIDI port(s)")
            trainer.note_ui.set_status("MIDI error – check Settings")

    _start_midi(settings)

    try:
        trainer.note_ui.window.mainloop()
    finally:
        active_stack.close()


def _open_settings_dialog(parent, settings: AppSettings, on_apply) -> None:
    from .settings_dialog import SettingsDialog

    SettingsDialog(parent, settings, on_apply)


if __name__ == "__main__":
    main()
