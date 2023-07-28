import sys
import itertools
from collections import defaultdict

from panda3d.core import NodePath
from panda3d.core import GeomVertexReader
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.core import LineSegs
from panda3d.core import CollisionTraverser
from panda3d.core import CollisionNode
from panda3d.core import CollisionRay
from panda3d.core import CollisionHandlerQueue
from panda3d.core import LineSegs

from direct.showbase.ShowBase import ShowBase

from pychology.search import TranspositionTable
#from pychology.search import FullExpansion
from pychology.search import PriorityLimitedExpansion
#from pychology.search import SingleNodeBreadthSearch
from pychology.search import PriorityExpansionQueue
#from pychology.search import AllCombinations
from pychology.search import Portfolio
from pychology.search import ZeroSumPlayer
from pychology.search import GameBasedEvaluation
from pychology.search import Minimax
#from pychology.search import BestMovePlayer
from pychology.search import BestPaths
from pychology.search import TTAnalysis
from pychology.search import Debug
from pychology.search import Search


def round_vec3_to_tuple(vec):
    return tuple([round(x*4.0)/4.0 for x in vec])

# Most make_nav_graph is written by Wezu as part of its pathfinding script
# in turn based on sample code from http://www.redblobgames.com/pathfinding/)
# Copyright 2014 Red Blob Games <redblobgames@gmail.com>
# License: Apache v2.0 <http://www.apache.org/licenses/LICENSE-2.0.html>
def make_nav_graph(mesh, edge_neighbors_only=True):
    def find_first_geom(mesh):
        for child in mesh.getChildren():
            node=child.node()
            if node.isGeomNode():
                return node.getGeom(0)

    def _get_center(vertex):
        return Vec3(
            (vertex[0][0]+vertex[1][0]+vertex[2][0])/3.0,
            (vertex[0][1]+vertex[1][1]+vertex[2][1])/3.0,
            (vertex[0][2]+vertex[1][2]+vertex[2][2])/3.0
        )

    def _get_neighbors(vertex, vert_dict, triangle_id, edge_only=True):
        common=set()
        if edge_only:
            for pair in itertools.combinations(vertex, 2):
                common=common | vert_dict[pair[0]] & vert_dict[pair[1]]
        else:
            for vert_id in vertex:
                common=common | vert_dict[vert_id]
        common=common-{triangle_id}
        return list(common)

    def _distance(start, end):
        v=end-start
        return v.length()

    #make a list of the triangles
    #get the id of each vert in each triangle and
    #get the position of each vert
    triangles=[]
    vert_dict=defaultdict(set)
    #only works ok with one geom so flatten the mesh befor comming here
    geom=find_first_geom(mesh)
    vdata = geom.getVertexData()
    vertex = GeomVertexReader(vdata, 'vertex')
    for prim in geom.getPrimitives():
        num_primitives=prim.getNumPrimitives()
        for p in range(num_primitives):
            #print ('primitive {} of {}'.format(p, num_primitives))
            s = prim.getPrimitiveStart(p)
            e = prim.getPrimitiveEnd(p)
            triangle={'vertex_id':[], 'vertex_pos':[]}
            for i in range(s, e):
                vi = prim.getVertex(i)
                vertex.setRow(vi)
                v =[round(i, 4) for i in vertex.getData3f() ]
                vertex_id=tuple([round(i*4.0)/4.0 for i in v])
                triangle['vertex_pos'].append(v)
                triangle['vertex_id'].append(vertex_id)
                vert_dict[vertex_id].add(len(triangles))
            triangles.append(triangle)

    #get centers and neighbors
    for i, triangle in enumerate(triangles):
        triangle['center']=_get_center(triangle['vertex_pos'])
        triangle['neighbors']=_get_neighbors(triangle['vertex_id'], vert_dict, i, edge_neighbors_only)
    #construct the dict
    edges={}
    cost={}
    positions={}
    for i, triangle in enumerate(triangles):
        #print ('neighbor ', i)
        edges[i]=triangle['neighbors']
        cost[i]={}
        start=triangle['center']
        positions[i]=start
        for neighbor in triangle['neighbors']:
            cost[i][neighbor]=_distance(start, triangles[neighbor]['center'])
    lookup={round_vec3_to_tuple(value):key for (key, value) in positions.items()}
    graph= {'neighbors':edges, 'cost':cost, 'pos':positions, 'lookup':lookup}
    return graph

def find_nearest_node(nav_graph, pos):
    pos=round_vec3_to_tuple(pos)
    if pos in nav_graph['lookup']:
        return nav_graph['lookup'][pos]
    dist={0.0}
    for i in range(50):
        dist.add(i*0.25)
        dist.add(i*-0.25)
        for x in itertools.permutations(dist, 3):
            key=(pos[0]+x[0], pos[1]+x[1], pos[2]+x[2])
            if key in nav_graph['lookup']:
                print(nav_graph['lookup'][key])
                return nav_graph['lookup'][key]
    return None

def load_map(name):
    level = loader.load_model(name)
    navmesh = level.find("**/navmesh")
    navmesh.detach_node()
    return level, navmesh



def make_players(p):
    def players():
        return [p]
    return players


def make_outcomes(p):
    def outcomes():
        return {p: 'player'}
    return outcomes


def make_initial_state(from_id):
    def initial_state():
        return [from_id]
    return initial_state


def make_game_winner(to_id, p):
    def game_winner(state):
        if state[-1] == to_id:
            return p
    return game_winner


def make_legal_moves(nav_graph, p):
    def legal_moves(state):
        pos = state[-1]
        return {p: nav_graph['neighbors'][pos]}
    return legal_moves


def make_make_move(p):
    def make_move(state, moves):
        move = moves[p]
        return state + [move]
    return make_move


# Tooling
def hash_state(state):
    return tuple(state)


# Expert knowledge
def path_value(state, nav_graph, to_id):
    # Accumulated path cost
    # FIXME: This is how it works with py>=3.10
    # costs = [nav_graph['cost'][a][b]
    #          for a, b in itertools.pairwise(state)]
    costs = []
    for idx in range(len(state) - 1):
        a = state[idx]
        b = state[idx + 1]
        costs.append(nav_graph['cost'][a][b])

    # Euclidean heuristic cost
    current_pos = nav_graph['pos'][state[-1]]
    target_pos = nav_graph['pos'][to_id]
    dist = (target_pos - current_pos).length()
    return -(sum(costs) + dist)


def make_state_value(p, nav_graph, to_id):
    def state_value(state):
        return {p: path_value(state, nav_graph, to_id)}
    return state_value


def make_state_priority(nav_graph, to_id):
    def state_priority(state):
        return path_value(state, nav_graph, to_id)
    return state_priority


def make_non_cyclic_walker(p):
    def non_cyclic_walker(state, moves):
        filtered_moves = [target
                          for target in moves[p]
                          if target not in state]
        return filtered_moves
        #return {p: filtered_moves}
    return non_cyclic_walker


PLAYER = 1

def make_game(nav_graph, from_id, to_id):
    #import pdb; pdb.set_trace()
    class Game:
        players = make_players(PLAYER)
        outcomes = make_outcomes(PLAYER)
        initial_state = make_initial_state(from_id)
        game_winner = make_game_winner(to_id, PLAYER)
        legal_moves = make_legal_moves(nav_graph, PLAYER)
        make_move = make_make_move(PLAYER)
        hash_state = hash_state
        evaluation_funcs = {
            'euclidean': make_state_value(PLAYER, nav_graph, to_id),
        }
        prioritization_funcs = {
            'euclidean': make_state_priority(nav_graph, to_id),
        }
        portfolios = {'ncw': make_non_cyclic_walker(PLAYER)}
        PLAYER = PLAYER
    return Game


if __name__ == '__main__':
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
    def make_transition_grid(id_paths):
        # Find all edges that need to be marked as belonging to a path
        path_edges = set()
        for path in id_paths:
            for idx in range(len(path)-1):
                path_edges.add(tuple(sorted([path[idx], path[idx+1]])))
                
        # Draw the grid
        transition_grid = LineSegs()
        already_drawn_pairs = set()
        for from_id in nav_graph['neighbors'].keys():
            from_pos = nav_graph['pos'][from_id]
            for to_id in nav_graph['neighbors'][from_id]:
                # Do we already know this couple?
                pair_id = tuple(sorted([from_id, to_id]))
                if pair_id in already_drawn_pairs:
                    continue
                already_drawn_pairs.add(pair_id)  # We do now.
                # Is it on a path?
                transition_grid.set_color(1,1,1)
                if pair_id in path_edges:
                    transition_grid.set_color(0,1,0)
                # Let's draw it already.
                to_pos = nav_graph['pos'][to_id]
                transition_grid.move_to(from_pos + Vec3(0, 0, 0.1))
                transition_grid.draw_to(to_pos + Vec3(0, 0, 0.1))
        np = NodePath(transition_grid.create())
        return np

    global debug_edges
    debug_edges = make_transition_grid([[]])
    debug_edges.reparent_to(level)
    

    class LabyrinthSearch(
            TranspositionTable,
            PriorityLimitedExpansion,
            PriorityExpansionQueue,
            #AllCombinations,
            Portfolio,
            ZeroSumPlayer,
            GameBasedEvaluation,
            Minimax,
            #BestMovePlayer,
            BestPaths,
            #TTAnalysis,
            Search,
    ):
        portfolio = 'ncw'
        evaluation_function = 'euclidean'
        prioritization_function = 'euclidean'

    from_node = loader.load_model('models/frowney')
    from_node.set_scale(3)
    to_node = loader.load_model('models/frowney')
    to_node.set_scale(3)

    def run_path(from_id, to_id):
        #import pdb; pdb.set_trace()
        from_node.reparent_to(debug_nav_nodes[from_id])
        to_node.reparent_to(debug_nav_nodes[to_id])
        print(f"Searching path from {from_id} to {to_id}")
        game_cls = make_game(nav_graph, from_id, to_id)
        search = LabyrinthSearch(
                game_cls,
                game_cls.initial_state(),
                game_cls.PLAYER,
        )
        paths = search.run()
        print(f"Found {len(paths)} paths from {from_id} to {to_id}.")
        #id_paths = [[state[-1] for state in path] for path in paths]
        for path in paths:
            print(path)
        global debug_edges
        debug_edges.remove_node()
        debug_edges = make_transition_grid(paths)
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
    base.run()
