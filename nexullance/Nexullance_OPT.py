import gurobipy as gp
from gurobipy import GRB
import networkx as nx
from global_helpers import access_link_flows_from_M_EPs, convert_M_EPs_to_M_R
import numpy as np

Graph = nx.graph.Graph

NUM_threads=1

from gurobi_license import gp_options

class Nexullance_OPT:
    def __init__(self, _nx_graph: Graph, _Cap_core: float, _Cap_access: float,  
                 num_routers:int = 0, _M_EPs:np.ndarray = np.ndarray([]),  _M_R: np.ndarray = np.ndarray([]), 
                 _solver:int=0, _verbose:bool=False):
        # assume uniform C^{core}
        '''   
        #LP solver options: 
        0: Automatic (solver chooses the method)
        1: Primal simplex
        2: Dual simplex
        3: Network simplex
        4: Barrier
        5: Concurrent (uses multiple methods)
        '''   
        
        # the input either has valid _M_R, or a valid combination of _M_EPs and num_routers
        if _M_R.size == 0:
            self.M_R = _M_R
            self.max_access_link_load = -1
        else:
            assert((num_routers > 0) and (_M_EPs.shape[0] > 0))
            self.M_R = convert_M_EPs_to_M_R(_M_EPs, num_routers, len(_M_EPs[0])//num_routers)
            self.max_access_link_load = max(access_link_flows_from_M_EPs(_M_EPs))/_Cap_access

         
        self.nx_graph: Graph = _nx_graph
        # although we use un-directed graph here, each link still has two loads on two directions
        self.solver: int = _solver
        self.verbose: bool = _verbose
        self.Cap_core: float = _Cap_core

        
        

    def init_model(self):
        self.s_d_pairs = [(s, d) for s in self.nx_graph.nodes() 
                            for d in self.nx_graph.nodes() if s != d]
        self.edge_list = list(self.nx_graph.edges())

        self.num_routers= self.nx_graph.number_of_nodes()
        assert(self.M_R.shape[0] == self.M_R.shape[1] == self.num_routers and \
                'traffic matrix shape is wrong, note that this should be a M_R traffic matrix!')
        
        _env = gp.Env(params=gp_options)
        _env.setParam('Threads', NUM_threads)
        self.model = gp.Model(env=_env)
        
        self.model.setParam(GRB.Param.OutputFlag, self.verbose)
        self.model.setParam(GRB.Param.Method, self.solver)
        self.model.setParam(GRB.Param.Crossover, 0)  
    
        # add variables and constraints
        self.link_share_var = {} # dict of dict, {link (i->j): {(s, d): share value}}. # 2*E*V^2 variables
        self.link_load_var = {} # 2*E variables, 
        link_load_expression = {} # 2*E constraints
        self.Max_load = self.model.addVar(vtype=GRB.CONTINUOUS, name='Max_load') # 2*E constraints
        for (i, j) in self.edge_list:
            self.link_load_var[(i, j)]=self.model.addVar(
                vtype=GRB.CONTINUOUS, name=f'link_load_({i},{j})')
            self.model.addConstr(self.link_load_var[(i, j)]<=self.Max_load)
            link_load_expression[(i, j)]=gp.LinExpr()
            link_load_expression[(i, j)]-=self.link_load_var[(i, j)]

            self.link_load_var[(j, i)]=self.model.addVar(
                vtype=GRB.CONTINUOUS, name=f'link_load_({j},{i})')
            self.model.addConstr(self.link_load_var[(j, i)]<=self.Max_load)
            link_load_expression[(j, i)]=gp.LinExpr()
            link_load_expression[(j, i)]-=self.link_load_var[(j, i)]

            self.link_share_var[(i, j)]={}
            self.link_share_var[(j, i)]={}
            for (s, d) in self.s_d_pairs:
                if s==d:
                    continue
                else:
                    self.link_share_var[(i, j)][(s, d)]=self.model.addVar(
                        vtype=GRB.CONTINUOUS, name=f'link_share^({s},{d})_({i},{j})')
                    self.link_share_var[(i, j)][(s, d)].setAttr(GRB.Attr.LB, 0.0)  # Lower bound
                    self.link_share_var[(i, j)][(s, d)].setAttr(GRB.Attr.UB, 1.0)  # Upper bound

                    self.link_share_var[(j, i)][(s, d)]=self.model.addVar(
                        vtype=GRB.CONTINUOUS, name=f'link_share^({s},{d})_({j},{i})')
                    self.link_share_var[(j, i)][(s, d)].setAttr(GRB.Attr.LB, 0.0)  # Lower bound
                    self.link_share_var[(j, i)][(s, d)].setAttr(GRB.Attr.UB, 1.0)  # Upper bound
                    
        for (s, d) in self.s_d_pairs: # flow conservation (V^3 linear constraints)
            for i in self.nx_graph.nodes():
                conservation=gp.LinExpr()
                for j in list(self.nx_graph.neighbors(i)):
                    assert(((i, j) in self.edge_list) or ((j, i) in self.edge_list))
                    conservation+=self.link_share_var[(i, j)][(s, d)]
                    conservation-=self.link_share_var[(j, i)][(s, d)]
                    link_load_expression[(i, j)]+=self.link_share_var[(i, j)][(s, d)]*self.M_R[s][d]/self.Cap_core
                if i == s:
                    conservation-=1
                if i == d:
                    conservation+=1

                self.model.addConstr(conservation==0)
                # flow_conservation.append(conservation)

        for linexp in link_load_expression.values():
            self.model.addConstr(linexp==0)

        # if max_access_link_load is given, set another constraint to limit the max link load
        if self.max_access_link_load > 0:
            self.model.addConstr(self.Max_load>=self.max_access_link_load)

        self.model.setObjective(self.Max_load, GRB.MINIMIZE)

    def solve(self):
        self.model.optimize()
        # traffic_shared = {} #{(s, d): {link (i->j): shared value}}
        result_link_loads={}
        if self.model.status == GRB.OPTIMAL:
            print("Optimal solution found")
            Max_load_result=self.Max_load.x
            if self.verbose:
                print("LP stats:")
                self.model.printStats() # only print out data if verbose
            # for (s, d) in self.s_d_pairs:
            #     traffic_shared[(s, d)]={}
            #     for (i, j) in self.edge_list:
            #         traffic_shared[(s, d)][(i, j)]=self.link_share_var[(i, j)][(s, d)].x
            #         traffic_shared[(s, d)][(j, i)]=self.link_share_var[(j, i)][(s, d)].x
            # for (u, v), load in self.link_load_var.items():
            #     result_link_loads[(u,v)]=load.x
                print(f'Max link load is: {self.Max_load.x}')

            return Max_load_result
            # return traffic_shared, result_link_loads, Max_load_result
        
        else:
            print("LP failed, possible infeasibility or unboundedness")
            self.model.setParam(GRB.Param.OutputFlag, 1)
            self.model.printStats()
            return None