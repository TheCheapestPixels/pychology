import queue


def search(adjacency_matrix, estimation_func, start, goal):
    frontier = queue.PriorityQueue()
    explored = {}
    frontier.put((0, 0, start, None))  # Total cost, fixed cost, node
    try:
        while True:
            total_cost, fixed_cost, node, from_node = frontier.get(block=False)
            if node not in explored or explored[node][0] > fixed_cost:
                explored[node] = (fixed_cost, from_node)
            if node == goal:  # Search succeeded
                path = [node]
                while True:
                    _, from_node = explored[node]
                    if from_node is None:
                        break
                    path.append(from_node)
                    node = from_node
                return fixed_cost, list(reversed(path))

            for next_node, transition_cost in adjacency_matrix[node].items():
                if next_node in explored:
                    continue
                next_fixed_cost = fixed_cost + transition_cost
                next_total_cost = next_fixed_cost + estimation_func(next_node, goal)
                frontier.put((next_total_cost, next_fixed_cost, next_node, node))
                #import pdb; pdb.set_trace()
    except queue.Empty:
        raise Exception("no path found")  # FIXME: Make this exception
