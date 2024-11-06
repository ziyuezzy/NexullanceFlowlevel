from topologies.HPC_topo import HPC_topo
import pickle
import os
import sys

def pickle_gen(topo_name: str, topo_config: tuple, paths: str = "ASP"):
    graph_data_path = os.environ.get('PICKLED_DATA')

    # create an instance of network topology
    topo_instance=HPC_topo.initialize_child_instance(topo_name, topo_config[0], topo_config[1])
    edge_list=list(topo_instance.nx_graph.edges())
    edgelist_file=graph_data_path+f"/from_graph_edgelists/({topo_config[0]},{topo_config[1]}){topo_name}_edgelist.pickle"
    if os.path.isfile(edgelist_file):
        print(f"edge list file already exists: {edgelist_file}")
    else:
        with open(edgelist_file, 'wb') as handle:
            pickle.dump(edge_list, handle)

    pathdict_file=graph_data_path+f"/from_graph_pathdicts/{paths}_({topo_config[0]},{topo_config[1]}){topo_name}_paths.pickle"
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
    pickle_gen("RRGtopo", (4, 3), "ASP")
    pickle_gen("RRGtopo", (4, 3), "APST_4")