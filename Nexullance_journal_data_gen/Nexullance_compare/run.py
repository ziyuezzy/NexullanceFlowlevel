import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')))
import global_helpers as gl
import numpy as np
import csv
from nexullance.ultility import nexullance_exp_container

ddf_configs=[config for config in gl.ddf_configs]
slimfly_configs=[config for config in gl.sf_configs]
polarfly_configs=[config for config in gl.pf_regular_configs]

Cap_core = 10 #GBps
Cap_access = 10 #GBps

num_rep = 5

def main():

    Topo_config=dict()
    Topo_config["DDF"] = ddf_configs
    Topo_config["Slimfly"] = slimfly_configs
    Topo_config["Polarfly"] = polarfly_configs
    Topo_config["RRG"] = sorted(ddf_configs + slimfly_configs + polarfly_configs)

    filename = f'ECMP_ASP.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'ave_phi'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core=Cap_core, Cap_access=Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result_phi = exp_container.run_ECMP_SP(M_EPs)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, result_phi])
                    csvfile.flush()

    filename = f'ECMP_8SP.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'ave_phi'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core=Cap_core, Cap_access=Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result_phi = exp_container.run_ECMP_SP(M_EPs, 8)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, result_phi])
                    csvfile.flush()


    filename = f'Nexullance_IT.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'ave_phi', 'std_phi', 'ave_time[s]', 'std_time[s]', 
                            'ave_PeakRAM[B]', 'std_PeakRAM[B]'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core=Cap_core, Cap_access=Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result = exp_container.run_and_profile_nexullance_IT(M_EPs, traffic_name, num_rep)
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
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core=Cap_core, Cap_access=Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result = exp_container.run_and_profile_nexullance_MP(4, M_EPs, traffic_name, num_rep)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, result["ave_phi"], result["std_phi"],
                                        result["ave_time[s]"], result["std_time[s]"], result["ave_PeakRAM[B]"], result["std_PeakRAM[B]"]])
                    csvfile.flush()

    filename = f'Nexullance_MP_ASP.csv'
    with open(filename, 'w', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(['topo', 'V', 'D', 'EPR', 'traffic', 'ave_phi', 'std_phi', 'ave_time[s]', 'std_time[s]', 
                            'ave_PeakRAM[B]', 'std_PeakRAM[B]'])

        for topo_name, configs in Topo_config.items():
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core=Cap_core, Cap_access=Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result = exp_container.run_and_profile_nexullance_MP(0, M_EPs, traffic_name, num_rep)
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
                if V > 50: # skip large networks for this formulation.
                    continue
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core=Cap_core, Cap_access=Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift-half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                Demand_matrices["nearst-neighbour"]=gl.generate_diagonal_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["shift-1"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 1)
                Demand_matrices["router-cluster"]=gl.generate_uniform_cluster_demand_matrix(V, EPR, 4)
                Demand_matrices["random-permute"]=gl.generate_shift_traffic_demand_matrix(V, EPR, 0)

                for traffic_name, M_EPs in Demand_matrices.items():
                    result = exp_container.run_and_profile_nexullance_OPT(M_EPs, traffic_name, num_rep)
                    csvwriter.writerow([topo_name, V, D, EPR, traffic_name, result["ave_phi"], result["std_phi"],
                                        result["ave_time[s]"], result["std_time[s]"], result["ave_PeakRAM[B]"], result["std_PeakRAM[B]"]])
                    csvfile.flush()


if __name__ == '__main__':
    main()
