from tkinter import *

from PIL import Image, ImageTk

WINDOW_HEIGHT = 800
WINDOW_WIDTH = 1913

IMAGE_NAMES = [
    "key_green_left",
    "key_green_mid",
    "key_green_right",
    "key_green_top",
    "key_red_left",
    "key_red_mid",
    "key_red_right",
    "key_red_top",
]
NOTES_TO_IMAGE_MAP = {
    0: "left",
    1: "top",
    2: "mid",
    3: "top",
    4: "right",
    5: "left",
    6: "top",
    7: "mid",
    8: "top",
    9: "mid",
    10: "top",
    11: "right",
    12: "left",
}
NOTES_Y = 401
NOTES_X = {
    36: 3,
    37: 52,
    38: 71,
    39: 120,
    40: 139,
    41: 207,
    42: 256,
    43: 275,
    44: 324,
    45: 343,
    46: 393,
    47: 412,
    48: 480,
    49: 529,
    50: 548,
    51: 597,
    52: 616,
    53: 685,
    54: 733,
    55: 753,
    56: 802,
    57: 821,
    58: 870,
    59: 889,
    60: 958,
    61: 1007,
    62: 1026,
    63: 1075,
    64: 1094,
    65: 1163,
    66: 1211,
    67: 1231,
    68: 1280,
    69: 1299,
    70: 1348,
    71: 1367,
    72: 1436,
    73: 1485,
    74: 1504,
    75: 1553,
    76: 1572,
    77: 1640,
    78: 1689,
    79: 1709,
    80: 1757,
    81: 1776,
    82: 1825,
    83: 1845,
}


class NoteDisplay:
    """
    A main class for UI display
    """

    def __init__(self, button_callback, button_replay_callback) -> None:
        self.window = Tk()
        self.window.title("Jazz Piano Trainer")
        self.window.geometry(f"{WINDOW_WIDTH}x{WINDOW_HEIGHT}")

        self.frame = Frame(self.window)
        self.frame.pack(side=RIGHT)

        self.canvas = Canvas(
            self.frame, bg="white", width=WINDOW_WIDTH, height=WINDOW_HEIGHT
        )
        self.canvas.pack()

        self.keys_img = ImageTk.PhotoImage(Image.open("images/keys.png"))
        self.canvas.create_image(0, 400, image=self.keys_img, anchor="w")

        self.images = {}
        for i in IMAGE_NAMES:
            image = ImageTk.PhotoImage(Image.open(f"images/{i}.png"))
            self.images[i] = image

        self.notes_widgets = {}
        self.button = Button(
            self.canvas, text="NEXT", command=button_callback, height=2, width=20
        )
        self.button_replay = Button(
            self.canvas, text="REPLAY", command=button_replay_callback, height=2, width=20
        )

        self.q_label = Label(self.canvas, text="Press NEXT to Start", font=("Arial", 25))
        self.q2_label = Label(self.canvas, text="", font=("Arial", 25))

        self.a_img = ImageTk.PhotoImage(Image.open("images/placeholder.png"))
        self.a_label = Label(self.canvas, text="")

        self.option_var = StringVar(self.canvas)
        self.option_var.set("MODES")
        self.selected_option = "MODES"
        self.option_widget = OptionMenu(
            self.canvas, self.option_var, "MODES", "CHORDS", command=self.option_update
        )

        self.canvas.create_window(300, 58, window=self.option_widget)
        self.canvas.create_window(300, 100, window=self.button)
        self.canvas.create_window(300, 150, window=self.button_replay)
        self.canvas.create_window(700, 100, window=self.q_label)
        self.canvas.create_window(700, 200, window=self.q2_label)
        self.canvas.create_window(1000, 100, window=self.a_label)

    def option_update(self, selected_option) -> None:
        """
        Update a selected option
        """
        self.selected_option = selected_option

    def get_note_image(self, note_id: int) -> str:
        """
        Get a note`s image
        """
        real_note = None
        for n in [72, 60, 48, 36]:
            if note_id >= n:
                real_note = note_id - n
                break
        return NOTES_TO_IMAGE_MAP[real_note] if real_note is not None else None

    def add_note(self, note_id: int, is_green: bool = True) -> None:
        """
        Add a note widget to the UI
        """
        note_name = self.get_note_image(note_id)
        note_image_name = f"key_green_{note_name}" if is_green else f"key_red_{note_name}"
        new_img = self.canvas.create_image(
            NOTES_X[note_id], NOTES_Y, image=self.images[note_image_name], anchor="w"
        )
        self.notes_widgets[note_id] = new_img

    def remove_note(self, note_id: int) -> None:
        """
        Remove a note widget from the UI
        """
        if note_id in self.notes_widgets:
            self.canvas.delete(self.notes_widgets[note_id])
            del self.notes_widgets[note_id]

    def update_question(self, txt: str) -> None:
        """
        Update a question text (UI)
        """
        self.q_label.config(text=txt)
        self.q_label.text = txt

    def update_answer(self, image_path: str, txt: str) -> None:
        """
        Update an answer image (UI)
        """
        new_img = ImageTk.PhotoImage(Image.open(image_path))
        self.a_label.config(image=new_img)
        self.a_label.image = new_img
        self.q2_label.config(text=txt)
        self.q2_label.text = txt
