from statistics import mean
# import nexullance.LP_cvspy as LP_cvspy
# import nexullance.LP_cvspy as LP_cvspy
import numpy as np
import random

#Configurations:
#slimfly configurations:
# sf_configs= [722]
sf_configs= [(722, 29), (1058, 35)]
#jellyfish configurations:
jf_configs =  [(722, 29), (900,32), (1058, 35)]
#GDBG configurations, the degree is doubled because it is a directed graph: 
gdbg_configs = [(722, 29), (900,32), (1058, 35)]
#Equality configurations:
eq_configs= [ # Note that E443 config is fault on the equality paper, so here it is commented out
# (800, 31, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E443"),
(900, 32, [-1, 1, 23, 25, 55, 121, 135, 165, 177, 333, 457, 475, 495, 543, 549, 557, 585, 615, 717, 727], [70, 130, 194, 256, 320, 360], "E441"),
(1000, 33, [-1, 1, 27, 39, 45, 105, 215, 327, 365, 401, 455, 491, 523, 545, 547, 605, 653, 701, 715, 771, 801, 813, 865, 875, 955], [70, 180, 320, 430], "E442")
]
ddf_configs=[(264, 11), (876, 17), (1386, 20)]

def process_path_dict(path_dict):
    # input is a path dictionary
    average_path_lengths=[]
    num_paths=[]

    for _, paths in path_dict.items():
        average_length=0
        for path in paths:
            average_length+=(len(path)-1)
        average_length/=len(paths)
        average_path_lengths.append(average_length)
        num_paths.append(len(paths))
    # Calculate the average path length of all s-d pairs, 
    # The output is a dictionary of average path lengths
    return average_path_lengths, num_paths

def process_weighted_path_dict(path_dict):
    # input is a weighted path dictionary
    average_path_lengths=[]
    num_paths=[]

    for _, paths in path_dict.items():
        temp_num_paths=0
        average_length=0
        for path, weight in paths:
            average_length+=(len(path)-1)*weight
            if weight > 0.001:
                temp_num_paths+=1
        average_length
        average_path_lengths.append(average_length)
        num_paths.append(temp_num_paths)
    # Calculate the average path length of all s-d pairs, 
    # The output is a dictionary of average path lengths
    return average_path_lengths, num_paths

def is_disjoint(path1, path2):
    # Function to check if two paths are edge-disjoint
    edges1 = [(path1[i], path1[i + 1]) for i in range(len(path1) - 1)]
    edges2 = [(path2[i], path2[i + 1]) for i in range(len(path2) - 1)]

    return not any(edge in edges2 for edge in edges1)

def count_disjoint_paths(paths_dict):
    disjoint_paths_count = []
    disjoint_paths_ratio = []
    for (s, d), paths in paths_dict.items():
        count = 0
        for i in range(len(paths)):
            is_disjoint_path = True
            for j in range(i + 1, len(paths)):
                if not is_disjoint(paths[i], paths[j]):
                    is_disjoint_path = False
                    break
            if is_disjoint_path:
                count += 1
        disjoint_paths_ratio.append(count/len(paths))
        disjoint_paths_count.append(count)
    return disjoint_paths_count, disjoint_paths_ratio


def calculate_data_shortest_paths(topology_instance, config):
    _diameter=topology_instance.calculate_diameter()
    paths_dict=topology_instance.calculate_all_shortest_paths()

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with shortest paths routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict

def calculate_data_shortest_paths_with_LP(topology_instance, config):
    edge_list=list(topology_instance.nx_graph.edges())
    _diameter=topology_instance.calculate_diameter()
    paths_dict=topology_instance.calculate_all_shortest_paths()

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    LP_weighted_path_dict=LP_cvspy.LP_load_balancing(paths_dict, edge_list)
    LP_weighted_link_load = topology_instance.distribute_uniform_flow_on_weighted_paths(LP_weighted_path_dict)
    LP_load_dict=list(LP_weighted_link_load.values())
    LP_load_min=min(LP_load_dict)
    LP_load_max=max(LP_load_dict)
    LP_load_mean=mean(LP_load_dict)
    
    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        "LP_weighted_link_load_statistics": [LP_load_min, LP_load_mean, LP_load_max]
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with LP-weighted paths routing")
    return _result, edge_list, paths_dict, LP_weighted_path_dict


def calculate_DDF_routing(topology_instance, config):
    _diameter=topology_instance.calculate_diameter()
    paths_dict=topology_instance.DDF_unipath_routing()

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with unipath routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict


def calculate_data_k_shortest_paths(topology_instance, config, k):
    _diameter=topology_instance.calculate_diameter()
    paths_dict=topology_instance.calculate_all_k_shortest_paths(k)

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with {k} shortest paths routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict


def calculate_data_paths_within_length(topology_instance, config, max_path_length):
    _diameter=topology_instance.calculate_diameter()
    if (_diameter > max_path_length):
        print(f"ERROR: diameter bigger than max path length")
    paths_dict=topology_instance.calculate_all_paths_within_length_parallel(max_path_length)

    _average_path_lengths, _num_paths=process_path_dict(paths_dict)
    _average_path_length_min=min(_average_path_lengths)
    _average_path_length_max=max(_average_path_lengths)
    _average_path_length_mean=mean(_average_path_lengths)
    _num_paths_min=min(_num_paths)
    _num_paths_max=max(_num_paths)
    _num_paths_mean=mean(_num_paths)

    link_load_dict=topology_instance.distribute_uniform_flow_on_paths(paths_dict)
    _load_dict=list(link_load_dict.values())
    _load_min=min(_load_dict)
    _load_max=max(_load_dict)
    _load_mean=mean(_load_dict)

    # s_d_bw_dist=list(topology_instance.s_d_bw_dist(paths_dict, link_load_dict).values())
    # s_d_bw_min=min(s_d_bw_dist)
    # s_d_bw_max=max(s_d_bw_dist)
    # s_d_bw_mean=mean(s_d_bw_dist)

    _result={ 
        "diameter": _diameter, 
        "ave_path_length_statistics": [_average_path_length_min, _average_path_length_mean, _average_path_length_max],
        "num_paths_statistics": [_num_paths_min, _num_paths_mean, _num_paths_max],
        "link_load_statistics": [_load_min, _load_mean, _load_max],
        # "s_d_bw_statistics": [s_d_bw_min, s_d_bw_mean, s_d_bw_max],
        # "graph_edge_list": list(topology_instance.nx_graph.edges()),
        # "paths_dict": paths_dict
        }
    print(f"calculation done for {config} with shorter-than-{max_path_length} paths routing")
    return _result, list(topology_instance.nx_graph.edges()), paths_dict

def ECMP(path_dict): # input is a dictionary (key=(src, dest))
    # convert a path dict to a weighted path dict using equal-cost multi-path routing (ECMP)
    ECMP_path_dict={}
    for (u,v), paths in path_dict.items():
        ECMP_path_dict[(u,v)]=[]
        for path in paths:
            ECMP_path_dict[(u,v)].append( (path, 1/len(paths)) ) 
            # TODO: assign the residual weight to the last path, to avoid rounding errors?
    return ECMP_path_dict

def ECMP_nx(path_dict):  # input is a dictionary (key=src) of dictionary (key=dest), as in the style of networkx
    # convert a path dict to a weighted path dict using equal-cost multi-path routing (ECMP)
    ECMP_path_dict={}
    for u, v_dict in path_dict.items():
        ECMP_path_dict[u]={}
        for v, paths in v_dict.items():
            for path in paths:
                ECMP_path_dict[u][v].append( (path, 1/len(paths)) ) 
                # TODO: assign the residual weight to the last path, to avoid rounding errors?
    return ECMP_path_dict

def clean_up_weighted_paths(weighted_path_dict):
    clean_weighted_path_dict={}
    for (u,v), paths in weighted_path_dict.items():
        weighted_paths=[]
        check_sum=0
        for j, (path, weight) in enumerate(paths):
            weight=round(weight, 3)
            if j == len(paths)-1:
                w=round(1-check_sum, 3)
                assert(abs(w-weight)<0.01)
                if weight > 0.001:
                    weighted_paths.append((path, float(w)))
                else:
                    weighted_paths[-1]=(weighted_paths[-1][0],weighted_paths[-1][1]+w )
            else:
                if weight > 0.001:
                    check_sum += weight
                    weighted_paths.append((path, float(weight)))
        clean_weighted_path_dict[(u,v)]=weighted_paths
    return clean_weighted_path_dict


def generate_uniform_traffic_pattern(num_routers, EPs_per_router):
    total_num_EP=EPs_per_router*num_routers
    traffic_matrix=np.ones((total_num_EP, total_num_EP))
    for i in range(total_num_EP):
        traffic_matrix[i][i]=0
    return traffic_matrix

def generate_shift_traffic_pattern(num_routers, EPs_per_router, shift):
    total_num_EP=EPs_per_router*num_routers
    traffic_matrix=np.zeros((total_num_EP, total_num_EP))
    for i in range(total_num_EP):
        traffic_matrix[i][(i+shift)%total_num_EP]=1

    return traffic_matrix

def generate_half_shift_traffic_pattern(num_routers, EPs_per_router):
    total_num_EP=EPs_per_router*num_routers
    traffic_matrix=np.zeros((total_num_EP, total_num_EP))
    for i in range(total_num_EP):
        traffic_matrix[i][(i+total_num_EP//2)%total_num_EP]=1

    return traffic_matrix

def generate_diagonal_traffic_pattern(num_routers, EPs_per_router, offset):
    total_num_EP=EPs_per_router*num_routers
    traffic_matrix=np.zeros((total_num_EP, total_num_EP))
    for i in range(total_num_EP):
        dst = i+offset
        if dst < total_num_EP:
            traffic_matrix[i][dst]=1
            traffic_matrix[dst][i]=1

    return traffic_matrix

def generate_uniform_cluster_pattern(num_routers, EPs_per_router):
    total_num_EP=EPs_per_router*num_routers
    traffic_matrix=np.zeros((total_num_EP, total_num_EP))
    for e in range(EPs_per_router):
        for i in range(num_routers):
            for j in range(num_routers):
                if i != j :
                    traffic_matrix[i*EPs_per_router+e][j*EPs_per_router+e]=1
    return traffic_matrix

def generate_random_cluster_pattern(num_routers, EPs_per_router, num_clusters=None, seed=0):
    if num_clusters==None:
        num_clusters=num_routers
    random.seed(seed)
    total_num_EP=EPs_per_router*num_routers
    EPs_per_cluster = total_num_EP//num_clusters
    traffic_matrix=np.zeros((total_num_EP, total_num_EP))
    EPs=list(range(total_num_EP))
    while EPs:
        cluster=random.sample(EPs, EPs_per_cluster)
        for v in cluster:
            for u in cluster:
                if v!=u:
                    traffic_matrix[v][u]=1
        for v in cluster:
            EPs.remove(v)  
    return traffic_matrix


# def generate_all_reduce_traffic_pattern(num_routers, EPs_per_router, _center):
#     # center as the center of all-reduce operation
#     total_num_EP=EPs_per_router*num_routers
#     traffic_matrix=np.zeros((total_num_EP, total_num_EP))
#     for i in range(total_num_EP):
#         if i != _center:
#             traffic_matrix[i][_center]=1 # TODO: this is wrong, should be a tree structure
#     return traffic_matrix

# def generate_broadcast_traffic_pattern(num_routers, EPs_per_router, _center):
#     # center as the center of the broadcast operation
#     total_num_EP=EPs_per_router*num_routers
#     traffic_matrix=np.zeros((total_num_EP, total_num_EP))
#     for i in range(total_num_EP):
#         if i != _center:
#             traffic_matrix[_center][i]=1 # TODO: this is wrong, should be a tree structure
#     return traffic_matrix

def convert_M_EPs_to_M_R(M_EPs, num_routers, EPs_per_router):
    assert(len(M_EPs)==len(M_EPs[0])==num_routers*EPs_per_router)
    M_R_traffic_matrix=np.zeros((num_routers, num_routers))
    for s in range(num_routers):
        for d in range(num_routers):
            if s==d:
                continue
            sum_M_R_flow=0
            for sp in range(EPs_per_router):
                for dp in range(EPs_per_router):
                    sum_M_R_flow+=M_EPs[sp+s*EPs_per_router][dp+d*EPs_per_router]
            M_R_traffic_matrix[s][d]=sum_M_R_flow

    return M_R_traffic_matrix


def evaluate_weighted_pathdict_LF_resilience(edgelist, weighted_path_dict, LFR, seed=0):
    random.seed(seed)
    # Get the list of edges in the graph
    assert(0<=LFR<1)
    num_edges_to_delete=int(LFR * len(edgelist))
    edges_to_delete = random.sample(edgelist, num_edges_to_delete)

    def path_is_broken(path):
        links_in_path=[(path[i], path[i+1]) for i in range(len(path)-1)]
        for (u,v) in edges_to_delete:
            if ((u,v) in links_in_path) or ((v,u) in links_in_path):
                return True
            
    success_rate={}    
    #calculate the communication success rate statistics among s-d pairs
    for (s,d), weighted_paths in weighted_path_dict.items():
        success_rate[(s,d)]=0
        for path, prob in weighted_paths:
            if not path_is_broken(path):
                success_rate[(s,d)]=success_rate[(s,d)]+prob

    return mean(list(success_rate.values()))
                    
def local_link_flows_from_M_EPs(M_EPs):
    local_link_flows=[]
    M_EPs=np.array(M_EPs)
    for row in M_EPs:
        local_link_flows.append(np.sum(row))
    for row in M_EPs.swapaxes(0,1):
        local_link_flows.append(np.sum(row))
    return local_link_flows

def network_total_throughput(M_EPs, max_remote_link_load, max_local_link_load):
    array_sum = np.sum(M_EPs)
    if max_remote_link_load<1 and max_local_link_load<1:
        return array_sum
    else:
        return array_sum / max([max_remote_link_load, max_local_link_load])



# automorphism methods using nauty:
import pynauty as nauty

def generate_nauty_graph_from_nx(nx_graph):
    adj_dict={n: list(nbrdict.keys()) for n, nbrdict in nx_graph.adjacency()}
    nauty_graph=nauty.Graph(nx_graph.number_of_nodes(), directed=False, adjacency_dict=adj_dict)
    return nauty_graph

def nauty_autgrp_verbose(nauty_graph, _verbose=True):
    # Compute the automorphism group
    aut_group = nauty.autgrp(nauty_graph)

    # Extract elements from the output tuple
    generators, grpsize1, grpsize2, orbits, numorbits = aut_group

    if _verbose:
        # Print the generators of the automorphism group
        print("Generators of the automorphism group:")
        print(generators)

        print("Size of the generator set:", len(generators))

        # print the size (order) of the group
        print("Size (order) of the automorphism group:", grpsize1*10**grpsize2)

        # Print the orbits of the vertices
        print("Orbits of the vertices:", orbits)

        # Print the number of orbits
        print("Number of orbits:", numorbits)

    return generators