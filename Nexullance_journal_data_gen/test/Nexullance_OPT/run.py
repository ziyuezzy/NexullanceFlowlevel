import os
import sys
sys.path.append(os.path.abspath(os.path.join(os.getcwd(), '../..')))
sys.path.append("/users/ziyzhang/topology-research/")
import globals as gl
import numpy as np
import csv
from nexullance.ultility import nexullance_exp_container

ddf_configs=[(6, 2), (36, 5)]
slimfly_configs=[(18, 5), (32, 6)]
polarfly_configs=[(7, 3), (13, 4), (21, 5), (31, 6)]

Cap_core = 10 #GBps
Cap_access = 10 #GBps

def main():

    Topo_config=dict()
    Topo_config["DDF"] = ddf_configs
    Topo_config["Slimfly"] = slimfly_configs
    Topo_config["Polarfly"] = polarfly_configs

    for topo_name, configs in Topo_config.items():
        filename = f'{topo_name}.csv'
        with open(filename, 'w', newline='') as csvfile:
            csvwriter = csv.writer(csvfile)
            csvwriter.writerow(['V', 'D', 'EPR', 'traffic', 'phi'])
            for V, D in configs:
                EPR = (D+1)//2
                exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core, Cap_access)
                
                # define traffic patterns
                Demand_matrices=dict()
                Demand_matrices["uniform"]=gl.generate_uniform_traffic_demand_matrix(V, EPR)
                Demand_matrices["shift_half"]=gl.generate_shift_half_traffic_demand_matrix(V, EPR)
                for traffic_name, M_EPs in Demand_matrices.items():
                    result_phi = exp_container.run_nexullance_OPT( M_EPs, traffic_name)
                    if result_phi:
                        csvwriter.writerow([V, D, EPR, traffic_name, result_phi])
                        csvfile.flush()


if __name__ == '__main__':
    main()
