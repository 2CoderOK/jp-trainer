import mido
from note_display import MainWindow
from PyQt6.QtWidgets import QApplication
from PyQt6.QtGui import QPixmap, QFont
from theory import ScaleGenerator
import random
import copy
class MainApp(MainWindow):
    def __init__(self):
        super().__init__()
        self.goodnotes = []
    def go_button_clicked (self):

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

    def reset_button_clicked(self):

        try:
            self.goodnotes = ScaleGenerator.generate_scales()[self.scalelabel.text()]
            self.scalelabel2.setText(f"{self.goodnotes}")
        except:
            pass
        pass
    def scales_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            randomtype = (random.randint(0 ,len (scaletypesselected)))
            randomnote = (random.randint(0,11))

            randomnote  = str(ScaleGenerator.note_midi_list[randomnote])

            randomtype = str(scaletypesselected[randomtype - 1])
            self.goodnotes = ScaleGenerator.generate_scales()[randomnote + " " + randomtype ]['ascending'] +ScaleGenerator.generate_scales()[randomnote + " " + randomtype ]['descending']
            self.scalelabel2.setText(f"{self.goodnotes}")
            self.scalelabel.setText (f"{randomnote} {randomtype}")
            self.fingeringlabel.setText(str(ScaleGenerator.fingering_patterns[randomnote]['right']))
            self.scalelabel2.setText(f"{self.goodnotes}")
            # filename = (f"{randomnote} {randomtype}.png")
            # self.illustrationpixmap = QPixmap("/Users/williamcorney/PycharmProjects/jp-trainer/images/" + filename)
            # self.illustration.setPixmap(self.illustrationpixmap)


        except:
            pass
            #   self.scalelabel2.setText(f"You need to select at least one sub type")
    def triads_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            inversionselected = [item.text() for item in self.subtheorysubtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randominversion = (random.randint(1, len(inversionselected)))
            randomnote = str(ScaleGenerator.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            randominversion = str(inversionselected[randominversion - 1])
            self.goodnotes = (ScaleGenerator.triads[randomnote + " " + randomtype][randominversion])
            self.scalelabel.setText(f'{randomnote} {randomtype} {randominversion}')
            self.scalelabel2.setText(f"{self.goodnotes}")
        except:
            self.scalelabel2.setText(f"You need to select at least one sub type")
    def sevenths_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            inversionselected = [item.text() for item in self.subtheorysubtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randominversion = (random.randint(1, len(inversionselected)))
            randomnote = str(ScaleGenerator.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            randominversion = str(inversionselected[randominversion - 1])
            self.goodnotes = (ScaleGenerator.sevenths[randomnote + " " + randomtype][randominversion])
            self.scalelabel.setText(f'{randomnote} {randomtype} {randominversion}')
            self.scalelabel2.setText(f"{self.goodnotes}")
        except:
            self.scalelabel2.setText(f"You need to select at least one item from all boxes above")
    def modes_clicked(self):
        try:
            scaletypesselected = [item.text() for item in self.theory_subtype.selectedItems()]
            randomtype = (random.randint(0, len(scaletypesselected)))
            randomnote = (random.randint(1, 11))
            randomnote = str(ScaleGenerator.note_midi_list[randomnote])
            randomtype = str(scaletypesselected[randomtype - 1])
            self.goodnotes = ScaleGenerator.modes[randomnote + " major " + randomtype]
            self.scalelabel.setText(f'{randomnote} {randomtype}')
            self.scalelabel2.setText(f"{self.goodnotes}")
        except:
            pass
    def midi_callback(self, message):
        if message.type == "note_on":

                self.notelabel.setText(str(message.note))
                if (message.note in self.goodnotes):

                    self.addnote(message.note, "green")
                    self.goodnotes.remove(message.note)
                    self.scalelabel2.setText(f"{self.goodnotes}")
                else:
                    self.addnote(message.note, "red")

                if len(self.goodnotes) == 0:
                    self.go_button_clicked()
        if message.type == "note_off":
                self.removenote(message.note)


try:
    app = QApplication([])
    window = MainApp()
    window.show()
    with mido.open_input( callback=window.midi_callback) as inport: app.exec()

except:
    print ('Error : No Midi Keyboard Detected')
