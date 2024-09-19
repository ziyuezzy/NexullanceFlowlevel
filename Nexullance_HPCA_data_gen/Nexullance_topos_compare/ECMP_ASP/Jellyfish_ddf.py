# TODO: first, try to compute ECMP_ASP for different sizes of DDF under a set of
# traffic demand matrices, then compare "Network throughput per EP"

# Then, calculate the average and standard deviation of the "Network throughput" 
# for different sizes of DDF under the same set of traffic demand matrices.

import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../../..')))
from topologies.RRG import RRGtopo
import globals as gl
import numpy as np
import csv


Cap_core = 10 #GBps
Cap_access = 10 #GBps

def main():
    # initialize output data file
    filename = f'RRG_ddf.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['V', 'D', 'EPR', 'traffic', 'Phi', 'Phi_per_EP', 'mu'])

        configs = gl.ddf_configs
        for V, D in configs:
            # various traffic patterns
            EPR = (D+1)//2

            _network = RRGtopo(V, D)
            ASP, _ = _network.calculate_all_shortest_paths()
            ECMP_ASP = gl.ECMP(ASP)

            traffic_pattern = "uniform"
            M_EPs = gl.generate_uniform_traffic_pattern(V, EPR)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            Phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), max_access_link_load/max_core_link_load])
            csvfile.flush()

            traffic_pattern = "nearst-neighbour"
            M_EPs = gl.generate_diagonal_traffic_pattern(V, EPR, 1)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            Phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), max_access_link_load/max_core_link_load])
            csvfile.flush()

            traffic_pattern = "shift_1"
            M_EPs = gl.generate_shift_traffic_pattern(V, EPR, 1)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            Phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), max_access_link_load/max_core_link_load])
            csvfile.flush()

            traffic_pattern = "shift_half"
            M_EPs = gl.generate_shift_half_traffic_pattern(V, EPR)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            Phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), max_access_link_load/max_core_link_load])
            csvfile.flush()

            traffic_pattern = "router-cluster"
            M_EPs = gl.generate_uniform_cluster_pattern(V, EPR, 4) # four clusters
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            Phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), max_access_link_load/max_core_link_load])
            csvfile.flush()

            traffic_pattern = "random-permute"
            M_EPs = gl.generate_random_permutation_pattern(V, EPR, 0)
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            # adapt the traffic scaling factor to 10x saturation
            traffic_scaling = 10.0/max(max_access_link_load, max_core_link_load)
            M_EPs = traffic_scaling * M_EPs
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
            max_core_link_load = np.max(core_link_flows)/Cap_core
            max_access_link_load = np.max(access_link_flows)/Cap_access
            Phi=gl.network_total_throughput(M_EPs, max_core_link_load, max_access_link_load)
            csvwriter.writerow([V, D, EPR, traffic_pattern, Phi, Phi/(V*EPR), max_access_link_load/max_core_link_load])
            csvfile.flush()



if __name__ == '__main__':
    main()
