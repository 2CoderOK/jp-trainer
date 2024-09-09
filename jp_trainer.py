import mido
from note_display import MainWindow
from PyQt6.QtWidgets import QApplication
from theory import ScaleGenerator
import random


class MainApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.goodnotes = []

    def go_button_clicked (self):

        match self.theory_type.currentItem().text():
            case 'Scales':
                self.scales_clicked()
            case 'Triads':
                self.triads_clicked()
            case 'Sevenths':
                self.sevenths_clicked()
            case 'Modes':
                self.modes_clicked()

    def scales_clicked(self):
        try:


            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]


            randomtype = (random.randint(0 ,len (scaletypesselected)))
            randomnote = (random.randint(1,11))


            randomnote  = str(ScaleGenerator.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            self.goodnotes = ScaleGenerator.generate_scales()[randomnote + " " + randomtype]
            self.scalelabel.setText (f"{randomnote} {randomtype} - {self.goodnotes}")

        except:
            pass

    def triads_clicked(self):

        try:
            #print(ScaleGenerator.triads['G major']['root'])

            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            inversionselected = [item.text() for item in self.subtheorysubtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randominversion = (random.randint(1, len(inversionselected)))

            randomnote = str(ScaleGenerator.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            randominversion = str(inversionselected[randominversion - 1])
            self.goodnotes = (ScaleGenerator.triads[randomnote + " " + randomtype][randominversion])
            self.scalelabel.setText(f'{randomnote} {randomtype} {randominversion} - {self.goodnotes}')

        except:
            pass

    def sevenths_clicked(self):

        try:
            #print(ScaleGenerator.triads['G major']['root'])

            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            inversionselected = [item.text() for item in self.subtheorysubtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randominversion = (random.randint(1, len(inversionselected)))

            randomnote = str(ScaleGenerator.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            randominversion = str(inversionselected[randominversion - 1])

            self.goodnotes = (ScaleGenerator.sevenths[randomnote + " " + randomtype][randominversion])
            self.scalelabel.setText(f'{randomnote} {randomtype} {randominversion} - {self.goodnotes}')

        except:
            pass

    def modes_clicked(self):

        try:


            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]

            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))


            randomnote = str(ScaleGenerator.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            self.goodnotes = ScaleGenerator.modes[randomnote + " major " + randomtype]
            self.scalelabel.setText(f'{randomnote} {randomtype} - {self.goodnotes} ')


        except:
            pass
    def midi_callback(self, message):

        if message.type == "note_on":
                self.notelabel.setText(str(message.note))

                if (message.note in self.goodnotes):
                    self.addnote(message.note, "green")
                else:
                    self.addnote(message.note, "red")

        if message.type == "note_off":
                self.removenote(message.note)


app = QApplication([])
window = MainApp()
window.show()
with mido.open_input( callback=window.midi_callback) as inport: app.exec()

