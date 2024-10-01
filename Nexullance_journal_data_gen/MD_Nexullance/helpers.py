import os
import sys
sys.path.append("/users/ziyzhang/topology-research")
from topologies import HPC_topo
import globals as gl
import numpy as np

def gen_M_EPs_s(topo_name: str, V:int, D:int, EPR:int, M_names:list[str], scaling_factor:float=0.0, Cap_core:int=10, Cap_access:int=10):
    
    _network = HPC_topo.HPC_topo.initialize_child_instance(topo_name+"topo", V, D)
    result=[]

    for M_name in M_names:
        temp_M = None
        if M_name == "uniform":
            temp_M=gl.generate_uniform_traffic_demand_matrix(V, EPR)
        elif M_name=="half_shift":
            temp_M=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
        elif M_name.startswith("shift"):# if the name contains "shift"
            temp_M=gl.generate_shift_traffic_demand_matrix(V, EPR, int(M_name.split("_")[1]))
        else: # other names are not supported yet
            print(f"Error: {M_name} not implemented yet")
        
        if scaling_factor!= 0.0:
            # try to scale the traffic demand matrix
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(_network.ECMP_ASP, EPR, temp_M)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            traffic_scaling = scaling_factor/max(max_access_link_load, max_core_link_load)
            temp_M = traffic_scaling * temp_M
        result.append(temp_M)
    return result
