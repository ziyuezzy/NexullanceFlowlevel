# TODO: first, try to compute ECMP_ASP for different sizes of DDF under a set of
# traffic demand matrices, then compare "Network throughput per EP"

# Then, calculate the average and standard deviation of the "Network throughput" 
# for different sizes of DDF under the same set of traffic demand matrices.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.DDF import DDFtopo
from nexullance.Nexullance_IT import Nexullance_IT
import globals as gl
import numpy as np
import csv


Cap_core = 10 #GBps
Cap_access = 10 #GBps
alpha_1 = 1
beta_1 = 1
alpha_2 = 0.1
beta_2 = 7
def weighted_method_1(s: int, d: int, edge_attributes: dict):
    return alpha_1 + edge_attributes['load']**beta_1
def weighted_method_2(s: int, d: int, edge_attributes: dict):
    return alpha_2 + edge_attributes['load']**beta_2

def main():
    # initialize output data file
    filename = f'DDF.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'EPR', 'traffic', 'Phi', 'Phi_per_EP', 'i_conv'])

        configs = gl.ddf_configs
        for V, D in configs:
            # various traffic patterns
            EPR = (D+1)//2

            _network = DDFtopo(V, D)
            ASP, _ = _network.calculate_all_shortest_paths()
            ECMP_ASP = gl.ECMP(ASP)

            traffic_pattern = "uniform"
            M_EPs = gl.generate_uniform_traffic_demand_matrix(V, EPR)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            nexu = Nexullance_IT(_network.nx_graph, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_core)
            _, _ = nexu.optimize(1, 6, weighted_method_1, weighted_method_2, V)
            Lcore_NEXU = nexu.get_result_max_link_load()
            Phi = gl.network_total_throughput(M_EPs, Lcore_NEXU, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu.get_method_2_attempts()])
            csvfile.flush()

            traffic_pattern = "nearst-neighbour"
            M_EPs = gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            nexu = Nexullance_IT(_network.nx_graph, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_core)
            _, _ = nexu.optimize(1, 6, weighted_method_1, weighted_method_2, V)
            Lcore_NEXU = nexu.get_result_max_link_load()
            Phi = gl.network_total_throughput(M_EPs, Lcore_NEXU, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu.get_method_2_attempts()])
            csvfile.flush()

            traffic_pattern = "shift_1"
            M_EPs = gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            nexu = Nexullance_IT(_network.nx_graph, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_core)
            _, _ = nexu.optimize(1, 6, weighted_method_1, weighted_method_2, V)
            Lcore_NEXU = nexu.get_result_max_link_load()
            Phi = gl.network_total_throughput(M_EPs, Lcore_NEXU, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu.get_method_2_attempts()])
            csvfile.flush()

            traffic_pattern = "shift_half"
            M_EPs = gl.generate_shift_half_traffic_demand_matrix(V, EPR)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            nexu = Nexullance_IT(_network.nx_graph, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_core)
            _, _ = nexu.optimize(1, 6, weighted_method_1, weighted_method_2, V)
            Lcore_NEXU = nexu.get_result_max_link_load()
            Phi = gl.network_total_throughput(M_EPs, Lcore_NEXU, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu.get_method_2_attempts()])
            csvfile.flush()

            traffic_pattern = "router-cluster"
            M_EPs = gl.generate_uniform_cluster_demand_matrix(V, EPR, 4) # four clusters
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            nexu = Nexullance_IT(_network.nx_graph, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_core)
            _, _ = nexu.optimize(1, 6, weighted_method_1, weighted_method_2, V)
            Lcore_NEXU = nexu.get_result_max_link_load()
            Phi = gl.network_total_throughput(M_EPs, Lcore_NEXU, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu.get_method_2_attempts()])
            csvfile.flush()

            traffic_pattern = "random-permute"
            M_EPs = gl.generate_random_permutation_demand_matrix(V, EPR, 0)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            nexu = Nexullance_IT(_network.nx_graph, gl.convert_M_EPs_to_M_R(M_EPs, V, EPR), Cap_core)
            _, _ = nexu.optimize(1, 6, weighted_method_1, weighted_method_2, V)
            Lcore_NEXU = nexu.get_result_max_link_load()
            Phi = gl.network_total_throughput(M_EPs, Lcore_NEXU, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), nexu.get_method_2_attempts()])
            csvfile.flush()



if __name__ == '__main__':
    main()
