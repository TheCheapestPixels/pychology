import math

from pychology.simple_search.a_star import search
from pychology.simple_search.a_star import get_neighbors_and_costs

level_1 = "I...O"


level_2 = """
"           "
" ..I.. ... "
"   .   .   "
" ..... ... "
" .     .   "
" ....... . "
" .       . "
" . ....... "
" . .   . . "
" ... ... . "
"         . "
" ......... "
"       .   "
"       O   "

"""[1:]


level_3 = """
I.                                                                                                   
...... ....... ........... . ......... ......... . ....... . . . . ... ... ......... ..... ..... . . 
   .   .       . .         . . .     .     .     .       . . . . .   .   .     .       .   .     . . 
 ..... ....... . ....... . ... ..... ................. . ... ....... ... ..... ..... ..... . ..... . 
     . . .     . .     . .   .   . .     .     .   . . . .       . . .   .   . .         . .     . . 
 ... . . ... ... ... ... . ..... . . ......... ... . . ... ... ... . ....... ..... ... . . . ..... . 
 . . .   . .   .       . . .   . .     .   .   .   . . .     .   .     .   . . .   .   . . . . . . . 
 . ..... . ..... . . ......... . . . ... ..... . . . ..... . . . ... ... ... . . ............. . ... 
 .   .     . . . . . . .   .   .   .         . . . .   .   . . . .       .       .     . .   .     . 
 . ..... . . . . . . . ... ... . ........... . ... . . ..... ......... ... ..... ..... . . ..... ... 
   .     .       . .     . .   . . .   .     .   .   .     . .   .     .   .   .   . .   .     .     
 . ... . ..... . ..... ... ... . . ... . ....... . ..... ..... . ... ....... ..... . . ... . ....... 
 . .   . .     .   . . .   .     .           .   .   . .       .   . .   .     .     .   . . . .     
 . ... ....... ... . ... ... . ........... . . ....... ......... ... . ... ..... . ... ... ... ..... 
 .   . . .   . . .       . . .   .   . . . .     .         .       . .         . . .     .   .     . 
 ....... . ..... ..... ... . ..... . . . . . ....... . . ..... . ......... ... ..... ..... . ... ... 
 . .           . .       . .     . .     . .   . .   . .   .   .     .       .           . .       . 
 . ... ..... . . . . . . . . ....... . ..... ... . ... ......... ... ... ... ... ... ..... ....... . 
 .   .   .   . .   . . .   .       . .     .       . . .     .     .     .     .   . . .   . .       
 . ..... ... ... ....... ....... . ... ..... ..... . . ..... ..... ... ......... ..... . ... . ... . 
     .   .   .       . . . .     . .     .   .   .   .     .     . .   . . .       .     .     . . . 
 . ... . . ... . . ... ... . ... ..... . ... . ....... ....... ... ... . . . ..... . . ... . ... ... 
 . .   . . .   . .     . .   .         .   .         .     .       .       . . .   . .   . .     . . 
 ......... ... ....... . . ... . ..... . . ... . . ......... . ......... . ... ... ... ......... . . 
   .   .   . . .           .   .   .   . . . . . . . .     . . .     . . . .   .     . .   .     .   
 . ... ... . ... ... ..... ......... ..... . ....... ... . ... ... ... ... . ... ... . ... . . ... . 
 .   .     . .     . .     . .   .   .       .   .     . . .     .   . . . . . . .   . . .   . . . . 
 ......... . . ... . ....... ... ......... ... ... . ... ... ....... . . . . . . ....... . . ... . . 
 . .     . .     . . .   .       .       .         . .   .       .   . .     .       .     . .   . . 
 . . ... . ......... ... ... ....... ... ... . ....... ......... . ... ... . ... ............. ..... 
   . . . .     . .   . .           .   . . . . .   . .       .           . . . .   . . .       . .   
 ... . ..... . . ..... . ... ..... . . ... ..... . . . ..... . ... . ... ..... ... . . . ... . . . . 
 . . . . .   .     . .   . .     . . .     .     . .   . . . . .   . . . .     . . . .     . . .   . 
 . . . . . ....... . ... . ............... . ... ... . . . . . ....... ... ..... . . ......... ..... 
 . . . .     .   .   .     .   .       .   .   . .   .   .   . . .   .   .         . . . .         . 
 . . . ... . ... . ... ... ... ... ... ... ..... ... ... ....... . . . ..... ... ... . . . . ... ... 
     . .   . .     .   . .   .   . .   .   .         .   . .   . . .   . .     . .   .     . . .     
 ..... ... ..... ....... . ... ... ....... ... . ... ... . ... . ..... . ... . ..... . ..... . . ... 
   .   .     .   . .   . .     . .   .     .   .   . . . .     .   .   .   . . .   .       . .   .   
 ..... ..... ..... ... . ..... . . ... ......... ..... ... ....... ... . ..... ... .................
                                                                                                   O"""[1:]


level_4 = """
   .....
   .   .
...I...O
   .   .
   .....
        
"""


level_5 = """
I....
. . .
....O
    
"""


def euclidean_distance(a, b):
    ax, ay = a
    bx, by = b
    ax, ay, bx, by = float(ax), float(ay), float(bx), float(by)
    dx, dy = ax - bx, ay - by
    return (math.sqrt(dx**2 + dy**2))


def create_adjacency_from_string(level):
    # Turn string representation into set of coordinate tuples
    tiles = set()
    start_node = None
    goal_node = None
    for l_idx, line in enumerate(level.split('\n')):
        for t_idx, tile in enumerate(line):
            if tile in '.IO':
                coord = (l_idx, t_idx)
                tiles.add(coord)
                if tile == 'I':
                    start_node = coord
                elif tile == 'O':
                    end_node = coord
    # And now create the adjacency matrix.
    adjacency_matrix = {}
    for tile in tiles:
        x, y = tile
        adjacents = {}
        for dx, dy in [(-1, 0), (1, 0), (0, -1), (0, 1)]:
            dc = (x+dx, y+dy)
            if dc in tiles:
                adjacents[dc] = 1  # Fixed cost of 1
        adjacency_matrix[tile] = adjacents
    # Done!
    return (adjacency_matrix, start_node, end_node)


def print_labyrinth(level, path=None):
    annotated_level = []
    for l_idx, line in enumerate(level.split('\n')):
        for t_idx, tile in enumerate(line):
            if path is not None and (l_idx, t_idx) in path:
                annotated_level.append("*")
            else:
                annotated_level.append(tile)
        annotated_level.append("\n")
    print(''.join(annotated_level))
    

level = level_2
adj_mat, start, goal = create_adjacency_from_string(level)
print(start, goal)
print_labyrinth(level)
cost, path = search(get_neighbors_and_costs(adj_mat), start, goal, euclidean_distance)
print(cost)
print_labyrinth(level, path)
