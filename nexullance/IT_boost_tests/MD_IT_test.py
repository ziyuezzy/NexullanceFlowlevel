import sys
import os
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../../')))

from topo_paths import IT_boost_bin
sys.path.append(str(IT_boost_bin))
from Nexullance_IT_cpp import Nexullance_IT_interface
import global_helpers as gl
import topologies.Slimfly as Slimfly
import numpy as np

V = 32
D = 6
EPR = (D+1)//2
_network = Slimfly.Slimflytopo(V, D)
ASP, _ = _network.calculate_all_shortest_paths()
ECMP_ASP = gl.ECMP(ASP)
arcs = _network.generate_graph_arcs()

Cap_remote = 16 #GBps
Cap_local = 16 #GBps

# M_EPs = gl.generate_uniform_traffic_demand_matrix(V, EPR)
# remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
# max_remote_link_load = np.max(remote_link_flows)/Cap_remote
# max_local_link_load = np.max(local_link_flows)/Cap_local
# # adapt the traffic scaling factor to 10x saturation
# traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
# uniform_M_EPs = traffic_scaling * M_EPs

M_EPs = gl.generate_shift_half_traffic_demand_matrix(V, EPR)
print(f"Loaded demand matrix shape: {M_EPs.shape}")
print(f"Demand matrix sum: {np.sum(M_EPs):.2e}")
np.set_printoptions(threshold=np.inf, linewidth=np.inf)
print(f"Demand matrix:\n{M_EPs}")
np.set_printoptions()  # Reset to default

remote_link_flows, local_link_flows = _network.distribute_M_EPs_on_weighted_paths(ECMP_ASP, EPR, M_EPs)
max_remote_link_load = np.max(remote_link_flows)/Cap_remote
max_local_link_load = np.max(local_link_flows)/Cap_local
# adapt the traffic scaling factor to 10x saturation
traffic_scaling = 10.0/max(max_local_link_load, max_remote_link_load)
half_shift_M_EPs = traffic_scaling * M_EPs

nexu_it = Nexullance_IT_interface(V, arcs, 10.0, 10.0, True)
nexu_it.run_MD_IT([half_shift_M_EPs], [1.0], EPR)
# nexu_it.run_MD_IT([uniform_M_EPs, half_shift_M_EPs], [0.7, 0.3], EPR)