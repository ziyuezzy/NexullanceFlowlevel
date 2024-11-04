import os
import sys
sys.path.append("/users/ziyzhang/topology-research/")
import globals as gl
import numpy as np
import csv
from nexullance.ultility import nexullance_exp_container
from topologies.HPC_topo import HPC_topo

# ddf_configs=[config for config in gl.ddf_configs if config[0]<=36]
# slimfly_configs=[config for config in gl.sf_configs if config[0]<=36]
# polarfly_configs=[config for config in gl.pf_regular_configs if config[0]<=36]

Cap_core = 10 #GBps
Cap_access = 10 #GBps

def main():

    Topo_config=dict()
    # Topo_config["DDF"] = ddf_configs
    # Topo_config["Slimfly"] = slimfly_configs
    # Topo_config["Polarfly"] = polarfly_configs
    Topo_config["RRG"] = [(4, 3), (4, 2)]

    filename = f'Nexullance_IT.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'ave_phi', 'std_phi', 'ave_time[s]', 'std_time[s]', 
                            'ave_PeakRAM[B]', 'std_PeakRAM[B]'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core, Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                # Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 2)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result = exp_container.run_and_profile_nexullance_IT(M_EPs, traffic_name)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, result["ave_phi"], result["std_phi"],
                                        result["ave_time[s]"], result["std_time[s]"], result["ave_PeakRAM[B]"], result["std_PeakRAM[B]"]])
                    csvfile.flush()

    filename = f'Nexullance_MP_APST_4.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'ave_phi', 'std_phi', 'ave_time[s]', 'std_time[s]', 
                            'ave_PeakRAM[B]', 'std_PeakRAM[B]'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core, Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                # Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result = exp_container.run_and_profile_nexullance_MP(4, M_EPs, traffic_name)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, result["ave_phi"], result["std_phi"],
                                        result["ave_time[s]"], result["std_time[s]"], result["ave_PeakRAM[B]"], result["std_PeakRAM[B]"]])
                    csvfile.flush()

    filename = f'Nexullance_OPT.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'ave_phi', 'std_phi', 'ave_time[s]', 'std_time[s]', 
                            'ave_PeakRAM[B]', 'std_PeakRAM[B]'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core, Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                # Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result = exp_container.run_and_profile_nexullance_OPT(M_EPs, traffic_name)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, result["ave_phi"], result["std_phi"],
                                        result["ave_time[s]"], result["std_time[s]"], result["ave_PeakRAM[B]"], result["std_PeakRAM[B]"]])
                    csvfile.flush()

    filename = f'ECMP_ASP.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'phi', 'max core load', 'max access load'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                # Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                _network = HPC_topo.initialize_child_instance(topo_name+"topo", V, D)
                _network.pre_calculate_ECMP_ASP()

                for traffic_name, M_EPs in Demand_matrices.items():

                    # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
                    core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(_network.ECMP_ASP, EPR, M_EPs)
                    traffic_scaling = 10/max(np.max(core_link_flows)/Cap_core, np.max(access_link_flows)/Cap_access)
                    scaled_M_EPs = traffic_scaling * M_EPs
                    # re-calculate after scaling
                    core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(_network.ECMP_ASP, EPR, scaled_M_EPs)
                    ECMP_ASP_max_core_link_load = np.max(core_link_flows)/Cap_core
                    ECMP_ASP_max_access_link_load = np.max(access_link_flows)/Cap_access
                    ECMP_ASP_phi = gl.network_total_throughput(M_EPs, ECMP_ASP_max_core_link_load, ECMP_ASP_max_access_link_load)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, ECMP_ASP_phi,  ECMP_ASP_max_core_link_load, ECMP_ASP_max_access_link_load])
                    csvfile.flush()



if __name__ == '__main__':
    main()
