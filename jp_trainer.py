import sys


import mido


from note_display import NoteDisplay

from theory import SCALES, Theory

notes_on: list = []
good_notes: list = []
required_notes: list = []
theory_item: dict

note_ui: NoteDisplay
replay_file: str
img_path: str
answer_text: str

th = Theory()



def generate_path(t_item: dict) -> str:
    """
    Generate a path to a given resource (audio/img)
    """
    print(t_item)
    tp = "03" if t_item["type"] == "Mode" else "04"
    file_path = (
        f"{tp}/{t_item['scale_id']+1:02d}/{tp}{t_item['scale_id']:02d}{t_item['id']:02d}"
    )
    print(file_path)
    return file_path

def button_handler() -> None:
    """
    UI button handler
    """
    global replay_file, img_path, good_notes, theory_item, timer, answer_text, required_notes

    if note_ui.selected_option == "CHORDS":
        theory_item = th.get_chord()
    else:
        theory_item = th.get_mode()

    good_notes = [n + i for i in [36, 48, 60, 72] for n in theory_item["notes"]]
    required_notes = [[n + 36, n + 48, n + 60, n + 72] for n in theory_item["notes"]]

    file_path = generate_path(theory_item)
    img_path = "images/" + file_path + "01.png"

    q = f"{SCALES[theory_item['scale_id']]}"
    if theory_item["type"] == "Chord":
        q += theory_item["name"]
        answer_text = q
    else:
        answer_text = q + " " + theory_item["desc"]
        img_path = img_path.replace(
            "0.png", "1.png"
        )  # hardcoded a single inversion for now

    inv_id = 0  # TODO: replace with inversion
    file_path += f"{inv_id:02d}"
    audio_path = "audio/" + file_path + ".mp3"
    replay_file = audio_path
    mixer.music.load(audio_path)
    mixer.music.play()
    note_ui.update_question(q)
    note_ui.update_answer("images/placeholder.png", "")

note_ui = NoteDisplay(button_handler)


def note_handler(note: mido.Message) -> None:
    """
    Midi message event handler
    """
    if note.type in ["note_on", "note_off"]:
        note_id = int(note.note) if note.note is not None else -1
        if note.type == "note_on":

            is_green = False
            if note_id in good_notes:
                ids_to_remove = []
                for i in required_notes:
                    if note_id in i:
                        ids_to_remove.append(required_notes.index(i))
                for i in ids_to_remove:
                    if i in required_notes:
                        del required_notes[i]
                if len(required_notes) == 0:
                    if timer:
                        timer.cancel()
                        note_ui.update_answer(img_path, answer_text)
                is_green = True
            note_ui.add_note(note_id, is_green)
            if note.note not in notes_on:
                notes_on.append(note.note)
        elif note.type == "note_off":

            note_ui.remove_note(note_id)
            if note_id in notes_on:
                notes_on.remove(note_id)


try:
    ignore_velocity = True if "--ignore_velocity" in sys.argv else False
    sustain = True if "--sustain" in sys.argv else False

    # First midi device selected from array returned from the command mido.get_input_names()
    # In the unlikely event you have multiple midi devices you could wrap the command
    # in a print statement and amend the command below accordingly.

    port_name = (mido.get_input_names()[0])





    with mido.open_input(port_name, callback=note_handler) as port:
        print("Using {}".format(port))
        note_ui.window.mainloop()
except Exception as e:
    print(e)
