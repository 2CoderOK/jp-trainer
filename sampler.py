from pygame import mixer

SAMPLER_POLYPHONY = 32


class Sampler:
    """
    A Sampler class that plays audio files on demand
    """

    def __init__(self, mix: mixer, ignore_velocity: bool, sustain: bool) -> None:
        """
        Load audio files and map them to midi notes ids
        """
        mix.set_num_channels(SAMPLER_POLYPHONY)

        self.ignore_velocity = ignore_velocity
        self.sustain = sustain
        self.id_to_note = {}
        self.id_to_file = {}
        notes = ["C", "Db", "D", "Eb", "E", "F", "Gb", "G", "Ab", "A", "Bb", "B"]
        octave = 1
        notes_id = 0
        for i in range(24, 96):
            self.id_to_note[i] = f"{notes[notes_id]}"
            self.id_to_file[i] = f"Piano.ff.{notes[notes_id]}{octave}.aiff"
            notes_id += 1
            if len(notes) == notes_id:
                notes_id = 0
            if i in [23, 35, 47, 59, 71, 83]:
                octave += 1
        self.sounds = {}
        for id, name in self.id_to_file.items():
            self.sounds[id] = mix.Sound("audio/samples/" + name)

    def play(self, note_id: int, vel: int) -> None:
        """
        Play an audio file mapped to a given note_id (midi note id)
        using a velocity supplied in the midi message
        """
        self.sounds[note_id].stop()
        if not self.ignore_velocity:
            self.sounds[note_id].set_volume(float((vel / 127) * 1.0))
        self.sounds[note_id].play()

    def stop(self, note_id: int) -> None:
        """
        Stop playing an audio file mapped to a given note_id (midi note id)
        Fadeout sounds better (less cracking) and setting it to bigger values (over 300)
        helps playing without a sustain pedal
        """
        self.sounds[note_id].fadeout(600 if self.sustain else 300)
