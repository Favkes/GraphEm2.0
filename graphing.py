import cv2

from button import CircularButton
from viewport import ViewportManager
from widgets import *
import numpy as np
import random
from multipledispatch import dispatch
from mouse import MouseEvent
import uuid


ColourTuple = tuple[int,int,int]


def random_coords_within_range(_from: tuple[int,int],
                               to: tuple[int,int],
                               margin:float = 0.0) -> tuple[int,int]|None:
    if margin < 0 or 0.5 <= margin:
        print(f"Invalid margin value: {margin}. Must fit within [0; 0.5).")
        return None

    _x = _from[0]
    _X = to[0]
    _y = _from[1]
    _Y = to[1]

    dx = _X - _x
    dy = _Y - _y

    mx = round(dx * margin)
    my = round(dy * margin)

    x = random.randint(_x + mx, _X - mx)
    y = random.randint(_y + my, _Y - my)

    return x, y


class Node:
    button_ref: CircularButton
    uuid: uuid.UUID
    identifier: int
    label: str|None

    main_colour: ColourTuple
    current_colour: ColourTuple

    def __init__(self,
                 parent:Widget,
                 identifier:int,
                 label:str = None,
                 colour:ColourTuple = (200, 200, 200)):
        self.uuid = uuid.uuid4()
        self.identifier = identifier
        self.label = label
        self.main_colour = colour
        self.current_colour = colour

        pos = random_coords_within_range((0, 0), parent.dimensions, 0.1)
        node_instance = CircularButton(parent, pos, 15, colour)
        node_instance.bind_to(MouseEvent.DRAG_START)

        def node_core_func(node_uuid: uuid.UUID, node_btn: CircularButton):
            parent.root.getmouse().drag(node_btn)
            GraphVisualHandler.get().focus_node(self)
        node_instance.set_command(
            lambda node_uuid=self.uuid,
                   instance=node_instance:
            node_core_func(node_uuid, instance)
        )  # lambda wrapper required for correct instancing

        self.button_ref = node_instance


    def render_line_to(self, other:"Node", colour:ColourTuple = None):
        if colour is None: colour = self.button_ref.colour
        self.button_ref.render_line_to(other.button_ref, colour)


    def _update_button_ref_colour(self):
        self.button_ref.colour = self.current_colour
    def set_main_colour(self, colour:ColourTuple):
        self.main_colour = colour
    def set_colour(self, colour:ColourTuple):
        self.current_colour = colour
        self._update_button_ref_colour()
    def reset_colour(self):
        self.current_colour = self.main_colour
        self._update_button_ref_colour()


    def __repr__(self):
        out = f"Node[{self.uuid}](id={self.identifier}, label='{self.label}')"
        return out


class NodePool:
    _list: list[Node]
    _map: dict[str, Node]
    _uuid_map: dict[uuid.UUID, Node]

    def __init__(self):
        self._list = []
        self._map = dict()
        self._uuid_map = dict()

    def node_of_id(self, _id:int) -> Node|None:
        if len(self._list) <= _id:
            print(f"[ERR] (NodePool): Node index {_id} out of bounds for pool of size {len(self._list)}.")
            return None

        return self._list[_id]

    def node_of_label(self, label:str) -> Node|None:
        out = self._map.get(label, None)
        if out is None:
            print(f"[ERR] (NodePool): Node label {label} does not exist in the pool.")
        return out

    def node_of_uuid(self, uuid:uuid.UUID) -> Node|None:
        out = self._uuid_map.get(uuid, None)
        if out is None:
            print(f"[ERR] (NodePool): Nodel uuid {uuid} does not exist in the pool.")
        return out

    def append(self, new:Node) -> None:
        self._list.append(new)
        self._map[new.label] = new
        self._uuid_map[new.uuid] = new


    def clear(self):
        self._list = []
        self._map = dict()
        self._uuid_map = dict()

    @property
    def arr(self):
        return self._list
    @arr.setter
    def arr(self, new:list[Node]):
        self._list = new

    @property
    def map(self):
        return self._map
    @map.setter
    def map(self, new:dict[str,Node]):
        self._map = new

    def __len__(self):
        return len(self._list)
    def __repr__(self):
        out = f"NodePool({self._list})"
        return out
    def __iter__(self):
        return iter(self._list)
    def __getitem__(self, item:int):
        return self._list[item]


class Edge:
    start: Node
    end: Node

    identifier: int
    label: str | None

    main_colour: ColourTuple
    current_colour: ColourTuple

    def __init__(self,
                 node1:Node,
                 node2:Node,
                 label:str = None,
                 _id:int = None,
                 colour:ColourTuple = (200, 200, 200)):
        self.start = node1
        self.end = node2
        self.label = label
        self.identifier = _id
        self.main_colour = colour
        self.current_colour = colour

    def render(self, colour:ColourTuple = None):
        if colour is None: colour = self.current_colour
        self.start.render_line_to(self.end, colour)


    def set_main_colour(self, colour:ColourTuple):
        self.main_colour = colour
    def set_colour(self, colour:ColourTuple):
        self.current_colour = colour
    def reset_colour(self):
        self.current_colour = self.main_colour


    def __repr__(self):
        out = f"Edge(id={self.identifier}, label='{self.label}')"
        return out


class EdgePool:
    _list: list[Edge]
    _map: dict[str, Edge]

    def __init__(self):
        self._list = []
        self._map = dict()

    def edge_of_id(self, _id:int) -> Edge|None:
        if len(self._list) <= _id:
            print(f"[ERR] (EdgePool): Edge index {_id} out of bounds for pool of size {len(self._list)}.")
            return None

        return self._list[_id]

    def edge_of_label(self, label:str) -> Edge|None:
        out = self._map.get(label, None)
        if out is None:
            print(f"[ERR] (EdgePool): Edge label {label} does not exist in the pool.")
        return out

    def append(self, new:Edge) -> None:
        self._list.append(new)
        self._map[new.label] = new


    def clear(self):
        self._list = []
        self._map = dict()

    @property
    def arr(self):
        return self._list
    @arr.setter
    def arr(self, new:list[Edge]):
        self._list = new

    @property
    def map(self):
        return self._map
    @map.setter
    def map(self, new:dict[str,Edge]):
        self._map = new

    def __len__(self):
        return len(self._list)
    def __repr__(self):
        out = f"NodePool({self._list})"
        return out
    def __iter__(self):
        return iter(self._list)
    def __getitem__(self, item:int):
        return self._list[item]


class GraphVisualHandler:
    _instance = None
    _initialized:bool

    def __new__(cls, vp: ViewportManager|None = None):
        if cls._instance is None:
            if vp is None:
                raise RuntimeError("[ERR] (GVH): GraphVisualHandler has not been initialized yet.")

            cls._instance = super().__new__(cls)
            cls._instance._initialized = False

        return cls._instance

    @classmethod
    def get(cls) -> "GraphVisualHandler":
        if cls._instance is None:
            raise RuntimeError("[ERR] (GVH): GraphVisualHandler has not been initialized yet.")
        return cls._instance

    vp: ViewportManager
    nodes_container: Widget|None

    nodes: NodePool
    edges: EdgePool

    node_highlight_col: ColourTuple
    edge_highlight_col: ColourTuple

    focused_node_ref: Node|None
    focused_edge_ref: Edge|None

    def __init__(self, vp:ViewportManager|None = None):
        if self._initialized:
            return

        if vp is None:
            raise RuntimeError("[ERR] (GVH): GraphVisualHandler must be initialized with vp first.")

        self.vp = vp
        self.nodes_container = None
        self.nodes = NodePool()
        self.edges = EdgePool()
        self.node_highlight_col = (200, 0, 200)
        self.edge_highlight_col = (200, 0, 200)
        self.focused_node_ref = None
        self.focused_edge_ref = None

        self._initialized = True

    # Main structure loader
    def load_graph(self,
                   adj_mat: np.ndarray,
                   node_label_arr:list[str]|None = None,
                   edge_label_arr:list[str]|None = None):
        if isinstance(adj_mat.shape, int):
            print(f"Invalid adjacency matrix given; must be 2D!")
            return
        if len(adj_mat.shape) != 2 or adj_mat.shape[0] != adj_mat.shape[1]:
            print(f"Invalid adjacency matrix with shape {adj_mat.shape} given (must be square!).")
            return
        v = adj_mat.shape[0]
        e = np.count_nonzero(adj_mat)
        print(f"Loading graph of v={v}, e={e} ...")

        edges_list = np.argwhere(adj_mat != 0)

        graph_frame = Frame(self.vp, self.vp.pos, self.vp.dimensions, transparent=True)
        self.nodes.clear()
        self.generate_nodes(v, graph_frame, node_label_arr)
        self.edges.clear()
        self.generate_edges(edges_list, edge_label_arr)

    # Node generator
    def generate_nodes(self, n_nodes:int, nodes_container:Widget = None, labels:list[str]|str = None):
        if nodes_container is None:
            nodes_container = self.vp
        self.nodes_container = nodes_container

        if isinstance(labels, str):
            labels = [labels] * n_nodes

        if labels:
            for v_i in range(n_nodes):
                node_instance = Node(nodes_container, v_i, labels[v_i], colour=(20, 100, 150))
                self.nodes.append(node_instance)
        else:
            for v_i in range(n_nodes):
                node_instance = Node(nodes_container, v_i, colour=(20, 100, 150))
                self.nodes.append(node_instance)

    # Edge generator
    def generate_edges(self, edges_list:list[tuple[int,int]]|np.ndarray, labels:list[str]|str = None):
        if isinstance(labels, str):
            labels = [labels] * len(edges_list)
        if labels:
            for e_i, (i1, i2) in enumerate(edges_list):
                node1 = self.nodes.node_of_id(i1)
                node2 = self.nodes.node_of_id(i2)
                if e_i < len(labels):
                    label = labels[e_i]
                else:
                    label = None
                edge_instance = Edge(node1, node2, label=label, _id=e_i)
                self.edges.append(edge_instance)
        else:
            for e_i, (i1, i2) in enumerate(edges_list):
                node1 = self.nodes.node_of_id(i1)
                node2 = self.nodes.node_of_id(i2)
                edge_instance = Edge(node1, node2, _id=e_i)
                self.edges.append(edge_instance)

    def add_node(self, label:str = None):
        self.nodes.append(
            Node(self.nodes_container, len(self.nodes), label, (20, 100, 150))
        )
    def add_edge(self, from_node:Node, to_node:Node, label:str = None):
        self.edges.append(
            Edge(from_node, to_node, label)
        )

    # Node focusers
    @dispatch(Node)
    def focus_node(self, instance_ref:Node):
        if self.focused_node_ref == instance_ref:
            # print("Already focused on this node.")
            return
        self.focused_node_ref = instance_ref
    @dispatch(int)
    def focus_node(self, instance_id:int):
        self.focus_node(self.nodes.node_of_id(instance_id))
    @dispatch(str)
    def focus_node(self, instance_label:str):
        self.focus_node(self.nodes.node_of_label(instance_label))

    # Edge focusers
    @dispatch(Edge)
    def focus_edge(self, instance_ref: Edge):
        if self.focused_edge_ref == instance_ref:
            # print("Already focused on this edge.")
            return
        self.focused_edge_ref = instance_ref
    @dispatch(int)
    def focus_edge(self, instance_id: int):
        self.focus_edge(self.edges.edge_of_id(instance_id))
    @dispatch(str)
    def focus_edge(self, instance_label: str):
        self.focus_edge(self.edges.edge_of_label(instance_label))

    # Defocusers
    def defocus_node(self):
        self.focused_node_ref = None
    def defocus_edge(self):
        self.focused_edge_ref = None

    # Highlight mode colour setters
    def set_node_highlight_col(self, colour:ColourTuple):
        self.node_highlight_col = colour
    def set_edge_highlight_col(self, colour:ColourTuple):
        self.edge_highlight_col = colour

    # Node highlight logic
    def highlight_node_focused(self):
        if self.focused_node_ref:
            self.highlight_node(self.focused_node_ref)

    @dispatch(Node)
    def highlight_node(self, node_ref: Node, colour: ColourTuple = None):
        if colour is None:
            colour = self.node_highlight_col
        node_ref.set_colour(colour)

    @dispatch(int)
    def highlight_node(self, node_i: int, colour:ColourTuple = None):
        if len(self.nodes) <= node_i:
            print(f"[ERR] (GVH): Index {node_i} out of bounds for self.nodes of len={len(self.nodes)}.")
            return
        if colour is None:
            colour = self.node_highlight_col
        self.nodes.node_of_id(node_i).set_colour(colour)

    @dispatch(str)
    def highlight_node(self, node_i: str, colour: ColourTuple = None):
        if colour is None:
            colour = self.node_highlight_col
        self.nodes.node_of_label(node_i).set_colour(colour)

    def clear_focused_node_highlight(self):
        if self.focused_node_ref:
            self.focused_node_ref.reset_colour()

    # Edge highlight logic
    def highlight_edge_focused(self):
        if self.focused_edge_ref:
            self.highlight_edge(self.focused_edge_ref)

    @dispatch(Edge)
    def highlight_edge(self, edge_ref: Edge, colour: ColourTuple = None):
        if colour is None:
            colour = self.edge_highlight_col
        edge_ref.set_colour(colour)

    @dispatch(int)
    def highlight_edge(self, edge_i: int, colour:ColourTuple = None):
        if len(self.edges) <= edge_i:
            print(f"[ERR] (GVH): Index {edge_i} out of bounds for self.edge of len={len(self.edges)}.")
            return
        if colour is None:
            colour = self.edge_highlight_col
        self.edges.edge_of_id(edge_i).set_colour(colour)

    @dispatch(str)
    def highlight_edge(self, edge_i: str, colour: ColourTuple = None):
        if colour is None:
            colour = self.edge_highlight_col
        self.edges.edge_of_label(edge_i).set_colour(colour)

    def clear_focused_edge_highlight(self):
        if self.focused_edge_ref:
            self.focused_edge_ref.reset_colour()



if __name__=="__main__":
    def render_routine(vp: ViewportManager):
        # print(vp.getmouse())
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

        gvh = GraphVisualHandler.get()
        gvh.highlight_edge_focused()
        gvh.highlight_node_focused()
        # gvh.edges.edge_of_id(1).set_colour((200, 150, 20))

        for edge in gvh.edges.arr:
            edge.render()

        for node in gvh.nodes.arr:
            node.button_ref.render()

        # vp.render_recursive()
        gvh.clear_focused_node_highlight()
        gvh.clear_focused_edge_highlight()

        for i, node in enumerate(gvh.nodes.arr):
            colour = (200, 200, 200)
            label = node.label
            (text_w, text_h), baseline = cv2.getTextSize(label, cv2.FONT_HERSHEY_PLAIN, 1, 1)
            tx, ty = node.button_ref.center_out
            text_coords = (
                tx - text_w//2,
                ty + text_h//2
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

    graph_matrix: np.ndarray | None = np.array((
        (0, 1, 1, 0, 0),
        (0, 0, 1, 1, 1),
        (0, 0, 0, 1, 0),
        (0, 0, 0, 0, 1),
        (0, 0, 0, 0, 0),
    ))
    vp = ViewportManager(500, 500)

    vp.bindmouse(Mouse(50))
    vp.bind(pygame.MOUSEBUTTONDOWN, vp.getmouse().set_down)
    vp.bind(pygame.MOUSEBUTTONUP, vp.getmouse().set_up)

    vp.set_render_routine(render_routine)
    gvh = GraphVisualHandler(vp)
    gvh.set_node_highlight_col((200, 150, 20))
    gvh.set_edge_highlight_col((200, 150, 20))

    gvh.load_graph(
        graph_matrix,
        ["Poznan", "Warszawa", "Lodz", "Krakow", "Wroclaw"],
        ["A1", "A2", "A3", "A4"]
    )
    print(gvh.nodes)
    gvh.focus_edge(2)


    vp.mainloop()
