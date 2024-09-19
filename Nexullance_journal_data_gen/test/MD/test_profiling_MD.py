import os
import sys
sys.path.append("/users/ziyzhang/topology-research/")
from topologies.DDF import DDFtopo
import globals as gl
import numpy as np
import csv
from nexullance.ultility import nexullance_exp_container
# import pickle

Cap_core = 10 #GBps
Cap_access = 10 #GBps

def main():
    config = gl.ddf_configs[0]
    V = config[0]
    D = config[1]
    EPR = (D+1)//2
    _network = DDFtopo(V, D)
    _network.pre_calculate_ECMP_ASP()
    _network.pre_calculate_APST_n(4)
    M_EPs_s = []
    ECMP_ASP_phis = []
    M_EPs_names=[]
    # # # Define multiple traffic demand matrices:
    # # shifts
    for _shift in range(1, V*EPR):
    # for _shift in range(1, 5):
        M_EPs = gl.generate_shift_traffic_pattern(V, EPR, _shift)
        # try to scale the traffic scaling factor to 10x saturation under ECMP_ASP
        core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(_network.ECMP_ASP, EPR, M_EPs)
        max_core_link_load = np.max(core_link_flows)/Cap_core
        max_access_link_load = np.max(access_link_flows)/Cap_access
        traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
        M_EPs = traffic_scaling * M_EPs
        # calculate phi for ECMP_ASP routing
        core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(_network.ECMP_ASP, EPR, M_EPs)
        max_core_link_load = np.max(core_link_flows)/Cap_core
        max_access_link_load = np.max(access_link_flows)/Cap_access
        ECMP_ASP_phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)/(V*EPR)
        ECMP_ASP_phis.append(ECMP_ASP_phi)
        # ==============

        # manage data
        M_EPs_s.append(M_EPs)
        # M_Rs.append(M_R)
        # max_access_link_loads.append(max_access_link_load)
        M_EPs_names.append(f"shift_{_shift}")

    M_EPs_weights = [1/len(M_EPs_s) for _ in range(len(M_EPs_s))]

    MD_MP_container = nexullance_exp_container("DDF", V, D, EPR)
    # calculate phi for MD_Nexullance_MP_APST4 routing
    MD_MP_result = MD_MP_container.run_and_profile_MD_nexullance_IT(M_EPs_s, M_EPs_weights, repetitions=1)
    

if __name__ == '__main__':
    main()