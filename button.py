from widgets import Widget, Callable, pygame, cv2, Mouse, MouseEvent, BaseViewport
# from viewport import ViewportManager
from multipledispatch import dispatch


ColourTuple = tuple[int,int,int]


class BaseButton(Widget):
    _runnable: Callable|None

    _is_click_scheduled: bool
    _was_click_fired_in_previous_frame: bool

    _is_two_state: bool             # Determines whether a button simply clicks, or stays ON or OFF
    _is_holdable: bool              # Determines whether a button can be held down, or will immediately click back up

    _is_pressed: bool

    pressed_colour: ColourTuple
    current_colour: ColourTuple


    def __init__(self,
                 parent:Widget|None,
                 position:tuple[int,int],
                 dimensions:tuple[int,int],
                 colour:tuple[int,int,int],
                 pressed_colour:ColourTuple = None,
                 transparent:bool = False,
                 clip_to_parent:bool = False,
                 runnable:Callable|None = None,
                 two_state:bool = False,
                 holdable:bool = False):
        Widget.__init__(self, parent, position, dimensions, colour, transparent, clip_to_parent)
        self.set_command(runnable)
        self._is_click_scheduled = False
        self._was_click_fired_in_previous_frame = False
        self._is_two_state = two_state
        self._is_holdable = holdable
        self._is_pressed = False
        self.current_colour = colour
        self.pressed_colour = colour if pressed_colour is None else pressed_colour

    def set_command(self, runnable:Callable|None):
        self._runnable = runnable

    def _run(self):
        if self._runnable:
            self._runnable()

    def click_routine(self):
        if self._is_two_state:
            self._is_pressed = not self._is_pressed
            self._run()
        else:   # is one state (clickable)
            self._run()

    def hitbox_bound(self, func:Callable):
        def wrapper():
            if self.hit_test(self.root.getmouse()):
                func()
        return wrapper

    def detect_clicked(self):
        if self.hit_test(self.root.getmouse().getpos()):
            self.click_routine()

    def bind_to(self, trigger:"pygame.event.Event|MouseEvent"):
        """
        Bind internal instance callable to a trigger.

        :param trigger: A trigger event supported by the ViewportHandler event bind system.
        :type trigger: pygame.event.Event|MouseEvent
        :return: None
        """
        self.root.bind(trigger, self.detect_clicked)

    def bind(self, trigger:"pygame.event.Event|MouseEvent", func:Callable):
        """
        Bind external callable to a trigger

        :param trigger:
        :param func:
        :return:
        """
        self.root.bind(trigger, func)

    def render(self, relative_pos:tuple[int,int] = (0,0)):
        cv2.rectangle(self.root.canvas,
                      self.globalpos,
                      self.globalPOS,
                      self.current_colour,
                      -1
        )



    # click_detected says whether a click was detected in this particular frame, and gets reset every frame
    @property
    def was_click_detected(self):
        return self._is_click_scheduled

    def post_click(self):
        self._is_click_scheduled = False
        self._was_click_fired_in_previous_frame = True
    def click(self):
        self._is_click_scheduled = True
        self.current_colour = self.pressed_colour
        # self.click_routine()

    @property
    def is_pressed(self):
        # return self._is_permanent_state_down
        return self._is_pressed

    def press_down(self):
        self._is_pressed = True
        self.click()
    def release(self):
        self._is_pressed = False


    def set_main_colour(self, colour:ColourTuple):
        self.colour = colour
    def set_colour(self, colour:ColourTuple):
        self.current_colour = colour
    def reset_colour(self):
        self.current_colour = self.colour
    def get_main_colour(self) -> ColourTuple:
        return self.colour


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

    def detect_click(self):
        if self.hit_test(self.root.getmouse()):
            self._run()

    def bind_to(self, trigger:"pygame.event.Event|MouseEvent"):
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


    @dispatch(tuple)
    def hit_test(self, pos:tuple[int,int]):
        dx = pos[0] - self.x
        dy = pos[1] - self.y
        r2 = dx * dx + dy * dy
        return r2 < self.r ** 2
    @dispatch(Mouse)
    def hit_test(self, mouse: Mouse):
        return self.hit_test(mouse.getpos())
    @dispatch(pygame.event.Event)
    def hit_test(self, event:pygame.event.Event):
        return self.hit_test(event.pos)


    def detect_click(self):
        if self.hit_test(self.root.getmouse()):
            self._run()

    def bind_to(self, trigger:"pygame.event.Event|MouseEvent"):
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



if __name__=="__main__":
    vp = ViewportManager(500, 500)
    vp.bindmouse(Mouse(200))
    vp.bind(pygame.MOUSEBUTTONDOWN, vp.getmouse().set_down)
    vp.bind(pygame.MOUSEBUTTONUP, vp.getmouse().set_up)

    btn1 = BaseButton(vp, (50, 50), (100, 100), (255, 0, 200), (200, 10, 0), two_state = False)
    def btn1_func_press(btn:BaseButton):
        # vp.getmouse().drag(btn1)
        print("press")
        btn.click()

    @btn1.hitbox_bound
    def btn1_func_release():
        print("release")
        # btn.click()
        btn1.reset_colour()

    btn1.set_command(lambda btn=btn1:btn1_func_press(btn))
    btn1.bind_to(MouseEvent.CLICK)
    # btn1.bind(MouseEvent.CLICK, lambda btn=btn1:btn1_func_release(btn))
    btn1.bind(MouseEvent.CLICK, btn1_func_release)

    vp.mainloop()
