from widgets import Widget, Callable, pygame, cv2, Mouse, BaseViewport


class Button(Widget):
    _runnable: Callable

    def __init__(self,
                 parent:Widget|None,
                 position:tuple[int,int],
                 dimensions:tuple[int,int],
                 colour:tuple[int,int,int],
                 transparent:bool = False,
                 clip_to_parent:bool = False,
                 runnable:Callable|None = None):
        Widget.__init__(self, parent, position, dimensions, colour, transparent, clip_to_parent)
        self.set_command(runnable)

    def set_command(self, runnable:Callable|None):
        self._runnable = runnable

    def _run(self):
        if self._runnable:
            self._runnable()

    def detect_click(self, trigger:"pygame.event.Event", mouse:Mouse = None):
        if self.hit_test(trigger):
            self._run()

    def bind_to(self, trigger:"pygame.event.Event|Mouse"):
        self.root.bind(trigger, self.detect_click)

    def render(self, relative_pos:tuple[int,int] = (0,0)):
        cv2.rectangle(self.root.canvas,
                      self.globalpos,
                      self.globalPOS,
                      self.colour,
                      -1
        )



class CircularButton(Widget):
    _runnable: Callable
    _r: int

    def __init__(self,
                 parent:Widget|None,
                 position:tuple[int,int],
                 radius:int,
                 colour:tuple[int,int,int],
                 transparent:bool = False,
                 clip_to_parent:bool = False,
                 runnable:Callable|None = None):
        Widget.__init__(self, parent, position, (0, 0), colour, transparent, clip_to_parent)
        self._r = radius
        self.set_command(runnable)

    def set_command(self, runnable:Callable|None):
        self._runnable = runnable

    def _run(self):
        if self._runnable:
            self._runnable()

    def render(self):
        cv2.circle(self.root.canvas,
                   self.globalpos,
                   self.r,
                   self.colour,
                   -1
        )

    def hit_test(self, event):
        dx = event.pos[0] - self.x
        dy = event.pos[1] - self.y
        r2 = dx*dx + dy*dy
        return r2 < self.r**2

    def detect_click(self, event:"pygame.event.Event"):
        if self.hit_test(event):
            self._run()

    def bind_to(self, trigger:"pygame.event.Event|Mouse"):
        self.root.bind(trigger, self.detect_click)

    @property
    def r(self):
        return self._r
    @r.setter
    def r(self, val):
        self._r = val
    @property
    def radius(self):
        return self._r
    @radius.setter
    def radius(self, val):
        self._r = val

