from theory import Theory,MainWindow
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QPixmap, QFont
import random, copy
class AppFunctions (Theory):

    def __init__(self):
        super().__init__()
        self.incorrect_note_count = 0


    def note_handler(self, mididata):
        if mididata.type == "note_on":
            self.notelabel.setText(str(mididata.note))
            if mididata.note in self.goodnotes:
                self.add_note_to_screen(mididata.note, "green")
                self.scalelabel2.setText(f"{self.goodnotes}")

                # Check if the note matches the first value of self.goodnotes
                if self.goodnotes and mididata.note == self.goodnotes[0]:
                    self.goodnotes.pop(0)  # Remove the first item

                    # Check if self.goodnotes is empty
                    if len(self.goodnotes) == 0:
                        self.go_button_clicked()

            else:
                self.add_note_to_screen(mididata.note, "red")
                self.incorrect_note_count += 1

                # Check if the incorrect note count exceeds 2
                if self.incorrect_note_count > 2:
                    self.reset_button_clicked()

        if mididata.type == "note_off":
            self.remove_note_from_screen(mididata.note)
            self.notelabel.setText("")

        # Update the scale label
        self.scalelabel2.setText(f"{self.goodnotes}")

    def go_button_clicked(self):

        try:

            match self.theory_type.currentItem().text():
                case 'Scales':
                    self.scales_clicked()
                case 'Triads':
                    self.triads_clicked()
                case 'Sevenths':
                    self.sevenths_clicked()
                case 'Modes':
                    self.modes_clicked()
        except:
            self.scalelabel2.setText(f"You need to select a theory type")

    def theory_type_clicked(self):
        self.subtheorysubtype.clear()
        match self.theory_type.currentItem().text():

            case "Scales":
                self.theory_subtype.clear()
                for item in ["Major", "Natural Minor", "Melodic Minor", "Harmonic Minor"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))
            case "Triads":
                self.theory_subtype.clear()
                for item in ["Major", "Minor"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))
            case "Sevenths":
                self.theory_subtype.clear()
                for item in ["Maj7", "Min7", "7", "Dim7",
                             "m7f5"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))

            case "Modes":
                self.theory_subtype.clear()
                for item in ["Ionian", "Dorian", "Phrygian", "Lydian", "Mixolydian", "Aeolian",
                             "Locrian"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))

    def theory_subtype_clicked(self):

        match self.theory_type.currentItem().text():
            case "Triads":
                self.subtheorysubtype.clear()
                for item in ["Root", "First", "Second"]: self.subtheorysubtype.addItem(
                    QListWidgetItem(item))
            case "Sevenths":
                self.subtheorysubtype.clear()
                for item in ["Root", "First", "Second", "Third"]: self.subtheorysubtype.addItem(
                    QListWidgetItem(item))

        pass

    def scales_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            if not scaletypesselected:
                self.scalelabel2.setText("You need to select at least one sub type")
                return

            if not hasattr(self, 'previous_scale'):
                self.previous_scale = None

            while True:
                randomtype = random.choice(scaletypesselected)
                randomnote = random.choice(self.note_midi_list)
                current_scale = f"{randomnote} {randomtype}"
                # Check if the new scale is different from the previous one
                if current_scale != self.previous_scale:
                    break
            scales = self.generate_scales()
            ascending_notes = scales[current_scale]['ascending']
            descending_notes = scales[current_scale]['descending']

            # Combine ascending and descending notes
            self.goodnotes = ascending_notes + descending_notes
            self.scalelabel.setText(current_scale)
            self.scalelabel2.setText(f"{self.goodnotes}")
            # Update the previous scale
            self.previous_scale = current_scale
            self.deepnotes = copy.deepcopy(self.goodnotes)
        except Exception as e:
            self.scalelabel2.setText(f"An error occurred: {str(e)}")

    def triads_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            inversionselected = [item.text() for item in self.subtheorysubtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randominversion = (random.randint(1, len(inversionselected)))
            randomnote = str(self.note_midi_list[randomnote])

            randomtype = str(scaletypesselected[randomtype - 1])
            randominversion = str(inversionselected[randominversion - 1])
            print(self.triads)
            self.goodnotes = (self.triads[randomnote + " " + randomtype][randominversion])

            self.scalelabel.setText(f'{randomnote} {randomtype} {randominversion}')
            self.scalelabel2.setText(f"{self.goodnotes}")
            self.deepnotes = copy.deepcopy(self.goodnotes)
        except:
            self.scalelabel2.setText(f"You need to select at least one sub type")
    def sevenths_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            inversionselected = [item.text() for item in self.subtheorysubtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randominversion = (random.randint(1, len(inversionselected)))
            randomnote = str(self.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            randominversion = str(inversionselected[randominversion - 1])
            self.goodnotes = (self.sevenths[randomnote + " " + randomtype][randominversion])
            self.scalelabel.setText(f'{randomnote} {randomtype} {randominversion}')
            self.scalelabel2.setText(f"{self.goodnotes}")
            self.deepnotes = copy.deepcopy(self.goodnotes)
        except:
            self.scalelabel2.setText(f"You need to select at least one item from all boxes above")

    def modes_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randomnote = str(self.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            self.goodnotes = self.modes[randomnote + " Major " + randomtype]
            self.scalelabel.setText(f'{randomnote} {randomtype}')
            self.scalelabel2.setText(f"{self.goodnotes}")
        except:
            pass

    def reset_button_clicked(self):
        if hasattr(self, 'deepnotes') and self.deepnotes:
            self.goodnotes = copy.deepcopy(self.deepnotes)
            self.scalelabel2.setText(f"{self.goodnotes}")
        else:
            print("deepnotes does not exist or is empty")