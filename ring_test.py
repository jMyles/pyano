import time

import mido

port = mido.open_output('Axiom Pro 25:Axiom Pro 25 MIDI 1 20:0')

try:
    while True:
        port.send(mido.Message(type="note_on", note=54, velocity=110))
        # port.send(mido.Message(type="note_on", note=59, velocity=90))
        port.send(mido.Message(type="note_on", note=66, velocity=110))
        port.send(mido.Message(type="note_on", note=88, velocity=110))
        port.send(mido.Message(type="note_on", note=90, velocity=110))
        port.send(mido.Message(type="note_on", note=91, velocity=110))
        time.sleep(.1)
        port.panic()
        port.reset()
        time.sleep(4)
finally:
    port.panic()
    port.reset()