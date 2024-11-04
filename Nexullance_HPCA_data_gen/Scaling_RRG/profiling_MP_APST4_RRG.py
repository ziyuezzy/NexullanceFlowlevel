import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.RRG import RRGtopo
from Nexullance_MP import Nexullance_MP
# from Nexullance_IT import Nexullance_IT
import globals as gl
import numpy as np
import time
import tracemalloc
import csv
import pickle

# this is a script to profile Nexullance_MP_APST4
# objectives: 
# 1. record result (\Phi) under several traffic patterns (uniform and shifts)
# 2. record time consumption
# 3. record maximum RAM

def main():
    # initialize output data file
    filename = f'data_RRG_MP_APST4.csv'

    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'traffic_pattern', 'Lcore_MAX_ECMP_APST4', 'Laccess_MAX_ECM_APST4', 'Phi_ECMP_APST4[GBps]', 'Lcore_NEXU_MP_APST4', 'Phi_NEXU[GBps]', 'init_time[s]', 'solving_time[s]', 'peak_RAM[MB]'])
        

        # configs = [(16, 5), (25, 6)]
        # configs = [(36, 7), (49, 8), (64, 9), (81, 10) , (100, 11)]
        configs = [(16, 5), (25, 6), (36, 7), (49, 8), (64, 9), (81, 10) , (100, 11)]
        for V, D in configs:
            # various traffic patterns
            traffic_pattern = "uniform"
            result = profile((V,D), traffic_pattern, 0)
            csvwriter.writerow([V, D, traffic_pattern, result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            
            EPR=(D+1)//2
            traffic_pattern = "shift"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            
            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            
            result = profile((V,D), traffic_pattern, EPR*V//2)
            csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            
            traffic_pattern = "diagonal"
            result = profile((V,D), traffic_pattern, EPR)
            csvwriter.writerow([V, D, traffic_pattern+"_1", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            
            result = profile((V,D), traffic_pattern, EPR*V//4)
            csvwriter.writerow([V, D, traffic_pattern+"_quater", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            
            # diagonal half is the same as shift half
            # result = profile((V,D), traffic_pattern, EPR*V//2)
            # csvwriter.writerow([V, D, traffic_pattern+"_half", result[0], result[1], result[2], result[3], result[4], result[5],result[6] , result[7]/1E6])
            
            csvfile.flush()
    return

def profile(config: tuple, traffic_pattern: str, _shift: int):
    EPR=(config[1]+1)//2
    _network = RRGtopo(config[0], config[1])
    Cap_core = 10 #GBps
    Cap_access = 10 #GBps
    M_EPs = None
    if traffic_pattern == "uniform":
        M_EPs = gl.generate_uniform_traffic_demand_matrix(config[0], EPR)
    elif traffic_pattern == "shift":
        M_EPs = gl.generate_shift_traffic_demand_matrix(config[0], EPR, _shift)
    elif traffic_pattern == "diagonal":
        M_EPs = gl.generate_diagonal_traffic_demand_matrix(config[0], EPR, _shift)
    else:
        raise ValueError("Invalidtraffic pattern name")


    # apply simple ECMP_ASP: (to make sure the input matrix for all nexu methods are the same)
    ASP, _ = _network.calculate_all_shortest_paths()
    ECMP_ASP = gl.ECMP(ASP)
    core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    max_core_link_load = np.max(core_link_flows)/Cap_core
    max_access_link_load = np.max(access_link_flows)/Cap_access
    # adapt the traffic scaling factor to 10x saturation
    traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
    M_EPs = traffic_scaling * M_EPs
    M_R = gl.convert_M_EPs_to_M_R(M_EPs, config[0], EPR)
    core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
    # max_core_link_load = np.max(core_link_flows)/Cap_core
    max_access_link_load = np.max(access_link_flows)/Cap_access
    # print("Max core link load: ", max_core_link_load)
    # print("Max access link load: ", max_access_link_load)
    # ECMP_ASP_Phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)


    # apply simple ECMP_MP_APST4:
    MP_APST4, _ = _network.calculate_all_paths_within_length(4)
    ECMP_MP_APST4 = gl.ECMP(MP_APST4)
    core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_MP_APST4, EPR, M_EPs)
    max_core_link_load_APST_4 = np.max(core_link_flows)/Cap_core
    max_access_link_load_APST_4 = np.max(access_link_flows)/Cap_access
    ECMP_MP_APST4_Phi=gl.network_total_throughput(M_EPs, max_core_link_load_APST_4, max_access_link_load_APST_4)


    tracemalloc.start()
    start_time = time.time()
    nexu = Nexullance_MP(_network.nx_graph, MP_APST4, M_R, Cap_core, 0, False)
    nexu.init_model()
    middle_time = time.time()
    Lcore_NEXU_MP_MP_APST4, _ = nexu.solve()
    # Lcore_NEXU_MP_MP_APST4, weighted_path_dict = nexu.solve()
    end_time = time.time()
    peak_RAM = tracemalloc.get_traced_memory()[1]
    Phi_NEXU_MP_MP_APST4 = gl.network_total_throughput(M_EPs, Lcore_NEXU_MP_MP_APST4, max_access_link_load)
    # pickle.dump(weighted_path_dict, open(f"./picked_path_dicts/Nexullance_MP_MP_APST4_RRG_{config[0]}_{config[1]}_{traffic_pattern}_{_shift}.pkl", "wb"))

    # current and peak memory usages are: {tracemalloc.get_traced_memory()} B")

    return [max_core_link_load_APST_4, max_access_link_load_APST_4, ECMP_MP_APST4_Phi, Lcore_NEXU_MP_MP_APST4, Phi_NEXU_MP_MP_APST4, middle_time - start_time, end_time - middle_time, peak_RAM]

if __name__ == '__main__':
    main()