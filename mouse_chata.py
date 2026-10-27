import pygame
from abc import abstractmethod, ABC
from enum import Enum, auto


class MouseEvent(Enum):
    CLICK = auto()
    HOVER = auto()
    DRAG = auto()
    DRAG_START = auto()
    DRAG_END = auto()
    MOUSE_DOWN = auto()
    MOUSE_UP = auto()

# class MouseEvent:
#     HOVER = "hover"
#     CLICK = "click"
#     DRAG = "drag"
#
#     _EVENTS:tuple[str] = ("hover", "click", "drag")
#     _event:int = None
#
#     def __init__(self, event:str):
#         try:
#             self._event = self._EVENTS.index(event)
#         except ValueError: # item not in list
#             RuntimeError(f"[ERR] (ME): No such mouse event exists: {event}")


class BaseMouse(ABC):
    instance = None
    _initialized: bool

    _is_down: bool
    _last_bound_event: pygame.event.Event

    drag_threshold: int     # time in ms
    _down_time_start: int|None
    _is_pressed_long: bool  # dragging
    _short_click_scheduled: bool # singular click
    _dragging_start: bool
    _dragging_end: bool
    _events: set[MouseEvent]

    def __new__(cls, *args, **kwargs):
        if cls.instance is None:
            cls.instance = super().__new__(cls)
            cls.instance._initialized = False
        return cls.instance

    def __init__(self, drag_threshold:int = 50):
        if self._initialized:
            return
        self._initialized = True

        self._is_down = False

        self.drag_threshold = drag_threshold
        self._down_time_start = None
        self._is_pressed_long = False
        self._short_click_scheduled = False
        self._events = set()

    def set_down(self, *args, **kwargs):
        self._is_down = True

        self._down_time_start = pygame.time.get_ticks()
        self._is_pressed_long = False

        self.schedule_event(MouseEvent.MOUSE_DOWN)

    def set_up(self, *args, **kwargs):
        was_dragging = self._is_pressed_long

        elapsed = 0
        if self._down_time_start is not None:
            elapsed = pygame.time.get_ticks() - self._down_time_start

        if was_dragging:
            self.schedule_event(MouseEvent.DRAG_END)
        elif elapsed <= self.drag_threshold:
            self.schedule_event(MouseEvent.CLICK)

        self.schedule_event(MouseEvent.MOUSE_UP)

        self._is_down = False
        self._is_pressed_long = False
        self._down_time_start = None


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
        return self._is_down
    # @down.setter
    # def down(self, val:bool):
    #     self._is_down = val
    #     self._down_time_start = pygame.time.get_ticks()
    #     self._check_is_click()
    #     self._is_pressed_long = False
    @property
    def up(self):
        return not self._is_down
    # @up.setter
    # def up(self, val:bool):
    #     self._is_down = not val
    #     self._check_is_click()
    #     self._is_pressed_long = False
    #     self._down_time_start = None

    def _check_is_click(self):
        if pygame.time.get_ticks() - self._down_time_start <= self.drag_threshold:
            self._short_click_scheduled = True
            self.schedule_event(MouseEvent.CLICK)
        else:
            print("DRAG END!")
            self.schedule_event(MouseEvent.DRAG_END)

    @property
    def is_dragging(self):
        was_dragging = self._is_pressed_long
        if self._down_time_start:
            # print(pygame.time.get_ticks(), self._down_time_start, pygame.time.get_ticks() - self._down_time_start, self.drag_threshold)
            is_dragging = pygame.time.get_ticks() - self._down_time_start > self.drag_threshold
        else:
            # print("NONETYPE OVERRIDE")
            is_dragging = False

        # print(was_dragging, is_dragging)
        # LH
        # if not was_dragging and is_dragging:
        #     # print("LH")
        #     self.schedule_event(MouseEvent.DRAG_START)
        # # HL
        # elif was_dragging and not is_dragging:
        #     # print("HL")
        #     self.schedule_event(MouseEvent.DRAG_END)
        # # HH
        # elif was_dragging and is_dragging:
        #     # print("HH")
        #     self.schedule_event(MouseEvent.DRAG)

        if self.up:
            return False

        self._is_pressed_long = is_dragging
        return self._is_pressed_long


    def update_events(self):
        if not self.down:
            return

        if self._down_time_start is None:
            return

        elapsed = pygame.time.get_ticks() - self._down_time_start

        if self.drag_threshold < elapsed:
            if not self._is_pressed_long:
                self.schedule_event(MouseEvent.DRAG_START)
            else:
                self.schedule_event(MouseEvent.DRAG)

            self._is_pressed_long = True

    def schedule_event(self, event:MouseEvent):
        self._events.add(event)

    @property
    def events(self) -> tuple[MouseEvent, ...]:
        # self._events.add(MouseEvent.HOVER)
        events = self._events
        self._events = set()
        return tuple(events)


    def __repr__(self):
        outL = []
        def addnext(conditon:bool, content:str):
            if conditon:
                if len(outL) > 0:
                    outL.append(", ")
                outL.append(content)

        addnext(self.down, "down")
        addnext(self.is_dragging, "dragging")
        # addnext(self.is_singular_click, "clicked")

        out = f"Mouse({''.join(outL)})"
        return out
