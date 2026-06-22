import numpy as np

from viewport import ViewportManager
from widgets import *
from button import *
import cv2
from collections import deque
from functools import lru_cache
from graphing import GraphVisualHandler


edges_base: np.ndarray|None = np.array((
    (0, 1, 1, 0, 0),
    (0, 0, 1, 1, 1),
    (0, 0, 0, 1, 0),
    (0, 0, 0, 0, 1),
    (0, 0, 0, 0, 0),
))


edges_base += np.transpose(edges_base)

edges_list = []
for col in range(edges_base.shape[0]):
    for row in range(edges_base.shape[1]):
        if edges_base[col, row] == 1:
            edges_list.append((col, row))
print(edges_list)


def weight_bfs(adj_mat: np.ndarray, start_node: int):
    if len(adj_mat.shape) != 2:
        return None

    n = adj_mat.shape[0]

    if adj_mat.shape[0] != adj_mat.shape[1]:
        return None

    if start_node < 0 or start_node >= n:
        return None

    visited = np.zeros(n, dtype=bool)
    dist = np.full(n, -1, dtype=int)

    weights_mat = np.zeros_like(adj_mat, dtype=int)

    q = deque()

    visited[start_node] = True
    dist[start_node] = 0
    q.append(start_node)

    while q:
        current = q.popleft()

        for i in range(n):
            if adj_mat[current, i] != 0:
                # To jest krawędź wychodząca z current.
                # Ważymy ją ZAWSZE, nawet jeśli i było już odwiedzone.
                weights_mat[current, i] = dist[current] + 1

                # Ale do kolejki wrzucamy tylko nieodwiedzone wierzchołki.
                if not visited[i]:
                    visited[i] = True
                    dist[i] = dist[current] + 1
                    q.append(i)

    return weights_mat

edges_weighted = weight_bfs(edges_base, 0)

edges: np.ndarray|None = edges_base.copy()

focused_edge: tuple[int,int]|None = None
focused_node: Button|CircularButton|None = None
focused_node_num: int|None = None


def weight_to_colour(weight: int):
    if weight == 1:
        return (250, 250, 250)
    elif weight == 2:
        return (200, 200, 200)
    elif weight == 3:
        return (150, 150, 150)
    elif weight == 4:
        return (100, 100, 100)
    elif weight == 5:
        return (50, 50, 50)
    else:
        return (200, 0, 0)  # edge exists, but BFS didnt reach it (directed graph)

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
                        if i == j: continue

                        # does the edge exist?:
                        if edges_base[i][j] == 0: continue

                        # if so:
                        weight = max(edges_weighted[i][j], edges_weighted[j][i])
                        colour: tuple[int,int,int] = weight_to_colour(weight)

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
            global focused_node, focused_node_num, edges_base, edges, edges_weighted
            mouse.drag(btn)
            if focused_node:
                focused_node.colour = (200, 200, 0)
            focused_node = btn
            # focused_node_num = btn_num
            btn.colour = (200, 0, 200)
            edges_weighted = weight_bfs(edges_base, btn_num)
            edges_weighted += np.transpose(edges_weighted)
            print(edges_weighted)

            edges = edges_base.copy()
            for j in range(len(edges)):
                edges[j] *= abs(btn_num - j) + 1

        btn2.set_command(lambda btn=btn2, _i=i: btn2_func(btn, _i))
        btn2.bind_to(mouse)

    print(viewport)

    viewport.mainloop()


if __name__=="__main__":
    main()
