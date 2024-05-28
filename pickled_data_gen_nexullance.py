from topologies.HPC_topo import HPC_topo
from topologies.DDF import DDFtopo
from topologies.Slimfly import Slimflytopo
from topologies.Equality import Equalitytopo
from topologies.RRG import RRGtopo
import pickle
import os
import globals as gl
import numpy as np
from nexullance.Nexullance_MP import Nexullance_MP
from nexullance.Nexullance_IT import Nexullance_IT

graph_data_path = os.environ.get('PICKLED_DATA')
## run this to know which topology classes are available
# HPC_topo.get_child_classes()

# create an instance of network topology
topo_name="RRGtopo"
config=(36, 7)
_network=HPC_topo.initialize_child_instance(topo_name, config[0], config[1])
edge_list=list(_network.nx_graph.edges())
edgelist_file=graph_data_path+f"/from_graph_edgelists/({config[0]},{config[1]}){topo_name}_edgelist.pickle"
with open(edgelist_file, 'wb') as handle:
    pickle.dump(edge_list, handle)

# generate ECMP paths:
ASP, routing_name=_network.calculate_all_shortest_paths()
# pathdict_file=graph_data_path+f"/from_graph_pathdicts/{routing_name}_({topo_config[0]},{topo_config[1]}){topo_name}_paths.pickle"
# with open(pathdict_file, 'wb') as handle:
#     pickle.dump(ASP, handle)
    
APST_4, routing_name=_network.calculate_all_paths_within_length(4)
# pathdict_file=graph_data_path+f"/from_graph_pathdicts/{routing_name}_({topo_config[0]},{topo_config[1]}){topo_name}_paths.pickle"
# with open(pathdict_file, 'wb') as handle:
#     pickle.dump(APST_4, handle)

# generate nexullance solutions (APST_4 and IT)

EPR=4
Cap_remote = 16 #GBps
Cap_local = 16 #GBps

traffic_pattern = "diagonal_1"
# generate traffic pattern
M_EPs = gl.generate_diagonal_traffic_pattern(config[0], EPR, 1)
    
# calibrate traffic to 10x saturation for ECMP_ASP
ECMP_ASP = gl.ECMP(ASP)
remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
max_remote_link_load = np.max(remote_link_flows)/Cap_remote
max_local_link_load = np.max(local_link_flows)/Cap_local
# adapt the traffic scaling factor to 10x saturation
traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
M_EPs = traffic_scaling * M_EPs
M_R = gl.convert_M_EPs_to_M_R(M_EPs, config[0], EPR)
remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
# max_remote_link_load = np.max(remote_link_flows)/Cap_remote
max_local_link_load = np.max(local_link_flows)/Cap_local


# generate NEXU_MP_APST4 solution
nexu = Nexullance_MP(_network.nx_graph, APST_4, M_R, Cap_remote, 0, False)
nexu.init_model()
Lremote_NEXU_MP_MP_APST4, Nexu_MP_APST_4_paths = nexu.solve()
routing_name = f"NEXU_MP_APST4_{traffic_pattern}"
pathdict_file=graph_data_path+f"/from_graph_pathdicts/{routing_name}_({config[0]},{config[1]}){topo_name}_paths.pickle"
with open(pathdict_file, 'wb') as handle:
    pickle.dump(gl.clean_up_weighted_paths(Nexu_MP_APST_4_paths), handle)

Phi_NEXU_MP_APST4 = gl.network_total_throughput(M_EPs, Lremote_NEXU_MP_MP_APST4, max_local_link_load)
print("NEXU_MP_APST4 network throughput:", Phi_NEXU_MP_APST4, "GBps")

# # generate NEXU_IT solution:
# nexu = Nexullance_IT(_network.nx_graph, M_R, Cap_remote, False)

# # # this was for uniform
# # num_method_1 = 2
# # num_method_2 = 6    
# # alpha_1 = 2.0
# # beta_1 = 0.4
# # alpha_2 = 3
# # beta_2 = 10

# # this was for shift_half
# num_method_1 = 1
# num_method_2 = 6    
# alpha_1 = 2.0
# beta_1 = 0.4
# alpha_2 = 3
# beta_2 = 10

# def weighted_method_1(s: int, d: int, edge_attributes: dict):
#     return alpha_1 + edge_attributes['load']**beta_1
# def weighted_method_2(s: int, d: int, edge_attributes: dict):
#     return alpha_2 + edge_attributes['load']**beta_2

# nexu_it = Nexullance_IT(_network.nx_graph, M_R, Cap_remote)
# nexu_it.optimize(num_method_1, num_method_2, weighted_method_1, weighted_method_2, alt = True)
# Nexu_IT_paths = nexu_it.get_routing_table()
# routing_name = f"NEXU_IT_{traffic_pattern}"
# pathdict_file=graph_data_path+f"/from_graph_pathdicts/{routing_name}_({config[0]},{config[1]}){topo_name}_paths.pickle"
# with open(pathdict_file, 'wb') as handle:
#     pickle.dump(gl.clean_up_weighted_paths(Nexu_IT_paths), handle)


# Phi_NEXU_IT = gl.network_total_throughput(M_EPs, nexu_it.get_result_max_link_load(), max_local_link_load)
# print("NEXU_IT network throughput:", Phi_NEXU_IT, "GBps")
# print("NEXU_IT achieved nearly", Phi_NEXU_IT/Phi_NEXU_MP_APST4*100, "% of NEXU_MP_APST4 network throughput")