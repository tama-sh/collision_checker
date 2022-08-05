import numpy as np
import networkx as nx

class FrequencyCollision:
    def __init__(self):
        self.name = None
        self.note = None
        self.body = None

        self.coupling = 15 # MHz
        self.cr_drive_amplitude_low_to_high = 400 # MHz
        self.cr_drive_amplitude_high_to_low = 400/3 # MHz
        
    def set_info(self, nodes, graph):
        self.nodes = nodes
        self.graph = graph

class Type0A(FrequencyCollision):
    def __init__(self):
        super().__init__()
        
        self.name = "Type0A"
        self.note = "bad or dead qubits"
        self.body = 1
        
    def check(self, i):
        wi = self.nodes[i]["frequency"]
        ai = self.nodes[i]["anharmonicity"]
        t1 = self.nodes[i]["t1"]
        t2 = self.nodes[i]["t2_echo"]
        
        if (wi < 6500) or (wi > 9500) or np.isnan(wi) or (t1 < 5) or (t2 < 5):
            return True
            
        return False
    
    def removal(self, i):
        removal_node = [i]
        removal_edge = []
        return removal_node, removal_edge

class Type0B(FrequencyCollision):
    def __init__(self):
        super().__init__()
        
        self.name = "Type0B"
        self.note = "too large detuning"
        self.body = 2
        
    def check(self, i,j):
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.nodes[i]["frequency"]
        wj = self.nodes[j]["frequency"]
        
        if (dij == 1) and abs(wi-wj) > 1000:
            return True
            
        return False
    
    def removal(self, i, j):
        removal_node = []
        removal_edge = [(i,j), (j,i)]
        return removal_node, removal_edge

class Type1A(FrequencyCollision):
    def __init__(self):
        super().__init__()
        
        self.name = "Type1A"
        self.note = "ge(i) - ge(j)"
        self.body = 2
        
    def check(self, i,j):
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.nodes[i]["frequency"]
        wj = self.nodes[j]["frequency"]
        ai = self.nodes[i]["anharmonicity"]
        aj = self.nodes[j]["anharmonicity"]
        g = self.coupling
        
        deff = wi - wj
        geff = g
        
        if dij == 1:
            collision = (abs(geff) > 0.1*abs(deff))
            return collision
        if dij == 2:
            collision = (abs(geff) > 5.3*abs(deff))
            return collision
        return False 
    
    def removal(self, i, j):
        removal_node = [i,j]
        removal_edge = []
        return removal_node, removal_edge
    
class Type1B(FrequencyCollision):
    def __init__(self):
        super().__init__()
        
        self.name = "Type1B"
        self.note = "CR(k>i) - CR(k>j)"
        self.body = 2
        
    def check(self, i,j):
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.nodes[i]["frequency"]
        wj = self.nodes[j]["frequency"]
        ai = self.nodes[i]["anharmonicity"]
        aj = self.nodes[j]["anharmonicity"]
        g = self.coupling
        
        deff = wi - wj
        
        if dij == 2:
            collision = (25 > abs(deff))
            return collision
        
        return False 
    
    def removal(self, i, j):
        removal_node = []
        removal_edge = []
        for k in self.nodes.keys():
            dik = nx.shortest_path_length(self.graph, i, k)
            djk = nx.shortest_path_length(self.graph, j, k)
            if (dik == 1) and (djk == 1):
                removal_edge.append((k,i))
                removal_edge.append((k,j))
        return removal_node, removal_edge

class Type2A(FrequencyCollision):
    def __init__(self):
        super().__init__()
        self.name = "Type2A"
        self.note = "gf/2(i) in CR(i>j)"
        self.body = 2
        
    def check(self, i,j):
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.nodes[i]["frequency"]
        wj = self.nodes[j]["frequency"]
        ai = self.nodes[i]["anharmonicity"]
        aj = self.nodes[j]["anharmonicity"]

        if self.nodes[i]["high_low"] == "low":
            oi = self.cr_drive_amplitude_low_to_high
        elif self.nodes[i]["high_low"] == "high":
            oi = self.cr_drive_amplitude_high_to_low
        else:
            oi = np.nan
        
        deff = 2*wi + ai - 2*wj
        geff = min(oi, abs(2**(-0.5)*oi**2*(1/(wi-wj)+1/(wj-(wi+ai)))))
        
        if dij == 1:
            collision = (abs(geff) > 0.1*abs(deff))
            return collision
                
        return False
    
    def removal(self, i, j):
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type2B(FrequencyCollision):
    def __init__(self):
        super().__init__()
        self.name = "Type2B"
        self.note = "fogi(i>j) in CR(i>j)"
        self.body = 2
        
    def check(self, i,j):
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.nodes[i]["frequency"]
        wj = self.nodes[j]["frequency"]
        ai = self.nodes[i]["anharmonicity"]
        aj = self.nodes[j]["anharmonicity"]
        
        g = self.coupling
        if self.nodes[i]["high_low"] == "low":
            oi = self.cr_drive_amplitude_low_to_high
        elif self.nodes[i]["high_low"] == "high":
            oi = self.cr_drive_amplitude_high_to_low
        else:
            oi = np.nan

        deff = 2*wi + ai - 2*wj
        geff = 2**(-0.5)*g*oi*(1/(wi-wj)+1/(wj-(wi+ai)))
        
        if dij == 1:
            collision = (abs(geff) > 0.1*abs(deff))
            return collision
                
        return False
    
    def removal(self, i, j):
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge
    
class Type3(FrequencyCollision):
    def __init__(self):
        super().__init__()
        self.name = "Type3"
        self.note = "ef(i) - ge(j)"
        self.body = 2
        
    def check(self, i,j):
        dij = nx.shortest_path_length(self.graph, i, j)
        wi = self.nodes[i]["frequency"]
        wj = self.nodes[j]["frequency"]
        ai = self.nodes[i]["anharmonicity"]
        aj = self.nodes[j]["anharmonicity"]
        g = self.coupling
        
        deff = wi + ai - wj
        geff = 2**0.5 * g
        
        if dij == 1:
            collision = (abs(geff) > 0.1*abs(deff))
            return collision
        if dij == 2:
            collision = (abs(geff) > 5.3*abs(deff))
            return collision
                
        return False
    
    def removal(self, i, j):
        removal_node = []
        removal_edge = [(i,j), (j,i)]
        return removal_node, removal_edge

class Type7(FrequencyCollision):
    def __init__(self):
        super().__init__()
        self.name = "Type7"
        self.note = "fogi(i>k) in CR(i>j)"
        self.body = 3
        
    def check(self, i,j,k):
        dij = nx.shortest_path_length(self.graph, i, j)
        dik = nx.shortest_path_length(self.graph, i, k)
        
        if dij == dik == 1:
            
            wi = self.nodes[i]["frequency"]
            wj = self.nodes[j]["frequency"]
            wk = self.nodes[k]["frequency"]
            ai = self.nodes[i]["anharmonicity"]
            aj = self.nodes[j]["anharmonicity"]
            ak = self.nodes[k]["anharmonicity"]

            g = self.coupling
            if self.nodes[i]["high_low"] == "low":
                oi = self.cr_drive_amplitude_low_to_high
            elif self.nodes[i]["high_low"] == "high":
                oi = self.cr_drive_amplitude_high_to_low
            else:
                oi = np.nan

            deff = 2*wi + ai - (wj + wk)
            geff = 2**(-0.5)*g*oi*(1/(wi-wj)+1/(wk-(wi+ai)) + 1/(wi+ai-wj) + 1/(wk-wi))
            
            collision = (abs(geff) > 0.1*abs(deff))
            return collision
        
        else:  
            return False    
           
    def removal(self, i, j, k):
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type8(FrequencyCollision):
    def __init__(self):
        super().__init__()
        self.name = "Type8"
        self.note = "ge(i)@CR(i>j) - ge(k)"
        self.body = 3
        
    def check(self, i,j,k):
        dij = nx.shortest_path_length(self.graph, i, j)
        dik = nx.shortest_path_length(self.graph, i, k)
        
        if (dij == 1) and (dik == 2):
            wi = self.nodes[i]["frequency"]
            wj = self.nodes[j]["frequency"]
            wk = self.nodes[k]["frequency"]
            ai = self.nodes[i]["anharmonicity"]
            aj = self.nodes[j]["anharmonicity"]
            ak = self.nodes[k]["anharmonicity"]

            if self.nodes[i]["high_low"] == "low":
                oi = self.cr_drive_amplitude_low_to_high
            elif self.nodes[i]["high_low"] == "high":
                oi = self.cr_drive_amplitude_high_to_low
            else:
                oi = np.nan

            deff = wi - wk
            geff = oi**2*ai/(2*(wi-wj)*(wi+ai-wj))
            
            collision = (deff*(deff+geff) < 0)
            
            return collision
        
        else:
            return False    
        
    def removal(self, i, j, k):
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge

class Type9(FrequencyCollision):
    def __init__(self):
        super().__init__()
        self.name = "Type9"
        self.note = "ge(i)@CR(i>j) - ef(k)"
        self.body = 3
        self.bound = {1:0.1, 2:1}
        
    def check(self, i,j,k):
        dij = nx.shortest_path_length(self.graph, i, j)
        dik = nx.shortest_path_length(self.graph, i, k)
        
        if (dij == 1) and (dik == 2):
            
            wi = self.nodes[i]["frequency"]
            wj = self.nodes[j]["frequency"]
            wk = self.nodes[k]["frequency"]
            ai = self.nodes[i]["anharmonicity"]
            aj = self.nodes[j]["anharmonicity"]
            ak = self.nodes[k]["anharmonicity"]

            if self.nodes[i]["high_low"] == "low":
                oi = self.cr_drive_amplitude_low_to_high
            elif self.nodes[i]["high_low"] == "high":
                oi = self.cr_drive_amplitude_high_to_low
            else:
                oi = np.nan

            deff = wi - (wk + ak)
            geff = oi**2*ai/(2*(wi-wj)*(wi+ai-wj))
            collision = (deff*(deff+geff) < 0)
            
            return collision
        
        else:
            return False
        
    def removal(self, i, j, k):
        removal_node = []
        removal_edge = [(i,j)]
        return removal_node, removal_edge