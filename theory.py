class ScaleGenerator:
    def __init__(self, base_midi_note=60, octaves=1):
        self.base_midi_note = base_midi_note
        self.octaves = octaves
        self.note_to_midi = {
            'C': 0, 'Db': 1, 'D': 2, 'Eb': 3, 'E': 4, 'F': 5, 'Gb': 6,
            'G': 7, 'Ab': 8, 'A': 9, 'Bb': 10, 'B': 11
        }
        self.note_midi_list = list(self.note_to_midi.keys())
        self.scales = {}
        self.triads = {}
        self.sevenths = {}
        self.modes = {}
        self.generate_scales()
        self.generate_chords()
        self.generate_modes()

    def get_midi_notes(self, root, intervals, repeat_root=False):
        root_midi = self.base_midi_note + self.note_to_midi[root]
        notes = []
        for octave in range(self.octaves):
            notes.extend([root_midi + interval + 12 * octave for interval in intervals])
        if repeat_root:
            notes.append(root_midi + 12 * self.octaves)
        return notes

    def generate_scales(self):
        scale_intervals = {
            'major': [0, 2, 4, 5, 7, 9, 11],
            'natural_minor': [0, 2, 3, 5, 7, 8, 10],
            'harmonic_minor': [0, 2, 3, 5, 7, 8, 11],
            'melodic_minor': [0, 2, 3, 5, 7, 9, 11]
        }
        for root in self.note_to_midi.keys():
            for scale_name, intervals in scale_intervals.items():
                scale_key = f"{root} {scale_name}"
                self.scales[scale_key] = self.get_midi_notes(root, intervals, repeat_root=True)

        return self.scales

    def generate_chords(self):
        triad_intervals = {
            'major': [0, 4, 7],
            'minor': [0, 3, 7]
        }
        seventh_intervals = {
            'major7': [0, 4, 7, 11],
            'minor7': [0, 3, 7, 10],
            'dominant7': [0, 4, 7, 10],
            'diminished7': [0, 3, 6, 9],
            'half_diminished7': [0, 3, 6, 10]
        }
        for root in self.note_to_midi.keys():
            for triad_name, intervals in triad_intervals.items():
                chord_name = f"{root} {triad_name}"
                self.triads[chord_name] = {
                    'root': self.get_midi_notes(root, intervals),
                    '1st_inversion': self.get_midi_notes(root, intervals[1:] + [intervals[0] + 12]),
                    '2nd_inversion': self.get_midi_notes(root, intervals[2:] + [intervals[0] + 12, intervals[1] + 12])
                }
            for seventh_name, intervals in seventh_intervals.items():
                chord_name = f"{root} {seventh_name}"
                self.sevenths[chord_name] = {
                    'root': self.get_midi_notes(root, intervals),
                    '1st_inversion': self.get_midi_notes(root, intervals[1:] + [intervals[0] + 12]),
                    '2nd_inversion': self.get_midi_notes(root, intervals[2:] + [intervals[0] + 12, intervals[1] + 12]),
                    '3rd_inversion': self.get_midi_notes(root, intervals[3:] + [intervals[0] + 12, intervals[1] + 12, intervals[2] + 12])
                }

    def generate_modes(self):
        mode_names = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian']
        for scale_key, notes in self.scales.items():
            root, scale_type = scale_key.split()
            if scale_type == 'major':
                for i, mode_name in enumerate(mode_names):
                    mode_key = f"{root} {scale_type} {mode_name}"
                    mode_notes = notes[i:] + [note + 12 for note in notes[:i]]
                    mode_notes.append(mode_notes[0] + 12)  # Add the starting note at the end
                    self.modes[mode_key] = mode_notes

# Example usage:
ScaleGenerator = ScaleGenerator(base_midi_note=60, octaves=1)
