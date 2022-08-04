def qubit_lattice(n,d):

    def node(i,j,k):
        q = 4*(i*d + j) + k
        return q

    nodes = range(n)
    edges = []
    for i in range(d):
        for j in range(d):

            # inner - mux
            edges.append((node(i,j,0), node(i,j,1)))
            edges.append((node(i,j,0), node(i,j,2)))
            edges.append((node(i,j,1), node(i,j,3)))
            edges.append((node(i,j,2), node(i,j,3)))

            # inter - mux
            if i != d-1:
                edges.append((node(i,j,2), node(i+1,j,0)))
                edges.append((node(i,j,3), node(i+1,j,1)))

            if j != d-1:
                edges.append((node(i,j,1), node(i,j+1,0)))
                edges.append((node(i,j,3), node(i,j+1,2)))
                
    pos = {}
    for i in range(d):
        for j in range(d):       
                pos[node(i,j,0)] = (j - 1/3, -i + 1/3)
                pos[node(i,j,1)] = (j +1/3, -i + 1/3)
                pos[node(i,j,2)] = (j - 1/3, -i - 1/3)
                pos[node(i,j,3)] = (j +1/3, -i - 1/3)
                
    return nodes, edges, pos

def mux_lattice(d):

    nodes = range(d**2)
    pos = {}
    for i in range(d):
        for j in range(d):
            pos[i*d+j] = (j,-i)
            
    return nodes, pos