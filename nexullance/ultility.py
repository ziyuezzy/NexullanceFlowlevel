"""
Utility module for executing Nexullance and MD_Nexullance algorithms.

This module provides a container class for running various routing algorithms
on HPC network topologies with traffic demand matrices.
"""

import os
import sys
import time
import tracemalloc
import statistics as st

import numpy as np

current_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.append(os.path.join(current_dir, ".."))
sys.path.append(os.path.join(current_dir, "IT_boost/build/"))

from Nexullance_IT_cpp import Nexullance_IT_interface
from topologies import HPC_topo
from nexullance import Nexullance_MP, Nexullance_OPT
from nexullance.MD_Nexullance_MP import MD_Nexullance_MP
import global_helpers as gl


class nexullance_exp_container:
    """
    Container class for running Nexullance experiments on HPC topologies.
    
    Attributes:
        topo_name: Name of the topology
        V: Number of vertices
        D: Degree
        EPR: Endpoints per router
        Demand_scaling_factor: Scaling factor for traffic demand
        Cap_core: Core link capacity
        Cap_access: Access link capacity
    """
    
    def __init__(self, topo_name: str, V: int, D: int, EPR: int,
                 Demand_scaling_factor: float = 10.0, Cap_core: float = 10.0, 
                 Cap_access: float = 10.0):
        """Initialize the experiment container with topology and capacity parameters."""
        self.topo_name = topo_name
        self.V = V
        self.D = D
        self.EPR = EPR
        self.Demand_scaling_factor = Demand_scaling_factor
        self.Cap_core = Cap_core
        self.Cap_access = Cap_access

        if not topo_name.endswith("topo"):
            topo_name = topo_name + "topo"
        self._network = HPC_topo.initialize_child_instance(topo_name, V, D)
        self._network.pre_calculate_ECMP_ASP()

    def _scale_traffic_demand(self, M_EPs: np.ndarray):
        """Scale traffic demand matrix based on ECMP_ASP max link load."""
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(
            self._network.ECMP_ASP, self.EPR, M_EPs)
        traffic_scaling = self.Demand_scaling_factor / max(
            np.max(core_link_flows) / self.Cap_core, 
            np.max(access_link_flows) / self.Cap_access)
        return traffic_scaling * M_EPs

    def _scale_multiple_traffic_demands(self, M_EPs_s: list[np.ndarray]):
        """Scale multiple traffic demand matrices, each with its own scaling factor."""
        scaled_matrices = []
        
        # Scale each demand matrix independently
        for M_EPs in M_EPs_s:
            scaled_matrices.append(self._scale_traffic_demand(M_EPs))
        
        return scaled_matrices

    def _calculate_phi(self, M_EPs: np.ndarray, max_core_link_load: float, 
                      max_access_link_load: float):
        """Calculate normalized throughput (phi)."""
        return gl.network_total_throughput(M_EPs, max_core_link_load, 
                                           max_access_link_load) / (self.V * self.EPR)

    def _aggregate_measurements(self, measured_time: list, measured_PeakRAM: list, 
                               measured_metric: list, metric_name: str = "phi"):
        """Aggregate measurement statistics."""
        return {
            f"ave_{metric_name}": st.mean(measured_metric), 
            f"std_{metric_name}": st.stdev(measured_metric),
            "ave_time[s]": st.mean(measured_time), 
            "std_time[s]": st.stdev(measured_time),
            "ave_PeakRAM[B]": st.mean(measured_PeakRAM), 
            "std_PeakRAM[B]": st.stdev(measured_PeakRAM)
        }


    def run_nexullance_OPT(self, M_EPs: np.ndarray, verbose: bool = False):
        """
        Run Nexullance OPT algorithm.
        
        Args:
            M_EPs: Traffic demand matrix
            verbose: Whether to print results
            
        Returns:
            phi value (normalized throughput)
        """
        assert self.V * self.EPR == M_EPs.shape[0] == M_EPs.shape[1]

        scaled_M_EPs = self._scale_traffic_demand(M_EPs)

        # Calculate ECMP baseline for fallback
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(
            self._network.ECMP_ASP, self.EPR, scaled_M_EPs)
        ECMP_max_core = np.max(core_link_flows) / self.Cap_core
        ECMP_max_access = np.max(access_link_flows) / self.Cap_access

        nexu = Nexullance_OPT.Nexullance_OPT(self._network.nx_graph, self.Cap_core, 
                                              self.Cap_access, self.V, scaled_M_EPs)
        nexu.init_model()
        max_load_Nexu = nexu.solve()

        if max_load_Nexu is None:
            if ECMP_max_core > ECMP_max_access:
                phi = self._calculate_phi(scaled_M_EPs, ECMP_max_core, ECMP_max_access)
            else:
                Warning("No result produced from Nexullance OPT")
                phi = self._calculate_phi(scaled_M_EPs, ECMP_max_core, ECMP_max_access)
        else:
            phi = self._calculate_phi(scaled_M_EPs, max_load_Nexu, ECMP_max_access)
        
        if verbose:
            print(f"max core link load from Nexullance_OPT=", max_load_Nexu)
            print(f"resulting phi from Nexullance_OPT=", phi)
        
        return phi

    def profile_nexullance_OPT(self, M_EPs: np.ndarray, repetitions: int = 10):
        """Profile Nexullance OPT algorithm performance."""
        assert self.V * self.EPR == M_EPs.shape[0] == M_EPs.shape[1]

        scaled_M_EPs = self._scale_traffic_demand(M_EPs)

        # Calculate ECMP baseline
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(
            self._network.ECMP_ASP, self.EPR, scaled_M_EPs)
        ECMP_max_core = np.max(core_link_flows) / self.Cap_core
        ECMP_max_access = np.max(access_link_flows) / self.Cap_access

        measured_time = []
        measured_PeakRAM = []
        measured_phi = []
        
        for i in range(repetitions + 1):
            nexu = Nexullance_OPT.Nexullance_OPT(self._network.nx_graph, self.Cap_core, 
                                                  self.Cap_access, self.V, scaled_M_EPs)
            nexu.init_model()
            
            start_time = time.time()
            tracemalloc.start()
            max_load_Nexu = nexu.solve()
            end_time = time.time()
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            
            if i == 0:
                continue
                
            measured_time.append(end_time - start_time)
            measured_PeakRAM.append(peak_RAM)
        
            if max_load_Nexu is None:
                if ECMP_max_core > ECMP_max_access:
                    measured_phi.append(self._calculate_phi(scaled_M_EPs, 
                        ECMP_max_core, ECMP_max_access))
                else:
                    Warning("No result produced")
            else:
                measured_phi.append(self._calculate_phi(scaled_M_EPs, max_load_Nexu, 
                                                       ECMP_max_access))

        return self._aggregate_measurements(measured_time, measured_PeakRAM, measured_phi)


    def run_nexullance_MP(self, M_EPs: np.ndarray, max_path_length: int = 4, 
                         return_RT: bool = True, verbose: bool = False):
        """
        Run Nexullance MP algorithm.
        
        Args:
            M_EPs: Traffic demand matrix
            max_path_length: Maximum path length (0 for ASP)
            return_RT: Whether to return routing table
            verbose: Whether to print results
            
        Returns:
            Routing table (if return_RT=True) or phi value
        """
        assert self.V * self.EPR == M_EPs.shape[0] == M_EPs.shape[1]

        if max_path_length > 0:
            self._network.pre_calculate_APST_n(max_path_length)
            path_set = self._network.__getattribute__(f"APST_{max_path_length}")
        else:
            path_set = self._network.ASP

        scaled_M_EPs = self._scale_traffic_demand(M_EPs)

        nexu = Nexullance_MP.Nexullance_MP(
            self._network.nx_graph, path_set,
            self.Cap_core, self.Cap_access, self.V, scaled_M_EPs)
        nexu.init_model()
        max_load_Nexu, result_RT = nexu.solve()
        
        if max_load_Nexu is None:
            print("Nexullance_MP failed")
            sys.exit(1)
        
        if verbose:
            Phi = gl.network_total_throughput(scaled_M_EPs, max_load_Nexu)
            print(f"max link load from Nexullance_MP_APST_{max_path_length}=", max_load_Nexu)
            print(f"resulting phi from Nexullance_MP_APST_{max_path_length}=", 
                  Phi / (self.V * self.EPR))
        
        if return_RT:
            return gl.clean_up_weighted_paths(result_RT)
        else:
            return self._calculate_phi(scaled_M_EPs, max_load_Nexu, max_load_Nexu)

    def profile_nexullance_MP(self, M_EPs: np.ndarray, max_path_length: int = 4, 
                             repetitions: int = 10):
        """Profile Nexullance MP algorithm performance."""
        assert self.V * self.EPR == M_EPs.shape[0] == M_EPs.shape[1]

        if max_path_length > 0:
            self._network.pre_calculate_APST_n(max_path_length)

        scaled_M_EPs = self._scale_traffic_demand(M_EPs)

        # Calculate ECMP baseline for fallback
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(
            self._network.ECMP_ASP, self.EPR, scaled_M_EPs)
        ECMP_max_core = np.max(core_link_flows) / self.Cap_core
        ECMP_max_access = np.max(access_link_flows) / self.Cap_access

        measured_time = []
        measured_PeakRAM = []
        measured_phi = []
        
        for i in range(repetitions + 1):
            path_set = (self._network.__getattribute__(f"APST_{max_path_length}") 
                       if max_path_length > 0 else self._network.ASP)
                
            nexu = Nexullance_MP.Nexullance_MP(self._network.nx_graph, path_set,
                                               self.Cap_core, self.Cap_access, 
                                               self.V, scaled_M_EPs)
            nexu.init_model()
            
            tracemalloc.start()
            start_time = time.time()
            max_load_Nexu, _ = nexu.solve()
            end_time = time.time()
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            
            if i == 0:
                continue
                
            measured_time.append(end_time - start_time)
            measured_PeakRAM.append(peak_RAM)
        
            if max_load_Nexu is None:
                if ECMP_max_core > ECMP_max_access:
                    measured_phi.append(self._calculate_phi(scaled_M_EPs, ECMP_max_core, 
                                                           ECMP_max_access))
                else:
                    Warning(f"No result produced")
            else:
                measured_phi.append(self._calculate_phi(scaled_M_EPs, max_load_Nexu, 
                                                       ECMP_max_access))

        return self._aggregate_measurements(measured_time, measured_PeakRAM, measured_phi)


    def run_ECMP_SP(self, M_EPs: np.ndarray, num_paths: int = 0):
        """Run ECMP shortest path routing."""
        assert self.V * self.EPR == M_EPs.shape[0] == M_EPs.shape[1]

        if num_paths > 0:
            self._network.pre_calculate_ECMP_nSP(num_paths)
        else:
            self._network.pre_calculate_ECMP_ASP()

        scaled_M_EPs = self._scale_traffic_demand(M_EPs)

        if num_paths > 0:
            path_set = self._network.__getattribute__(f"ECMP_{num_paths}SP")
        else:
            path_set = self._network.ECMP_ASP
            
        core_link_flows, access_link_flows = self._network.distribute_M_EPs_on_weighted_paths(
            path_set, self.EPR, scaled_M_EPs)
        
        ECMP_phi = self._calculate_phi(scaled_M_EPs, 
                                       max(core_link_flows) / self.Cap_core,
                                       max(access_link_flows) / self.Cap_access)
        return ECMP_phi


    def run_nexullance_IT(self, M_EPs: np.ndarray, return_RT: bool = True, 
                         verbose: bool = False, debug: bool = False):
        """
        Run Nexullance IT algorithm.
        
        Args:
            M_EPs: Traffic demand matrix
            return_RT: Whether to return routing table
            verbose: Whether to print results
            debug: Debug mode
            
        Returns:
            Routing table (if return_RT=True) or phi value
        """
        assert self.V * self.EPR == M_EPs.shape[0] == M_EPs.shape[1]
        
        scaled_M_EPs = self._scale_traffic_demand(M_EPs)
        arcs = self._network.generate_graph_arcs()
        
        nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, 
                                       self.Cap_access, debug=debug)
        nexu.set_parameters(0.1, 7.0, 0.00001, 5, min(self.V ** 4, 2147483647), self.V * 3, False)
        nexu_result = nexu.run_IT(scaled_M_EPs, self.EPR)
        
        if verbose:
            print(f"max core link load from Nexullance_IT=", nexu_result.get_max_core_link_load())
            print(f"resulting phi from Nexullance_IT=", nexu_result.get_phi())
        
        if return_RT:
            return nexu_result.get_routing_table()
        else:
            return nexu_result.get_phi()

    def profile_nexullance_IT(self, M_EPs: np.ndarray, repetitions: int = 10):
        """Profile Nexullance IT algorithm performance."""
        assert self.V * self.EPR == M_EPs.shape[0] == M_EPs.shape[1]

        scaled_M_EPs = self._scale_traffic_demand(M_EPs)
        arcs = self._network.generate_graph_arcs()

        measured_time = []
        measured_PeakRAM = []
        measured_phi = []
        
        for i in range(repetitions + 1):
            nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, 
                                          self.Cap_access, debug=False)
            nexu.set_parameters(0.1, 7.0, 0.00001, 5, min(self.V ** 4, 2147483647), self.V * 3, False)
            
            tracemalloc.start()
            start_time = time.time()
            nexu_result = nexu.run_IT(scaled_M_EPs, self.EPR)
            end_time = time.time()
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            
            if i == 0:
                continue
                
            measured_time.append(end_time - start_time)
            measured_PeakRAM.append(peak_RAM)
            measured_phi.append(nexu_result.get_phi())

        return self._aggregate_measurements(measured_time, measured_PeakRAM, measured_phi)


    def run_MD_nexullance_IT(self, M_EPs_s: list[np.ndarray], M_EPs_weights: list[float], 
                            return_RT: bool = True, verbose: bool = False, 
                            debug: bool = False, scale_traffic: bool = True):
        """
        Run MD Nexullance IT algorithm.
        
        Args:
            M_EPs_s: List of traffic demand matrices
            M_EPs_weights: Weights for each demand matrix
            return_RT: Whether to return routing table
            verbose: Whether to print results
            debug: Debug mode
            scale_traffic: Whether to scale traffic demand matrices
            
        Returns:
            (obj, routing_table) if return_RT=True, else (obj, phis)
        """
        assert len(M_EPs_s) == len(M_EPs_weights)
        
        # Optionally scale all demand matrices
        scaled_M_EPs_s = self._scale_multiple_traffic_demands(M_EPs_s) if scale_traffic else M_EPs_s
        
        arcs = self._network.generate_graph_arcs()
        nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, 
                                       self.Cap_access, debug=debug)
        nexu.set_parameters(0.1, 7.0, 0.00001, 5, min(self.V ** 4, 2147483647), self.V * 3, False)
        nexu_result = nexu.run_MD_IT(scaled_M_EPs_s, M_EPs_weights, self.EPR)
        
        if verbose:
            print("resulting MD_Nexullance_IT obj function:", nexu_result.get_obj())
        
        if return_RT:
            return nexu_result.get_obj(), nexu_result.get_routing_table()
        else:
            return nexu_result.get_obj(), nexu_result.get_phis()

    def profile_MD_nexullance_IT(self, M_EPs_s: list[np.ndarray], 
                                 M_EPs_weights: list[float], 
                                 repetitions: int = 10, scale_traffic: bool = True):
        """Profile MD Nexullance IT algorithm performance."""
        assert len(M_EPs_s) == len(M_EPs_weights)
        
        # Optionally scale all demand matrices
        scaled_M_EPs_s = self._scale_multiple_traffic_demands(M_EPs_s) if scale_traffic else M_EPs_s
        
        arcs = self._network.generate_graph_arcs()
        measured_time = []
        measured_PeakRAM = []
        OBJ_s = []
        
        for i in range(repetitions + 1):
            nexu = Nexullance_IT_interface(self.V, arcs, self.Cap_core, 
                                          self.Cap_access, debug=False)
            nexu.set_parameters(0.1, 7.0, 0.00001, 5, min(self.V ** 4, 2147483647), self.V * 3, False)
            
            tracemalloc.start()
            nexu_result = nexu.run_MD_IT(scaled_M_EPs_s, M_EPs_weights, self.EPR)
            peak_RAM = tracemalloc.get_traced_memory()[1]
            tracemalloc.stop()
            
            if i == 0:
                continue
                
            measured_time.append(nexu_result.get_elapsed_time())
            measured_PeakRAM.append(peak_RAM)
            OBJ_s.append(nexu_result.get_obj())

        return self._aggregate_measurements(measured_time, measured_PeakRAM, OBJ_s, "obj")


    def run_MD_nexullance_MP(self, M_EPs_s: list[np.ndarray], M_EPs_weights: list[float], 
                            max_path_length: int = 4, return_RT: bool = True, 
                            verbose: bool = False, scale_traffic: bool = True):
        """
        Run MD Nexullance MP algorithm.
        
        Args:
            M_EPs_s: List of traffic demand matrices
            M_EPs_weights: Weights for each demand matrix
            max_path_length: Maximum path length
            return_RT: Whether to return routing table
            verbose: Whether to print results
            scale_traffic: Whether to scale traffic demand matrices
            
        Returns:
            (obj, routing_table) if return_RT=True, else (obj, phis)
        """
        assert len(M_EPs_s) == len(M_EPs_weights)
        
        # Optionally scale all demand matrices
        scaled_M_EPs_s = self._scale_multiple_traffic_demands(M_EPs_s) if scale_traffic else M_EPs_s
        
        self._network.pre_calculate_APST_n(max_path_length)
        md_nexu = MD_Nexullance_MP.MD_Nexullance_MP(
            self._network.nx_graph, 
            self._network.__getattribute__(f"APST_{max_path_length}"),
            self.Cap_core, self.Cap_access, self.V, scaled_M_EPs_s, M_EPs_weights, 
            _verbose=verbose)
        md_nexu.init_model(self.EPR)
        maxL_NEXU_s, RT = md_nexu.solve()
        
        obj_value = md_nexu.get_Objective_func() / (self.V * self.EPR)
        
        if return_RT:
            return obj_value, RT
        else:
            phis = []
            for m, maxL_NEXU in enumerate(maxL_NEXU_s):
                phis.append(gl.network_total_throughput(scaled_M_EPs_s[m], maxL_NEXU, maxL_NEXU) / 
                           (self.V * self.EPR))
            return obj_value, phis

    def profile_MD_nexullance_MP(self, M_EPs_s: list[np.ndarray], 
                                 M_EPs_weights: list[float], 
                                 max_path_length: int = 4, 
                                 repetitions: int = 10, scale_traffic: bool = True):
        """Profile MD Nexullance MP algorithm performance."""
        assert len(M_EPs_s) == len(M_EPs_weights)
        
        # Optionally scale all demand matrices
        scaled_M_EPs_s = self._scale_multiple_traffic_demands(M_EPs_s) if scale_traffic else M_EPs_s
        
        self._network.pre_calculate_APST_n(max_path_length)
        measured_time = []
        measured_PeakRAM = []
        OBJ_s = []
        
        for i in range(repetitions + 1):
            md_nexu = MD_Nexullance_MP.MD_Nexullance_MP(
                self._network.nx_graph, 
                self._network.__getattribute__(f"APST_{max_path_length}"),
                self.Cap_core, self.Cap_access, self.V, scaled_M_EPs_s, M_EPs_weights, 
                _verbose=False)
            
            tracemalloc.start()
            start_time = time.time()
            md_nexu.init_model(self.EPR)
            _, _ = md_nexu.solve()
            end_time = time.time()
            MD_peak_RAM = tracemalloc.get_traced_memory()[1] / 1024 / 1024
            MD_time = end_time - start_time
            tracemalloc.stop()
            
            if i == 0:
                continue
                
            measured_time.append(MD_time)
            measured_PeakRAM.append(MD_peak_RAM)
            OBJ_s.append(md_nexu.get_Objective_func() * self.V * self.EPR)

        return self._aggregate_measurements(measured_time, measured_PeakRAM, OBJ_s, "obj")

    # ============================================================================
    # Backward Compatibility Wrappers
    # ============================================================================
    
    def run_and_profile_nexullance_OPT(self, M_EPs: np.ndarray, traffic_name: str = "", 
                                       repetitions: int = 10):
        """Backward compatibility wrapper for profile_nexullance_OPT."""
        return self.profile_nexullance_OPT(M_EPs, repetitions)
    
    def run_and_profile_nexullance_MP(self, max_path_length: int, M_EPs: np.ndarray, 
                                      traffic_name: str = "", repetitions: int = 10):
        """Backward compatibility wrapper for profile_nexullance_MP."""
        return self.profile_nexullance_MP(M_EPs, max_path_length, repetitions)
    
    def run_nexullance_MP_return_RT(self, max_path_length: int, M_EPs: np.ndarray, 
                                    traffic_name: str = ""):
        """Backward compatibility wrapper for run_nexullance_MP with return_RT=True."""
        return self.run_nexullance_MP(M_EPs, max_path_length, return_RT=True, verbose=True)
    
    def run_and_profile_nexullance_IT(self, M_EPs: np.ndarray, traffic_name: str = "", 
                                      repetitions: int = 10):
        """Backward compatibility wrapper for profile_nexullance_IT."""
        return self.profile_nexullance_IT(M_EPs, repetitions)
    
    def run_nexullance_IT_return_RT(self, M_EPs: np.ndarray, traffic_name: str = "", 
                                    _debug: bool = False):
        """Backward compatibility wrapper for run_nexullance_IT with return_RT=True."""
        return self.run_nexullance_IT(M_EPs, return_RT=True, verbose=True, debug=_debug)
    
    def run_and_profile_MD_nexullance_IT(self, M_EPs_s: list[np.ndarray], 
                                         M_EPs_weights: list[float], 
                                         repetitions: int = 10):
        """Backward compatibility wrapper for profile_MD_nexullance_IT."""
        return self.profile_MD_nexullance_IT(M_EPs_s, M_EPs_weights, repetitions)
    
    def run_MD_nexullance_IT_return_RT(self, M_EPs_s: list[np.ndarray], 
                                       M_EPs_weights: list[float], 
                                       _debug: bool = False, 
                                       cal_least_margin: bool = False):
        """Backward compatibility wrapper for run_MD_nexullance_IT with return_RT=True."""
        return self.run_MD_nexullance_IT(M_EPs_s, M_EPs_weights, return_RT=True, 
                                        verbose=True, debug=_debug)
    
    def run_and_profile_MD_nexullance_MP(self, M_EPs_s: list[np.ndarray], 
                                         M_EPs_weights: list[float], 
                                         max_path_length: int, 
                                         _debug: bool = False, 
                                         repetitions: int = 10):
        """Backward compatibility wrapper for profile_MD_nexullance_MP."""
        return self.profile_MD_nexullance_MP(M_EPs_s, M_EPs_weights, max_path_length, 
                                            repetitions)
    
    def run_MD_nexullance_MP_return_RT(self, M_EPs_s: list[np.ndarray], 
                                       M_EPs_weights: list[float], 
                                       max_path_length: int, 
                                       _debug: bool = False):
        """Backward compatibility wrapper for run_MD_nexullance_MP with return_RT=True."""
        return self.run_MD_nexullance_MP(M_EPs_s, M_EPs_weights, max_path_length, 
                                        return_RT=True, verbose=_debug)
