from threading import Thread, Event
import time


def wait_for_event(e):
    while True:
        event_is_set = e.wait()
        print("\nPerforming single algorithm step.\n")
        e.clear()


e = Event()
t = Thread(
    target=wait_for_event,
    args=(e,),
    daemon=True
)

t.start()
while True:
    user_in = input("> ")
    if user_in == "step":
        e.set()
    else:
        print(user_in)


