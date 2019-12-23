import time

import mido

port = mido.open_output('Axiom Pro 25:Axiom Pro 25 MIDI 1 20:0')

try:
    while True:
        pedal_down = mido.Message(type="control_change", control=64, value=127)
        pedal_up = mido.Message(type="control_change", control=64, value=0)

        print("Testing pedal down.")
        port.send(pedal_down)
        port.send(mido.Message(type="note_on", note=40, velocity=80))
        time.sleep(.5)
        port.send(mido.Message(type="note_on", note=52, velocity=80))
        time.sleep(.2)
        port.send(mido.Message(type="note_off", note=40, velocity=127))
        port.send(mido.Message(type="note_off", note=52, velocity=127))

        time.sleep(5)

        print("Testing pedal up.")
        port.send(pedal_up)
        time.sleep(.25)

        port.send(mido.Message(type="note_on", note=40, velocity=80))
        time.sleep(.5)
        port.send(mido.Message(type="note_on", note=52, velocity=80))
        time.sleep(.2)
        port.send(mido.Message(type="note_off", note=40, velocity=127))
        port.send(mido.Message(type="note_off", note=52, velocity=127))

        time.sleep(3)
finally:
    port.panic()
    port.reset()