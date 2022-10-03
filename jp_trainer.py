import threading

import mido
from pygame import mixer

from note_display import NoteDisplay
from theory import SCALES, Theory

notes_on = []
good_notes = []
theory_item = None

note_ui = None
replay_file = None
answer_img_path = None
answer_text = None
timer = None

mixer.init()
th = Theory()


def timer_func():
    note_ui.update_answer(img_path)


def generate_path(theory_item):
    tp = "03" if theory_item["type"] == "Mode" else "04"
    file_path = f"{tp}/{theory_item['scale_id']+1:02d}/{tp}{theory_item['scale_id']:02d}{theory_item['id']:02d}"
    return file_path


def replay_handler():
    if replay_file:
        mixer.music.stop()
        mixer.music.play()


def button_handler():
    global replay_file, img_path, good_notes, theory_item, timer, answer_text

    if note_ui.selected_option == "CHORDS":
        theory_item = th.get_chord()
    else:
        theory_item = th.get_mode()

    good_notes = [n + 36 for n in theory_item["notes"]] + [n + 48 for n in theory_item["notes"]]

    file_path = generate_path(theory_item)
    img_path = "images/" + file_path + "01.png"

    q = f"{SCALES[theory_item['scale_id']]}"
    if theory_item["type"] == "Chord":
        q += theory_item["name"]
    else:
        answer_text = theory_item["desc"]
        img_path = img_path.replace("0.png", "1.png")  # hardcoded a single inversion for now

    inv_id = 0  # TODO: replace with inversion
    file_path += f"{inv_id:02d}"
    audio_path = "audio/" + file_path + ".mp3"
    replay_file = audio_path
    mixer.music.load(audio_path)
    mixer.music.play()
    note_ui.update_question(q)
    note_ui.update_answer("images/placeholder.png")

    if timer:
        timer.cancel()
    timer = threading.Timer(10, timer_func)
    timer.start()


note_ui = NoteDisplay(button_handler, replay_handler)


def note_handler(note):
    note_id = int(note.note) if note.note is not None else -1
    if note.type == "note_on":
        is_green = False
        if note_id in good_notes:
            is_green = True
        note_ui.add_note(note_id, is_green)
        if note.note not in notes_on:
            notes_on.append(note.note)
    elif note.type == "note_off":
        note_ui.remove_note(note_id)
        notes_on.remove(note_id)


try:
    portname = "Impulse 2" # replace with your MIDI INPUT
    with mido.open_input(portname, callback=note_handler) as port:
        print("Using {}".format(port))
        note_ui.window.mainloop()
except Exception as e:
    print(e)
