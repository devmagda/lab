from sshkeyboard import listen_keyboard
from electronics import TrackController

global n

tc = TrackController.from_config()


def on_key_press(key):
    global n
    n = 0
    if key == 'w':
        tc.forward(100)
        n += 1
        print('Forward')
    elif key == 'a':
        tc.rotate_left(100)
        n += 1
        print('Rotate left')
    elif key == 's':
        tc.backward(100)
        n += 1
        print('Backward')
    elif key == 'd':
        tc.rotate_right(100)
        n += 1
        print('Rotate right')
    elif key == 'p':
        quit(0)
    else:
        print(f"Unmapped key: {key}")
    if n == 0:
        tc.stop()
        print('Stop')


def release(key):
    global n
    n -= 1
    print(f'Release {n}')
    if n == 0:
        tc.stop()


# Set up the keyboard hook
with listen_keyboard(on_press=on_key_press, on_release=release) as listener:
    try:
        listener.join()
    except KeyboardInterrupt:
        print("Program terminated.")
