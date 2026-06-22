from __future__ import annotations
from abc import ABC, abstractmethod
from collections.abc import Callable
from multipledispatch import dispatch

import numpy as np
import pygame
import cv2
from mouse import BaseMouse, MouseEvent


class Widget(ABC):
    root: BaseViewport|None = None
    parent = None
    children: list

    _x: int
    _y: int

    _x_global: int
    _y_global: int

    _width: int
    _height: int

    pygame_rect: pygame.Rect

    _is_render: bool
    colour: tuple[int,int,int]

    _is_clip_to_parent: bool


    def __init__(self,
                 parent:Widget|None,
                 pos:tuple[int,int],
                 dimensions:tuple[int,int],
                 colour:tuple[int,int,int] = (200, 200, 200),
                 transparent:bool = False,
                 clip_to_parent:bool = False):
        self.attach_to(parent)
        self.children = []
        self._x, self._y = pos
        self._x_global, self._y_global = 0, 0
        self._recompute_globals()
        self._width, self._height = dimensions
        self.recalculate_pygame_rect()
        self.colour = colour
        self._is_render = not transparent
        self._is_clip_to_parent = clip_to_parent

    def __repr__(self):
        return f"Widget(pos={self.pos}, dim={self.dimensions}{', Transparent' if self.transparence else ''})"

    def attach_to(self, parent:Widget|BaseViewport|None):
        if parent is None:
            return

        if self.parent is parent:
            return

        self.detach()
        self.parent = parent
        if parent.is_root:
            self.root = parent
        else:
            self.root = parent.root

        if self not in parent.children:
            parent.children.append(self)

    def detach(self):
        if self.parent is not None:
            self.parent.children.remove(self)
            self.parent = None
            self.root = None

    def recalculate_pygame_rect(self):
        self.pygame_rect = pygame.Rect(self._x_global, self._y_global, self._width, self._height)


    @dispatch(tuple)
    def hit_test(self, pos: tuple[int, int]):
        return self.pygame_rect.collidepoint(pos)
    @dispatch(BaseMouse)
    def hit_test(self, mouse:BaseMouse):
        return self.hit_test(mouse.getpos())
    # @dispatch(pygame.event.Event)
    # def hit_test(self, event: pygame.event.Event):
    #     if hasattr(event, "pos"):
    #         return self.pygame_rect.collidepoint(event.pos)
    #     return False


    @abstractmethod
    def render(self):
        pass
    def render_recursive(self):
        if self._is_render:
            self.render()
        for child in self.children:
            child.render_recursive()

    @property
    def transparence(self):
        return not self._is_render
    @transparence.setter
    def transparence(self, val):
        self._is_render = not val

    def render_line_to(self, other:Widget, colour:tuple[int,int,int] = None):
        if colour is None:
            colour = self.colour
        cv2.line(self.root.canvas, self.center_out, other.center_out, colour, 1)

    def _try_clip_to_parent(self):
        if self._is_clip_to_parent:
            if self.x < 0:
                self.x = 0
            if self.y < 0:
                self.y = 0
            if self.parent.w < self.X:
                self.X = self.parent.w
            if self.parent.h < self.Y:
                self.Y = self.parent.h

    def _recompute_globals(self):
        self._x_global = self._x
        self._y_global = self._y
        if self.parent:
            self._x_global += self.parent._x_global
            self._y_global += self.parent._y_global

    @property
    def x(self):
        return self._x
    @x.setter
    def x(self, val):
        self._x = val
        self._try_clip_to_parent()
        self._recompute_globals()
        self.pygame_rect.x = self._x_global

    @property
    def y(self):
        return self._y
    @y.setter
    def y(self, val):
        self._y = val
        self._try_clip_to_parent()
        self._recompute_globals()
        self.pygame_rect.y = self._y_global

    @property
    def pos(self):
        return self._x, self._y
    @pos.setter
    def pos(self, val):
        self.x, self.y = val

    @property
    def width(self):
        return self._width
    @width.setter
    def width(self, val):
        self._width = val
        self.pygame_rect.w = val

    @property
    def height(self):
        return self._height
    @height.setter
    def height(self, val):
        self._height = val
        self.pygame_rect.h = val

    @property
    def w(self):
        return self._width
    @w.setter
    def w(self, val):
        self._width = val
        self.pygame_rect.w = val

    @property
    def h(self):
        return self._height
    @h.setter
    def h(self, val):
        self._height = val
        self.pygame_rect.h = val

    @property
    def dimensions(self):
        return self.w, self.h
    @dimensions.setter
    def dimensions(self, val):
        self.width, self.height = val
    @property
    def center_in(self):
        return self._width // 2, self._height // 2
    @property
    def center_out(self):
        return self._x + self.center_in[0], self._y + self.center_in[1]

    @property
    def X(self):
        return self._x + self.w
    @X.setter
    def X(self, val):
        self._x += val - self.X
        self._X = val
        self._try_clip_to_parent()
        self._recompute_globals()
        self.pygame_rect.x = self._x_global

    @property
    def Y(self):
        return self._y + self.h
    @Y.setter
    def Y(self, val):
        self._y += val - self.Y
        self._Y = val
        self._try_clip_to_parent()
        self._recompute_globals()
        self.pygame_rect.y = self._y_global

    @property
    def POS(self):
        return self.X, self.Y
    @POS.setter
    def POS(self, val):
        self.X, self.Y = val

    @property
    def globalpos(self):
        return self._x_global, self._y_global
    @globalpos.setter
    def globalpos(self, val):
        """ Changes the relative position of the object to match global coordinates given """
        anchor_x = self._x_global - self._x
        anchor_y = self._y_global - self._y
        self._x_global, self._y_global = val
        self._x = self._x_global - anchor_x
        self._y = self._y_global - anchor_y

    @property
    def globalPOS(self):
        return self._x_global + self.w, self._y_global + self.h
    @globalPOS.setter
    def globalPOS(self, val):
        pass

    @property
    def is_root(self):
        if self.parent:
            return False
        return True


class BaseViewport(Widget):
    fps: int

    canvas: np.ndarray
    screen_ref: pygame.display

    bindmap: dict[pygame.event.Event|MouseEvent, list[Callable]]

    _mouse: BaseMouse


    def __init__(self, width:int, height:int, fps:int = 30):
        Widget.__init__(self, None, (0, 0), (width, height))
        pygame.init()
        self.fps = fps
        self.try_init_screen()
        self.bindmap = dict()

    def try_init_screen(self):
        if pygame.get_init():
            self.screen_ref = pygame.display.set_mode(self.dimensions)
        else:
            raise Exception("Pygame not initialized!")

    def bind(self, trigger:pygame.event|MouseEvent, runnable:Callable|None):
        if not runnable:
            print("[WRN] (BV) No command given to bind", trigger)
            return

        if trigger in self.bindmap.keys():
            self.bindmap[trigger].append(runnable)
        else:
            self.bindmap[trigger] = []
            self.bindmap[trigger].append(runnable)

    def unbind(self, trigger:pygame.event|MouseEvent, runnable:Callable):
        if trigger in self.bindmap.keys() and runnable in self.bindmap[trigger]:
            self.bindmap[trigger].remove(runnable)
        else:
            print("Runnable", runnable, "could not be unbound from", trigger, "as it was not bound there.")

    def render(self, relative_pos:tuple[int,int] = (0,0)):
        pass

    def bindmouse(self, mouse:BaseMouse):
        self._mouse = mouse

    def getmouse(self):
        return self._mouse


class Mouse(BaseMouse):
    drag_offset: list[int]|None
    drag_widget: Widget|None

    def __init__(self, drag_threshold:int = 50):
        BaseMouse.__init__(self, drag_threshold)
        self.drag_offset = None
        self.drag_widget = None


    def bind_to_viewport(self, vp: BaseViewport):
        vp.bindmouse(self)

    def drag(self, widget:Widget = None):
        # Reset dragging if mouse is no longer down
        if self.up:
            # print("Cannot drag anything if the mouse isn't down.")
            self.drag_offset = None
            self.drag_widget = None
            return

        # If dragging, not just clicking once:
        if self.is_dragging:
            # If no widget is currently held:
            if self.drag_widget is None:
                # if no widget was given, abort.
                if widget is None:
                    return
                # else, if a widget was given, begin holding it.
                self.drag_widget = widget

            # Dragging offset math
            if self.drag_offset is None:
                self.drag_offset = [
                    self.drag_widget.x - self.getpos()[0],
                    self.drag_widget.y - self.getpos()[1]
                ]

            self.drag_widget.x = self.getpos()[0] + self.drag_offset[0]
            self.drag_widget.y = self.getpos()[1] + self.drag_offset[1]


class Frame(Widget):
    def __init__(self, *args, **kwargs):
        Widget.__init__(self, *args, **kwargs)

    def render(self, relative_pos:tuple[int,int] = (0,0)):
        cv2.rectangle(
            self.root.canvas,
            self.globalpos,
            self.globalPOS,
            self.colour,
            1
        )
