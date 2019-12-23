
def sort_into_octaves(starting_note, ending_note):
    note_order = []
    for key in range(starting_note, ending_note):
        if key == starting_note + 12 or key==ending_note:
            break
        candidate_note = key
        while True:
            if candidate_note > ending_note:
                break
            else:
                note_order.append(candidate_note)
                candidate_note += 12
    return note_order


def sort_into_major_scale(starting_note, ending_note):
    note_order = []
    for key in range(starting_note, ending_note):
        if key==ending_note:
            break
        root = key
        while True:
            if root > ending_note - 12:
                break
            for interval in (0, 2, 2, 1, 2, 2, 2, 1, 0):
                candidate_note = root + interval
                if candidate_note > ending_note:
                    break
                else:
                    note_order.append(candidate_note)
                    root = candidate_note
    return note_order


def test_all_notes(delay=1,
                   starting_note=50,
                   ending_note=108,
                   calibrate=True,
                   by_octave=False,
                   by_major_scale=True):
    new_velocities = {}
    if by_octave:
        notes_to_test = sort_into_octaves(starting_note, ending_note)
    elif by_major_scale:
        notes_to_test = sort_into_major_scale(starting_note, ending_note)
    else:
        notes_to_test = range(starting_note, ending_note)

    for note in notes_to_test:
        velocity = activation_velocities[note]
        simple_note(note_number=note, velocity=velocity, delay=delay)
        if calibrate:
            adjustment = input("Good?")
            if adjustment == "g":
                new_velocities[note] = velocity
            if adjustment == "l":
                new_velocities[note] = velocity - 1
            if adjustment == "m":
                new_velocities[note] = velocity + 1
            if adjustment == "mm":
                new_velocities[note] = velocity + 3

    pprint.pprint(new_velocities)