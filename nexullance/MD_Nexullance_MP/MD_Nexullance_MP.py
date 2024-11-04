import gurobipy as gp
from gurobipy import GRB
import networkx as nx
import numpy as np
from globals import access_link_flows_from_M_EPs, convert_M_EPs_to_M_R, network_total_throughput

Graph = nx.graph.Graph

NUM_threads=1

gp_options = {
    "WLSACCESSID": "6f6ff6a8-32e2-447d-b681-592b24fc09d1",
    "WLSSECRET": "333995b6-ce3f-4053-b4bf-7dcdb2b167df",
    "LICENSEID": 2411299,
}

class MD_Nexullance_MP:
    # This is a version of Nexullance_MP that optimize the routing table accroding to many different inter-router traffic demand matrices
    # Each traffic demand matrix has a weight in the cost function. The sum of all weights is 1.
    def __init__(self, _nx_graph: Graph, path_dict: dict, _Cap_core: float, _Cap_access: float, _V:int, 
                 _M_EPs_s: list[np.ndarray], _M_EP_weights: list[float], _solver:int=0, _verbose:bool=False):
        # assume uniform C^{core}
        #LP solver options:
        '''    
        0: Automatic (solver chooses the method)
        1: Primal simplex
        2: Dual simplex
        3: Network simplex
        4: Barrier
        5: Concurrent (uses multiple methods)
        '''    
        self.nx_graph: Graph = _nx_graph 
        # although we use un-directed graph here, each link still has two loads on two directions as in line 57,59
        self.M_EPs_s: list[np.ndarray] = _M_EPs_s # this is list of list of list, each sub-list is a traffic demand matrix
        self.M_EP_weights: list[float] = _M_EP_weights
        assert(len(self.M_EPs_s) == len(self.M_EP_weights) and 'length of M_R_weights should be the same as length of M_Rs')
        self.solver: int = _solver
        self.verbose: bool = _verbose
        self.Cap_core: float = _Cap_core
        self.Cap_access: float = _Cap_access
        self.path_dict: dict = path_dict
        self.V = _V

        self.max_access_link_loads = []
        self.M_Rs = []
        # self.phis = []
        # self.weighted_phi: float = 0.0

        for m, M_EPs in enumerate(self.M_EPs_s):
            self.M_Rs.append(convert_M_EPs_to_M_R(M_EPs, self.V, len(M_EPs[0])//self.V))
            self.max_access_link_loads.append(max(access_link_flows_from_M_EPs(M_EPs))/_Cap_access)



    def init_model(self, EPR):
        num_routers=(1+pow(1+4*len(self.path_dict), 0.5))/2
        assert(num_routers==self.nx_graph.number_of_nodes() and 'length of path_dict should be N*(N-1), N is the number of routers')
        assert(len(self.M_EPs_s[0])==len(self.M_EPs_s[0][0])==num_routers*EPR and \
                'traffic matrix shape is wrong, note that this should be a M_EPs traffic matrix!')
        self.edge_list = list(self.nx_graph.edges())
        
        _env = gp.Env(params=gp_options)
        _env.setParam('Threads', NUM_threads)
        self.model = gp.Model(env=_env)
        self.model.setParam(GRB.Param.OutputFlag, self.verbose)
        self.model.setParam(GRB.Param.Method, self.solver)
        self.model.setParam(GRB.Param.Crossover, 0)  

        # add variables and constraints
        self.path_prob = {}
        link_load_var = []
        link_load_constr = []
        self.max_loads = []
        self.Objective_func = self.model.addVar(vtype=GRB.CONTINUOUS, name='self.Objective_func') # weighted average across all input M_Rs
        for m in range(len(self.M_Rs)):
            link_load_var.append({})
            link_load_constr.append({})
            self.max_loads.append(self.model.addVar(vtype=GRB.CONTINUOUS, name=f'max_load_{m}'))
            for (u,v) in self.edge_list:
                link_load_var[m][(u, v)]=self.model.addVar(vtype=GRB.CONTINUOUS, name=f'link_load_({u},{v})')
                link_load_constr[m][(u, v)]= gp.LinExpr()
                link_load_var[m][(v, u)]=self.model.addVar(vtype=GRB.CONTINUOUS, name=f'link_load_({v},{u})')
                link_load_constr[m][(v, u)]= gp.LinExpr()

        normalization_constr={}
        unique_path_id=0
        for (s, d), paths in self.path_dict.items():
            if len(paths)>1: 
                normalization_constr[(s, d)]=gp.LinExpr()

            for path in paths:      
                if len(paths)>1:  
                    self.path_prob[unique_path_id]=self.model.addVar(vtype=GRB.CONTINUOUS, name=f'path_prob_({s}, {d})_{unique_path_id}')

                    self.path_prob[unique_path_id].setAttr(GRB.Attr.LB, 0)  # Lower bound
                    self.path_prob[unique_path_id].setAttr(GRB.Attr.UB, 1.0)  # Upper bound
                else:
                    self.path_prob[unique_path_id]=1.0

                if len(paths)>1: 
                    normalization_constr[(s, d)]+=self.path_prob[unique_path_id]
                for i in range(len(path) - 1):
                    vertex1, vertex2 = path[i], path[i + 1]
                    for m, M_R in enumerate(self.M_Rs):
                        link_load_constr[m][(vertex1, vertex2)]+= self.path_prob[unique_path_id]*M_R[s][d]/self.Cap_core
                unique_path_id+=1

        for m in range(len(self.M_Rs)):
            for (u, v), linexp in link_load_constr[m].items():
                self.model.addConstr(linexp==link_load_var[m][(u, v)])
                self.model.addConstr(self.max_loads[m]>=link_load_var[m][(u, v)])
            self.model.addConstr(self.max_loads[m]>=self.max_access_link_loads[m])
        for linexp in normalization_constr.values():
            self.model.addConstr(linexp==1.0)

        # define the weighted max load as a weighted average from all input M_Rs
        Objective_func_exp=gp.LinExpr()
        for m, max_load in enumerate(self.max_loads):
            Objective_func_exp += max_load*self.M_EP_weights[m]/(np.sum(self.M_EPs_s[m]))
        self.model.addConstr(self.Objective_func==Objective_func_exp)

        # print(f'number of variables = {len(self.path_prob)+len(link_load_var)}, number of constraints = {len(link_load_constr)+len(normalization_constr)}')
        # Set objective
        self.model.setObjective(self.Objective_func, GRB.MINIMIZE)

    def get_Objective_func(self):
        if self.model.status == GRB.OPTIMAL:
            if self.Objective_func.X == 0:
                print("Warning: objective function is 0??")
                return 0.0 # to avoid numerical error
            
            # assert(self.Objective_func.X > 0)
            return 1/self.Objective_func.X # a harmonic mean of network data throughput
        else:
            raise Exception("did not solve LP, or LP failed")
    
    def solve(self):
        self.model.optimize()
        # traffic_shared = {} #{(s, d): {link (i->j): shared value}}
        all_weighted_paths={}
        if self.model.status == GRB.OPTIMAL:
            print("Optimal solution found")
            # Max_load_result=self.Objective_func.x
            # if self.verbose:
            #     print("LP stats:")
            #     self.model.printStats() # only print out data if verbose
            #     print(f'Max link load is: {self.Objective_func.x}')

            Max_load_results = []
            for m, max_load in enumerate(self.max_loads):
                Max_load_results.append(max_load.x)
                if self.verbose:
                    print(f'Max link load for M_R {m} is: {max_load.x}')

            unique_path_id=0
            for (s,d), paths in self.path_dict.items():
                all_weighted_paths[(s, d)]=[]
                for path in paths:
                    if len(paths)>1:
                        all_weighted_paths[(s, d)].append( (path, self.path_prob[unique_path_id].x) )
                    else:
                        all_weighted_paths[(s, d)].append( (path, 1.0) )
                    unique_path_id+=1
            return Max_load_results, all_weighted_paths
            # return traffic_shared, result_link_loads, Max_load_result
        
        else:
            self.model.setParam(GRB.Param.OutputFlag, 1)
            self.model.printStats()
            raise Exception("LP failed")