"""settings_dialog.py – Modal Settings dialog for Jazz Piano Trainer."""

from __future__ import annotations

import tkinter as tk
import tkinter.filedialog as fd
import tkinter.ttk as ttk
from pathlib import Path
from typing import Callable, List, Optional

import mido

from .settings import AppSettings, save_settings

from .theme import (
    ACCENT,
    ACCENT2,
    BG,
    BORDER,
    BTN_TXT,
    CARD,
    ENTRY_BG,
    ERR,
    FONT,
    HOVER_P,
    MUTED,
    SURF,
    TEXT,
)


def _styled_entry(parent, textvariable=None, width=22) -> tk.Entry:
    e = tk.Entry(
        parent,
        textvariable=textvariable,
        width=width,
        bg=ENTRY_BG,
        fg=TEXT,
        insertbackground=TEXT,
        relief="flat",
        bd=0,
        highlightthickness=1,
        highlightbackground=BORDER,
        highlightcolor=ACCENT,
        font=(FONT, 10),
    )
    return e


def _label(parent, text, *, muted=False, bold=False) -> tk.Label:
    weight = "bold" if bold else "normal"
    color = MUTED if muted else TEXT
    return tk.Label(
        parent,
        text=text,
        bg=CARD,
        fg=color,
        font=(FONT, 9, weight),
    )


def _section(parent, title: str) -> tk.Frame:
    """Returns a labelled card frame."""
    outer = tk.Frame(parent, bg=CARD, padx=16, pady=12)
    tk.Label(outer, text=title, bg=CARD, fg=MUTED, font=(FONT, 8, "bold")).pack(
        anchor="w", pady=(0, 8)
    )
    tk.Frame(outer, bg=BORDER, height=1).pack(fill="x", pady=(0, 8))
    return outer


class SettingsDialog(tk.Toplevel):
    """
    Modal settings window.  Call ``SettingsDialog(parent, settings, on_apply)``
    where *on_apply* receives the new ``AppSettings`` instance when the user
    clicks **Apply**.
    """

    def __init__(
        self,
        parent: tk.Misc,
        settings: AppSettings,
        on_apply: Callable[[AppSettings], None],
    ) -> None:
        super().__init__(parent)
        self.title("Settings")
        self.configure(bg=BG)
        self.resizable(False, False)
        self.grab_set()  # modal

        self._orig = settings
        self._on_apply = on_apply

        # live copies of the mutable data
        self._midi_selected: List[str] = list(settings.midi_ports)

        self._setup_styles()
        self._build()
        self.update_idletasks()

        # Centre over parent using requested (post-layout) dimensions
        pw = parent.winfo_rootx()
        py = parent.winfo_rooty()
        sw = parent.winfo_width()
        sh = parent.winfo_height()
        dw = self.winfo_reqwidth()
        dh = self.winfo_reqheight()
        self.geometry(f"+{pw + max(0, (sw - dw) // 2)}+{py + max(0, (sh - dh) // 2)}")

    # ── Internal helpers ──────────────────────────────────────────────────────

    def _setup_styles(self) -> None:
        st = ttk.Style(self)
        # re-apply to this Toplevel's style context
        st.configure("Dlg.TNotebook", background=BG, borderwidth=0)
        st.configure(
            "Dlg.TNotebook.Tab",
            background=SURF,
            foreground=MUTED,
            font=(FONT, 9),
            padding=(14, 6),
        )
        st.map(
            "Dlg.TNotebook.Tab",
            background=[("selected", CARD)],
            foreground=[("selected", TEXT)],
        )

        st.configure(
            "DlgPrimary.TButton",
            background=ACCENT,
            foreground=BTN_TXT,
            font=(FONT, 10, "bold"),
            padding=(18, 8),
            relief="flat",
            borderwidth=0,
        )
        st.map(
            "DlgPrimary.TButton", background=[("active", HOVER_P), ("pressed", HOVER_P)]
        )

        st.configure(
            "DlgSecondary.TButton",
            background=CARD,
            foreground=TEXT,
            font=(FONT, 10),
            padding=(18, 8),
            relief="flat",
            borderwidth=0,
        )
        st.map("DlgSecondary.TButton", background=[("active", BORDER)])

        st.configure(
            "DlgCheck.TCheckbutton", background=CARD, foreground=TEXT, font=(FONT, 10)
        )
        st.map("DlgCheck.TCheckbutton", background=[("active", CARD)])

        # Horizontal.TScale is the correct built-in style name for orient=horizontal
        st.configure(
            "Horizontal.TScale",
            background=CARD,
            troughcolor=BORDER,
            sliderlength=18,
        )

    def _build(self) -> None:
        nb = ttk.Notebook(self, style="Dlg.TNotebook")
        nb.pack(fill="both", expand=True, padx=0, pady=0)

        self._build_midi_tab(nb)
        self._build_sampler_tab(nb)
        self._build_display_tab(nb)

        # ── Footer buttons ────────────────────────────────────────────────
        footer = tk.Frame(self, bg=SURF, padx=16, pady=10)
        footer.pack(fill="x")
        tk.Frame(footer, bg=BORDER, height=1).pack(fill="x", pady=(0, 10))

        ttk.Button(
            footer, text="Cancel", style="DlgSecondary.TButton", command=self.destroy
        ).pack(side="right", padx=(6, 0))
        ttk.Button(
            footer, text="✔  Apply", style="DlgPrimary.TButton", command=self._apply
        ).pack(side="right")

    # ── MIDI tab ──────────────────────────────────────────────────────────────

    def _build_midi_tab(self, nb: ttk.Notebook) -> None:
        frame = tk.Frame(nb, bg=CARD, padx=6, pady=6)
        nb.add(frame, text="  MIDI  ")

        sec = _section(frame, "MIDI INPUT PORTS")
        sec.pack(fill="both", expand=True)

        tk.Label(
            sec,
            text="Check the ports to listen on. No selection = MIDI disabled.",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 8),
            justify="left",
        ).pack(anchor="w", pady=(0, 8))

        # Listbox with checkboxes (use variables per row)
        list_frame = tk.Frame(sec, bg=CARD)
        list_frame.pack(fill="both", expand=True)

        try:
            available_ports: List[str] = mido.get_input_names()
        except Exception:
            available_ports = []

        self._port_vars: dict[str, tk.BooleanVar] = {}
        if not available_ports:
            tk.Label(
                list_frame,
                text="No MIDI devices detected.",
                bg=CARD,
                fg=ERR,
                font=(FONT, 9),
            ).pack(anchor="w")
        else:
            for port in available_ports:
                var = tk.BooleanVar(value=(port in self._midi_selected))
                self._port_vars[port] = var
                cb = ttk.Checkbutton(
                    list_frame,
                    text=port,
                    variable=var,
                    style="DlgCheck.TCheckbutton",
                )
                cb.pack(anchor="w", pady=2)

        # Refresh button
        tk.Button(
            sec,
            text="↺  Refresh ports",
            bg=CARD,
            fg=ACCENT2,
            font=(FONT, 8),
            relief="flat",
            bd=0,
            cursor="hand2",
            activebackground=CARD,
            activeforeground=HOVER_P,
            command=self._refresh_ports,
        ).pack(anchor="w", pady=(10, 0))

        self._midi_list_frame = list_frame
        self._available_ports = available_ports

    def _refresh_ports(self) -> None:
        for w in self._midi_list_frame.winfo_children():
            w.destroy()
        self._port_vars.clear()
        try:
            ports: List[str] = mido.get_input_names()
        except Exception:
            ports = []
        self._available_ports = ports
        if not ports:
            tk.Label(
                self._midi_list_frame,
                text="No MIDI devices detected.",
                bg=CARD,
                fg=ERR,
                font=(FONT, 9),
            ).pack(anchor="w")
        else:
            for port in ports:
                var = tk.BooleanVar(value=(port in self._midi_selected))
                self._port_vars[port] = var
                ttk.Checkbutton(
                    self._midi_list_frame,
                    text=port,
                    variable=var,
                    style="DlgCheck.TCheckbutton",
                ).pack(anchor="w", pady=2)

    # ── Sampler tab ───────────────────────────────────────────────────────────

    def _build_sampler_tab(self, nb: ttk.Notebook) -> None:
        frame = tk.Frame(nb, bg=CARD, padx=6, pady=6)
        nb.add(frame, text="  Sampler  ")

        sec = _section(frame, "PIANO SAMPLER")
        sec.pack(fill="x")

        # enabled toggle
        self._sampler_enabled = tk.BooleanVar(value=self._orig.sampler_enabled)
        row = tk.Frame(sec, bg=CARD)
        row.pack(fill="x", pady=3)
        ttk.Checkbutton(
            row,
            text="Enable sampler (piano sound playback)",
            variable=self._sampler_enabled,
            style="DlgCheck.TCheckbutton",
        ).pack(side="left")

        # ignore velocity
        self._ignore_vel = tk.BooleanVar(value=self._orig.ignore_velocity)
        row2 = tk.Frame(sec, bg=CARD)
        row2.pack(fill="x", pady=3)
        ttk.Checkbutton(
            row2,
            text="Ignore velocity (all notes play at full volume)",
            variable=self._ignore_vel,
            style="DlgCheck.TCheckbutton",
        ).pack(side="left")

        # sustain
        self._sustain = tk.BooleanVar(value=self._orig.sustain)
        row3 = tk.Frame(sec, bg=CARD)
        row3.pack(fill="x", pady=3)
        ttk.Checkbutton(
            row3,
            text="Sustain (notes ring until next note-off)",
            variable=self._sustain,
            style="DlgCheck.TCheckbutton",
        ).pack(side="left")

        tk.Frame(sec, bg=BORDER, height=1).pack(fill="x", pady=(10, 8))

        # polyphony (slider + numeric entry)
        poly_row = tk.Frame(sec, bg=CARD)
        poly_row.pack(fill="x", pady=4)
        _label(poly_row, "Polyphony", muted=True).pack(side="left", padx=(0, 10))
        self._polyphony = tk.IntVar(value=self._orig.polyphony)
        slider = ttk.Scale(
            poly_row,
            from_=1,
            to=256,
            orient="horizontal",
            variable=self._polyphony,
            length=160,
            command=lambda v: self._polyphony.set(int(float(v))),
        )
        slider.pack(side="left")
        _styled_entry(poly_row, textvariable=self._polyphony, width=5).pack(
            side="left", padx=(8, 0)
        )

        # samples path
        path_row = tk.Frame(sec, bg=CARD)
        path_row.pack(fill="x", pady=(10, 0))
        _label(path_row, "Samples file", muted=True).pack(anchor="w", pady=(0, 4))
        path_inner = tk.Frame(sec, bg=CARD)
        path_inner.pack(fill="x")
        self._samples_path = tk.StringVar(value=self._orig.samples_path)
        _styled_entry(path_inner, textvariable=self._samples_path, width=32).pack(
            side="left"
        )
        tk.Button(
            path_inner,
            text="Browse…",
            bg=BORDER,
            fg=TEXT,
            font=(FONT, 8),
            relief="flat",
            bd=0,
            padx=8,
            cursor="hand2",
            activebackground=ACCENT,
            activeforeground=BTN_TXT,
            command=self._browse_samples,
        ).pack(side="left", padx=(6, 0))

    def _browse_samples(self) -> None:
        path = fd.askopenfilename(
            title="Select piano samples archive",
            filetypes=[("ZIP files", "*.zip"), ("All files", "*.*")],
        )
        if path:
            self._samples_path.set(path)

    # ── Display tab ───────────────────────────────────────────────────────────

    def _build_display_tab(self, nb: ttk.Notebook) -> None:
        frame = tk.Frame(nb, bg=CARD, padx=6, pady=6)
        nb.add(frame, text="  Display  ")

        sec = _section(frame, "VIRTUAL KEYBOARD")
        sec.pack(fill="x")

        _label(sec, "Octaves to display  (1 – 7)", muted=True).pack(
            anchor="w", pady=(0, 8)
        )

        oct_row = tk.Frame(sec, bg=CARD)
        oct_row.pack(fill="x")

        self._octaves = tk.IntVar(value=max(1, min(7, self._orig.octaves)))

        scale = ttk.Scale(
            oct_row,
            from_=1,
            to=7,
            orient="horizontal",
            variable=self._octaves,
            length=240,
            command=lambda v: self._octaves.set(max(1, min(7, int(float(v))))),
        )
        scale.pack(side="left")

        self._oct_label = tk.Label(
            oct_row,
            text=str(self._octaves.get()),
            bg=CARD,
            fg=TEXT,
            font=(FONT, 11, "bold"),
            width=3,
        )
        self._oct_label.pack(side="left", padx=(10, 0))
        self._octaves.trace_add(
            "write", lambda *_: self._oct_label.config(text=str(self._octaves.get()))
        )

        tk.Label(
            sec,
            text="The keyboard rescales live when you click Apply.",
            bg=CARD,
            fg=MUTED,
            font=(FONT, 8),
        ).pack(anchor="w", pady=(12, 0))

    # ── Apply ─────────────────────────────────────────────────────────────────

    def _apply(self) -> None:
        selected_ports = [p for p, v in self._port_vars.items() if v.get()]

        new_settings = AppSettings(
            midi_ports=selected_ports,
            sampler_enabled=self._sampler_enabled.get(),
            ignore_velocity=self._ignore_vel.get(),
            sustain=self._sustain.get(),
            polyphony=max(1, min(256, self._polyphony.get())),
            samples_path=self._samples_path.get().strip(),
            octaves=max(1, min(7, self._octaves.get())),
            debug=self._orig.debug,
        )
        save_settings(new_settings)
        self._on_apply(new_settings)
        self.destroy()
