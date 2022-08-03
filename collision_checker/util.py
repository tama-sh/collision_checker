def get_node_info(node_list, calibration_notes):
    node_info = {}
    for node in node_list:
        name = f"Q{node}"
        note = calibration_notes[name]
        
        if node%4 in [0,3]:
            high_low = "low"
        if node%4 in [1,2]:
            high_low = "high"
        else:
            raise
        
        node_info[node] = {
            "frequency" : note.qubit_dressed_frequency_jazz["MHz"],
            "anharmonicity" : note.anharmonicity["MHz"],
            "high_low" : high_low
        }
    return node_info