from collections import defaultdict
import itertools

from panda3d.core import NodePath
from panda3d.core import GeomVertexReader
from panda3d.core import Vec3
from panda3d.core import Point3
from panda3d.core import LineSegs
from panda3d.core import LineSegs


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


def make_transition_grid(nav_graph, path):
    # Find all edges that need to be marked as belonging to a path
    path_edges = set()
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
