import queue


def get_neighbors_and_costs(nav_graph):
    def inner(node):
        return nav_graph[node].items()
    return inner


def estimate_zero(node_a, node_b):
    return 0.0


def search(transition_func, start, goal, cost_heuristic=estimate_zero):
    frontier = queue.PriorityQueue()  # (total_cost, fixed_cost, node, from_node)
    explored = {}  # node: (fixed_cost, from_node)
    frontier.put((0, 0, start, None))  # Total cost, fixed cost, node
    try:
        while True:
            total_cost, fixed_cost, node, from_node = frontier.get(block=False)
            if node in explored:
                if explored[node][0] > fixed_cost:
                    explored[node] = (fixed_cost, from_node)
                continue
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

            for next_node, transition_cost in transition_func(node):
                if next_node in explored:
                    continue
                next_fixed_cost = fixed_cost + transition_cost
                next_total_cost = next_fixed_cost + cost_heuristic(next_node, goal)
                frontier.put((next_total_cost, next_fixed_cost, next_node, node))
    except queue.Empty:
        raise Exception("no path found")  # FIXME: Make this exception
