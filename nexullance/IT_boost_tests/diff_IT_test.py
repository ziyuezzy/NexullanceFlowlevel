import sys
from topoResearch.paths import IT_boost_debug
sys.path.append(IT_boost_debug)
from Nexullance_IT_cpp import diff_Nexullance_IT_interface
import topoResearch.global_helpers as gl
import topoResearch.topologies.RRG as RRG
import numpy as np

V = 16
D = 5
EPR = (D+1)//2
_network = RRG.RRGtopo(V, D)
ASP, _ = _network.calculate_all_shortest_paths()
ECMP_ASP = gl.ECMP(ASP)
arcs = _network.generate_graph_arcs()

Cap_remote = 10 #GBps
Cap_local = 10 #GBps

M_EPs = gl.generate_uniform_traffic_demand_matrix(V, EPR)
remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
max_remote_link_load = np.max(remote_link_flows)/Cap_remote
max_local_link_load = np.max(local_link_flows)/Cap_local
# adapt the traffic scaling factor to 10x saturation
traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
uniform_M_EPs = traffic_scaling * M_EPs

M_EPs = gl.generate_shift_half_traffic_demand_matrix(V, EPR)
remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
max_remote_link_load = np.max(remote_link_flows)/Cap_remote
max_local_link_load = np.max(local_link_flows)/Cap_local
# adapt the traffic scaling factor to 10x saturation
traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
half_shift_M_EPs = traffic_scaling * M_EPs

nexu_it = diff_Nexullance_IT_interface(V, arcs, 10.0, 10.0, False, True)
# nexu_it.set_parameters(0.1, 7.0)
results = nexu_it.run_for_batch_matrices([uniform_M_EPs, half_shift_M_EPs], EPR)

for i, res in enumerate(results):
    print("======for matrix no. ", i, "======")
    print("elasped_time: ", res.get_elapsed_time())
    print("max_load: ", res.get_max_core_link_load())
    print("phi: ", res.get_phi())
    print("num_attempts: ", res.get_num_attempts())