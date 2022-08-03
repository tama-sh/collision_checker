import itertools
import networkx as nx

def get_collision(node_list, edge_list, node_info, condition):
    
    n = len(node_list)
    
    graph = nx.Graph()
    graph.add_nodes_from(node_list)
    graph.add_edges_from(edge_list)
    
    collision_info = {}
    for col in condition:
        collision_info[col.name] = []
        col.set_info(node_info, graph)
        for i in itertools.permutations(range(n), r=col.body):
            flag = col.check(*i)
            if flag:
                collision_info[col.name].append(i)

    return collision_info

def get_safe_lattice(node_list, edge_list, collision_info):
    
    col_qubits = set()
    for col_name, col_list in collision_info.items():
        tmp = set()
        for qubits in col_list:
            tmp |= set(qubits)
        col_qubits |= tmp
        
    safe_nodes = list(set(node_list) - col_qubits)
    safe_edges = []
    for edge in edge_list:
        if (edge[0] in safe_nodes) and (edge[1] in safe_nodes):
            safe_edges.append(edge)
    return safe_nodes, safe_edges