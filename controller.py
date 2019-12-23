import readchar
import signal
import requests


while True:
    key = readchar.readkey()
    signals = {
        '\x03': getattr(signal, 'SIGINT', getattr(signal, 'CTRL_C_EVENT', None)),
        '\x1a': getattr(signal, 'SIGTSTP', None),
    }
    try:
        if key in signals:
            raise KeyboardInterrupt
        elif key == '\x1b[A':
            print("UP!")
                requests.post("http://localhost:8670", data="llamas")
        elif key == '\x1b[B':
            print("Down!")
        print(key)
    except Exception as e:
        print(e)
        break