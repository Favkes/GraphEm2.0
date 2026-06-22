import pygame
from abc import abstractmethod, ABC
from enum import Enum, auto


class MouseEvent(Enum):
    CLICK = auto()
    HOVER = auto()

    DRAG = auto()
    DRAG_START = auto()
    DRAG_END = auto()
    DRAG_CHANGE = auto()

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
        self.down = True

    def set_up(self, *args, **kwargs):
        # print("UPP 2")
        self.up = True


    def getpos(self):
        return pygame.mouse.get_pos()

    @abstractmethod
    def drag(self):
        pass

    @property
    def down(self):
        return self._is_down
    @down.setter
    def down(self, val:bool):
        self._is_down = val
        self._down_time_start = pygame.time.get_ticks()
        self._is_pressed_long = False
        # self._check_is_click()
        self.schedule_event(MouseEvent.MOUSE_DOWN)
    @property
    def up(self):
        return not self._is_down
    @up.setter
    def up(self, val:bool):
        # print("UPP")
        self._is_down = not val
        self._check_is_click()
        self.schedule_event(MouseEvent.MOUSE_UP)
        self._is_pressed_long = False
        self._down_time_start = None


    def _check_is_click(self):
        print("checkisclick")
        if self._down_time_start is None:
            return

        if pygame.time.get_ticks() - self._down_time_start <= self.drag_threshold:
            print("click detected")
            self._short_click_scheduled = True
            self.schedule_event(MouseEvent.CLICK)
        else:
            print("DRAG END!")
            self.schedule_event(MouseEvent.DRAG_END)
            self.schedule_event(MouseEvent.DRAG_CHANGE)

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
        if not was_dragging and is_dragging:
            # print("LH")
            self.schedule_event(MouseEvent.DRAG_START)
            self.schedule_event(MouseEvent.DRAG_CHANGE)
        # HL
        elif was_dragging and not is_dragging:
            # print("HL")
            self.schedule_event(MouseEvent.DRAG_END)
            self.schedule_event(MouseEvent.DRAG_CHANGE)
        # HH
        elif was_dragging and is_dragging:
            # print("HH", self._down_time_start)
            self.schedule_event(MouseEvent.DRAG)

        if self.up:
            return False

        self._is_pressed_long = is_dragging
        return self._is_pressed_long

    # @property
    # def is_singular_click(self):
    #     # Only one action eats the click, all the others in line get False
    #     answer = self._short_click_scheduled
    #     self._short_click_scheduled = False
    #     return answer

    def update_events(self):
        _ = self.is_dragging

    @property
    def events(self) -> tuple[MouseEvent, ...]:
        # self._events.add(MouseEvent.HOVER)
        # print(self._events)
        return tuple(self._events)

    def clear_events(self):
        # print("CLEAR EVENTS")
        self._events = set()

    def schedule_event(self, event:MouseEvent):
        self._events.add(event)



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