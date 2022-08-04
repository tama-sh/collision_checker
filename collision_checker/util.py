import numpy as np

def get_node_info(node_list, calibration_notes):
    node_info = {}
    for node in node_list:
        name = f"Q{node}"
        
        if name in calibration_notes.keys():
            note = calibration_notes[name]
            
            if node%4 in [0,3]:
                high_low = "low"
            if node%4 in [1,2]:
                high_low = "high"
            else:
                pass

            node_info[node] = {
                "frequency" : note.qubit_dressed_frequency["MHz"],
                "anharmonicity" : note.anharmonicity["MHz"],
                "t1" : note.t1["us"],
                "t2_echo" : note.t2_echo["us"],
                "high_low" : high_low
            }
        else:
            node_info[node] = {
                "frequency" : np.nan,
                "anharmonicity" : np.nan,
                "t1" : np.nan,
                "t2_echo" : np.nan,
                "high_low" : np.nan,
            }
            
    return node_info