from theory import Theory,MainWindow
from PyQt6.QtWidgets import QListWidgetItem
from PyQt6.QtGui import QPixmap, QFont
import random, copy
import pygame

class AppFunctions (Theory):

    def __init__(self):
        super().__init__()
        self.incorrect_note_count = 0
        self.previous_scale = None
        self.previous_mode = None
        self.previous_seventh = None

        pygame.mixer.init()


    def note_handler(self, mididata):
        if mididata.type == "note_on":

            self.notelabel.setText(str(mididata.note))

                # Check if the note matches the first value of self.goodnotes
            if mididata.note == self.goodnotes[0]:

                self.add_note_to_screen(mididata.note, "green")
                self.scalelabel2.setText(f"{self.goodnotes}")
                self.goodnotes.pop(0)  # Remove the first item

                # Check if self.goodnotes is empty
                if len(self.goodnotes) == 0:

                    self.go_button_clicked()


            else:
                self.add_note_to_screen(mididata.note, "red")
                self.incorrect_note_count += 1
                sound2 = pygame.mixer.Sound("/Users/williamcorney/Downloads/2.mp3")
                sound2.play()

                # Check if the incorrect note count exceeds 2
                if self.incorrect_note_count > 2:

                    self.reset_button_clicked()

        if mididata.type == "note_off":
            self.remove_note_from_screen(mididata.note)
            self.notelabel.setText("")

        # Update the scale label
        self.scalelabel2.setText(f"{self.goodnotes}")

    def go_button_clicked(self):
        self.goodnotes = []
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
            self.goodnotes = copy.deepcopy(ascending_notes + descending_notes)
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

            if not scaletypesselected or not inversionselected:
                self.scalelabel2.setText("You need to select at least one sub type")
                return

            while True:
                randomtype = random.randint(0, len(scaletypesselected) - 1)
                randomnote = random.randint(0, 11)
                randominversion = random.randint(0, len(inversionselected) - 1)

                randomnote_str = str(self.note_midi_list[randomnote])
                randomtype_str = str(scaletypesselected[randomtype])
                randominversion_str = str(inversionselected[randominversion])

                current_scale = f'{randomnote_str} {randomtype_str} {randominversion_str}'

                if current_scale != self.previous_scale:
                    self.previous_scale = current_scale
                    break

            self.goodnotes = copy.deepcopy(self.triads[randomnote_str + " " + randomtype_str][randominversion_str])

            self.scalelabel.setText(current_scale)
            self.scalelabel2.setText(f"{self.goodnotes}")
            self.deepnotes = copy.deepcopy(self.goodnotes)
        except Exception as e:
            self.scalelabel2.setText(f"An error occurred: {e}")

    def sevenths_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            inversionselected = [item.text() for item in self.subtheorysubtype.selectedItems()]

            if not scaletypesselected or not inversionselected:
                self.scalelabel2.setText("You need to select at least one item from all boxes above")
                return

            while True:
                randomtype = random.randint(0, len(scaletypesselected) - 1)
                randomnote = random.randint(1, 11)
                randominversion = random.randint(0, len(inversionselected) - 1)

                randomnote_str = str(self.note_midi_list[randomnote])
                randomtype_str = str(scaletypesselected[randomtype])
                randominversion_str = str(inversionselected[randominversion])

                current_seventh = f'{randomnote_str} {randomtype_str} {randominversion_str}'

                if current_seventh != self.previous_seventh:
                    self.previous_seventh = current_seventh
                    break

            self.goodnotes = copy.deepcopy(self.sevenths[randomnote_str + " " + randomtype_str][randominversion_str])
            self.scalelabel.setText(current_seventh)
            self.scalelabel2.setText(f"{self.goodnotes}")
            self.deepnotes = copy.deepcopy(self.goodnotes)
        except Exception as e:
            self.scalelabel2.setText(f"An error occurred: {e}")

    def modes_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]

            if not scaletypesselected:
                self.scalelabel2.setText("You need to select at least one sub type")
                return

            while True:
                randomtype = random.randint(0, len(scaletypesselected) - 1)
                randomnote = random.randint(1, 11)

                randomnote_str = str(self.note_midi_list[randomnote])
                randomtype_str = str(scaletypesselected[randomtype])

                current_mode = f'{randomnote_str} {randomtype_str}'

                if current_mode != self.previous_mode:
                    self.previous_mode = current_mode
                    break

            self.goodnotes = self.modes[randomnote_str + " Major " + randomtype_str]
            self.scalelabel.setText(current_mode)
            self.scalelabel2.setText(f"{self.goodnotes}")
        except Exception as e:
            self.scalelabel2.setText(f"An error occurred: {e}")

    def reset_button_clicked(self):
        if hasattr(self, 'deepnotes') and self.deepnotes:

            self.goodnotes = copy.deepcopy(self.deepnotes)
            self.scalelabel2.setText(f"{self.goodnotes}")
        else:
            print("deepnotes does not exist or is empty")