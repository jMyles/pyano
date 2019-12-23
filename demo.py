import cgi
import os
import signal
import time
import player

import mido
from twisted.internet import reactor

from twisted.web import server, resource

def all_songs_from_dir(dir):
    songs = os.listdir(dir)
    songs_with_dir = [mido.MidiFile(f"{dir}/{song}") for song in songs]
    return songs_with_dir

songs = [
# mido.MidiFile("/home/jmyles/Music/midi/flashman.mid"),
# mido.MidiFile("/home/jmyles/Music/midi/metroid_overworld_piano.mid"),
# mido.MidiFile("/home/jmyles/Music/midi/Ridley-p.mid"),
# mido.MidiFile("/home/jmyles/Music/midi/Dire_Dire_Docks_SM64.mid"),
#     mido.MidiFile("/home/jmyles/Music/midi/metroid_overworld_piano.mid"),

#     # mido.MidiFile("/home/jmyles/Music/midi/Rocket_Man_-_Elton_John__Piano_Tutorial.mid"),
#     # mido.MidiFile("/home/jmyles/Music/midi/from-youtube-dropbox-to-sort/Mario - Overworld Theme.mid"),
#     mido.MidiFile("/home/jmyles/Music/midi/FF4PC/FF4PC_03_Prologue.MID"),
#     mido.MidiFile("/home/jmyles/Music/midi/from-youtube-dropbox-to-sort/FF7 Cosmo Canyon.mid"),
#     mido.MidiFile("/home/jmyles/Music/midi/from-youtube-dropbox-to-sort/Corridors of Time (Zohar).mid"),
#     mido.MidiFile("/home/jmyles/Music/midi/from-youtube-dropbox-to-sort/Chrono Trigger - Secret of the Forest (Zohar).mid"),
#
#     #

#
#     # mido.MidiFile("/home/jmyles/Music/midi/FF4PC/FF4PC_12_The_Battle.MID"),
#
    # mido.MidiFile("/home/jmyles/Music/midi/totoro/Tonari no Totoro - Tonari no totoro.mid"),
    # mido.MidiFile("/home/jmyles/Music/midi/totoro/Tonari no Totoro - Kaze no Toori Michi.mid"),
    # mido.MidiFile("/home/jmyles/Music/midi/totoro/Tonari no Totoro - Sanpo.mid"),
    #
    #     mido.MidiFile("/home/jmyles/Music/midi/kiki/kikis-delivery-service-the-changing-seasons.mid"),
    # mido.MidiFile("/home/jmyles/Music/midi/kiki/kikis-delivery-service-touched-by-your-tenderness.mid"),
# mido.MidiFile("/home/jmyles/Music/midi/Chrono Trigger - Wind scene.mid"),
    # mido.MidiFile("/home/jmyles/Music/midi/radicaldreamers-piano.mid"),
#     # mido.MidiFile("/home/jmyles/Music/midi/wings.mid"),

#     # mido.MidiFile("/home/jmyles/Music/midi/Chrono Trigger - End of Time.mid"),
]

# ff4pc = all_songs_from_dir("/home/jmyles/Music/midi/from-youtube-dropbox-to-sort/")
ff9pc = all_songs_from_dir("/home/jmyles/Music/midi/new-from-vgmsheetmusicbyolimar12345.com/")
# ff9pc = all_songs_from_dir("/home/jmyles/Music/midi/FF4PC/")
songs.extend(ff9pc)
# songs.extend(ff4pc)




class Simple(resource.Resource):
    isLeaf = True

    def render_POST(self, request):
        if request.args.get(b'action') == [b"next"]:
            new_song = player.next_song()
        if request.args.get(b'action') == [b"pause"]:
            player.pause()
        if request.args.get(b'velocity_adjustment') is not None:
            player.controls['VELOCITY_ADJUSTMENT'] = int(request.args.get(b'velocity_adjustment')[0])
        return (b"Hello world.")


site = server.Site(Simple())
player.port = mido.open_output('Axiom Pro 25:Axiom Pro 25 MIDI 1 20:0')
player.start(playlist=songs)
reactor.listenTCP(8670, site)



def simple_note(note_number, velocity=60, delay=1):
    print(f"playing {note_number} at velocity {velocity}")
    port.send(mido.Message(type="note_on", note=note_number, velocity=velocity))
    time.sleep(delay)
    port.send(mido.Message(type="note_off", note=note_number, velocity=0))
    port.send(mido.Message(type="note_off", note=note_number, velocity=127))






def main_thing():
    try:
        for song in songs:
            play_song(song)
    except (SystemExit, KeyboardInterrupt):
        return





if __name__ == "__main__":
    try:
        # delay = .25
        # while True:
        #     test_all_notes(delay=delay, calibrate=False)
        #     delay = delay * 2

        # d = reactor.callWhenRunning(main_thing)
        signal.signal(signal.SIGINT, player.shutdown)
        reactor.run()  # Weird place to do this.
        print("Ending main stuff.")

    except Exception as e:
        print(e)
        raise
