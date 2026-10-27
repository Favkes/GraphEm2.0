# import numpy as np
# import pygame
# import cv2
# from collections.abc import Callable
import pygame.time

from widgets import *
from button import Button, CircularButton
from events import EventScheduler


class ViewportManager(BaseViewport):
    running: bool
    render_routine: Callable


    def __init__(self, width:int, height:int, fps:int = 30):
        BaseViewport.__init__(self, width, height, fps)
        self.running = False
        self.clear_canvas()
        self.set_render_routine()

    def __repr__(self):
        out = f"ViewportManager instance:"
        for child in self.children:
            out += f"\n\t{child}"
        return out

    def clear_canvas(self):
        self.canvas = np.zeros(self.dimensions + (3,), dtype=np.uint8)

    def numpy_to_surface(self):
        arr_rgb = cv2.cvtColor(self.canvas, cv2.COLOR_BGR2RGB)
        return pygame.surfarray.make_surface(arr_rgb.swapaxes(0, 1))

    def update_screen(self):
        self.numpy_to_surface()
        self.screen_ref.blit(self.numpy_to_surface(), (0, 0))

    def render(self, relative_pos:tuple[int,int] = (0,0)):
        pass

    def set_render_routine(self, func: Callable = None, pass_viewport: bool = True):
        if func:
            if pass_viewport:
                self.render_routine = lambda: func(self)
            else:
                self.render_routine = func
        else:
            self.render_routine = self.draw_scene

    def draw_scene(self):
        self.canvas[:] = (25, 25, 25)
        cv2.putText(self.canvas, "This is a demo", (self.center_in[0] - 150, self.center_in[1]), cv2.FONT_HERSHEY_PLAIN, 3, (200, 0, 0), 1)
        cv2.circle(self.canvas, pygame.mouse.get_pos(), 40, (0, 255, 0), -1)

        for child in self.children:
            if isinstance(child, Frame):
                for i in range(len(child.children)-1):
                    child.children[i].render_line_to(child.children[i+1])

        self.render_recursive()


    def handle_events(self):
        self.getmouse().drag()
        # self.getmouse().update_events()
        mouse_events = self.getmouse().events
        # print("events>", mouse_events)
        self.getmouse().clear_events()
        # for k, v in self.bindmap.items():
        #     print(k, v)
        # print()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                self.running = False

            for bound_trigger in self.bindmap.keys():

                if event.type == bound_trigger:
                    bound = self.bindmap[bound_trigger]
                    if isinstance(bound, list):
                        for runnable in bound:
                            runnable(event)

        for bound_trigger in self.bindmap.keys():
            if bound_trigger in mouse_events:
                # print("AAA", bound_trigger, mouse_events)
                # print(bound_trigger, mouse_events)
                # print(bound_trigger)
                bound = self.bindmap[bound_trigger]
                if isinstance(bound, list):
                    for runnable in bound:
                        runnable()
        # print()


    def mainloop(self):
        self.running = True
        clock = pygame.time.Clock()
        scheduler = EventScheduler.get()

        while self.running:
            dt = clock.tick(self.fps) / 1000.0

            self.clear_canvas()
            self.handle_events()

            scheduler.update(dt)


            if self.render_routine:
                self.render_routine()

            self.update_screen()
            pygame.display.flip()

    def __exit__(self):
        pygame.quit()



def but1_func():
    # btn1.x += 10
    mouse.drag(btn1)

def but2_func():
    # btn2.y += 10
    mouse.drag(btn2)

def but3_func():
    mouse.drag(btn3)

if __name__ == "__main__":
    print("viewport")
    viewport = ViewportManager(500, 500, fps=30)
    mouse = Mouse()
    mouse.bind_to_viewport(viewport) # or alt: viewport.bindmouse(mouse)

    viewport.bind(pygame.MOUSEBUTTONDOWN, mouse.set_down)
    viewport.bind(pygame.MOUSEBUTTONUP, mouse.set_up)

    print("btn1")
    btn1 = Button(viewport, (10, 10), (30, 30), (200, 200, 0), but1_func)
    btn1.bind_to(mouse)

    print("btn2")
    btn2 = CircularButton(viewport, (100, 100), 30, (200, 200, 0), but2_func)
    btn2.bind_to(mouse)

    print("w1")
    w1 = Frame(viewport, (150, 150), (50, 50), transparent=False)

    print("btn3")
    btn3 = Button(w1, (0, 0), (10, 10), (200, 0, 200), but3_func)
    btn3.bind_to(mouse)

    print(viewport)

    viewport.mainloop()
