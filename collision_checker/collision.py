import numpy as np
import networkx as nx

class FrequencyCollision:
    """Class of Frequency Collision"""

    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """

        self.name = None
        self.note = None
        self.body = None

        design_nn_detuining = 700 # MHz

        self.default = {
            "frequency" : np.nan, # MHz
            "anharmonicity" : np.nan, # MHz
            "t1" : np.nan, # us
            "t2_echo" : np.nan, # us
            "coupling" : 15, # MHz
            "cnot_time" : 100, # ns
            "max_frequency" : 9500, # MHz
            "min_frequency" : 6500, # MHz
            "max_detuning" : 1300, # MHz
            "min_t1" : 5, # us
            "min_t2" : 5, # us
            "bound_dist_1" : 0.2,
            "nnn_coupling" : np.nan,
        }
        if default is not None:
            for key, val in default.items():
                self.default[key] = val

        if np.isnan(self.default['nnn_coupling']):
            nn_detuning = 800 # MHz
            self.default['nnn_coupling'] = self.default['coupling']**2/nn_detuning # qubit mediated interaction

        # set alias
        self.b1 = self.default["bound_dist_1"]
        self.ozx = 1000/(4*self.default["cnot_time"]) # MHZ (zx interaction while CR)

    def set_graph(self, nodes, edges):
        """reflect the graph information
        Args:
            nodes (list): list of the node labels = [0,1,2...]
            edges (list): list of the edge labels = [(0,1), (1,2), ...]
        """
        self.nodes = nodes
        self.edges = edges
        self.graph = nx.Graph()
        self.graph.add_nodes_from(self.nodes)
        self.graph.add_edges_from(self.edges)

    def set_info(self, node_info, edge_info={}):
        """reflect the information about nodes and edges
        Args:
            node_info (dict): dictionary contains the values of the frequency and anharmonicity of qubits
            edge_info (dict): dictionary contains the values of the coupling between qubits
        """
        self.node_info = node_info
        self.edge_info = edge_info

    def get_value(self, target, key):
        """get the desired value from self.node_info or self.edge_info or self.default
        Args:
            target (int or tuple): label of the node or edge
            key (str): name of the values you want to get
        """
        if type(target) is tuple:
            if (target in self.edge_info.keys()):
                if key in self.edge_info[target].keys():
                    return self.edge_info[target][key]
            return self.default[key]
        else:
            if (target in self.node_info.keys()):
                if key in self.node_info[target].keys():
                    return self.node_info[target][key]
            return self.default[key]

class Type0A(FrequencyCollision):
    """
    Class of Frequency Collision Type0A

        targets:
            i : any qubit

        conditions:
            (1) qubit unmeasured (frequency or anharmonicity is NaN)
            (2) qubit frequency out of range
            (3) qubit t1, t2 is too short

        removals:
            i
    """

    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type0A"
        self.note = "bad or dead qubits"
        self.body = 1

    def check(self, i):
        """check the collision for target
        Args:
            i (int): target qubit
        """
        wi = self.get_value(i, "frequency")
        ai = self.get_value(i, "anharmonicity")
        t1 = self.get_value(i, "t1")
        t2 = self.get_value(i, "t2_echo")
        wmax = self.get_value(i, "max_frequency")
        wmin = self.get_value(i, "min_frequency")
        t1min = self.get_value(i, "min_t1")
        t2min = self.get_value(i, "min_t2")
        if (wi < wmin) or (wi > wmax) or np.isnan(wi) or np.isnan(ai) or (t1 < t1min) or (t2 < t2min):
            return True
        return False
    
    def remove(self, i):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): target qubit
        """
        removal_node = [i]
        removal_edge = []
        return removal_node, removal_edge

class Type0B(FrequencyCollision):
    """
    Class of Frequency Collision Type0B

        targets:
            i : any qubit
            j : qubit (nearest neighbor of i)

        conditions:
            (1) ge(i)-ge(j) is too far to implement the fast CR(i>j) or CR(j>i)

        removals:
            (i,j), (j,i)
    """
    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type0B"
        self.note = "too large detuning"
        self.body = 2

    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.get_value(i, "frequency")
        wj = self.get_value(j, "frequency")
        dmax = self.get_value((i,j), "max_detuning")
        if (dij == 1) and abs(wi-wj) > dmax:
            return True
        return False
    
    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        removal_node = []
        removal_edge = [(i,j), (j,i)]
        return removal_node, removal_edge

class Type1A(FrequencyCollision):
    """
    Class of Frequency Collision Type1A

        targets:
            i : any qubit
            j : qubit (nearest or next nearest neighbor of i)

        conditions:
            (1) ge(i)-ge(j) is too near

        removals:
            i,j
    """
    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type1A"
        self.note = "ge(i) - ge(j)"
        self.body = 2

    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.get_value(i, "frequency")
        wj = self.get_value(j, "frequency")
        deff = wi - wj
        if dij == 1:
            gij = self.get_value((i,j), "coupling")
            collision = (2*abs(gij) > self.b1*abs(deff))
            return collision
        if dij == 2:
            gij = self.get_value((i,j), "nnn_coupling")
            collision = (2*abs(gij) > self.b1*abs(deff))
            return collision
        return False
    
    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        removal_node = [i,j]
        removal_edge = []
        return removal_node, removal_edge

class Type1B(FrequencyCollision):
    """
    Class of Frequency Collision Type1B

        targets:
            i : CR control qubit
            j : CR target qubit

        conditions:
            (1) CR(?>i) and CR(?>j) can interfere with each other

        removals:
            (k>i), (k>j) for k is the nearest neighbor of i and j
    """

    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type1B"
        self.note = "CR(k>i) - CR(k>j)"
        self.body = 2
        
    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): control qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.get_value(i, "frequency")
        wj = self.get_value(j, "frequency")
        deff = wi - wj
        if dij == 2:
            collision = (self.ozx > self.b1*abs(deff))
            return collision
        return False
    
    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): control qubit
            j (int): target qubit
        """
        removal_node = []
        removal_edge = []
        for k in self.nodes:
            dik = nx.shortest_path_length(self.graph, i, k)
            djk = nx.shortest_path_length(self.graph, j, k)
            if (dik == 1) and (djk == 1):
                removal_edge.append((k,i))
                removal_edge.append((k,j))
        return removal_node, removal_edge

class Type1C(FrequencyCollision):
    """
    Class of Frequency Collision Type1C

        targets:
            i : CR control qubit
            j : CR target qubit

        conditions:
            (1) CR(i->j) excits GE(i) transition

        removals:
            (i,j)
    """

    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type1C"
        self.note = "ge(i) - CR(i>j)"
        self.body = 2
        
    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        if dij == 1:
            wi = self.get_value(i, "frequency")
            wj = self.get_value(j, "frequency")
            ai = self.get_value(i, "anharmonicity")
            gij = self.get_value((i,j), "coupling")
            oi = self.ozx*abs((wi-wj)*(wi+ai-wj)/(gij*ai))
            deff = wi - wj
            geff = oi
            collision = (abs(geff) > self.b1*abs(deff))
            # print(self.note, collision, (i,j), oi, geff, deff)
            return collision
        else:
            return False

    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type2A(FrequencyCollision):
    """
    Class of Frequency Collision Type2A

        targets:
            i : CR control qubit
            j : CR target qubit

        conditions:
            (1) GF/2(i) and CR(i>j) are too near

        removals:
            (i,j)
    """
    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type2A"
        self.note = "gf/2(i) in CR(i>j)"
        self.body = 2
        
    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): control qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        if dij == 1:
            wi = self.get_value(i, "frequency")
            wj = self.get_value(j, "frequency")
            ai = self.get_value(i, "anharmonicity")
            gij = self.get_value((i,j), "coupling")
            oi = self.ozx*abs((wi-wj)*(wi+ai-wj)/(gij*ai))
            deff = 2*wi + ai - 2*wj
            geff = abs(2**(-1.5)*oi**2*(1/((wi+ai)-wj)-1/(wi-wj)))
            collision = (abs(geff) > self.b1*abs(deff))
            return collision
        else:
            return False
    
    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): control qubit
            j (int): target qubit
        """
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type2B(FrequencyCollision):
    """
    Class of Frequency Collision Type2B
    
        targets:
            i : CR control qubit
            j : CR target qubit

        conditions:
            (1) Fogi(i>j) and CR(i>j) are too near

        removals:
            (i,j)
    """
    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type2B"
        self.note = "fogi(i>j) in CR(i>j)"
        self.body = 2
        
    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): control qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        if dij == 1:
            wi = self.get_value(i, "frequency")
            wj = self.get_value(j, "frequency")
            ai = self.get_value(i, "anharmonicity")
            gij = self.get_value((i,j), "coupling")
            oi = self.ozx*abs((wi-wj)*(wi+ai-wj)/(gij*ai))
            deff = 2*wi + ai - 2*wj
            geff = 2**0.5*gij*oi*(1/(wi-wj)+1/(wj-(wi+ai)))
            collision = (abs(geff) > self.b1*abs(deff))
            return collision
        else:
            return False
    
    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): control qubit
            j (int): target qubit
        """
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge
    
class Type3A(FrequencyCollision):
    """
    Class of Frequency Collision Type3A

        targets:
            i : any qubit
            j : qubit (nearest or next nearest neighbor of i)

        conditions:
            (1) EF(i) and GE(j) are too near

        removals:
            if safe_mode is True:
                i,j
            else:
                (i,j), (j,i)
    """
    def __init__(self, default=None, safe_mode=False):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
            safe_mode (bool): whether you remove the both of the nodes in Type3 or not
        """
        super().__init__(default)
        self.name = "Type3A"
        self.note = "ef(i) - ge(j)"
        self.body = 2
        self.safe_mode = safe_mode
        
    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.get_value(i, "frequency")
        wj = self.get_value(j, "frequency")
        ai = self.get_value(i, "anharmonicity")
        deff = wi + ai - wj
        if dij == 1:
            gij = self.get_value((i,j), "coupling")
            geff = 2**1.5 * gij
            collision = (abs(geff) > self.b1*abs(deff))
            return collision
        if dij == 2:
            gij = self.get_value((i,j), "nnn_coupling")
            geff = 2**1.5 * gij
            collision = (abs(geff) > self.b1*abs(deff))
            return collision
        return False

    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        if self.safe_mode:
            removal_node = [i,j]
            removal_edge = []
        else:
            removal_node = []
            removal_edge = [(i,j), (j,i)]
        return removal_node, removal_edge

class Type3B(FrequencyCollision):
    """
    Class of Frequency Collision Type3B

        targets:
            i : any qubit
            j : qubit (nearest or next nearest neighbor of i)

        conditions:
            (1) CR(i>j) excits EF(i) transition

        removals:
            (i,j)
    """
    def __init__(self, default=None, safe_mode=False):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
            safe_mode (bool): whether you remove the both of the nodes in Type3 or not
        """
        super().__init__(default)
        self.name = "Type3B"
        self.note = "ef(i) - CR(i>j)"
        self.body = 2
        
    def check(self, i,j):
        """check the collision for target
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        if dij == 1:
            wi = self.get_value(i, "frequency")
            wj = self.get_value(j, "frequency")
            ai = self.get_value(i, "anharmonicity")
            gij = self.get_value((i,j), "coupling")
            oi = self.ozx*abs((wi-wj)*(wi+ai-wj)/(gij*ai))
            deff = wi + ai - wj
            geff = 2**0.5 * oi
            collision = (abs(geff) > self.b1*abs(deff))
            # print(self.note, collision, (i,j), oi, geff, deff)
            return collision
        else:
            return False

    def remove(self, i, j):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): target qubit
            j (int): target qubit
        """
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type7(FrequencyCollision):
    """
    Class of Frequency Collision Type7

        targets:
            i : CR control qubit
            j : CR target qubit
            k : spectator qubit (neareset neighbor of i)

        conditions:
            (1) Fogi(i>k) and CR(i>j) are too near

        removals:
            (i,j)
    """
    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type7"
        self.note = "fogi(i>k) in CR(i>j)"
        self.body = 3
        
    def check(self, i,j,k):
        """check the collision for target
        Args:
            i (int): control qubit
            j (int): target qubit
            k (int): spectator qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        dik = nx.shortest_path_length(self.graph, i, k)
        if dij == dik == 1:
            wi = self.get_value(i, "frequency")
            wj = self.get_value(j, "frequency")
            wk = self.get_value(k, "frequency")
            ai = self.get_value(i, "anharmonicity")
            gij = self.get_value((i,j), "coupling")
            gik = self.get_value((i,k), "coupling")
            oi = self.ozx*abs((wi-wj)*(wi+ai-wj)/(gij*ai))
            deff = 2*wi + ai - (wj + wk)
            geff = 2**(-0.5)*gik*oi*(1/(wi+ai-wj)+1/(wi+ai-wk)-1/(wi-wj)-1/(wi-wk))
            collision = (abs(geff) > self.b1*abs(deff))
            return collision
        else:
            return False
           
    def remove(self, i, j, k):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): control qubit
            j (int): target qubit
            k (int): spectator qubit
        """
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type8(FrequencyCollision):
    """
    Class of Frequency Collision Type8

        targets:
            i : CR control qubit
            j : CR target qubit
            k : spectator qubit (next neareset neighbor of i)

        conditions:
            (1) GE(i) and GE(k) become too near while CR(i>j)

        removals:
            (i,j)
    """
    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type8"
        self.note = "ge(i)@CR(i>j) - ge(k)"
        self.body = 3
        
    def check(self, i,j,k):
        """check the collision for target
        Args:
            i (int): control qubit
            j (int): target qubit
            k (int): spectator qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        dik = nx.shortest_path_length(self.graph, i, k)
        
        if (dij == 1) and (dik == 2):
            wi = self.get_value(i, "frequency")
            wj = self.get_value(j, "frequency")
            wk = self.get_value(k, "frequency")
            ai = self.get_value(i, "anharmonicity")
            gij = self.get_value((i,j), "coupling")
            oi = self.ozx*abs((wi-wj)*(wi+ai-wj)/(gij*ai))
            deff = wi - wk
            geff = oi**2*ai/(2*(wi-wj)*(wi+ai-wj))
            collision = (deff*(deff+geff) < 0)
            return collision
        else:
            return False
        
    def remove(self, i, j, k):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): control qubit
            j (int): target qubit
            k (int): spectator qubit
        """
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type9(FrequencyCollision):
    """
    Class of Frequency Collision Type9

        targets:
            i : CR control qubit
            j : CR target qubit
            k : spectator qubit (next neareset neighbor of i)

        conditions:
            (1) GE(i) and EF(k) become too near while CR(i>j)

        removals:
            (i,j)
    """
    def __init__(self, default=None):
        """Initailize the Class
        Args:
            default (dict): dictionary of the default values
        """
        super().__init__(default)
        self.name = "Type9"
        self.note = "ge(i)@CR(i>j) - ef(k)"
        self.body = 3
        
    def check(self, i,j,k):
        """check the collision for target
        Args:
            i (int): control qubit
            j (int): target qubit
            k (int): spectator qubit
        """
        dij = nx.shortest_path_length(self.graph, i, j)
        dik = nx.shortest_path_length(self.graph, i, k)
        
        if (dij == 1) and (dik == 2):
            wi = self.get_value(i, "frequency")
            wj = self.get_value(j, "frequency")
            wk = self.get_value(k, "frequency")
            ai = self.get_value(i, "anharmonicity")
            ak = self.get_value(k, "anharmonicity")
            gij = self.get_value((i,j), "coupling")
            oi = self.ozx*abs((wi-wj)*(wi+ai-wj)/(gij*ai))
            deff = wi - (wk + ak)
            geff = oi**2*ai/(2*(wi-wj)*(wi+ai-wj))
            collision = (deff*(deff+geff) < 0)
            return collision
        else:
            return False
        
    def remove(self, i, j, k):
        """remove the corresponding nodes or edges of the collision
        Args:
            i (int): control qubit
            j (int): target qubit
            k (int): spectator qubit
        """
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge