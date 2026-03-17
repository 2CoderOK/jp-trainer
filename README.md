# Jazz Piano Trainer

A desktop application to help you learn jazz piano **modes** and **chords** using your MIDI keyboard.  
Press **NEXT** to get a question, play the notes on your keyboard, and the app reveals the answer automatically once you hit all the right keys.

[<img alt="Jazz Piano Trainer preview" src="https://raw.githubusercontent.com/2CoderOK/jp-trainer/main/assets/jptrainer_preview.png" />](https://www.youtube.com/watch?v=WCQai649s_Q)

> Watch the walkthrough video: <https://www.youtube.com/watch?v=WCQai649s_Q>

---

## Features

- **Modes & Chords** — randomised questions covering all 12 keys, 7 modes, and a curated set of jazz chords
- **MIDI input** — connect one or more MIDI keyboards; correct notes light up green, wrong notes red on the virtual keyboard
- **Virtual piano keyboard** — resizable, scrollable, supports 1–7 octaves
- **Built-in sampler** — plays back audio samples for each note via [piano-sampler](https://github.com/2coderok/piano-sampler); can be disabled
- **Persistent settings** — MIDI ports, sampler options, and display preferences saved to `jptrainer.json`

---

## Dependencies

| Package | Purpose |
|---|---|
| [piano-sampler](https://github.com/2coderok/piano-sampler) | Audio sample playback engine (sister project) |
| [mido](https://mido.readthedocs.io/) + [python-rtmidi](https://spotlightkid.github.io/python-rtmidi/) | MIDI input handling |
| [pygame](https://www.pygame.org/) | Audio mixing |
| [Pillow](https://python-pillow.org/) | Image loading and keyboard scaling |
| tkinter (stdlib) | GUI framework |

---

## Installation

### With uv (recommended)

```bash
uv tool install jptrainer
jptrainer
```

### With pip

```bash
pip install jptrainer
jptrainer
```

---

## Usage

1. Launch the app — the virtual keyboard and dark-themed UI open automatically.
2. Open **⚙ Settings** (gear icon, top-right of the header) to:
   - Select which MIDI input port(s) to use
   - Configure the sampler (enable/disable, velocity, sustain, polyphony, sample path)
   - Set how many octaves to display (1–7)
3. Choose **MODES** or **CHORDS** from the mode selector in the header.
4. Click **▶ NEXT** — a question appears (e.g. *"G Dorian"*).
5. Play the required notes on your MIDI keyboard.  Correct notes glow **green**; the answer reveals itself when all notes are played. After 10 seconds the answer is shown automatically.
6. Click **↺ REPLAY** to hear the audio example again.

---

## Settings file

Settings are saved to `jptrainer.json` in the project root:

```json
{
  "midi_ports": ["Your MIDI Device"],
  "sampler_enabled": true,
  "ignore_velocity": true,
  "sustain": false,
  "polyphony": 32,
  "samples_path": "./piano_samples.zip",
  "octaves": 4,
  "debug": false
}
```

---

## Related projects

- **[piano-sampler](https://github.com/2coderok/piano-sampler)** — the simple piano sampler used by this app

---

[<img alt="Buy me a coffee" height="50px" src="https://raw.githubusercontent.com/2CoderOK/jp-trainer/main/assets/yellow-button.png" />](https://www.buymeacoffee.com/coderok)


---


🚨 WARNING: INCOMING SHAMELESS PLUG 🚨
Please avert your eyes if you are allergic to indie devs promoting their own stuff on their free MIT repos! 🫣

🎹 JazzPianoTrainer — Meet its beefy C++ sibling, [JazzPianoLab](https://jazzpianolab.app/s/4p7ZtR)!

I loved working on this repo, but my curiosity got the better of me. I really wanted to build my own highly controllable audio tool from the ground up, just to see what I could do. Fast forward a bit, and I accidentally spent way too much time creating a massive, supercharged version called [JazzPianoLab](https://jazzpianolab.app/s/4p7ZtR)!

It's written in C++ using the JUCE 8 audio framework and is packed with features I nerded out on:

🎹 VST3 Virtual Instrument Support

🎼 Advanced Chord Profile System

⚡ Real-Time Chord Identification

🔴 Built-in MIDI Recorder

...and much more!

Don't worry, this MIT project isn't going anywhere! But if you’re looking for a next-level jazz piano training tool (or just want to see what happens when a developer gets completely carried away), check out [JazzPianoLab](https://jazzpianolab.app/s/4p7ZtR) for the latest updates and downloads.

Let’s make jazz piano learning smarter and more fun together!

[<img width="500px" alt="JazzPianoLabr" src="https://jazzpianolab.app/static/assets/img/illustrations/jpl_image_5.jpg" />](https://jazzpianolab.app/s/4p7ZtR)