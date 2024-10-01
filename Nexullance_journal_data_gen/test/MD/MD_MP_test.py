import os
import sys
sys.path.append("/users/ziyzhang/topology-research/")
from topologies.DDF import DDFtopo
import globals as gl
import numpy as np
import csv
from nexullance.ultility import nexullance_exp_container
import pickle

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
        M_EPs = gl.generate_shift_traffic_demand_matrix(V, EPR, _shift)
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
    MD_MP_result = MD_MP_container.run_MD_nexullance_MP(M_EPs_s, M_EPs_weights, 4)

    print("resulting objective function = ", MD_MP_result[0]) # TODO: validate objective function from MD_MP
    MD_MP_phis = MD_MP_result[1]

    # print("validated objective function = ", gl.cal_MD_obj_func(MD_MP_phis,M_EPs_weights)) # TODO: validate objective function from MD_MP
    
    # pickle output routing tables
    # routing_name = f"MD_NEXU_MP_APST_4_all_shifts"
    # pathdict_file=f"{routing_name}_({V},{D})DDFtopo_paths.pickle"
    # with open(pathdict_file, 'wb') as handle:
    #     pickle.dump(gl.clean_up_weighted_paths(weight_path_dict), handle)
    #====================================

    filename = f'DDF_{V}_{D}_MD_MP_all_shifts.csv'
    # save data to csv file
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'included_M_R', 'M_R_weight', 'phi_ECMP_ASP', 
                            'phi_MD_MP'])
        csvfile.flush()
        for i in range(len(M_EPs_s)):
            csvwriter.writerow([V, D, M_EPs_names[i], M_EPs_weights[i], ECMP_ASP_phis[i], 
                                MD_MP_phis[i]])

if __name__ == '__main__':
    main()