import sys
import logging
from argparse import ArgumentParser

from panda3d.core import Vec3
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionNode
from panda3d.core import CollisionRay
from panda3d.core import CollisionHandlerQueue

from direct.showbase.ShowBase import ShowBase

from pychology.simple_search.a_star import search
from pychology.simple_search.a_star import get_neighbors_and_costs

from navgraph import make_nav_graph
from navgraph import make_transition_grid
from navgraph import find_nearest_node


def load_map(name):
    level = loader.load_model(name)
    navmesh = level.find("**/navmesh")
    navmesh.detach_node()
    return level, navmesh


if __name__ == '__main__':
    parser = ArgumentParser(
        description="Test application for pathfinding and navmesh.",
        epilog="",
    )
    parser.add_argument(
        '-log',
        '--loglevel',
        default='warning',
        help='Set logging level; debug, info, warning, error, or critical.',
    )
    args = parser.parse_args()
    logging.basicConfig(level=args.loglevel.upper())

    logging.info("Initializing ShowBase.")

    ShowBase()
    base.cTrav = CollisionTraverser()
    base.accept('escape', sys.exit)
    base.cam.set_pos(Vec3(1, -1, 2) * 30)
    base.cam.look_at(0, 0, 0)

    level, navmesh = load_map("navmesh_test.bam")
    level.reparent_to(base.render)
    nav_graph = make_nav_graph(navmesh)
    navmesh.reparent_to(level)
    navmesh.hide()
    navmesh.set_collide_mask(1)

    # Navmesh visualization
    debug_nav_nodes = {}
    for idx, pos in enumerate(nav_graph['pos'].values()):
            m = base.loader.load_model('models/smiley')
            m.reparent_to(level)
            m.set_pos(pos)
            m.set_scale(0.2)
            debug_nav_nodes[idx] = m

    global debug_edges
    debug_edges = make_transition_grid(nav_graph, [[]])
    debug_edges.reparent_to(level)
    
    from_node = loader.load_model('models/frowney')
    from_node.set_scale(3)
    to_node = loader.load_model('models/frowney')
    to_node.set_scale(3)

    def run_path(from_id, to_id):
        # Visualize start and end
        from_node.reparent_to(debug_nav_nodes[from_id])
        to_node.reparent_to(debug_nav_nodes[to_id])

        # The actual search
        logging.info(f"Searching path from {from_id} to {to_id}.")
        adjacency_matrix = {
            node: {
                neighbor: nav_graph['cost'][node][neighbor]
                for neighbor in neighbors
            }
            for node, neighbors in nav_graph['neighbors'].items()
        }
        def estimator(node_a, node_b):
            pos_a = nav_graph['pos'][node_a]
            pos_b = nav_graph['pos'][node_b]
            return (pos_a - pos_b).length()

        cost, path = search(get_neighbors_and_costs(adjacency_matrix), estimator, from_id, to_id)
        print(path)

        # Visualize path
        global debug_edges
        debug_edges.remove_node()
        debug_edges = make_transition_grid(nav_graph, path)
        debug_edges.reparent_to(level)

    class Picker:
        def __init__(self):
            self.node = CollisionNode('mouseRay')
            self.path = base.cam.attach_new_node(self.node)
            self.node.set_from_collide_mask(1)
            self.ray = CollisionRay()
            self.node.add_solid(self.ray)
            self.handler = CollisionHandlerQueue()
            base.cTrav.add_collider(self.path, self.handler)
            self.from_picked = None
            self.to_picked = None
            self.model = base.loader.load_model("models/jack").copy_to(render)
            self.model.set_scale(0.5)
            base.accept("mouse1", self.pick)

        def set_next(self, node):
            if not self.from_picked:
                self.from_picked = node
            elif not self.to_picked:
                self.to_picked = node
                run_path(self.from_picked, self.to_picked)
                self.from_picked = self.to_picked = None

        def pick(self):
            if base.mouseWatcherNode.has_mouse():
                mpos = base.mouseWatcherNode.get_mouse()
                self.ray.set_from_lens(base.camNode, mpos.get_x(), mpos.get_y())
                base.cTrav.traverse(render)
                if self.handler.get_num_entries() > 0:
                    self.handler.sort_entries()
                    pos = self.handler.get_entry(0).get_surface_point(render)
                    self.model.set_pos(pos)
                    if base.mouseWatcherNode.is_button_down("mouse1"):
                        self.set_next(find_nearest_node(nav_graph, pos))

    Picker()
    run_path(93, 27)
    base.run()
