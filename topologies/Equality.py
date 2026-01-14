import networkx as nx
import sys
from pathlib import Path
from statistics import mean

# Add current directory to path for imports
TOPO_DIR = Path(__file__).resolve().parent
if str(TOPO_DIR) not in sys.path:
    sys.path.insert(0, str(TOPO_DIR))

try:
    from .HPC_topo import HPC_topo
except ImportError:
    from HPC_topo import HPC_topo

# Notations for Equality network:
# n = number of routers; k = inter-router radix; p = number of endpoints per router
# ahops: a list of odd numbers, each number contribute to one link connected to each router
# bhops: a list of even numbers, each number contribute to two link connected to each router
# Therefore, this should hold: k = len(ahops)+2*len(bhops)
class Equalitytopo(HPC_topo):
    # def __init__(self, n, k, ahops, bhops):
    #     super(Equalitytopo, self).__init__()
    #     self.generate_Equality_topo(n, k, ahops, bhops)

    # def __init__(self, edgelist):
    #     super(Equalitytopo, self).__init__()
    #     # create the embedded graph
    #     graph = nx.Graph()
    #     graph.add_edges_from(edgelist)
    #     self.nx_graph = graph

    def __init__(self, *args, **kwargs):
        if len(args) == 4 and isinstance(args[0], int) and isinstance(args[1], int):
            assert(isinstance(args[2], list) and isinstance(args[3], list))
            super(Equalitytopo, self).__init__()
            self.generate_Equality_topo(args[0], args[1], args[2], args[3])
        elif len(args) == 1 and isinstance(args[0], list):
            super(Equalitytopo, self).__init__()
            # create the embedded graph
            graph = nx.Graph()
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')


    def generate_Equality_topo(self, n, k, ahops, bhops):
        assert(k==len(ahops)+2*len(bhops))
        assert(ahops[0]==-1 and ahops[1]==1)
        edges=[]
        # calculate edge list according to the rules of Equality network
        for v in range(n):
            if v%2 == 0:
                for odd_number in ahops:
                    edges.extend([(v, (odd_number+v)%n)])
                for even_number in bhops:
                    edges.extend([(v, (even_number+v)%n)])
            else:
                for odd_number in ahops:
                    edges.extend([(v, (-odd_number+v)%n)])
                for even_number in bhops:
                    edges.extend([(v, (-even_number+v)%n)])

        # create the embedded graph
        graph = nx.Graph()
        graph.add_edges_from(edges)
        self.nx_graph = graph
        assert(mean([i[1] for i in list(self.nx_graph.degree)])==k)
        return