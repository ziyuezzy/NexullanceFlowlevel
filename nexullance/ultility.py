import os
import sys

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "IT_boost/build/"))

from Nexullance_IT_cpp import *

from topologies import HPC_topo
from nexullance import Nexullance_MP, Nexullance_OPT
from nexullance.MD_Nexullance_MP import MD_Nexullance_MP

import global_helpers as gl
import numpy as np
import csv
from networkx import Graph
import time
import tracemalloc
import statistics as st

# def remove_outliers(data):

#     # Step 1: Calculate mean and standard deviation
#     mean = st.mean(data)
#     stdev = st.stdev(data)

#     # Step 2: Define threshold (e.g., 2 standard deviations from the mean)
#     threshold = 2

#     # Step 3: Identify and remove outliers
#     cleaned_data = [x for x in data if abs(x - mean) <= threshold * stdev]

#     # give warning if there are more than two ourliners:
#     if len(data) - len(cleaned_data) > 2:
#         Warning("Warning: more than two outliers removed!")

#     return cleaned_data


class nexullance_exp_container:
    def __init__(self, topo_name:str, V:int, D:int, EPR:int, 
                 Demand_scaling_factor:float=10.0, Cap_core:float = 10.0, Cap_access:float=10.0,):
        self.topo_name = topo_name
        self.V = V
        self.D = D
        self.EPR = EPR
        self.Demand_scaling_factor = Demand_scaling_factor
        self.Cap_core = Cap_core
        self.Cap_access = Cap_access

        if not topo_name.endswith("topo"):
            topo_name = topo_name + "topo"
        self._network = HPC_topo.HPC_topo.initialize_child_instance(topo_name, V, D)
        self._network.pre_calculate_ECMP_ASP()


    def run_and_profile_nexullance_OPT(self, M_EPs:np.ndarray, traffic_name:str, repetitions:int=10):
        assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])

        # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, M_EPs)
        traffic_scaling = self.Demand_scaling_factor/max(np.max(core_link_flows)/self.Cap_core, np.max(access_link_flows)/self.Cap_access)

        scaled_M_EPs = traffic_scaling * M_EPs

        # re-calculate after scaling
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, scaled_M_EPs)
        ECMP_ASP_max_core_link_load = np.max(core_link_flows)/self.Cap_core
        ECMP_ASP_max_access_link_load = np.max(access_link_flows)/self.Cap_access

        measured_time=[]
        measured_PeakRAM=[]
        measured_phi=[]
        for i in range(repetitions+1):
            nexu = Nexullance_OPT.Nexullance_OPT(self._network.nx_graph, self.Cap_core, self.Cap_access, self.V, scaled_M_EPs)
            nexu.init_model()
            start_time = time.time()
            tracemalloc.start()
            max_load_Nexu = nexu.solve()
            end_time = time.time()
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            if i==1:
                continue
            measured_time.append(end_time - start_time)
            measured_PeakRAM.append(peak_RAM)
        
            if max_load_Nexu is None:
                # if max_load_Nexu is None, check if the bottleneck links are the access links
                if ECMP_ASP_max_core_link_load > ECMP_ASP_max_access_link_load:
                    # ok, we guessed right, continue
                    measured_phi.append(gl.network_total_throughput(scaled_M_EPs, ECMP_ASP_max_core_link_load, ECMP_ASP_max_access_link_load)/(self.V*self.EPR))
                else:
                    # we guessed wrong, this need to be investigated, maybe the random starting point in gurobi is makeing the core link load lower than access link load.
                    Warning(f"no result is produced for traffic: {traffic_name}, {self.topo_name}({self.V}, {self.D}) network")
            else:
                measured_phi.append(gl.network_total_throughput(scaled_M_EPs, max_load_Nexu, ECMP_ASP_max_access_link_load)/(self.V*self.EPR))

       # measured_time=remove_outliers(measured_time)
       # measured_PeakRAM=remove_outliers(measured_PeakRAM)
       # measured_phi=remove_outliers(measured_phi)
        return {"ave_phi": st.mean(measured_phi), "std_phi": st.stdev(measured_phi), 
                "ave_time[s]": st.mean(measured_time), "std_time[s]": st.stdev(measured_time), 
                "ave_PeakRAM[B]": st.mean(measured_PeakRAM), "std_PeakRAM[B]": st.stdev(measured_PeakRAM)}
        
    # def run_nexullance_OPT(self, M_EPs:np.ndarray, traffic_name:str):
    #     assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])

    #     # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
    #     core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, M_EPs)
    #     traffic_scaling = self.Demand_scaling_factor/max(np.max(core_link_flows)/self.Cap_core, np.max(access_link_flows)/self.Cap_access)

    #     scaled_M_EPs = traffic_scaling * M_EPs

    #     # re-calculate after scaling
    #     core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, scaled_M_EPs)
    #     ECMP_ASP_max_core_link_load = np.max(core_link_flows)/self.Cap_core
    #     ECMP_ASP_max_access_link_load = np.max(access_link_flows)/self.Cap_access

    #     nexu = Nexullance_OPT.Nexullance_OPT(self._network.nx_graph, self.Cap_core, self.Cap_access, self.V, scaled_M_EPs)
    #     nexu.init_model()
    #     max_load_Nexu = nexu.solve()


    
    #     if max_load_Nexu is None:
    #         # if max_load_Nexu is None, check if the bottleneck links are the access links
    #         if ECMP_ASP_max_core_link_load > ECMP_ASP_max_access_link_load:
    #             # ok, we guessed right, continue
    #             return gl.network_total_throughput(scaled_M_EPs, ECMP_ASP_max_core_link_load, ECMP_ASP_max_access_link_load)/(self.V*self.EPR)
    #         else:
    #             # we guessed wrong, this need to be investigated, maybe the random starting point in gurobi is makeing the core link load lower than access link load.
    #             Warning(f"no result is produced for traffic: {traffic_name}, {self.topo_name}({self.V}, {self.D}) network")
    #     else:
    #         print("result max core link load:", max_load_Nexu )
    #         return gl.network_total_throughput(scaled_M_EPs, max_load_Nexu, ECMP_ASP_max_access_link_load)/(self.V*self.EPR)

    def run_and_profile_nexullance_MP(self, max_path_length: int, M_EPs:np.ndarray, traffic_name:str, repetitions:int=10):
        assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])

        if max_path_length > 0:
            self._network.pre_calculate_APST_n(max_path_length)

        # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, M_EPs)
        traffic_scaling = self.Demand_scaling_factor/max(np.max(core_link_flows)/self.Cap_core, np.max(access_link_flows)/self.Cap_access)

        scaled_M_EPs = traffic_scaling * M_EPs

        # re-calculate after scaling
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, scaled_M_EPs)
        ECMP_ASP_max_core_link_load = np.max(core_link_flows)/self.Cap_core
        ECMP_ASP_max_access_link_load = np.max(access_link_flows)/self.Cap_access

        measured_time=[]
        measured_PeakRAM=[]
        measured_phi=[]
        for i in range(repetitions+1):
            if max_path_length > 0:
                nexu = Nexullance_MP.Nexullance_MP(self._network.nx_graph, self._network.__getattribute__(f"APST_{max_path_length}") ,
                                                self.Cap_core, self.Cap_access, self.V, scaled_M_EPs)
            else:
                nexu = Nexullance_MP.Nexullance_MP(self._network.nx_graph, self._network.ASP,
                                                self.Cap_core, self.Cap_access, self.V, scaled_M_EPs)
            nexu.init_model()
            tracemalloc.start()
            start_time = time.time()
            max_load_Nexu, _ = nexu.solve()
            end_time = time.time()
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            if i==1:
                continue
            measured_time.append(end_time - start_time)
            measured_PeakRAM.append(peak_RAM)
        
            if max_load_Nexu is None:
                # if max_load_Nexu is None, check if the bottleneck links are the access links
                if ECMP_ASP_max_core_link_load > ECMP_ASP_max_access_link_load:
                    # ok, we guessed right, continue
                    measured_phi.append(gl.network_total_throughput(scaled_M_EPs, ECMP_ASP_max_core_link_load, ECMP_ASP_max_access_link_load)/(self.V*self.EPR))
                else:
                    # we guessed wrong, this need to be investigated, maybe the random starting point in gurobi is makeing the core link load lower than access link load.
                    Warning(f"no result is produced for traffic: {traffic_name}, {self.topo_name}({self.V}, {self.D}) network")
            else:
                measured_phi.append(gl.network_total_throughput(scaled_M_EPs, max_load_Nexu, ECMP_ASP_max_access_link_load)/(self.V*self.EPR))

       # measured_time=remove_outliers(measured_time)
       # measured_PeakRAM=remove_outliers(measured_PeakRAM)
       # measured_phi=remove_outliers(measured_phi)
        return {"ave_phi": st.mean(measured_phi), "std_phi": st.stdev(measured_phi), 
                "ave_time[s]": st.mean(measured_time), "std_time[s]": st.stdev(measured_time), 
                "ave_PeakRAM[B]": st.mean(measured_PeakRAM), "std_PeakRAM[B]": st.stdev(measured_PeakRAM)}
        
    def run_nexullance_MP_return_RT(self, max_path_length: int, M_EPs:np.ndarray, traffic_name:str):
        
        assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])

        self._network.pre_calculate_APST_n(max_path_length)

        # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, M_EPs)
        ECMP_ASP_max_core_link_load = np.max(core_link_flows)/self.Cap_core
        ECMP_ASP_max_access_link_load = np.max(access_link_flows)/self.Cap_access
        traffic_scaling = self.Demand_scaling_factor/max(ECMP_ASP_max_core_link_load, ECMP_ASP_max_access_link_load)

        scaled_M_EPs = traffic_scaling * M_EPs

        nexu = Nexullance_MP.Nexullance_MP(self._network.nx_graph, self._network.__getattribute__(f"APST_{max_path_length}") ,
                                           self.Cap_core, self.Cap_access, self.V, scaled_M_EPs)
        nexu.init_model()
        max_load_Nexu, result_RT = nexu.solve()
        
        if max_load_Nexu is None:
            print("Nexullance_MP failed")
            sys.exit(1)   
        else:
            Phi = gl.network_total_throughput(scaled_M_EPs, max_load_Nexu)
            print(f"max link load from Nexullance_MP_APST_{max_path_length}=", max_load_Nexu)
            print(f"resulting phi from Nexullance_MP_APST_{max_path_length}=", Phi/(self.V*self.EPR))

            return gl.clean_up_weighted_paths(result_RT)
        
    def run_ECMP_SP(self, M_EPs:np.ndarray, num_paths: int=0):
        assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])

        if num_paths > 0:
            self._network.pre_calculate_ECMP_nSP(num_paths)
        else:
            self._network.pre_calculate_ECMP_ASP()

        # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, M_EPs)
        traffic_scaling = self.Demand_scaling_factor/max(np.max(core_link_flows)/self.Cap_core, np.max(access_link_flows)/self.Cap_access)
        scaled_M_EPs = traffic_scaling * M_EPs

        if num_paths > 0:
            core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(
                                                    self._network.__getattribute__(f"ECMP_{num_paths}SP"), self.EPR, scaled_M_EPs)
        else:
            core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, scaled_M_EPs)
        
        ECMP_ASP_phi = gl.network_total_throughput(scaled_M_EPs, max(core_link_flows), max(access_link_flows))/(self.V*self.EPR)
        return ECMP_ASP_phi


        
    def run_and_profile_nexullance_IT(self, M_EPs:np.ndarray, traffic_name:str, repetitions:int=10):
        assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])

        # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, M_EPs)
        traffic_scaling = self.Demand_scaling_factor/max(np.max(core_link_flows)/self.Cap_core, np.max(access_link_flows)/self.Cap_access)

        scaled_M_EPs = traffic_scaling * M_EPs

        arcs = self._network.generate_graph_arcs()

        measured_time=[]
        measured_PeakRAM=[]
        measured_phi=[]
        for i in range(repetitions+1):
            nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, self.Cap_access, debug=False)        
            nexu.set_parameters(0.1, 7.0, 0.00001, 5, 1000000, self.V*3, False)
            tracemalloc.start()
            start_time = time.time()
            nexu_result = nexu.run_IT(scaled_M_EPs, self.EPR)
            end_time = time.time()
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            if i==1:
                continue
            measured_time.append(end_time - start_time)
            measured_PeakRAM.append(peak_RAM)
            measured_phi.append(nexu_result.get_phi())

       # measured_time=remove_outliers(measured_time)
       # measured_PeakRAM=remove_outliers(measured_PeakRAM)
       # measured_phi=remove_outliers(measured_phi)
        return {"ave_phi": st.mean(measured_phi), "std_phi": st.stdev(measured_phi), 
                "ave_time[s]": st.mean(measured_time), "std_time[s]": st.stdev(measured_time), 
                "ave_PeakRAM[B]": st.mean(measured_PeakRAM), "std_PeakRAM[B]": st.stdev(measured_PeakRAM)}
        
    def run_nexullance_IT_return_RT(self, M_EPs:np.ndarray, traffic_name:str, _debug=False):
        
        assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])
        # Scale the traffic demand matrix, so that the max link load (under ECMP_ASP) equals to "Demand_scaling_factor"
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(self._network.ECMP_ASP, self.EPR, M_EPs)
        ECMP_ASP_max_core_link_load = np.max(core_link_flows)/self.Cap_core
        ECMP_ASP_max_access_link_load = np.max(access_link_flows)/self.Cap_access
        traffic_scaling = self.Demand_scaling_factor/max(ECMP_ASP_max_core_link_load, ECMP_ASP_max_access_link_load)

        scaled_M_EPs = traffic_scaling * M_EPs

        arcs = self._network.generate_graph_arcs()
        nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, self.Cap_access, debug=_debug)        
        nexu.set_parameters(0.1, 7.0, 0.00001, 5, 1000000, self.V*3, False)
        nexu_result = nexu.run_IT(scaled_M_EPs, self.EPR)
        print(f"max core link load from Nexullance_IT=", nexu_result.get_max_link_load())
        print(f"resulting phi from Nexullance_IT=", nexu_result.get_phi())

        return nexu_result.get_routing_table()
    
    def run_and_profile_MD_nexullance_IT(self, M_EPs_s:list[np.ndarray], M_EPs_weights:list[float], repetitions:int=10):
        # assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])
        assert(len(M_EPs_s) == len(M_EPs_weights))
        arcs = self._network.generate_graph_arcs()
        measured_time=[]
        measured_PeakRAM=[]
        OBJ_s=[]
        for i in range(repetitions+1):
            nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, self.Cap_access, debug=False)        
            nexu.set_parameters(0.1, 7.0, 0.00001, 5, 100000000, self.V*3, False)
            tracemalloc.start()
            nexu_result = nexu.run_MD_IT(M_EPs_s, M_EPs_weights, self.EPR)
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            if i==1:
                continue
            measured_time.append(nexu_result.get_elapsed_time())
            measured_PeakRAM.append(peak_RAM)
            OBJ_s.append(nexu_result.get_obj())
        # measured_time=remove_outliers(measured_time)
        # measured_PeakRAM=remove_outliers(measured_PeakRAM)
        # measured_phi=remove_outliers(measured_phi)
        return {"ave_obj": st.mean(OBJ_s), "std_obj": st.stdev(OBJ_s), 
                "ave_time[s]": st.mean(measured_time), "std_time[s]": st.stdev(measured_time), 
                "ave_PeakRAM[B]": st.mean(measured_PeakRAM), "std_PeakRAM[B]": st.stdev(measured_PeakRAM)}
    
    def run_MD_nexullance_IT(self, M_EPs_s:list[np.ndarray], M_EPs_weights:list[float], _debug=False):
        # assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])
        assert(len(M_EPs_s) == len(M_EPs_weights))
        arcs = self._network.generate_graph_arcs()
        nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, self.Cap_access, debug=_debug)        
        nexu.set_parameters(0.1, 7.0, 0.00001, 5, 100000000, self.V*3, False)
        nexu_result = nexu.run_MD_IT(M_EPs_s, M_EPs_weights, self.EPR)
        return nexu_result.get_obj(), nexu_result.get_phis()
    
    def run_MD_nexullance_IT_return_RT(self, M_EPs_s:list[np.ndarray], M_EPs_weights:list[float], _debug=False):
        # assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])
        assert(len(M_EPs_s) == len(M_EPs_weights))
        arcs = self._network.generate_graph_arcs()
        nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, self.Cap_access, debug=_debug)        
        nexu.set_parameters(0.1, 7.0, 0.00001, 5, 100000000, self.V*3, False)
        nexu_result = nexu.run_MD_IT(M_EPs_s, M_EPs_weights, self.EPR)
        # print("resulting MD_Nexullance_IT obj function:", nexu_result.get_obj())
        return nexu_result.get_obj(), nexu_result.get_routing_table()
        
    def run_and_profile_MD_nexullance_MP(self, M_EPs_s:list[np.ndarray], M_EPs_weights:list[float],  max_path_length:int, _debug=False, repetitions:int=10):
        # assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])
        assert(len(M_EPs_s) == len(M_EPs_weights))
        self._network.pre_calculate_APST_n(max_path_length)
        measured_time=[]
        measured_PeakRAM=[]
        OBJ_s=[]
        for i in range(repetitions+1):
            md_nexu = MD_Nexullance_MP.MD_Nexullance_MP(self._network.nx_graph, self._network.__getattribute__(f"APST_{max_path_length}") ,
                                                self.Cap_core, self.Cap_access, self.V, M_EPs_s, M_EPs_weights, _verbose=_debug)
            tracemalloc.start()
            start_time = time.time()
            md_nexu.init_model(self.EPR)
            _, _ = md_nexu.solve()
            end_time = time.time()
            MD_peak_RAM = tracemalloc.get_traced_memory()[1]/1024/1024
            MD_time = end_time-start_time
            tracemalloc.stop()
            if i==1:
                continue
            measured_time.append(MD_time)
            measured_PeakRAM.append(MD_peak_RAM)
            OBJ_s.append(md_nexu.get_Objective_func()*self.V*self.EPR)
        # measured_time=remove_outliers(measured_time)
        # measured_PeakRAM=remove_outliers(measured_PeakRAM)
        # measured_phi=remove_outliers(measured_phi)
        return {"ave_obj": st.mean(OBJ_s), "std_obj": st.stdev(OBJ_s), 
                "ave_time[s]": st.mean(measured_time), "std_time[s]": st.stdev(measured_time), 
                "ave_PeakRAM[B]": st.mean(measured_PeakRAM), "std_PeakRAM[B]": st.stdev(measured_PeakRAM)}
        
    def run_MD_nexullance_MP(self, M_EPs_s:list[np.ndarray], M_EPs_weights:list[float],  max_path_length:int, _debug=False):
        # assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])
        assert(len(M_EPs_s) == len(M_EPs_weights))
        self._network.pre_calculate_APST_n(max_path_length)
        md_nexu = MD_Nexullance_MP.MD_Nexullance_MP(self._network.nx_graph, self._network.__getattribute__(f"APST_{max_path_length}") ,
                                            self.Cap_core, self.Cap_access, self.V, M_EPs_s, M_EPs_weights, _verbose=_debug)
        md_nexu.init_model(self.EPR)
        maxL_NEXU_s, _ = md_nexu.solve()
        phis=[]
        for m, maxL_NEXU in enumerate(maxL_NEXU_s):
            phis.append(gl.network_total_throughput(M_EPs_s[m], maxL_NEXU, maxL_NEXU)/(self.V*self.EPR))
        return md_nexu.get_Objective_func()/(self.V*self.EPR), phis
    
    def run_MD_nexullance_MP_return_RT(self, M_EPs_s:list[np.ndarray], M_EPs_weights:list[float],  max_path_length:int, _debug=False):
        # assert(self.V*self.EPR == M_EPs.shape[0] == M_EPs.shape[1])
        assert(len(M_EPs_s) == len(M_EPs_weights))
        self._network.pre_calculate_APST_n(max_path_length)
        md_nexu = MD_Nexullance_MP.MD_Nexullance_MP(self._network.nx_graph, self._network.__getattribute__(f"APST_{max_path_length}") ,
                                            self.Cap_core, self.Cap_access, self.V, M_EPs_s, M_EPs_weights, _verbose=_debug)
        md_nexu.init_model(self.EPR)
        maxL_NEXU_s, RT = md_nexu.solve()
        # phis=[]
        # print("resulting MD_Nexullance_MP obj function:", md_nexu.get_Objective_func()/(self.V*self.EPR))
        # for m, maxL_NEXU in enumerate(maxL_NEXU_s):
        #     phis.append(gl.network_total_throughput(M_EPs_s[m], maxL_NEXU, maxL_NEXU)/(self.V*self.EPR))
        # return phis, RT
        return md_nexu.get_Objective_func()/(self.V*self.EPR), RT
        