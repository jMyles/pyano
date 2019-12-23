import pprint
import random
import time
from collections import defaultdict
from contextlib import suppress

from mido import merge_tracks, tick2second, second2tick
from mido.midifiles.midifiles import DEFAULT_TEMPO
from twisted.internet import reactor
from twisted.internet.threads import deferToThreadPool
from twisted.python.threadpool import ThreadPool

from velocities import get_minimum_velocities_for_all_keys
from constant_sorrow.constants import SEQUENTIAL, SHUFFLED

playing = False
paused = True

port = None
play_order = SEQUENTIAL

song_threadpool = ThreadPool(minthreads=1, maxthreads=1, name="Song Player")
note_threadpool = ThreadPool(minthreads=256, maxthreads=256, name="Note Player")

controls = dict(
    VELOCITY_FLOOR_BOOST=0,
    VELOCITY_ADJUSTMENT=30,
    VELOCITY_GROOVE=3,
    SWING_VALUE=0.00,
    TEMPO_ADJUSTMENT=100,
    TEMPO=500000,
)

min_velocities = get_minimum_velocities_for_all_keys(controls['VELOCITY_FLOOR_BOOST'])
TAP_RATE = .10


class _PlayerInternalState:
    STOP_SIGNAL = False
    PAUSED = False
    playlist = []

    class StopPlaying(RuntimeError):
        """
        No more ha-has.
        """

    @classmethod
    def toggle_pause(cls):
        if cls.PAUSED:
            cls.PAUSED = False
        else:
            cls.PAUSED = True


def soften_note(msg):
    if hasattr(msg, "velocity") and msg.velocity > 0:
        old_velocity = msg.velocity
        min_velocity = min_velocities[msg.note]

        velocity_groove = random.randint(0, controls['VELOCITY_GROOVE'])
        adjusted_velocity = int(old_velocity * controls['VELOCITY_ADJUSTMENT'] / 100) + velocity_groove
        new_velocity = max(adjusted_velocity, min_velocity)
        msg.velocity = new_velocity


def play_message_with_groove(message):
    if _PlayerInternalState.STOP_SIGNAL:
        return

    soften_note(message)
    port.send(message)

    if hasattr(message, "control") and message.control == 64:
        if message.value > 63:
            print("=== Pressing Pedal ===")
        else:
            print("=== Releasing Pedal ===")


def generate_messages_from_song(song):
    note_off_times = {}
    cummulative_ticks = 0
    borrowed_time = 0
    all_messages = defaultdict(list)

    tempo = DEFAULT_TEMPO
    tap_rate_in_ticks = round(second2tick(TAP_RATE, song.ticks_per_beat, tempo))

    # The tracks of type 2 files are not in sync, so they can
    # not be played back like this.
    if song.type == 2:
        raise TypeError("can't merge tracks in type 2 (asynchronous) file")



    by_note = defaultdict(list)


    for message in merge_tracks(song.tracks):
        cummulative_ticks += message.time
        all_messages[cummulative_ticks].append(message)
        with suppress(AttributeError):
            index = len(all_messages[cummulative_ticks]) - 1  # Silly hack - there's a better way.
            by_note[message.note].append((index, cummulative_ticks, message))

    last_tick = list(all_messages.keys())[-1]
    messages_with_seconds = []
    for _note, messages in by_note.items():
        off_at = on_at = last_tick
        for _delete_me_index, tick, message in reversed(messages):
            if message.type == "note_on":
                on_at = tick
            elif message.type == "note_off":
                off_at = tick
                too_soon_by = on_at - off_at - tap_rate_in_ticks
                if too_soon_by < 0:
                    print(f"Too soon by {too_soon_by}")
                    adjusted_tick = tick - abs(too_soon_by)
                    try:
                        all_messages[tick].remove(message)
                    except Exception as e:
                        pprint.pprint(all_messages[tick])
                        raise
                    # message.time = 66666666666666666666666666
                    all_messages[adjusted_tick].append(message)
                    # TODO: In the future, probably keep adjusting backwards in the event that the note on before this was too close.
            else:
                raise TypeError("What kind of note is this?!")

    # Now turn these into notes with seconds.

    cummulative_ticks = 0
    for ticks, messages in sorted(all_messages.items()):
        for message in messages:
            if message.type == 'set_tempo':
                tempo = message.tempo
        delta_ticks = ticks - cummulative_ticks
        if delta_ticks > 0:
            delta = tick2second(delta_ticks, song.ticks_per_beat, tempo)
        else:
            delta = 0
        messages_with_seconds.append((delta, messages))
        cummulative_ticks = ticks
    return messages_with_seconds



##############################
##########################

    for index, message in enumerate(song):
        if message.is_meta:
            all_messages.append(message)
            continue

        cummulative_ticks += message.time

        # Try to pay back borrowed time.
        if borrowed_time and message.time > 0:
            after_repayment = message.time - borrowed_time
            if after_repayment >= 0:
                message.time = after_repayment
                print(f"Paid back all {borrowed_time}")
                borrowed_time = 0
            else:
                new_borrowed_time = abs(after_repayment)
                message.time = 0
                print(f"Paid back {borrowed_time - new_borrowed_time} out of {borrowed_time}")
                borrowed_time = new_borrowed_time

        swing = random.uniform(0, controls['SWING_VALUE'])
        if message.type == "note_on":
            if swing > 0:
                borrowed_time += swing
                message.time = message.time + swing

        times += message.time

        if message.type == "note_on":
            note_last_off, note_off_message_index = note_off_times.pop(message.note, (0, None))
            if note_last_off:
                note_off_message = all_messages[note_off_message_index]
                note_off_and_on_time = times - note_last_off
                sleeper = max(TAP_RATE - note_off_and_on_time, 0)
                if sleeper:
                    if note_off_message.time > 0:
                        assert False
                    borrowed_time += sleeper
                    print(f"Note was on and off in only {note_off_and_on_time}; sleeping {sleeper}")
                    message.time = message.time + sleeper
                    # Give velocity a boost too.
                    message.velocity = min(message.velocity + 5, 127)
        elif message.type == "note_off":
            note_off_times[message.note] = (times, index)
        all_messages.append(message)
    return all_messages

def play_song(song):
    song_messages = generate_messages_from_song(song)
    for group_counter, (sleep_time, messages) in enumerate(song_messages):
        if _PlayerInternalState.STOP_SIGNAL:
            raise _PlayerInternalState.StopPlaying
        else:
            while True:
                if _PlayerInternalState.PAUSED:
                    if _PlayerInternalState.STOP_SIGNAL:
                        raise _PlayerInternalState.StopPlaying
                    silence()
                    time.sleep(.01)
                else:
                    break
            time.sleep(sleep_time * controls['TEMPO_ADJUSTMENT'] / 100)  # Delay until the message is supposed to play.
            for message in messages:
                if not message.is_meta and not message.type == "sysex":
                    message.channel = 0  # Piano only plays 0
                    d = deferToThreadPool(reactor, note_threadpool, play_message_with_groove, message)
                else:
                    print(message)

def silence():
    reactor.callFromThread(port.reset)


def next_song():
    if _PlayerInternalState.PAUSED:
        _PlayerInternalState.PAUSED = False
    else:
        _PlayerInternalState.STOP_SIGNAL = True
        _PlayerInternalState.advance_to_next_song = True


def play():
    try:
        if play_order is SEQUENTIAL:
            for song in _PlayerInternalState.playlist:
                try:
                    play_song(song)
                    silence()
                    time.sleep(1)
                except _PlayerInternalState.StopPlaying:
                    if _PlayerInternalState.advance_to_next_song:
                        _PlayerInternalState.advance_to_next_song = False
                        silence()
                        time.sleep(.5)
                        _PlayerInternalState.STOP_SIGNAL = False
                        continue
                    else:
                        silence()
                        return



    except (SystemExit, KeyboardInterrupt):
        _PlayerInternalState.STOP_SIGNAL = True
        return


def start(playlist):
    _PlayerInternalState.playlist = playlist
    deferToThreadPool(reactor, song_threadpool, play)
    note_threadpool.start()
    song_threadpool.start()


def pause():
    _PlayerInternalState.toggle_pause()


def shutdown(signum, stackframe):
    _PlayerInternalState.STOP_SIGNAL = True
    reactor.callFromThread(song_threadpool.stop)
    reactor.callFromThread(note_threadpool.stop)
    reactor.stop()
    silence()