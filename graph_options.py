import numpy as np
# from PIL import Image, ImageTk
import pygame
import cv2


class Window:
    width: int
    height: int
    fps: int
    dimensions: tuple[int, int]

    def __init__(self, width, height, fps = 30):
        self.width = width
        self.height = height
        self.fps = fps
        self.dimensions = (width, height)

window = Window(500, 500)


class GraphRenderer:
    def __init__(self):
        ...

    def render_node(self, node):
        ...

    def render_edge(self, edge):
        ...


class Graph1:
    order: int
    nodes: list
    edges: list[tuple[int, int]]

    def __init__(self, nodes: list, edges: list[tuple[int, int]]):
        self.nodes = nodes
        self.edges = edges
        self.order = len(nodes)

class Graph2:
    order: int
    nodes: list[str|int]
    edges: list[tuple[str|int, str|int]]

    def __init__(self, nodes: list[str|int], edges: list[tuple[str|int, str|int]]):
        self.nodes = nodes
        self.edges = edges
        self.order = len(nodes)

class Graph3:
    order: int
    edges: list[tuple[int, int]]

    def __init__(self, edges: list[tuple[int, int]], order: int = None):
        self.edges = edges
        self.order = order
        if not order:
            self.order = max(sum(self.edges, ()))

class Graph4:
    order: int
    adj_matrix: list[list[int,]]

    def __init__(self, adj_matrix: list[list[int,]]):
        self.adj_matrix = adj_matrix
        self.order = len(adj_matrix)


if __name__=="__main__":
    Graph1(
        ["A", "B", "C"],
        [
            (0, 1), (1, 1), (2, 0)
        ]
    )

    Graph2(
        ["A", "B", "C"],
        [
            ("A", "B"), ("B", "B"), ("C", "A")
        ]
    )

    Graph3(
        [
            (0, 1), (1, 1), (2, 0)
        ]
    )

    Graph4(
        [
            [0, 1, 0],
            [0, 1, 0],
            [1, 0, 0]
        ]
    )

    pygame.init()
    screen = pygame.display.set_mode(window.dimensions)
    pygame.display.set_caption("Numpy renderer in pygame")
    clock = pygame.time.Clock()

    canvas = np.zeros(window.dimensions + (3,), dtype=np.uint8)



    running = True
    while running:
        mouse_pos = pygame.mouse.get_pos()

        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            elif event.type == pygame.MOUSEBUTTONDOWN:
                x, y = event.pos

        # draw_numpy_scene(canvas, mouse_pos)

        # surface = numpy_to_surface(canvas)
        # screen.blit(surface, (0,0))
        # pygame.display.flip()
        clock.tick(window.fps)
    pygame.quit()


