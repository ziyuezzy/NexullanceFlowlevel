import pickle
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from topologies.HPC_topo import HPC_topo
from nexullance.ultility import nexullance_exp_container
import global_helpers as gl

def pickle_nexullance_paths(topo_name: str, topo_config: tuple, Cap_core, Cap_access, traffic_pattern="uniform", method: str = "IT"):
    graph_data_path = os.environ.get('PICKLED_DATA')

    if not topo_name.endswith("topo"):
        topo_name += "topo"

    edgelist_file=graph_data_path+f"/from_graph_edgelists/({topo_config[0]},{topo_config[1]}){topo_name}_edgelist.pickle"
    pathdict_file=graph_data_path+f"/from_graph_pathdicts/Nexullance_{method}_{traffic_pattern}_({topo_config[0]},{topo_config[1]}){topo_name}_paths.pickle"

    if os.path.isfile(edgelist_file) and os.path.isfile(pathdict_file):
        print(f"all required files exists, skipping pickle")
        return
    
    if os.path.isfile(edgelist_file):
        print(f"edge list file already exists: {edgelist_file}")
    else:
        # create an instance of network topology
        topo_instance=HPC_topo.initialize_child_instance(topo_name, topo_config[0], topo_config[1])
        edge_list=list(topo_instance.nx_graph.edges())
        with open(edgelist_file, 'wb') as handle:
            pickle.dump(edge_list, handle)

    if os.path.isfile(pathdict_file):
        print(f"path dict file already exists: {pathdict_file}")
    else:
        V = topo_config[0]
        D = topo_config[1]
        EPR = (topo_config[1]+1)//2
        nexu_exp = nexullance_exp_container(topo_name,  V, D, EPR, Cap_core=Cap_core, Cap_access=Cap_access)
        
        if traffic_pattern == "uniform":
            M_EPs = gl.generate_uniform_traffic_demand_matrix(V, EPR)
        elif traffic_pattern.startswith("shift_"):
            try:
                # Extract the part after "shift_" and convert it to an integer
                shift = int(traffic_pattern[6:])
                M_EPs = gl.generate_shift_traffic_demand_matrix(V, EPR, shift)
            except ValueError:
                print(f"Error: traffic pattern: ", traffic_pattern)
                sys.exit(1)
        else:
            print(f"Error: invalid traffic pattern: ", traffic_pattern)
            sys.exit(1)

        if method == "IT":
            with open(pathdict_file, 'wb') as handle:
                pickle.dump(gl.clean_up_weighted_paths(nexu_exp.run_nexullance_IT_return_RT(M_EPs, traffic_pattern)), handle)
        elif method.startswith("MP_APST_"):
            max_path_length = int(method[8:])
            assert(3<=max_path_length<=5)
            with open(pathdict_file, 'wb') as handle:
                pickle.dump(gl.clean_up_weighted_paths(nexu_exp.run_nexullance_MP_return_RT(max_path_length, M_EPs, traffic_pattern)), handle)
        else:
            print(f"Error: invalid method: ", method)
            sys.exit(1)


if __name__ == "__main__":
    pickle_nexullance_paths("RRGtopo", (36, 5), 16, 16, "shift_1", "IT")
    pickle_nexullance_paths("RRGtopo", (36, 5), 16, 16, "shift_1", "MP_APST_4")