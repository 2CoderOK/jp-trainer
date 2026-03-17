"""note_display.py – Modern resizable UI for Jazz Piano Trainer."""

import json
import tkinter as tk
import tkinter.ttk as ttk
from pathlib import Path
from typing import Optional

from PIL import Image, ImageTk

# ── Package-local resources ───────────────────────────────────────────────────
_ASSET_DIR = Path(__file__).parent / "images"


def _load_ui_config() -> dict:
    cfg_path = Path(__file__).parent / "config" / "note_display_config.json"
    if cfg_path.exists():
        try:
            with cfg_path.open("r", encoding="utf-8") as fh:
                return json.load(fh)
        except Exception:
            pass
    raise FileNotFoundError(f"UI config not found: {cfg_path}")


_CFG = _load_ui_config()

# Keyboard image is fixed-width (drives scroll region)
KEYBOARD_WIDTH = int(_CFG.get("WINDOW_WIDTH", 1913))
# Original canvas placed keys at anchor="w", y=400 in a tall canvas
_KEYS_CANVAS_CY = 400  # original vertical center of keyboard in old canvas
IMAGE_NAMES = list(_CFG.get("IMAGE_NAMES", []))
NOTES_TO_IMAGE_MAP = {int(k): v for k, v in _CFG.get("NOTES_TO_IMAGE_MAP", {}).items()}
NOTES_Y = int(_CFG.get("NOTES_Y", 401))
NOTES_X = {int(k): int(v) for k, v in _CFG.get("NOTES_X", {}).items()}

from .theme import (
    ACCENT,
    ACCENT2,
    BG,
    BORDER,
    BTN_TXT,
    CARD,
    ENTRY_BG,
    FONT,
    HOVER_P,
    KB_BG,
    MUTED,
    SURF,
    TEXT,
)

MIN_W, MIN_H = 900, 620


class NoteDisplay:
    """Modern, resizable UI for the Jazz Piano Trainer."""

    def __init__(self, button_callback, button_replay_callback) -> None:
        self._btn_cb = button_callback
        self._replay_cb = button_replay_callback
        self._settings_cb = None  # set later via set_open_settings()

        # keyboard state
        self._octaves: int = 4  # visible octaves (updated by set_octaves)
        self._kb_scale_x: float = 1.0  # current horizontal scale vs original image
        self._note_states: dict = {}  # note_id -> is_green
        self._scaled_images: dict = {}  # name -> ImageTk (at current scale)
        self._note_widgets: dict = {}  # note_id -> canvas item id
        self._resize_job = None  # debounce handle

        self.window = tk.Tk()
        self.window.title("Jazz Piano Trainer")
        self.window.configure(bg=BG)
        self.window.minsize(MIN_W, MIN_H)
        self.window.geometry("1280x760")

        self._setup_styles()
        self._load_images()
        self._build_layout()

    # ── Styles ────────────────────────────────────────────────────────────────

    def _setup_styles(self) -> None:
        st = ttk.Style(self.window)
        st.theme_use("clam")

        st.configure("App.TFrame", background=BG)
        st.configure("Surf.TFrame", background=SURF)
        st.configure("Card.TFrame", background=CARD)

        # Primary action button
        st.configure(
            "Primary.TButton",
            background=ACCENT,
            foreground=BTN_TXT,
            font=(FONT, 12, "bold"),
            padding=(22, 11),
            relief="flat",
            borderwidth=0,
            focuscolor=ACCENT,
        )
        st.map(
            "Primary.TButton",
            background=[("active", HOVER_P), ("pressed", HOVER_P)],
            relief=[("pressed", "flat")],
        )

        # Secondary / ghost button
        st.configure(
            "Secondary.TButton",
            background=CARD,
            foreground=ACCENT2,
            font=(FONT, 11),
            padding=(22, 11),
            relief="flat",
            borderwidth=0,
            focuscolor=CARD,
        )
        st.map(
            "Secondary.TButton", background=[("active", BORDER), ("pressed", BORDER)]
        )

        # Mode drop-down button
        st.configure(
            "Mode.TMenubutton",
            background=CARD,
            foreground=TEXT,
            font=(FONT, 10),
            padding=(12, 6),
            relief="flat",
            borderwidth=0,
            arrowcolor=ACCENT,
        )
        st.map("Mode.TMenubutton", background=[("active", BORDER)])

        # Scrollbar (keyboard panel)
        st.configure(
            "KB.Horizontal.TScrollbar",
            background=SURF,
            troughcolor=BG,
            bordercolor=BG,
            arrowcolor=MUTED,
            relief="flat",
            borderwidth=0,
        )
        st.map("KB.Horizontal.TScrollbar", background=[("active", BORDER)])

        # Separator
        st.configure("Div.TSeparator", background=BORDER)

    # ── Image loading ─────────────────────────────────────────────────────────

    def _load_images(self) -> None:
        self._keys_pil = Image.open(_ASSET_DIR / "keys.png")

        # Y offset: original canvas placed keys at anchor="w", cy=_KEYS_CANVAS_CY.
        # New canvas places image at anchor="nw", so y_new = NOTES_Y - (CY - h/2).
        key_h = self._keys_pil.height
        self._adj_notes_y = NOTES_Y - (_KEYS_CANVAS_CY - key_h // 2)

        # Keep original PIL images for rescaling later
        self._orig_images: dict = {}
        for name in IMAGE_NAMES:
            self._orig_images[name] = Image.open(_ASSET_DIR / f"{name}.png")

        # Initialise Tk references at 1:1 scale
        self.keys_img = ImageTk.PhotoImage(self._keys_pil)
        self.images: dict = {
            name: ImageTk.PhotoImage(pil) for name, pil in self._orig_images.items()
        }
        self._scaled_images = dict(self.images)  # will be updated on resize

        self._placeholder = Image.open(_ASSET_DIR / "placeholder.png")
        self.a_img = ImageTk.PhotoImage(self._placeholder)

        # Compute how many pixels one octave spans in the original image
        # C2=MIDI36 @ x=3, C3=MIDI48 @ x=480  => 477 px/octave
        self._orig_oct_span_px: int = NOTES_X[48] - NOTES_X[36]

    # ── Layout ────────────────────────────────────────────────────────────────

    def _build_layout(self) -> None:
        w = self.window
        w.columnconfigure(0, weight=1)
        w.rowconfigure(0, weight=0)  # header
        w.rowconfigure(1, weight=0)  # divider
        w.rowconfigure(2, weight=1)  # main content
        w.rowconfigure(3, weight=0)  # keyboard
        w.rowconfigure(4, weight=0)  # status bar

        self._build_header()
        tk.Frame(w, bg=BORDER, height=1).grid(row=1, column=0, sticky="ew")
        self._build_main()
        self._build_keyboard()
        self._build_statusbar()

    def _build_header(self) -> None:
        hdr = tk.Frame(self.window, bg=SURF)
        hdr.grid(row=0, column=0, sticky="ew")
        hdr.columnconfigure(2, weight=1)  # spacer column

        # App title / logo
        tk.Label(
            hdr,
            text="🎹  Jazz Piano Trainer",
            bg=SURF,
            fg=TEXT,
            font=(FONT, 14, "bold"),
            padx=20,
            pady=12,
        ).grid(row=0, column=0, sticky="w")

        # Thin vertical divider
        tk.Frame(hdr, bg=BORDER, width=1).grid(
            row=0, column=1, sticky="ns", padx=(4, 16), pady=8
        )

        # Spacer
        tk.Frame(hdr, bg=SURF).grid(row=0, column=2, sticky="ew")

        # Mode label + selector
        tk.Label(hdr, text="Mode", bg=SURF, fg=MUTED, font=(FONT, 9)).grid(
            row=0, column=3, padx=(0, 6)
        )

        self.option_var = tk.StringVar(value="MODES")
        self.selected_option = "MODES"
        self.option_widget = ttk.OptionMenu(
            hdr,
            self.option_var,
            "MODES",
            "CHORDS",
            style="Mode.TMenubutton",
        )
        self.option_var.trace_add(
            "write", lambda *_: self.option_update(self.option_var.get())
        )
        self.option_widget.grid(row=0, column=4, padx=(0, 12), pady=8)

        # ⚙ Settings button
        self._gear_btn = tk.Button(
            hdr,
            text="⚙",
            bg=SURF,
            fg=MUTED,
            font=(FONT, 13),
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=SURF,
            activeforeground=ACCENT,
            command=self._open_settings,
        )
        self._gear_btn.grid(row=0, column=5, padx=(0, 18), pady=8)

    def _build_main(self) -> None:
        main = tk.Frame(self.window, bg=BG)
        main.grid(row=2, column=0, sticky="nsew", padx=16, pady=12)
        main.columnconfigure(0, weight=0)  # sidebar
        main.columnconfigure(1, weight=1)  # content card
        main.rowconfigure(0, weight=1)

        # ── Sidebar ──────────────────────────────────────────────────────────
        side = tk.Frame(main, bg=SURF, padx=18, pady=18)
        side.grid(row=0, column=0, sticky="ns", padx=(0, 12))
        side.rowconfigure(3, weight=1)

        tk.Label(side, text="CONTROLS", bg=SURF, fg=MUTED, font=(FONT, 8, "bold")).grid(
            row=0, column=0, sticky="w", pady=(0, 14)
        )

        self.button = ttk.Button(
            side, text="▶  NEXT", style="Primary.TButton", command=self._btn_cb
        )
        self.button.grid(row=1, column=0, sticky="ew", pady=(0, 8))

        self.button_replay = ttk.Button(
            side, text="↺  REPLAY", style="Secondary.TButton", command=self._replay_cb
        )
        self.button_replay.grid(row=2, column=0, sticky="ew")

        tk.Label(
            side,
            text="Play notes on\nyour MIDI keyboard",
            bg=SURF,
            fg=MUTED,
            font=(FONT, 8),
            justify="center",
        ).grid(row=4, column=0, pady=(20, 0))

        # ── Content card ─────────────────────────────────────────────────────
        card = tk.Frame(main, bg=CARD, padx=24, pady=20)
        card.grid(row=0, column=1, sticky="nsew")
        card.columnconfigure(0, weight=1)
        card.columnconfigure(1, weight=1)
        card.rowconfigure(1, weight=1)

        # Section headers
        tk.Label(card, text="QUESTION", bg=CARD, fg=MUTED, font=(FONT, 8, "bold")).grid(
            row=0, column=0, sticky="nw"
        )
        tk.Label(card, text="ANSWER", bg=CARD, fg=MUTED, font=(FONT, 8, "bold")).grid(
            row=0, column=1, sticky="nw"
        )

        # Question text
        self.q_label = tk.Label(
            card,
            text="Press NEXT to Start",
            bg=CARD,
            fg=TEXT,
            font=(FONT, 22, "bold"),
            anchor="nw",
            justify="left",
            wraplength=420,
        )
        self.q_label.grid(row=1, column=0, sticky="nw", pady=(10, 0), padx=(0, 20))

        # Answer frame (image + text stacked)
        ans_frame = tk.Frame(card, bg=CARD)
        ans_frame.grid(row=1, column=1, sticky="nw", pady=(10, 0))

        self.q2_label = tk.Label(
            ans_frame,
            text="",
            bg=CARD,
            fg=ACCENT2,
            font=(FONT, 16),
            anchor="nw",
            justify="left",
            wraplength=380,
        )
        self.q2_label.pack(anchor="nw")

        self.a_label = tk.Label(ans_frame, image=self.a_img, bg=CARD, bd=0)
        self.a_label.pack(anchor="nw", pady=(10, 0))

    def _build_keyboard(self) -> None:
        key_h = self._keys_pil.height

        # Accent line above keyboard
        tk.Frame(self.window, bg=ACCENT, height=2).grid(row=3, column=0, sticky="ew")

        kb_wrap = tk.Frame(self.window, bg=KB_BG)
        kb_wrap.grid(row=3, column=0, sticky="ew")
        kb_wrap.columnconfigure(0, weight=1)

        self.kb_canvas = tk.Canvas(
            kb_wrap,
            bg=KB_BG,
            height=key_h,
            bd=0,
            highlightthickness=0,
        )
        self._kb_hscroll = ttk.Scrollbar(
            kb_wrap,
            orient="horizontal",
            command=self.kb_canvas.xview,
            style="KB.Horizontal.TScrollbar",
        )
        self.kb_canvas.configure(xscrollcommand=self._kb_hscroll.set)
        self.kb_canvas.grid(row=1, column=0, sticky="ew")
        self._kb_hscroll.grid(row=2, column=0, sticky="ew")

        # Redraw after the canvas has been laid out (first Configure event)
        self.kb_canvas.bind("<Configure>", self._on_kb_resize)

    def _on_kb_resize(self, event=None) -> None:
        """Debounced handler for canvas resize or octave change."""
        if self._resize_job is not None:
            self.window.after_cancel(self._resize_job)
        self._resize_job = self.window.after(80, self._redraw_keyboard)

    def _redraw_keyboard(self) -> None:
        """Render the keyboard image at the right scale and restore note overlays."""
        canvas_w = self.kb_canvas.winfo_width()
        if canvas_w <= 1:
            return  # not yet laid out; will be called again by <Configure>

        # --- compute horizontal scale --------------------------------------
        # We want `self._octaves` octaves to fit exactly in canvas_w pixels.
        # The original image contains 4 octaves.
        scale_x = canvas_w / (self._octaves * self._orig_oct_span_px)

        orig_w = self._keys_pil.width
        orig_h = self._keys_pil.height
        new_w = max(1, int(orig_w * scale_x))

        # --- scale keyboard background image --------------------------------
        scaled_kb = self._keys_pil.resize((new_w, orig_h), Image.LANCZOS)
        self.keys_img = ImageTk.PhotoImage(scaled_kb)

        # --- scale note-overlay images (horizontal only) --------------------
        self._scaled_images = {}
        for name, pil_img in self._orig_images.items():
            ow, oh = pil_img.size
            nw = max(1, int(ow * scale_x))
            self._scaled_images[name] = ImageTk.PhotoImage(
                pil_img.resize((nw, oh), Image.LANCZOS)
            )
        # keep .images in sync so legacy callers still work
        self.images = self._scaled_images

        # --- update canvas geometry & content --------------------------------
        self.kb_canvas.configure(
            height=orig_h,
            scrollregion=(0, 0, new_w, orig_h),
        )
        self.kb_canvas.delete("all")
        self.kb_canvas.create_image(0, 0, image=self.keys_img, anchor="nw")
        self.kb_canvas.create_rectangle(0, 0, new_w, 2, fill=ACCENT, outline="")

        self._kb_scale_x = scale_x

        # --- restore note overlays -------------------------------------------
        # iterate only integer note ids and ignore/clean stray keys
        for note_id in list(self._note_states.keys()):
            if not isinstance(note_id, int):
                try:
                    del self._note_states[note_id]
                except Exception:
                    pass
                continue
            is_green = self._note_states[note_id]
            self._draw_note_overlay(note_id, is_green)

    def _draw_note_overlay(self, note_id: int, is_green: bool) -> None:
        """Draw (or redraw) a single note overlay at the current scale."""
        note_name = self.get_note_image(note_id)
        if note_name is None:
            return
        img_key = f"key_green_{note_name}" if is_green else f"key_red_{note_name}"
        img = self._scaled_images.get(img_key)
        if img is None:
            return
        x = int(NOTES_X.get(note_id, 0) * self._kb_scale_x)
        # remove any previous widget for this note before redrawing
        old = self._note_widgets.get(note_id)
        if old:
            try:
                self.kb_canvas.delete(old)
            except Exception:
                pass
        wid = self.kb_canvas.create_image(x, self._adj_notes_y, image=img, anchor="w")
        # stash canvas item id separately
        self._note_widgets[note_id] = wid

    def _build_statusbar(self) -> None:
        bar = tk.Frame(self.window, bg=SURF, height=24)
        bar.grid(row=4, column=0, sticky="ew")

        self.status_var = tk.StringVar(value="Ready")
        tk.Label(
            bar,
            textvariable=self.status_var,
            bg=SURF,
            fg=ACCENT2,
            font=(FONT, 8),
            padx=12,
            pady=4,
        ).pack(side=tk.LEFT)

        tk.Label(
            bar,
            text="Jazz Piano Trainer 2026 CoderOK",
            bg=SURF,
            fg=MUTED,
            font=(FONT, 8),
            padx=12,
        ).pack(side=tk.RIGHT)

    # ── Internal callbacks ────────────────────────────────────────────────────

    def _open_settings(self) -> None:
        if self._settings_cb:
            self._settings_cb()

    # ── Public API (compatible with original) ─────────────────────────────────

    def set_open_settings(self, callback) -> None:
        """Register the callable that opens the Settings dialog."""
        self._settings_cb = callback

    def set_octaves(self, octaves: int) -> None:
        """Change the number of visible octaves and immediately redraw the keyboard."""
        self._octaves = max(1, min(7, octaves))
        self._on_kb_resize()

    def option_update(self, selected_option: str) -> None:
        self.selected_option = selected_option

    def get_note_image(self, note_id: int) -> Optional[str]:
        real_note = None
        for n in [72, 60, 48, 36]:
            if note_id >= n:
                real_note = note_id - n
                break
        return NOTES_TO_IMAGE_MAP.get(real_note) if real_note is not None else None

    def add_note(self, note_id: int, is_green: bool = True) -> None:
        self._note_states[note_id] = is_green
        self._draw_note_overlay(note_id, is_green)

    def remove_note(self, note_id: int) -> None:
        if note_id in self._note_states:
            del self._note_states[note_id]
        if note_id in self._note_widgets:
            try:
                self.kb_canvas.delete(self._note_widgets.pop(note_id))
            except Exception:
                pass

    def update_question(self, txt: str) -> None:
        self.q_label.config(text=txt)

    def update_answer(self, image_path: str, txt: str) -> None:
        photo = ImageTk.PhotoImage(Image.open(image_path))
        self.a_label.config(image=photo)
        self.a_label.image = photo  # keep reference
        self.q2_label.config(text=txt)

    def set_status(self, msg: str) -> None:
        """Update the bottom status bar."""
        self.status_var.set(msg)
