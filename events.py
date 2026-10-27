import uuid
from dataclasses import dataclass
from typing import Callable


# class BaseEvent:
#     callable: Callable
#     uuid: uuid.UUID
#
#     def __init__(self, runnable:Callable):
#         self.callable = runnable
#         self.uuid = uuid.uuid4()


@dataclass
class TimedEvent:
    duration: float
    on_finish: Callable[[], None] = None
    on_update: Callable[[float], None] | None = None

    elapsed: float = 0.0
    cancelled: bool = False

    def update(self, dt:float) -> bool:
        """
        Returns true, if event finished and can be removed.
        :param dt:
        :return:
        """
        if self.cancelled:
            return True

        self.elapsed += dt

        if self.on_update is not None:
            progress = min(self.elapsed / self.duration, 1.0)
            self.on_update(progress)

        if self.duration <= self.elapsed:
            if self.on_finish is not None:
                self.on_finish()
            return True

        return False

    def cancel(self) -> None:
        self.cancelled = True


class EventScheduler:
    _instance: "EventScheduler | None" = None

    @classmethod
    def get(cls) -> "EventScheduler":
        if cls._instance is None:
            cls._instance = cls()

        return cls._instance


    _events:list[TimedEvent]
    _events_map:dict[str, TimedEvent]

    def __init__(self):
        if EventScheduler._instance is not None:
            raise RuntimeError("EventScheduler is a singleton. Use EventScheduler.get() instead.")

        self._events = []
        self._events_map = dict()

    def add(self, event:TimedEvent, tag:str = None, replace:bool = False) -> TimedEvent:
        if tag is None:
            self._events.append(event)
            return event

        tagged_event = self._events_map.get(tag, None)

        if tagged_event is not None:
            is_active = any(existing_event is tagged_event for existing_event in self._events)

            if is_active:
                if not replace:
                    return tagged_event

                tagged_event.cancel()
                self._events = [
                    existing_event
                    for existing_event in self._events
                    if existing_event is not tagged_event
                ]

        self._events_map[tag] = event
        self._events.append(event)
        return event


    def update(self, dt:float) -> None:
        remaining_events = []

        for event in self._events:
            finished = event.update(dt)

            if not finished:
                remaining_events.append(event)

        self._events = remaining_events

    def clear(self):
        self._events = []
        self._events_map = dict()
