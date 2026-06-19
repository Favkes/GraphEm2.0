from viewport import ViewportManager
from widgets import *
from button import *
import cv2



edges_base: np.ndarray|None = np.array((
    (0, 1, 1, 0, 0)123
    (0, 0, 1, 1, 1),
    (0, 0, 0, 1, 0),
    (0, 0, 0, 0, 1),
    (0, 0, 0, 0, 0),
))

edges: np.ndarray|None = edges_base.copy()

focused_edge: tuple[int,int]|None = None
focused_node: Button|CircularButton|None = None
focused_node_num: int|None = None


def render_routine(vp: ViewportManager):
    vp.canvas[:] = (25, 25, 25)
    cv2.circle(vp.canvas, pygame.mouse.get_pos(), 40, (40, 40, 40), -1)

    cv2.putText(vp.canvas, "This is a demo", (vp.center_in[0] - 150, vp.center_in[1]), cv2.FONT_HERSHEY_PLAIN, 3,
                (200, 0, 0), 1)

    for child in vp.children:
        if isinstance(child, Frame):
            for i, node1 in enumerate(child.children):
                    for j, node2 in enumerate(child.children):
                        if node1 is node2: continue

                        # if edges[i][j] == 0: continue

                        colour = None
                        if 1 in (edges[i][j], edges[j][i]): colour = (250, 250, 250)
                        elif 2 in (edges[i][j], edges[j][i]): colour = (200, 200, 200)
                        elif 3 in (edges[i][j], edges[j][i]): colour = (150, 150, 150)
                        elif 4 in (edges[i][j], edges[j][i]): colour = (100, 100, 100)
                        elif 5 in (edges[i][j], edges[j][i]): colour = (50, 50, 50)
                        else: continue

                        node1.render_line_to(node2, colour)

    vp.render_recursive()


def main():
    print("viewport")
    viewport = ViewportManager(500, 500, fps=30)
    viewport.set_render_routine(render_routine)
    mouse = Mouse()
    mouse.bind_to_viewport(viewport)  # or alt: viewport.bindmouse(mouse)

    viewport.bind(pygame.MOUSEBUTTONDOWN, mouse.set_down)
    viewport.bind(pygame.MOUSEBUTTONUP, mouse.set_up)

    f1 = Frame(viewport, (0, 0), viewport.dimensions, (0, 0, 0), transparent=True)


    for i in range(5):
        print("btn", i)
        btn2 = CircularButton(f1, (100, 100), 15, (200, 200, 0), clip_to_parent=True, runnable=None)
        def btn2_func(btn, btn_num):
            global focused_node, focused_node_num, edges_base, edges
            mouse.drag(btn)
            if focused_node:
                focused_node.colour = (200, 200, 0)
            focused_node = btn
            # focused_node_num = btn_num
            btn.colour = (200, 0, 200)

            edges = edges_base.copy()
            for j in range(len(edges)):
                edges[j] *= abs(btn_num - j) + 1

        btn2.set_command(lambda btn=btn2, _i=i: btn2_func(btn, _i))
        btn2.bind_to(mouse)

    print(viewport)

    viewport.mainloop()


if __name__=="__main__":
    main()
