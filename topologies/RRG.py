import networkx as nx
import sys
from pathlib import Path

# Add current directory to path for imports
TOPO_DIR = Path(__file__).resolve().parent
if str(TOPO_DIR) not in sys.path:
    sys.path.insert(0, str(TOPO_DIR))

from HPC_topo import HPC_topo

class RRGtopo(HPC_topo):
    # def __init__(self, degree, num_vertices, seed = 0):
    #     super(RRGtopo, self).__init__()
    #     self.nx_graph = nx.random_regular_graph(degree, num_vertices, seed=seed)

    # def __init__(self, edgelist):
    #     super(RRGtopo, self).__init__()
    #     # create the embedded graph
    #     graph = nx.Graph()
    #     graph.add_edges_from(edgelist)
    #     self.nx_graph = graph

    def __init__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            super(RRGtopo, self).__init__()
            degree=args[1]
            num_vertices=args[0]
            self.nx_graph = nx.random_regular_graph(degree, num_vertices, seed=0)

        elif len(args) == 3 and isinstance(args[0], int) and isinstance(args[1], int) and isinstance(args[2], int):
            super(RRGtopo, self).__init__()
            degree=args[1]
            num_vertices=args[0]
            self.nx_graph = nx.random_regular_graph(degree, num_vertices, seed=args[2])

        elif len(args) == 1 and isinstance(args[0], list):
            super(RRGtopo, self).__init__()
            # create the embedded graph
            graph = nx.Graph()
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')