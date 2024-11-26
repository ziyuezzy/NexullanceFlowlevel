import pickle
import os
import sys
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
from topologies.HPC_topo import HPC_topo

def pickle_paths(topo_name: str, topo_config: tuple, paths: str = "ASP"):
    graph_data_path = os.environ.get('PICKLED_DATA')

    if not topo_name.endswith("topo"):
        topo_name += "topo"

    edgelist_file=graph_data_path+f"/from_graph_edgelists/({topo_config[0]},{topo_config[1]}){topo_name}_edgelist.pickle"
    pathdict_file=graph_data_path+f"/from_graph_pathdicts/{paths}_({topo_config[0]},{topo_config[1]}){topo_name}_paths.pickle"

    if os.path.isfile(edgelist_file) and os.path.isfile(pathdict_file):
        print(f"all required files exists, skipping pickle")
        return

    # create an instance of network topology
    topo_instance=HPC_topo.initialize_child_instance(topo_name, topo_config[0], topo_config[1])
    edge_list=list(topo_instance.nx_graph.edges())
    if os.path.isfile(edgelist_file):
        print(f"edge list file already exists: {edgelist_file}")
    else:
        with open(edgelist_file, 'wb') as handle:
            pickle.dump(edge_list, handle)

    if os.path.isfile(pathdict_file):
        print(f"path dict file already exists: {pathdict_file}")
    else:
        if paths == "ASP":
            path_dict, _=topo_instance.calculate_all_shortest_paths()
            with open(pathdict_file, 'wb') as handle:
                pickle.dump(path_dict, handle)
        elif paths.startswith("APST_"):
            try:
                # Extract the part after "APST_" and convert it to an integer
                max_length = int(paths[5:])
                path_dict, _=topo_instance.calculate_all_paths_within_length(max_length)
                with open(pathdict_file, 'wb') as handle:
                    pickle.dump(path_dict, handle)
            except ValueError:
                print(f"Error: invalid max path length: ", paths)
                sys.exit(1)
        else:
            print(f"Error: invalid paths' name: ", paths)
            sys.exit(1)

if __name__ == "__main__":
    pickle_paths("RRGtopo", (4, 3), "ASP")
    pickle_paths("RRGtopo", (4, 3), "APST_4")