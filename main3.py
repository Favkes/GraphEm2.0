import cv2
from viewport import ViewportManager
from widgets import *
from graphing import GraphVisualHandler
from button import *
from mouse import MouseEvent


def render_routine(vp: ViewportManager):
    vp.canvas[:] = (25, 25, 25)
    cv2.circle(vp.canvas, pygame.mouse.get_pos(), 40, (40, 40, 40), -1)

    cv2.putText(vp.canvas, "Graphing", (vp.center_in[0] - 150, vp.center_in[1]), cv2.FONT_HERSHEY_PLAIN, 3,
                (200, 0, 0), 1)

    # for child in vp.children:
    #     if isinstance(child, Frame):
    #         for i, node1 in enumerate(gvh.nodes.arr):
    #             for j, node2 in enumerate(gvh.nodes.arr):
    #                 if i == j: continue
    #
    #                 if edges_base[i, j] == 0: continue
    #
    #                 colour = (200, 200, 200)
    #                 label = node1.label
    #                 node1.render_line_to(node2, colour)
    #                 # cv2.putText(vp.canvas, label, node1.button_ref.center_out,
    #                 #             cv2.FONT_HERSHEY_PLAIN, 2,
    #                 #             (200, 0, 0), 1)

    gvh.highlight_edge_focused()
    gvh.highlight_node_focused()
    # gvh.edges.edge_of_id(1).set_colour((200, 150, 20))

    for edge in gvh.edges.arr:
        edge.render()

    # for node in gvh.nodes.arr:
    #     node.button_ref.render()
    vp.render_recursive()

    gvh.clear_focused_node_highlight()
    gvh.clear_focused_edge_highlight()

    for i, node in enumerate(gvh.nodes.arr):
        colour = (200, 200, 200)
        label = node.label
        (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1, 1)
        tx, ty = node.button_ref.center_out
        text_coords = (
            tx - text_w // 2,
            ty + text_h // 2
        )
        cv2.putText(vp.canvas, label, text_coords,
                    cv2.FONT_HERSHEY_PLAIN, 1,
                    colour, 1)

    for i, edge in enumerate(gvh.edges.arr):
        colour = (200, 200, 200)
        label = edge.label
        (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1, 1)
        tx = (edge.start.button_ref.center_out[0] + edge.end.button_ref.center_out[0]) // 2
        ty = (edge.start.button_ref.center_out[1] + edge.end.button_ref.center_out[1]) // 2
        text_coords = (
            tx - text_w // 2,
            ty + text_h // 2
        )
        cv2.putText(vp.canvas, label, text_coords,
                    cv2.FONT_HERSHEY_PLAIN, 1,
                    colour, 1)


def build_gui(vp: ViewportManager):
    btn1pos = (
        vp.center_in[0] - 50//2,
        vp.dimensions[1] - 50 - 10
    )
    btn1 = Button(vp, btn1pos, (50, 50), (200, 100, 0))
    def btn1_func():
        print("btn pressed!")
        btn1.colour = (0, 20, 100)
    btn1.set_command(btn1_func)
    btn1.bind_to(MouseEvent.CLICK)


if __name__=="__main__":
    vp = ViewportManager(500, 500)

    vp.bindmouse(Mouse(40))
    vp.bind(pygame.MOUSEBUTTONDOWN, vp.getmouse().set_down)
    vp.bind(pygame.MOUSEBUTTONUP, vp.getmouse().set_up)

    build_gui(vp)

    vp.set_render_routine(render_routine)
    gvh = GraphVisualHandler(vp)
    gvh.set_node_highlight_col((200, 150, 20))
    gvh.set_edge_highlight_col((200, 150, 20))


    graph_matrix: np.ndarray | None = np.array((
        (0, 1, 1, 0, 0),
        (0, 0, 1, 1, 1),
        (0, 0, 0, 1, 0),
        (0, 0, 0, 0, 1),
        (0, 0, 0, 0, 0),
    ))
    gvh.load_graph(
        graph_matrix,
        ["Poznan", "Warszawa", "Lodz", "Krakow", "Wroclaw"],
        ["A1", "A2", "A3", "A4"]
    )
    print(gvh.nodes)
    gvh.focus_edge(2)


    vp.mainloop()