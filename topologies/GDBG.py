import networkx as nx
import sys
from pathlib import Path

# Add current directory to path for imports
TOPO_DIR = Path(__file__).resolve().parent
if str(TOPO_DIR) not in sys.path:
    sys.path.insert(0, str(TOPO_DIR))

import HPC_topo

class GDBG_topo(HPC_topo.HPC_topo):

    def __init__(self, *args, **kwargs):
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            num_vertices = args[0]
            degree = args[1]
            self.nx_graph = nx.DiGraph()
            self.diameter = None

            assert(num_vertices > degree)
            # Create a list of edges
            edges = []    
            for v in range(num_vertices):
                for e in range(degree):
                    if v != (degree*v+e)%num_vertices: #exclude self-loop arcs
                        edges.extend([(v, (degree*v+e)%num_vertices)])
            self.nx_graph.add_edges_from(edges)
        elif len(args) == 1 and isinstance(args[0], list):
            graph = nx.DiGraph()
            self.diameter = None
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')

    def distribute_uniform_flow_on_paths(self, path_dict):
        link_flows = {}
        for u, v in list(self.nx_graph.edges()):
            link_flows[(u, v)]=0
        for paths in path_dict.values():
            k = float(len(paths))
            for path in paths:
                for i in range(len(path) - 1):
                    u, v = path[i], path[i + 1]
                    link_flows[(u, v)] += 1 / k
        return link_flows
