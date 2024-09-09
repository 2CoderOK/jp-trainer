from PyQt6.QtWidgets import QApplication, QLabel, QMainWindow, QPushButton, QListWidget, QListWidgetItem,QAbstractItemView
from PyQt6.QtGui import QPixmap, QFont
import mido
from theory import  ScaleGenerator

class MainWindow(QMainWindow ):


    def __init__(self):
        super().__init__()
        self.setWindowTitle("Jazz Piano Trainer")
        self.setGeometry(500, 300, 1060, 400)
        self.labels = {}

        self.setup_button()
        self.setup_labels()
        self.setup_list_widgets()

        self.BASE_PATH = "/Users/williamcorney/PycharmProjects/jp-trainer/images/key_"

        self.NOTE_VALUES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
        self.NOTE_FILENAMES = ["_left.png", "_top.png", "_mid.png", "_top.png", "_right.png", "_left.png", "_top.png",
                               "_mid.png", "_top.png", "_mid.png", "_top.png", "_right.png", "_left.png"]
        self.NOTE_COORDINATES = [1, 26, 35, 60, 69, 103, 129, 138, 162, 172, 196, 206, 240]
    def setup_button(self):
        font = QFont()
        font.setPointSize(24)
        self.gobutton = QPushButton("GO!", self)
        self.gobutton.setFont(font)
        self.gobutton.setGeometry(950, 10, 100, 100)
        self.gobutton.clicked.connect(self.go_button_clicked)
        self.gobutton.setStyleSheet("background-color: green;color: white;")

    def setup_labels(self):
        self.scalelabel = QLabel("", self)
        self.scalelabel.setGeometry(0, 300, 850, 50)
        self.scalelabel.setFont(QFont("Arial", 36))
        self.notelabel = QLabel("", self)
        self.notelabel.setGeometry(1000, 300, 300, 50)
        self.notelabel.setFont(QFont("Arial", 36))

        self.labels['keys'] = QLabel(self)
        self.labels['keys'].setPixmap(QPixmap("/Users/williamcorney/PycharmProjects/jp-trainer/images/keys.png"))
        self.labels['keys'].setGeometry(0, 150, 1060, 155)
        for note in range(48, 101): self.labels[note] = QLabel(self)

    def setup_list_widgets(self):
        self.theory_type = QListWidget(self)
        self.theory_subtype = QListWidget(self)
        self.subtheorysubtype = QListWidget(self)
        self.list_widget4 = QListWidget(self)

        for item in ["Scales", "Triads","Sevenths","Modes"]: self.theory_type.addItem(QListWidgetItem(item))
        #self.theorytype.setCurrentRow(0)
        self.theory_type.clicked.connect(self.theory_type_clicked)
        self.theory_subtype.clicked.connect (self.theory_subtype_clicked)
        self.theory_type.setGeometry(0, 0, 150, 125)
        self.theory_subtype.setGeometry(150, 0, 150, 125)
        self.subtheorysubtype.setGeometry(300, 0, 150, 125)
        self.list_widget4.setGeometry(450, 0, 150, 125)

        self.subtheorysubtype.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

        self.theory_subtype.setSelectionMode(QAbstractItemView.SelectionMode.MultiSelection)

    def addnote(self, note, color):

        self.xcord = self.NOTE_COORDINATES[note % 12] + ((note // 12) - 4) * 239
        self.labels[note].setPixmap(QPixmap(self.BASE_PATH + color + self.NOTE_FILENAMES[note % 12]))
        self.labels[note].setGeometry(self.xcord, 128, 100, 200)
        self.labels[note].show()

    def removenote(self, note):
        self.labels[note].hide()
    # manipulating guis in these theory /theory subtype functions .  logic is in the
    def theory_type_clicked (self):
        self.subtheorysubtype.clear()
        match self.theory_type.currentItem().text():

            case "Scales":
                self.theory_subtype.clear()
                for item in ["major", "natural_minor", "melodic_minor", "harmonic_minor"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))
            case "Triads":
                self.theory_subtype.clear()
                for item in ["major", "minor"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))
            case "Sevenths":
                self.theory_subtype.clear()
                for item in ["major7", "minor7","dominant7","diminished7","half_diminished7"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))
            case "Modes":
                self.theory_subtype.clear()
                for item in ["Ionian", "Dorian","Phrygian","Lydian","Mixolydian","Aeolian","Locrian"]: self.theory_subtype.addItem(
                    QListWidgetItem(item))

    def theory_subtype_clicked(self):

        match self.theory_type.currentItem().text():


            case "Triads":

                self.subtheorysubtype.clear()
                for item in ["root", "1st_inversion","2nd_inversion"]: self.subtheorysubtype.addItem(
                    QListWidgetItem(item))
            case "Sevenths":
                self.subtheorysubtype.clear()
                for item in ["root", "1st_inversion", "2nd_inversion","3rd_inversion"]: self.subtheorysubtype.addItem(
                    QListWidgetItem(item))


        pass

