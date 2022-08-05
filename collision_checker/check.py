import itertools

def get_collision_info(condition, nodes, edges, node_info, edge_info=None):
    """check collisions
    Args:
        condition (list): list of the collision conditions
        nodes (list): list of the node labels
        edges (list): list of the edge labels
        node_info (dict): dictionary of the node information
        edge_info (dict): dictionary of the edge information
    Returns:
        collision_info (dict): dictionary of the collision information
    """
    collision_info = {}
    for col in condition:
        collision_info[col] = []
        col.set_info(node_info, edge_info)
        col.set_graph(nodes, edges)
        for i in itertools.permutations(nodes, r=col.body):
            if col.check(*i):
                collision_info[col].append(i)
    return collision_info

def get_safe_lattice(nodes, edges, collision_info):
    """find safe lattice
    Args:
        nodes (list): list of the node labels
        edges (list): list of the edge labels
        collision_info (dict): dictionary of the collision information
    Returns:
        safe_nodes (list): list of the safe node labels
        safe_edges (list): list of the safe edge labels
    """
    all_edges = []
    for i in edges:
        all_edges.append(i)
        all_edges.append((i[1], i[0]))

    cnodes = set()
    cedges = set()
    for collision, i in collision_info.items():
        for j in i:
            rnodes, redges = collision.remove(*j)
            cnodes |= set(rnodes)
            cedges |= set(redges)

    sedges = []
    for i in all_edges:
        if (i[0] not in cnodes) and (i[1] not in cnodes):
            sedges.append(i)

    snodes = list(set(nodes) - cnodes)
    sedges = list(set(sedges) - cedges)

    return snodes, sedges