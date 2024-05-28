import networkx as nx
from joblib import Parallel, delayed
from random import sample, shuffle
Graph = nx.graph.Graph
DiGraph = nx.DiGraph
import time
import tracemalloc
import numpy as np

def weight_function( s: int, d: int, edge_attributes: dict):
    # define the weight function for the dijkstra or the bellman-ford algorithm.
    alpha: float = 10.0
    beta: float = 20.0
    return alpha+edge_attributes['load']**beta

class Nexullance_IT:
    def __init__(self, _nx_graph: Graph, _M_R: list, _Cap_remote: float, _verbose:bool=False):
        # clear node and edge attributes
        for (n1, n2, d) in _nx_graph.edges(data=True):
            d.clear()
        for (n1, d) in _nx_graph.nodes(data=True):
            d.clear()

        # prepare for access
        self.vertex_pairs = [(v1, v2) for v1 in _nx_graph.nodes() for v2 in _nx_graph.nodes() if v1 != v2]

        self.nx_digraph = _nx_graph.to_directed()
        self.M_R: list = _M_R
        self.verbose: bool = _verbose
        self.Cap_remote: float = _Cap_remote
        self.result_max_link_load: float = 0.0
        self.method_2_attempts: int = 0

        self.calibration_factor: float = 1.0



    def initialize(self):
        # initialize the data structures.
        # the routing table is a dictionary of dictionary (to be the same as networkx)
        # the key of the first dictionary is the source node, and the key of the second dictionary is the destination node
        # the key of the thrid dictionary is the unique ids of paths, and the value is the weight of the path
        self.next_path_id: int = 0
        self.routing_table : dict = {}
        # another dictionary maps from the unique id of a path to the actual path itself.
        self.path_id_to_path: dict = {}
        # link loads are stored in a the "load" edge attributes in the nx graph
        # meanwhile, another edge attribute "path_ids" is added to store the unique ids of the paths that pass through this link.
        # now we initialize the edge attributes in the nx graph:
        for (n1, n2, d) in self.nx_digraph.edges(data=True):
            d['load'] = 1.0
            d['path_ids'] = []
        # in parallel to the loads in the graph attributes, we also keep another dictionary to store the link loads:
        # keys are link tuples (u, v), values are the load on the link
        # this is for accessing the maximum link load easier
        self.link_loads: dict = {}
        # alternatively, a heapq could be used. However, the overhead of pushing updated link loads are probably high (need to invoke 'find' operations) in heap queues
        
        # TODO: calibrate the link loads to 10x, so that the parameters "alpha and beta" is suitable for general input

        # TODO: in the end return the original scale of link loads

    # for experimenting the combination of different methods, 
    # copy.deepcopy() could be used after applying any of the methods
     
    def optimization_method_1(self, init_for_method2: bool, _weights: callable = weight_function):
        # weighted dijkstra algorithm to find the least-weighted paths (for ties, apply ECMP) for all s-d pairs.
        path_dict = self.least_weighted_paths_for_all_s_d(self.nx_digraph, _weights, "dijkstra", 1)
        max_link_load = 0.0
        # clear edge attributes
        for (n1, n2, d) in self.nx_digraph.edges(data=True):
            d['load'] = 0.0
            d['path_ids'] = []

        if init_for_method2: #=
            self.next_path_id=0
            self.routing_table = {}
        #======================
        for src, dst_dict in path_dict.items():
            if init_for_method2:#=
                self.routing_table[src]={}
            #=====================
            for dst, paths in dst_dict.items():
                if init_for_method2:#=
                    self.routing_table[src][dst]={}
                #=====================
                num_paths = len(paths)
                for path in paths:
                    # calculate load for the links passed by
                    for i in range(len(path)-1):
                        u = path[i]
                        v = path[i+1]
                        # if u==9 and v==26:
                        #     print("debug")
                        self.nx_digraph[u][v]['load'] += self.M_R[src][dst]*1/num_paths/self.Cap_remote
                        # update the maximum link load
                        max_link_load = max(self.nx_digraph[u][v]['load'], max_link_load)                       
                        if init_for_method2:#=
                            self.nx_digraph[u][v]['path_ids'].append(self.next_path_id)
                        #=====================
                    if init_for_method2:#=
                        self.routing_table[src][dst][self.next_path_id]=1/len(paths)
                        self.path_id_to_path[self.next_path_id] = path
                        self.next_path_id += 1
                    #=====================
        if init_for_method2:#=
            # construct self.link_loads
            for (u, v, l) in self.nx_digraph.edges(data='load'):
                self.link_loads[(u, v)] = l
        #=====================
        return max_link_load

    def optimization_method_2(self, step: float, _weights: callable = weight_function, 
                threshold: float = 0.001, randomize: bool = True, 
                algorithm: str = "dijkstra", max_attempts: int = 1000) -> 'tuple[bool, list]':
        # the first returned boolean indciates whether further decreasing the step size is possible for further progress
        # the second returned list contains the maximum link after each successful iteration
        # TODO: randomize?
        # optimization_method_2 is more fine-grained than optimization_method_1,
        # it finds the maximum loaded link, and then find alternative routes for a path that passes by
        # the new path is found by a weighted (bidirectional) dijkstra / bellman-ford algorithm.
        # the 'step' parameter is the maximum path weight transfer in one iteration
        # the 'threshold' parameter determines when the iteration stops, but at least 10 iterations.
        max_link_loads = [max(self.link_loads.values())]
        attempts:int = 0
        while True:
            if (attempts>max_attempts or (len(max_link_loads) > 10 and ((np.average(max_link_loads[-10:-1]) - max_link_loads[-1]) < threshold ))):
                break

            # u, v = max(self.link_loads, key=lambda k: self.link_loads[k])
            max_keys = [key for key, value in self.link_loads.items() if value == max_link_loads[-1]]

            success: bool = False # successful for not in making possible progress
            for u, v in max_keys:
                # select a path whose contribution to the load of the link is the largest
                # this path's weight will be decreased later      
                current_path_ids: list = self.nx_digraph[u][v]['path_ids']
                path_contributions = {} # to be sorted
                for path_id in current_path_ids:
                    current_path = self.path_id_to_path[path_id]
                    src = current_path[0]
                    dst = current_path[-1]
                    contribution = self.routing_table[src][dst][path_id]*self.M_R[src][dst]
                    path_contributions[path_id] = contribution

                # sort the contributions in descending order
                sorted_keys = sorted(path_contributions, key=lambda k: path_contributions[k], reverse=True)
                for old_path_id in sorted_keys:
                    old_path = self.path_id_to_path[old_path_id]
                    src = old_path[0]
                    dst = old_path[-1]
                    new_path = self.least_weighted_path_for_pair(self.nx_digraph, src, dst, _weights, algorithm)
                    if new_path == old_path:
                        continue
                    else:
                        success = True
                    self.update_paths(old_path_id, old_path, new_path, src, dst, step)
                if success:
                    break
                else:
                    continue
            if success:
                # update the maximum link load
                max_link_load = max(self.link_loads.values())
                max_link_loads.append(max_link_load)
                attempts+=1
                self.method_2_attempts+=1
                continue # go to the next iteration
            else:
                print("No possible progress, terminating.")
                return (False, max_link_loads) 
                # return False, meaning that even decreasing the step parameter should not make any progress
        return (True, max_link_loads)                
        # return True, meaning that decreasing the step parameter might make further progress


                   
    def optimization_method_2_alt(self, step: float, _weights: callable = weight_function, 
                threshold: float = 0.01, randomize: bool = True, 
                algorithm: str = "dijkstra", max_attempts: int = 1000) -> 'tuple[bool, list]':
        # the first returned boolean indciates whether further decreasing the step size is possible for further progress
        # the second returned list contains the maximum link after each successful iteration
        # TODO: randomize?
        # optimization_method_2 is more fine-grained than optimization_method_1,
        # it finds the maximum loaded link, and then find alternative routes for a path that passes by
        # the new path is found by a weighted (bidirectional) dijkstra / bellman-ford algorithm.
        # the 'step' parameter is the maximum path weight transfer in one iteration
        # the 'threshold' parameter determines when the iteration stops, but at least 10 iterations.
        max_link_loads = [max(self.link_loads.values())]
        attempts:int = 0
        while True:
            if (attempts>max_attempts or (len(max_link_loads) > 100 and ((np.average(max_link_loads[-50:-1]) - max_link_loads[-1]) < threshold ))):
                break

            # u, v = max(self.link_loads, key=lambda k: self.link_loads[k])
            max_keys = [key for key, value in self.link_loads.items() if value == max_link_loads[-1]]

            success: bool = False # successful for not in making possible progress
            for u, v in max_keys:
                # select a path whose contribution to the load of the link is the largest
                # this path's weight will be decreased later      
                current_path_ids: list = self.nx_digraph[u][v]['path_ids']
                path_contributions = {} # to be sorted
                for path_id in current_path_ids:
                    current_path = self.path_id_to_path[path_id]
                    src = current_path[0]
                    dst = current_path[-1]
                    contribution = self.routing_table[src][dst][path_id]*self.M_R[src][dst]
                    path_contributions[path_id] = contribution

                # sort the contributions in descending order
                sorted_keys = sorted(path_contributions, key=lambda k: path_contributions[k], reverse=True)
                for old_path_id in sorted_keys:
                    old_path = self.path_id_to_path[old_path_id]
                    src = old_path[0]
                    dst = old_path[-1]
                    new_paths = self.least_weighted_paths_for_pair(self.nx_digraph, src, dst, _weights, algorithm)
                    if randomize:
                        shuffle(new_paths)
                    for new_path in new_paths:
                        if new_path == old_path:
                            continue
                        else:
                            success = True
                            self.update_paths(old_path_id, old_path, new_path, src, dst, step)
                            break

                    if success:
                        break
                    else:
                        continue

                if success:
                    break
                else:
                    continue
            if success:
                # update the maximum link load
                max_link_load = max(self.link_loads.values())
                max_link_loads.append(max_link_load)
                attempts+=1
                self.method_2_attempts+=1
                continue # go to the next iteration
            else:
                print("No possible progress, terminating.")
                return (False, max_link_loads) 
                # return False, meaning that even decreasing the step parameter should not make any progress
        # print(f"done with step = {step} for {attempts} attempts.")
        return (True, max_link_loads)                
        # return True, meaning that decreasing the step parameter might make further progress

    def update_paths(self, old_path_id:int, old_path:list, new_path:list, src:int, dst:int, step:float):
        old_path_weight = self.routing_table[src][dst][old_path_id]
        # first check whether the new path is already in the routing table
        new_path_exists = False
        new_path_id = None
        delta_weight = None
        current_path_dict = self.routing_table[src][dst]
        for path_id, weight in current_path_dict.items():
            if self.path_id_to_path[path_id] == new_path:
                new_path_exists = True
                new_path_id = path_id
                delta_weight = min([step, old_path_weight, 1-weight])
                break
        if not new_path_exists:
            # if the new path is not in the routing table, give it new id and add it to the graph attributes(later)
            new_path_id = self.next_path_id
            self.next_path_id += 1
            self.path_id_to_path[new_path_id] = new_path
            delta_weight = min([step, old_path_weight])
            self.routing_table[src][dst][new_path_id] = 0.0
        # now we update the consequence of decreasing the weight of the old path
        # first handle the weigth
        self.routing_table[src][dst][old_path_id] -= delta_weight
        assert(1.0>= self.routing_table[src][dst][old_path_id] >= 0.0) # TODO: delete this assertion
            # if the remaining weight of theold path is very small, delete the old path
        if self.routing_table[src][dst][old_path_id] < 0.0001:
            del self.routing_table[src][dst][old_path_id]
            del self.path_id_to_path[old_path_id]
            for i in range(len(old_path)-1):
                self.nx_digraph[old_path[i]][old_path[i+1]]['path_ids'].remove(old_path_id)
        # then handle the link loads (nx graph and link_loads dictionary)
        for i in range(len(old_path)-1):
            self.nx_digraph[old_path[i]][old_path[i+1]]['load'] -= delta_weight*self.M_R[src][dst]/self.Cap_remote
            self.link_loads[(old_path[i], old_path[i+1])] -= delta_weight*self.M_R[src][dst]/self.Cap_remote
            assert(self.link_loads[(old_path[i], old_path[i+1])] == self.nx_digraph[old_path[i]][old_path[i+1]]['load']) # TODO: delete this assertion
        # now we update the consequence of increasing the weight of the new path
        # first handle the weigth
        self.routing_table[src][dst][new_path_id] += delta_weight
        # then the link loads
        for i in range(len(new_path)-1):
            self.nx_digraph[new_path[i]][new_path[i+1]]['load'] += delta_weight*self.M_R[src][dst]/self.Cap_remote
            self.link_loads[(new_path[i], new_path[i+1])] += delta_weight*self.M_R[src][dst]/self.Cap_remote
            assert(self.link_loads[(new_path[i], new_path[i+1])] == self.nx_digraph[new_path[i]][new_path[i+1]]['load']) # TODO: delete this assertion
            if not new_path_exists:
                assert(new_path_id not in self.nx_digraph[new_path[i]][new_path[i+1]]['path_ids'])# TODO: delete this assertion
                self.nx_digraph[new_path[i]][new_path[i+1]]['path_ids'].append(new_path_id)

    def optimize(self, num_method_1: int, max_num_method_2: int, 
        method_1_weights: callable = weight_function, method_2_weights: callable = weight_function, alt: bool = False):
        self.initialize()
        # execute optimization_method_1 without weights
        # equivalently, the routing table is initialized with ECMP-ASP

        assert(num_method_1 >= 1 and "num_method_1 should be a positive integer greater than 1.")
        # repeat optimization_method_1 num_method_1 times
        results_method_1 = []
        init_for_method2 = False
        for i in range(num_method_1):
            if i == num_method_1-1:
                init_for_method2 = True
            max_link_load = self.optimization_method_1(init_for_method2, method_1_weights)
            results_method_1.append(max_link_load)

        # repeat optimization_method_2 num_method_2 times, 
        results_method_2 = []
        # each time decreasing the step parameter by a factor of 0.5.
        step = 0.5
        max_link_loads = [0]
        for i in range(max_num_method_2):
            if alt:
                _continue, max_link_loads = self.optimization_method_2_alt(step, method_2_weights)
            else:
                _continue, max_link_loads = self.optimization_method_2(step, method_2_weights)
            results_method_2.append(max_link_loads)
            step *= 0.5
            if not _continue:
                break
        self.result_max_link_load = max_link_loads[-1]
        return results_method_1, results_method_2
    
    def optimize_and_profile(self, num_method_1: int, max_num_method_2: int, 
        method_1_weights: callable = weight_function, method_2_weights: callable = weight_function, alt: bool = False):
        self.initialize()
        # execute optimization_method_1 without weights
        # equivalently, the routing table is initialized with ECMP-ASP

        assert(num_method_1 >= 1 and "num_method_1 should be a positive integer greater than 1.")
        # repeat optimization_method_1 num_method_1 times
        results_method_1 = []
        times_method_1 = []
        peakRAMs_method_1 = []
        init_for_method2 = False
        for i in range(num_method_1):
            if i == num_method_1-1:
                init_for_method2 = True

            start_time = time.time()
            tracemalloc.start()

            max_link_load = self.optimization_method_1(init_for_method2, method_1_weights)

            end_time = time.time()
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()

            times_method_1.append(end_time - start_time)
            peakRAMs_method_1.append(peak_RAM)

            results_method_1.append(max_link_load)

        time_method_2 = 0
        peakRAM_method_2 = 0
        # repeat optimization_method_2 num_method_2 times, 
        # results_method_2 = []
        # each time decreasing the step parameter by a factor of 0.5.
        step = 0.5
        max_link_loads = [0]

        start_time = time.time()
        tracemalloc.start()

        for i in range(max_num_method_2):
            if alt:
                _continue, max_link_loads = self.optimization_method_2_alt(step, method_2_weights)
            else:
                _continue, max_link_loads = self.optimization_method_2(step, method_2_weights)
            # results_method_2.append(max_link_loads)
            step *= 0.5
            if not _continue:
                break
        end_time = time.time()
        peak_RAM = tracemalloc.get_traced_memory()[1]
        tracemalloc.stop()

        time_method_2 = (end_time - start_time)
        peakRAM_method_2 = peak_RAM
        self.result_max_link_load = max_link_loads[-1]

        return times_method_1, peakRAMs_method_1, time_method_2, peakRAM_method_2, results_method_1

    # a weighted dijkstra algorithm to find the least-weighted path for all s-d pairs.
    def least_weighted_paths_for_all_s_d(self, _G: Graph, _weights: callable, algorithm: str, MAX_KERNELS: int) -> dict:
        if algorithm == "dijkstra" or algorithm == "bellman-ford": 
            # only two options to pass to netowrkx
            paths_dict = {}
            for u in _G.nodes():
                paths_dict[u] = {}

            def calculate_shortest_paths(v1, v2):
                return list(nx.all_shortest_paths(_G, v1, v2, _weights, algorithm))
                
            if MAX_KERNELS == 1:
                # do not parallelize
                for (v1, v2) in self.vertex_pairs:
                    all_paths = calculate_shortest_paths(v1, v2)
                    if not all_paths:
                        raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
                    paths_dict[v1][v2] = all_paths
                
            elif MAX_KERNELS > 1:
                # parallelize the computation
                results = Parallel(n_jobs=MAX_KERNELS)(
                    delayed(calculate_shortest_paths)(v1, v2) for v1, v2 in self.vertex_pairs
                )
                for (v1, v2), all_paths in zip(self.vertex_pairs, results):
                    if not all_paths:
                        raise ValueError(f"Error, no path found between vertex {v1} and vertex {v2}")
                    paths_dict[v1][v2] = all_paths
            else:
                raise ValueError("MAX_KERNELS need to be a positive integer.")
        else:
            raise ValueError("Invalid algorithm choice.")
        
        return paths_dict

    def least_weighted_path_for_pair(self,_G: Graph, _s: int, _d: int, _weights: callable, algorithm: str) -> dict:
        # the following algorithms return only one least-weighted path that the algorithm encouters,
        # alternatively, find all least-weighted paths and then arbitrate.

        if algorithm == "dijkstra":
            # use dijkstra algorithm
            return nx.dijkstra_path(_G, _s, _d, weight=_weights)
        elif algorithm == "bellman-ford":
            # use bellman-ford algorithm
            return nx.bellman_ford_path(_G, _s, _d, weight=_weights)
        elif algorithm == "bidirectional-dijkstra":
            # use bidirectinal dijkstra algorithm, 
            # but this might have some problem with floating numbers
            return nx.bidirectional_dijkstra(_G, _s, _d, weight=_weights)
        else:
            raise ValueError("Invalid algorithm choice.")

    def least_weighted_paths_for_pair(self,_G: Graph, _s: int, _d: int, _weights: callable, algorithm: str) -> dict:
        # the following algorithms return all least-weighted paths between two nodes.
        if algorithm == "dijkstra" or algorithm == "bellman-ford": 
            _result = list(nx.all_shortest_paths(_G, _s, _d, _weights, algorithm))
            if not _result:
                raise ValueError(f"Error, no path found between vertex {_s} and vertex {_d}")
            
            return _result
                
        else:
            raise ValueError("Invalid algorithm choice.")

    def get_result_max_link_load(self):
        return self.result_max_link_load

    def get_method_2_attempts(self):
        return self.method_2_attempts

    def get_routing_table(self):
        
        # Inside this class property, the routing table is a dictionary of dictionary (to be the same as networkx)
        # the key of the first dictionary is the source node, and the key of the second dictionary is the destination node
        # the key of the thrid dictionary is the unique ids of paths, and the value is the weight of the path
       
        # output the routing table in the format of a dictionary, keys are (src, dst), values are lists of (path, weight)

        _routing_table = {}
        for (src, dst_dict) in self.routing_table.items():
            for (dst, path_dict) in dst_dict.items():
                _routing_table[(src, dst)] = [(self.path_id_to_path[path_id], weight) for (path_id, weight) in path_dict.items()]

        return _routing_table
