import sys

from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QListWidget, QListWidgetItem,QAbstractItemView
from PyQt6.QtGui import QPixmap, QFont



class MainWindow(QMainWindow):


    def __init__(self):
        super().__init__()


        pass

    def setup_gui(self):
        self.setWindowTitle("Jazz Piano Trainer")
        self.setGeometry(500, 300, 1060, 400)

    def setup_gui_variables(self):

        self.BASE_PATH = "/Users/williamcorney/PycharmProjects/jp-trainer/images/key_"

        self.NOTE_VALUES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.NOTE_FILENAMES = ["_left.png", "_top.png", "_mid.png", "_top.png", "_right.png", "_left.png", "_top.png",
                               "_mid.png", "_top.png", "_mid.png", "_top.png", "_right.png", "_left.png"]
        self.NOTE_COORDINATES = [1, 26, 35, 60, 69, 103, 129, 138, 162, 172, 196, 206, 240]

    def setup_buttons(self):
        font = QFont()
        font.setPointSize(24)
        self.gobutton = QPushButton("GO!", self)
        self.gobutton.setFont(font)
        self.gobutton.setGeometry(950, 10, 50, 50)
        self.gobutton.clicked.connect(self.go_button_clicked)
        self.gobutton.setStyleSheet("background-color: green;color: white;")

    def setup_labels(self):
        self.labels = {}

        self.scalelabel = QLabel("", self)
        self.scalelabel.setGeometry(0, 300, 850, 50)
        self.scalelabel.setFont(QFont("Arial", 36))
        self.scalelabel2 = QLabel("", self)
        self.scalelabel2.setGeometry(0, 350, 850, 50)
        self.scalelabel2.setFont(QFont("Arial", 18))

        self.notelabel = QLabel("", self)
        self.notelabel.setGeometry(900, 300, 300, 50)
        self.notelabel.setFont(QFont("Arial", 24))

        self.labels['keys'] = QLabel(self)
        self.labels['keys'].setPixmap(QPixmap("/Users/williamcorney/PycharmProjects/jp-trainer/images/keys.png"))
        self.labels['keys'].setGeometry(0, 150, 1060, 155)


        for note in range(48, 101): self.labels[note] = QLabel(self)


        pass

    def setup_listwidgets(self):
        self.theory_type = QListWidget(self)
        self.theory_subtype = QListWidget(self)
        self.subtheorysubtype = QListWidget(self)
        self.list_widget4 = QListWidget(self)

        for item in ["Scales", "Triads", "Sevenths", "Modes"]: self.theory_type.addItem(QListWidgetItem(item))
        # self.theorytype.setCurrentRow(0)
        self.theory_type.clicked.connect(self.theory_type_clicked)
        self.theory_subtype.clicked.connect(self.theory_subtype_clicked)
        self.theory_type.setGeometry(0, 00, 150, 125)
        self.theory_subtype.setGeometry(150, 0, 150, 125)
        self.subtheorysubtype.setGeometry(300, 0, 150, 125)
        self.list_widget4.setGeometry(450, 0, 150, 125)

        self.subtheorysubtype.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.theory_subtype.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

    def add_note_to_screen(self,note,color):
        self.xcord = self.NOTE_COORDINATES[note % 12] + ((note // 12) - 4) * 239
        self.labels[note].setPixmap(QPixmap(self.BASE_PATH + color + self.NOTE_FILENAMES[note % 12]))
        self.labels[note].setGeometry(self.xcord, 128, 100, 200)
        self.labels[note].show()

    def remove_note_from_screen(self,note):
        self.labels[note].hide()

