from threading import Event
from dataclasses import dataclass


@dataclass
class PauseCommand:
    resume_event: Event

@dataclass
class HighlightEdge:
    edge_id: int

@dataclass
class HighlightNode:
    node_id: int

class UserGraph:
    def __init__(self, ui_q):
        self.ui_q = ui_q

    def pause(self):
        resume_event = Event()

        self.ui_q.put(
            PauseCommand(resume_event=resume_event)
        )

        resume_event.wait()


def main():



if __name__=="__main__":
    main()