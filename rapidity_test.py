import time

import mido

port = mido.open_output('Axiom Pro 25:Axiom Pro 25 MIDI 1 20:0')

try:
    for i in range(100):
        port.send(mido.Message(type="note_on", note=69, velocity=30))
        time.sleep(.5)
        port.send(mido.Message(type="note_off", note=69, velocity=0))
        time.sleep(.025)
finally:
    port.panic()
    port.reset()