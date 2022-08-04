import itertools
import networkx as nx
import matplotlib.pyplot as plt
from .lattice import qubit_lattice, mux_lattice

def visualize(n, d, collisions=None, safe_nodes=None, safe_edges=None):
    nodes, edges, pos = qubit_lattice(n=64,d=4)
    mnodes, mpos = mux_lattice(d=4)
    
    q = nx.Graph()
    q.add_nodes_from(nodes)
    q.add_edges_from(edges)

    m = nx.Graph()
    m.add_nodes_from(mnodes)
    
    c = nx.DiGraph()
    if collisions is not None:
        cnodes = set()
        for i in collisions:
            cnodes |= set(i[:1])
        cnodes = list(cnodes)
        c.add_nodes_from(cnodes)

        cedges = []
        for i in collisions:
            if len(i) >= 2:
                cedges.append((i[0], i[1]))
        cedges = list(set(cedges))
        c.add_edges_from(cedges)

    s = nx.DiGraph()
    if safe_nodes is not None:
        s.add_nodes_from(safe_nodes)
    if safe_edges is not None:
        s.add_edges_from(safe_edges)

    plt.figure(figsize=(6,6))
    nx.draw(q, pos, with_labels=True, node_color="k", edge_color="k", width=3, font_color="w", font_size=15, node_size=500)
    nx.draw(m, mpos, with_labels=True, node_color="w", edge_color="k", width=3, font_size=20)
    nx.draw(c, pos, with_labels=True, arrowsize=10, arrowstyle="->",node_color="r", edge_color="r", width=3, font_color="w", font_size=15, node_size=500)
    nx.draw(s, pos, with_labels=True, arrowsize=10, arrowstyle="->",node_color="b", edge_color="b", width=3, font_color="w", font_size=15, node_size=500)
    plt.axis('off')
    plt.show()