import sys
from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
from PyQt6.QtGui import QPixmap
from PyQt6.QtCore import Qt
import mido


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.labels = {}
        self.setWindowTitle("MIDI Image Switcher")
        self.setGeometry(100, 100, 800, 600)
        self.fullnotelist =[]
        self.notearray = ["C1", "C2", "C3"]
        self.note_value = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

        for octave in range(0, 4):
            for note in self.note_value:
                self.fullnotelist.append (note + str(octave))

        for note in self.fullnotelist: self.labels[note] = QLabel(self)


        # self.label = QLabel(self)
        # self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        # self.setCentralWidget(self.label)
        #
        # self.dog_pixmap = QPixmap("/Users/williamcorney/PycharmProjects/jp-trainer/C1.png")
        # self.cat_pixmap = QPixmap("/Users/williamcorney/PycharmProjects/jp-trainer/C2.png")
        # self.label.setPixmap(self.dog_pixmap)

    def midi_callback(self, message):
        if message.type == 'note_on':
            print('Match')
            pixmap = QPixmap("/C1.png")
            self.labels['C1'].setPixmap(pixmap)
        if message.type == 'note_off':
            self.dog_pixmap = QPixmap("/C1.png")

            self.label.setPixmap(self.dog_pixmap)


app = QApplication(sys.argv)
window = MainWindow()
window.show()

with mido.open_input(callback=window.midi_callback) as inport:
    sys.exit(app.exec())

# import sys
# from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow
# from PyQt6.QtGui import QPixmap
# from PyQt6.QtCore import Qt
# import mido
# from mido import MidiInput
#
# class MainWindow(QMainWindow):
#     def __init__(self):
#         super().__init__()
#         self.setWindowTitle("MIDI Image Switcher")
#         self.setGeometry(100, 100, 800, 600)
#
#         self.label = QLabel(self)
#         self.label.setAlignment(Qt.AlignmentFlag.AlignCenter)
#         self.setCentralWidget(self.label)
#
#         self.dog_pixmap = QPixmap("dog.jpg")
#         self.cat_pixmap = QPixmap("cat.jpg")
#         self.label.setPixmap(self.dog_pixmap)
#
#         self.init_midi()
#
#     def init_midi(self):
#         self.midi_input = MidiInput()
#         self.midi_input.callback = self.midi_callback
#         self.midi_input.open_port(0)
#
#     def midi_callback(self, message):
#         if message.type == 'note_on' and message.note == 60:
#             self.label.setPixmap(self.cat_pixmap)
#
# app = QApplication(sys.argv)
# window = MainWindow()
# window.show()
# sys.exit(app.exec())
