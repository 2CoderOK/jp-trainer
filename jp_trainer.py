import mido
from theory import Theory, MainWindow
from PyQt6.QtWidgets import QApplication
from functions import AppFunctions

"""

The object of splitting program into its component parts is
to make it easier to follow the program flow

"""

class MainApp(AppFunctions):
    def __init__(self):
        super().__init__()

        self.setup_gui()
        self.setup_buttons()
        self.setup_labels()
        self.setup_listwidgets()
        self.setup_gui_variables()

    def midi_callback(self, message):
        self.note_handler(message)


app = QApplication([])
window = MainApp()
window.show()

with mido.open_input( callback=window.midi_callback) as inport: app.exec()


