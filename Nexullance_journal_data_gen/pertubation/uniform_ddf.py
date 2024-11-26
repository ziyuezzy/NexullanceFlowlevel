import sys
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(os.path.abspath(__file__)), '../..')))
import global_helpers as gl
import numpy as np
import csv
from nexullance.ultility import nexullance_exp_container
from topologies import HPC_topo
from nexullance import Nexullance_MP

Cap_core = 10 #GBps
Cap_access = 10 #GBps

def main():
    topo_name = "DDF"
    (V,D) = gl.ddf_configs[0]
    EPR = (D+1)//2
    exp_container = nexullance_exp_container(topo_name, V, D, EPR, Cap_core, Cap_access)
    baseline_M = gl.generate_uniform_traffic_demand_matrix(V, EPR) # the baseline matrix, here it is uniform
    # perturbation_rates=[0.01, 0.02, 0.04]
    perturbation_rates=[0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
    perturbated_Ms={key:[] for key in perturbation_rates}
    num_rep = 10 # number of repetitions, the number of perturbation to make per data point
    for rate in perturbated_Ms:
        for i in range(num_rep):
            perturbated_Ms[rate].append(gl.perturbate_gaussian(baseline_M, rate))
    perturbated_Ms[0.0]=[baseline_M]
    
    # apply Nexullance_MP_APST4 on each of the traffic demand matrix
    Nexullance_MP_APST_phis = {key: [] for key in perturbated_Ms}
    for rate, M_list in perturbated_Ms.items():
        for M in M_list:
            result = exp_container.run_nexullance_MP(4, M, f"perturbation_rate_{rate}")
            Nexullance_MP_APST_phis[rate].append(result[0])

    # apply ECMP_ASP and Nexullance_MP_APST4(uniform) on each of the traffic demand matrix
    ECMP_ASP_phis = {key: [] for key in perturbated_Ms}
    Nexullance_MP_APST_uniform_phis = {key: [] for key in perturbated_Ms}
    # calculate the routing table of Nexullance_MP_APST4 for 'uniform'
    _network = HPC_topo.HPC_topo.initialize_child_instance(topo_name+"topo", V, D)
    _network.pre_calculate_ECMP_ASP()
    _network.pre_calculate_APST_n(4)
    nexu = Nexullance_MP.Nexullance_MP(_network.nx_graph, _network.__getattribute__(f"APST_{4}") ,
                                        Cap_core, Cap_access, V, baseline_M)
    nexu.init_model()
    _, MP_APST4_RT = nexu.solve()
    for rate, M_list in perturbated_Ms.items():
        for M in M_list:
            # apply this routing table on all traffic demand matrices
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(MP_APST4_RT, EPR, M)
            # calculate phi
            Nexullance_MP_APST_uniform_phis[rate].append(gl.network_total_throughput(M, max(core_link_flows)/Cap_core, max(access_link_flows)/Cap_access)/(V*EPR))
  
            # apply ECMP_ASP routing table on all traffic demand matrices
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(_network.ECMP_ASP, EPR, M)
            # calculate phi
            ECMP_ASP_phis[rate].append(gl.network_total_throughput(M, max(core_link_flows)/Cap_core, max(access_link_flows)/Cap_access)/(V*EPR))
        # =================================================================

    # apply MD_Nexullance on this group of traffic demand matrices
    # first 'train' a routing table for a different set of perturbated matrices
    perturbated_Ms_train_set={key:[] for key in perturbation_rates}
    for rate in perturbated_Ms_train_set:
        for i in range(num_rep):
            perturbated_Ms_train_set[rate].append(gl.perturbate_gaussian(baseline_M, rate))
    perturbated_Ms_train_set[0.0]=[baseline_M]

    MD_MP_phis_training = {key: [] for key in perturbated_Ms_train_set}
    MD_MP_RT = dict()
    for rate, M_list in perturbated_Ms_train_set.items():
        if rate == 0.0:
            MD_MP_phis_training[rate]=["NAN"]
            continue
        M_weights = [1/num_rep for i in range(num_rep)]
        result = exp_container.run_MD_nexullance_MP_return_RT(M_list, M_weights, 4)
        MD_MP_RT = gl.clean_up_weighted_paths( result[1] )
        MD_MP_phis_training[rate]=result[0]

    MD_MP_phis_verification = {key: [] for key in perturbated_Ms_train_set}
    for rate, M_list in perturbated_Ms.items():
        for M in M_list:
            # apply this routing table on all traffic demand matrices
            core_link_flows, access_link_flows = _network.distribute_M_EPs_on_weighted_paths(MD_MP_RT, EPR, M)
            # calculate phi
            MD_MP_phis_verification[rate].append(gl.network_total_throughput(M, max(core_link_flows)/Cap_core, max(access_link_flows)/Cap_access)/(V*EPR))
    MD_MP_phis_verification[0.0]=["NAN"]

    # now train on the verification set
    MD_MP_phis_trained_on_verification_set = {key: [] for key in perturbated_Ms}
    for rate, M_list in perturbated_Ms.items():
        if rate == 0.0:
            MD_MP_phis_trained_on_verification_set[rate]=["NAN"]
            continue
        M_weights = [1/num_rep for i in range(num_rep)]
        result = exp_container.run_MD_nexullance_MP(M_list, M_weights, 4)
        MD_MP_phis_trained_on_verification_set[rate]=result[1]


    # write to csv file 1:
    csv_cols = ['V', 'D', 'perturbation_rate', 'repetition_id', 'MD_MP_phis_training', 
                'Nexullance_MP_APST_uniform_phis', 'ECMP_ASP_phis']
    filename = f'{topo_name}_{V}_{D}_uniform_perturbation.csv'
    # save data to csv file
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(csv_cols)
        csvfile.flush()
        for rate, M_list in perturbated_Ms.items():
            for repetition_id in range(len(M_list)):
                csvwriter.writerow([ V, D, rate, repetition_id, Nexullance_MP_APST_phis[rate][repetition_id], 
                    Nexullance_MP_APST_uniform_phis[rate][repetition_id], ECMP_ASP_phis[rate][repetition_id] ])
                csvfile.flush()
                
    # write to csv file 2: # TODO: fix
    csv_cols = ['V', 'D', 'perturbation_rate', 'repetition_id', 'MD_MP_phis_training',
                'MD_MP_phis_verification', 'MD_MP_phis_trained_on_verification_set']
    filename = f'{topo_name}_{V}_{D}_uniform_MD_MP_perturbation.csv'
    # save data to csv file
    with open(filename, 'a', newline='') as csvfile:
        csvwriter = csv.writer(csvfile)
        csvwriter.writerow(csv_cols)
        csvfile.flush()
        for rate, M_list in perturbated_Ms.items():
            for repetition_id in range(len(M_list)):
                csvwriter.writerow([ V, D, rate, repetition_id, MD_MP_phis_training[rate][repetition_id],
                    MD_MP_phis_verification[rate][repetition_id], MD_MP_phis_trained_on_verification_set[rate][repetition_id] ])
                csvfile.flush()

if __name__ == '__main__':
    main()
