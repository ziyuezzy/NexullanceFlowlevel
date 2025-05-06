
This repository serves as a data-reproducing source for the paper 'Nexullance: Link load-balancing for HPC networks'  submitted to IATON in 2025.

## required python packages:
numpy, matplotlib, networkx, joblib (for multi-thread cpu algorithms), galois (for slimfly), gurobipy, (pynauty)

install: 
apt install python3.12-dev (need python 3.12)
pip3.12 install numpy matplotlib networkx joblib galois gurobipy pandas 

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

Notebooks in "./Nexullance_journal_data_gen/demand_matrices" generates figure 2.

Notebooks in "./Nexullance_journal_data_gen/Nexullance_compare" generates figure 3 and 4

