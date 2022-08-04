import itertools
import networkx as nx
from collision_checker.collision import *

def get_collision(nodes, edges, node_info, condition):
    
    graph = nx.Graph()
    graph.add_nodes_from(nodes)
    graph.add_edges_from(edges)
    
    collision_info = {}
    for col in condition:
        collision_info[col.name] = []
        col.set_info(node_info, graph)
        for i in itertools.permutations(nodes, r=col.body):
            flag = col.check(*i)
            if flag:
                collision_info[col.name].append(i)

    return collision_info

def get_safe_lattice(nodes, edges, collision_info):
    
    all_edges = []
    for i in edges:
        all_edges.append(i)
        all_edges.append((i[1], i[0]))

    cnodes = set()
    for name, i in collision_info.items():
        collision = eval(name)()
        if collision.node_unusable:
            for j in i:
                cnodes |= set(j)

    cedges = []
    for name, i in collision_info.items():
        collision = eval(name)()
        if collision.body >= 2:
            for j in i:
                cedges.append((j[0], j[1]))
    cedges = set(cedges)

    sedges = []
    for i in all_edges:
        if (i[0] not in cnodes) and (i[1] not in cnodes):
            sedges.append(i)

    snodes = list(set(nodes) - cnodes)
    sedges = list(set(sedges) - cedges)
    
    return snodes, sedges