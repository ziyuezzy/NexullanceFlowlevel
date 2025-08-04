import sys
from topoResearch.paths import IT_boost_debug, IT_boost_release
# sys.path.append(IT_boost_release)
sys.path.append(IT_boost_debug)
from Nexullance_IT_cpp import diff_Nexullance_IT_interface, Nexullance_IT_interface
import topoResearch.global_helpers as gl
import topoResearch.topologies.DDF as DDF
import numpy as np
from paths import REPO_ROOT
from diff_nexu.sampled_demand_analyzer import sampled_demand_analyzer

config = gl.ddf_configs[0]
V = config[0]
D = config[1]
EPR = (D+1)//2
topo_name="DDF"
_network = DDF.DDFtopo(V, D)
ASP, _ = _network.calculate_all_shortest_paths()
ECMP_ASP = gl.ECMP(ASP)
arcs = _network.generate_graph_arcs()

Cap_remote = 10 #GBps
Cap_local = 10 #GBps
_num_samples = 8
bench="FFT3D"

pickle_file = f"{REPO_ROOT}/diff_nexu/data/{bench} nx=256 ny=256 nz=256 npRow=12_(36,5)RRG_ECMP_ASP_sent.pickle"
demand_analyzer = sampled_demand_analyzer(pickle_file)
M_EPs_s = demand_analyzer.get_inter_EP_demand_matrices(num_samples=_num_samples)[0]

nexu_it = diff_Nexullance_IT_interface(V, arcs, 10.0, 10.0, False, False)
nexu_it.set_parameters(0.1, 7.0, 0.00001, 5, 100000000, V*3)
# nexu_it.set_parameters(0.1, 7.0)
results = nexu_it.run_for_batch_matrices(M_EPs_s, EPR)

for i, res in enumerate(results):
    print("======diff nexu for matrix no. ", i, "======")
    print("elasped_time: ", res.get_elapsed_time())
    print("max_load: ", res.get_max_core_link_load())
    print("phi: ", res.get_phi())
    print("num_attempts: ", res.get_num_attempts())

nexu_it = Nexullance_IT_interface(V, arcs, 10.0, 10.0, False)
nexu_it.set_parameters(0.1, 7.0, 0.00001, 5, 100000000, V*3, False)
for i, M_EPs in enumerate(M_EPs_s):
    nexu_result = nexu_it.run_IT(M_EPs, EPR)
    print("======nexu for matrix no. ", i, "======")
    print("elasped_time: ", nexu_result.get_elapsed_time())
    print("max_load: ", nexu_result.get_max_core_link_load())
    print("phi: ", nexu_result.get_phi())
    print("num_attempts: ", nexu_result.get_num_attempts())