import math
import networkx as nx
import matplotlib.pyplot as plt
from .lattice import qubit_lattice, mux_lattice

def visualize(n, d, collision=None, safe_nodes=None, safe_edges=None, output=True):
    """visualize collision or safe lattice information
    Args:
        n (int): number of qubits
        d (int): number of mux in a line
        collision (list): list of the qubit pairs in collision
        safe_nodes (list): list of the safe node labels
        safe_edges (list): list of the safe edge labels
        output (bool): Whether to visualize the figure immediately or not
    """
    nodes, edges, pos = qubit_lattice(n,d)
    mnodes, mpos = mux_lattice(d)
    
    q = nx.Graph()
    q.add_nodes_from(nodes)
    q.add_edges_from(edges)

    m = nx.Graph()
    m.add_nodes_from(mnodes)
    
    c = nx.DiGraph()
    if collision is not None:
        cnodes = set()
        for i in collision:
            cnodes |= set(i[:1])
        cnodes = list(cnodes)
        c.add_nodes_from(cnodes)

        cedges = []
        for i in collision:
            if len(i) >= 2:
                cedges.append((i[0], i[1]))
        cedges = list(set(cedges))
        c.add_edges_from(cedges)

    s = nx.DiGraph()
    if safe_nodes is not None:
        s.add_nodes_from(safe_nodes)
    if safe_edges is not None:
        s.add_edges_from(safe_edges)

    if output:
        plt.figure(figsize=(1.5*d, 1.5*d))
    nx.draw(q, pos, with_labels=True, node_color="k", edge_color="k", width=3, font_color="w", font_size=15, node_size=500)
    nx.draw(m, mpos, with_labels=True, node_color="w", edge_color="k", width=3, font_size=20)
    nx.draw(c, pos, with_labels=True, arrowsize=10, arrowstyle="->",node_color="r", edge_color="r", width=3, font_color="w", font_size=15, node_size=500)
    nx.draw(s, pos, with_labels=True, arrowsize=10, arrowstyle="->",node_color="b", edge_color="b", width=3, font_color="w", font_size=15, node_size=500)
    if output:
        plt.show()

def visualize_all(n, d, collision_info, safe_nodes, safe_edges):
    """visualize all information about collisions and safe lattice
    Args:
        n (int): number of qubits
        d (int): number of mux in a line
        collision_info (dict): dictionary of the collision information
        safe_nodes (list): list of the safe node labels
        safe_edges (list): list of the safe edge labels
    """
    cn = len(collision_info)
    x = math.ceil((cn+1)**0.5)

    plt.figure(figsize=(1.5*d*x, 1.5*d*x))
    for i, (collision, collision_list) in enumerate(collision_info.items()):
        plt.subplot(x,x,i+1)
        plt.title(collision.name)
        visualize(n, d, collision=collision_list, output=False)
    plt.subplot(x,x,i+2)
    plt.title("Safe Lattice")
    visualize(n, d, safe_nodes=safe_nodes, safe_edges=safe_edges, output=False)
    plt.tight_layout()
    plt.show()