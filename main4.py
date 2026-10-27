# import cv2
from viewport import ViewportManager
from widgets import *
from graphing import GraphVisualHandler
from button import *
from mouse import MouseEvent
import events
import threading


def render_routine(vp: ViewportManager):
    vp.canvas[:] = (25, 25, 25)
    cv2.circle(vp.canvas, pygame.mouse.get_pos(), 40, (40, 40, 40), -1)

    cv2.putText(vp.canvas, "Graphing", (vp.center_in[0] - 150, vp.center_in[1]), cv2.FONT_HERSHEY_PLAIN, 3,
                (200, 0, 0), 1)

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



class GUI:
    vp: ViewportManager
    _contentsmap: dict[str,Widget]

    def __init__(self, vp):
        self.vp = vp
        self._contentsmap = dict()

    def add_widget(self, widget:Widget, tag:str):
        self._contentsmap[tag] = widget

    def del_widget(self, tag:str):
        del self._contentsmap[tag]

    def get_widget(self, tag:str):
        return self._contentsmap[tag]


def build_gui(vp: ViewportManager):
    print("[INF] (init): Building gui")
    btn1pos = (
        vp.center_in[0] - 50//2,
        vp.dimensions[1] - 50 - 10
    )
    btn1 = BaseButton(vp, btn1pos, (50, 50), (200, 100, 0), two_state=False)

    @btn1.hitbox_bound
    def btn1_func():
        btn1.set_colour((0, 20, 100))
        code_step_signal.set()
        events.EventScheduler.get().add(
            events.TimedEvent(0.1, btn1.reset_colour),
            "btn1.click",
            replace=False
        )
    btn1.bind(MouseEvent.CLICK, btn1_func)

    def make_hover_handler(btn: BaseButton):
        first_run = True
        original_colour: ColourTuple|None = None

        @btn1.hitbox_bound
        def on_hover():
            nonlocal first_run, original_colour

            if first_run:
                original_colour = btn.get_main_colour()
                btn.set_main_colour((100, 20, 100))
                btn.reset_colour()
                first_run = False

            def after_hover():
                nonlocal first_run, original_colour

                btn1.set_main_colour(original_colour)
                btn1.reset_colour()
                first_run = True

            events.EventScheduler.get().add(
                events.TimedEvent(0.1, on_finish=after_hover),
                "btn1.hover",
                replace=True
            )
        return on_hover
    btn1.bind(MouseEvent.HOVER, make_hover_handler(btn1))
    gui.add_widget(btn1, "btn1")



def load_data(gvh:GraphVisualHandler):
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


def user_code(gvh:GraphVisualHandler, gui:GUI):
    while True:
        for edge in gvh.edges:
            gvh.clear_focused_edge_highlight()
            gvh.focus_edge(edge)
            gvh.highlight_edge_focused()
            code_step_signal.wait()
            code_step_signal.clear()
            gvh.add_node("new node")
            gvh.add_edge(gvh.nodes[-1], gvh.nodes[-2])

        for node in gvh.nodes:
            gvh.clear_focused_node_highlight()
            gvh.focus_node(node)
            gvh.highlight_node_focused()
            code_step_signal.wait()
            code_step_signal.clear()


if __name__=="__main__":
    vp = ViewportManager(500, 500)

    vp.bindmouse(Mouse(70))
    vp.bind(pygame.MOUSEBUTTONDOWN, vp.getmouse().set_down)
    vp.bind(pygame.MOUSEBUTTONUP, vp.getmouse().set_up)

    gui = GUI(vp)
    code_step_signal = threading.Event()
    build_gui(vp)

    vp.set_render_routine(render_routine)
    gvh = GraphVisualHandler(vp)
    gvh.set_node_highlight_col((200, 150, 20))
    gvh.set_edge_highlight_col((200, 150, 20))


    load_data(gvh)

    threading.Thread(
        target=user_code,
        args=(gvh, gui),
        daemon=True
    ).start()

    vp.mainloop()