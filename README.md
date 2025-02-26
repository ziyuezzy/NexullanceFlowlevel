
This repository serves as a data-reproducing source for the paper 'Nexullance: Link load-balancing for HPC networks'  submitted to IATON in 2025.

## required python packages:
numpy, matplotlib, networkx, joblib (for multi-thread cpu algorithms), galois (for slimfly), gurobipy, (pynauty)

install: 
apt install python3.12-dev (need python 3.12)
apt install libboost-all-dev libeigen3-dev  (for making and using IT_boost)
pip3.12 install numpy matplotlib networkx joblib galois gurobipy pandas pybind11 cmake 

# Overview:
## subdir "topolgies/":
Network topologies are defined here. Some helper functions are implemented here, e.g., calculating paths and link loads.

Slimfly, RRG(Jellyfish), Dally-DragonFly, Polarfly, etc, network topologies are implemented as child classes of "HPC_topo" which are based on undiretional graphs.
GDBG is implemented separately because of its di-graph nature.



## subdir "nexullance/":

Here is the implementation of The Nexullance method.

Nexullance is an flow-level optimization technique for core link load balancing. Some basics about flow-level modeling, and detail descriptions of the Nexullance method can be found in the nexullance paper. 

For Single-Demand Nexullance (SD_Nexullance), three formulations are implemented:
* the optimal formulation (topology-research/nexullance/Nexullance_OPT.py)
* the LP formulation (topology-research/nexullance/Nexullance_MP.py)
* the iterative heuristic (topology-research/nexullance/IT_boost/src/Nexullance_IT.cpp)

For Multi-Demand Nexullance (MD_Nexullance), two formulations are implemented:
* the LP formulation (topology-research/nexullance/MD_Nexullance_MP/MD_Nexullance_MP.py)
* the iterative heuristic (topology-research/nexullance/IT_boost/src/MD_Nexullance_IT.cpp)

Note that the optimal formulation and LP formulations uses GUROBI, which uses Clang underneath.
The iterative heuristics are implemented in C++, and can be exported as library in python with pybind11.

## subdir "Nexullance_journal_data_gen/":

Some python files that generates the data for the IATON paper.
/groups/ilabt-imec-be/hpcnetworksimulation/ziyzhang/topology-research/

Notebooks in "Nexullance_journal_data_gen/demand_matrices" generates figure 2.

Notebooks in "/groups/ilabt-imec-be/hpcnetworksimulation/ziyzhang/topology-research/Nexullance_journal_data_gen/Nexullance_compare" generates figure 3 and 4


<!-- # Update April 2024:

There are some useful functions in networkx source code that are not in the documentation, such as "single_source_all_shortest_paths" and "all_pairs_all_shortest_paths"

The time complexity of "single_source_all_shortest_paths" is O((E+VlogV) + V*(V+E)), the first terms comes from the dijkstra search which produces the predecessor tree, and the second terms comes from the construction of the paths using a tree search in predecessor tree. This is because the multiple paths (but only one path) are not storaged in the lowest-layer dijkstra algorithm in networkx.

But in the context of HPC networkx, and the Nexullance problem, the second step of tree search is **probably** marginal, as only a small part of the predecessor tree should be explored. (low diameter graphs)

The time complexity of "all_pairs_all_shortest_paths" is simply V times the time complexity of "single_source_all_shortest_paths", which is O(V*((E+VlogV) + V*(V+E))).

https://networkx.org/documentation/stable/_modules/networkx/algorithms/shortest_paths/generic.html#all_shortest_paths

Bayesian Optimization: 
https://github.com/bayesian-optimization/BayesianOptimization -->
