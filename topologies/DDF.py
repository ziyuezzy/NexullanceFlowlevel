import networkx as nx
from .HPC_topo import HPC_topo
from statistics import mean
import random

# Dally DragonFly (DDF) network topology
class DDFtopo(HPC_topo):

    def __init__(self, *args, **kwargs): 
        # DF parameters: Number of routers per group = a, Number of groups = g,
        # Number of inter-group links per router = h, 
        # Number of terminals per router = p (p is not modeled in the graph),
        # Router radix = k = p+a+h-1
        # for DDF, a=2p=2h, g=ah+1
        # Input to this class is the number of routers = R = a*g; router radix = k = a+p+h-1= 2*a-1, then we deduct all parameters
        if len(args) == 2 and isinstance(args[0], int) and isinstance(args[1], int):
            super(DDFtopo, self).__init__()
            self.generate_DDF_topo(args[0], args[1])
        elif len(args) == 1 and isinstance(args[0], list):
            super(DDFtopo, self).__init__()
            # create the embedded graph
            graph = nx.Graph()
            graph.add_edges_from(args[0])
            self.nx_graph = graph
        else:
            raise ValueError('Input arguements not accepted.')


    def generate_DDF_topo(self, R, d): #Note that the k here includes host ports
        self.routers_per_group=(2*(d+1))//3
        if (2*(d+1))%3:
            raise ValueError("input DDF router radix wrong")
        intergroup_link_per_router=self.routers_per_group//2
        if self.routers_per_group%2:
            raise ValueError("input DDF router radix wrong")
        self.num_groups=self.routers_per_group*intergroup_link_per_router+1

        # Create a graph
        G = nx.Graph()

        # Add routers
        for group in range(self.num_groups):
            for router_in_group in range(self.routers_per_group):
                router_id = group * self.routers_per_group + router_in_group
                G.add_node(router_id, group=group, adjacency=dict()) 
                # adjacent_groups contains (core group id -> core router id)

        # Add intragroup links
        for group in range(self.num_groups):
            routers_in_group = list(range(group * self.routers_per_group, (group + 1) * self.routers_per_group))
            for src in routers_in_group:
                for dest in routers_in_group:
                    if src!=dest:
                        G.add_edge(src, dest, intergroup=False)

        next_router=[0]*self.num_groups #note that this is the relative router id in a group
        groups_to_connect=[]
        for i in range(self.num_groups):
            groups_to_connect.append([j for j in range(self.num_groups) if j!=i])
        # Add intergroup links
        for group in range(self.num_groups):
            while len(groups_to_connect[group])!=0:
                src_r = next_router[group]+group*self.routers_per_group
                dest_g = groups_to_connect[group].pop(0)
                groups_to_connect[dest_g].remove(group)
                dest_r = next_router[dest_g]+dest_g*self.routers_per_group
                next_router[group]=(next_router[group]+1)%self.routers_per_group
                next_router[dest_g]=(next_router[dest_g]+1)%self.routers_per_group
                assert(dest_r<R)
                assert(src_r<R)
                G.add_edge(src_r, dest_r, intergroup=True)
                G.nodes[src_r]["adjacency"][dest_g]=dest_r
                G.nodes[dest_r]["adjacency"][group]=src_r

        assert(mean([i[1] for i in list(G.degree)])==d)
        self.nx_graph=G
        return
    

    def DDF_unipath_routing(self):
        G=self.nx_graph
        vertices = G.nodes()
        vertex_pairs = [(v1, v2) for v1 in vertices for v2 in vertices if v1 != v2]
        paths_dict={}

        for (v1, v2) in vertex_pairs:
            paths_dict[(v1, v2)]=[]
            path=[]
            if G.nodes[v1]["group"]==G.nodes[v2]["group"]: # in the same group
                path=[v1, v2]
                assert(G.has_edge(v1, v2))
            else: # not in the same group
                if G.nodes[v2]["group"] in G.nodes[v1]["adjacency"].keys():
                    adjacent_r=G.nodes[v1]["adjacency"][G.nodes[v2]["group"]]
                    assert(G.has_edge(v1, adjacent_r))
                    if adjacent_r == v2:
                        path=[v1, v2]
                    else:
                        assert(G.nodes[v2]["group"]==G.nodes[adjacent_r]["group"] and G.has_edge(adjacent_r, v2))
                        path=[v1, adjacent_r, v2]
                else: #route to the correct router in the same group 
                    group_id=G.nodes[v1]["group"]
                    routers_in_group = list(range(group_id * self.routers_per_group, (group_id + 1) * self.routers_per_group))
                    next_router=-1
                    for r in routers_in_group:
                        if r != v1:
                            if G.nodes[v2]["group"] in G.nodes[r]["adjacency"].keys():
                                next_router=r
                                break
                    assert(next_router!=-1)
                    adjacent_r=G.nodes[next_router]["adjacency"][G.nodes[v2]["group"]]
                    if adjacent_r == v2:
                        path=[v1, next_router, adjacent_r]
                    else:
                        assert(G.nodes[v2]["group"]==G.nodes[adjacent_r]["group"] and G.has_edge(adjacent_r, v2))
                        path=[v1, next_router, adjacent_r, v2]
            paths_dict[(v1, v2)].append(path)
        
        return paths_dict, "DDFunipath"
    
        
    def set_intergroup_link_failures(self, failure_ratio, seed=0):
        random.seed(seed)
        G=self.nx_graph
        # Find edges with the desired attribute
        num_edges=len(G.edges())
        edges_to_delete = [(u, v) for u, v, attrs in G.edges(data=True) if attrs['intergroup'] == True]
        # Shuffle the list of edges to delete
        random.shuffle(edges_to_delete)
        # Select a random subset of edges to delete
        num_edges_to_delete = int(failure_ratio * num_edges)
        if num_edges_to_delete>len(edges_to_delete):
            raise ValueError("not enough intergroup links to delete!")
        
        edges_to_delete = edges_to_delete[:num_edges_to_delete]
        # Delete the selected edges
        G.remove_edges_from(edges_to_delete)
        print(f"{num_edges_to_delete} edge(s) has been deleted from inter-group edge list")
        if not nx.is_connected(G):
            raise ValueError("Graph is not connected after the deletions!")
        
        return

    def set_intragroup_link_failures(self, failure_ratio, seed=0):
        random.seed(seed)
        G=self.nx_graph
        # Find edges with the desired attribute
        num_edges=len(G.edges())
        edges_to_delete = [(u, v) for u, v, attrs in G.edges(data=True) if attrs['intergroup'] == False]
        # Shuffle the list of edges to delete
        random.shuffle(edges_to_delete)
        # Select a random subset of edges to delete
        num_edges_to_delete = int(failure_ratio * num_edges)
        if num_edges_to_delete>len(edges_to_delete):
            raise ValueError("not enough intergroup links to delete!")
        
        edges_to_delete = edges_to_delete[:num_edges_to_delete]
        # Delete the selected edges
        G.remove_edges_from(edges_to_delete)
        print(f"{num_edges_to_delete} edge(s) has been deleted from inter-group edge list")
        if not nx.is_connected(G):
            raise ValueError("Graph is not connected after the deletions!")
        
        return