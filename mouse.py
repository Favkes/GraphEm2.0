import pygame
from abc import abstractmethod, ABC


class BaseMouse(ABC):
    instance = None
    _initialized: bool

    _down: bool
    _last_bound_event: pygame.event.Event

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self):
        if self._initialized:
            return
        self._down = False
        self._initialized = True

    def set_down(self, *args, **kwargs):
        self.down = True

    def set_up(self, *args, **kwargs):
        self.up = True

    def wrap_mouse_event(self, event:pygame.event.Event):
        self._last_bound_event = event
        return event

    def getpos(self):
        return self._last_bound_event.pos

    @abstractmethod
    def drag(self):
        pass

    @property
    def down(self):
        return self._down
    @down.setter
    def down(self, val:bool):
        self._down = val
    @property
    def up(self):
        return not self._down
    @up.setter
    def up(self, val:bool):
        self._down = not val