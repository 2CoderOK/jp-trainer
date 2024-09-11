from gui import MainWindow
class Theory(MainWindow):
    def __init__(self):
        super().__init__()


        self.setup_theory_variables()
        self.generate_scales()
        self.generate_chords()
        self.generate_modes()
    def setup_theory_variables(self,base_midi_note=60, octaves=1):

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
        self.fingers = {"C major": "123 1234"}

    def get_midi_notes(self, root, intervals, repeat_root=False):
        if root not in self.note_to_midi:
            print(f"Invalid root note: {root}")
            return []

        root_midi = self.base_midi_note + self.note_to_midi[root]
        notes = []
        for octave in range(self.octaves):
            notes.extend([root_midi + interval + 12 * octave for interval in intervals])

        if repeat_root:
            notes.append(root_midi + 12 * self.octaves)

        if not notes:
            print(f"Generated empty notes for root: {root}, intervals: {intervals}")

        return notes

    def generate_scales(self):
        scale_intervals = {
            'Major': [0, 2, 4, 5, 7, 9, 11],
            'Natural Minor': [0, 2, 3, 5, 7, 8, 10],
            'Harmonic Minor': [0, 2, 3, 5, 7, 8, 11],
            'Melodic Minor': [0, 2, 3, 5, 7, 9, 11]
        }

        descending_intervals = {
            'Harmonic Minor': [10, 8, 7, 5, 3, 2, 0]  # Natural Minor intervals for descending
        }

        for root in self.note_to_midi.keys():
            for scale_name, intervals in scale_intervals.items():
                scale_key = f"{root} {scale_name}"
                ascending_notes = self.get_midi_notes(root, intervals, repeat_root=True)

                if scale_name == 'Harmonic Minor':
                    descending_notes = self.get_midi_notes(root, descending_intervals[scale_name], repeat_root=True)
                else:
                    descending_notes = ascending_notes[::-1]

                self.scales[scale_key] = {
                    'ascending': ascending_notes,
                    'descending': descending_notes
                }

        return self.scales

    def generate_chords(self):
        triad_intervals = {
            'Major': [0, 4, 7],
            'Minor': [0, 3, 7]
        }
        # seventh_intervals = {
        #     'major7': [0, 4, 7, 11],
        #     'minor7': [0, 3, 7, 10],
        #     'dominant7': [0, 4, 7, 10],
        #     'diminished7': [0, 3, 6, 9],
        #     'half_diminished7': [0, 3, 6, 10]
        # }

        seventh_intervals = {
            'Maj7': [0, 4, 7, 11],
            'Min7': [0, 3, 7, 10],
            '7': [0, 4, 7, 10],
            'Dim7': [0, 3, 6, 9],
            'm7f5': [0, 3, 6, 10]
        }

        for root in self.note_to_midi.keys():
            for triad_name, intervals in triad_intervals.items():
                chord_name = f"{root} {triad_name}"
                self.triads[chord_name] = {
                    'Root': self.get_midi_notes(root, intervals),
                    'First': self.get_midi_notes(root, intervals[1:] + [intervals[0] + 12]),
                    'Second': self.get_midi_notes(root, intervals[2:] + [intervals[0] + 12, intervals[1] + 12])
                }
            for seventh_name, intervals in seventh_intervals.items():
                chord_name = f"{root} {seventh_name}"
                self.sevenths[chord_name] = {
                    'Root': self.get_midi_notes(root, intervals),
                    'First': self.get_midi_notes(root, intervals[1:] + [intervals[0] + 12]),
                    'Second': self.get_midi_notes(root, intervals[2:] + [intervals[0] + 12, intervals[1] + 12]),
                    'Third': self.get_midi_notes(root, intervals[3:] + [intervals[0] + 12, intervals[1] + 12, intervals[2] + 12])
                }

        return self.triads

    def generate_modes(self):
        mode_names = ['Ionian', 'Dorian', 'Phrygian', 'Lydian', 'Mixolydian', 'Aeolian', 'Locrian']
        for scale_key, notes in self.scales.items():
            parts = scale_key.split()
            root = parts[0]
            scale_type = ' '.join(parts[1:])
            if scale_type == 'Major':
                for i, mode_name in enumerate(mode_names):
                    mode_key = f"{root} {scale_type} {mode_name}"
                    mode_notes = notes['ascending'][i:] + [note + 12 for note in notes['ascending'][:i]]
                    if mode_notes[-1] != mode_notes[0] + 12:
                        mode_notes.append(
                            mode_notes[0] + 12)  # Add the starting note at the end if it's not already there
                    self.modes[mode_key] = mode_notes

#


