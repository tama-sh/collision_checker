def get_node_info(nodes, edges, node_notes, edge_notes=None):
    """generate node_info object from calibration_notes in measurement_tools_automation
    Args:
        nodes (list): list of the node labels
        node_notes (dict): dictionary of the CalibrationNote class about node
        edge_notes (dict): dictionary of the CalibrationNote class about edge
    Returns:
        node_info (dict): dictionary of the node information
        edge_info (dict): dictionary of the edge information
    """
    node_info = {}
    for node in nodes:
        name = f"Q{node}"
        if name in node_notes.keys():
            note = node_notes[name]
            node_info[node] = {
                "frequency" : note.qubit_dressed_frequency["MHz"],
                "anharmonicity" : note.anharmonicity["MHz"],
                "t1" : note.t1["us"],
                "t2_echo" : note.t2_echo["us"],
            }
        else:
            node_info[node] = {}

    edge_info = {}
    for edge in edges:
        name = f"(Q{edge[0]}, Q{edge[1]})"
        if name in edge_notes.keys():
            note = edge_notes[name]
            edge_info[edge] = {
                "coupling" : note.coupling_strength["MHz"],
            }
        else:
            edge_info[edge] = {}
    return node_info, edge_info