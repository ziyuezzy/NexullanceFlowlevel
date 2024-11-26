# HPC network research

# required python packages:
numpy, matplotlib, networkx, joblib (for multi-thread cpu algorithms), galois (for slimfly), gurobipy, (pynauty)

install: 
apt install python3 pip (need python 3.12)
pip3.12 install numpy matplotlib networkx joblib galois gurobipy pynauty

# classes in folder "topolgies/":
Slimfly, RRG and Equality are implemented as child classes of "HPC_topo" which are based on undiretional graphs.
While GDBG is implemented separately because of its di-graph nature.


# Definitions and Notations for flow-level modeling:

See Nexullance paper draft section II

# Nexullance:

Nexullance is an flow-level optimization technique for core link load balancing. Detail description can be found in the nexullance paper draft section III.

Input: 
inter-router graph, traffic demand matrix

Output:
Link load distribution,
(ideally, ) also the traffic-agnostic routing tables,

Measurements:
Execution time,
RAM occupation,


## Nexullance formulations :
Nexullance_OPT: an optimal LP formulation
Nexullance_MP: a near-optimal LP formulation
Nexullance_IT: a heuristic


# Update April 2024:

There are some useful functions in networkx source code that are not in the documentation, such as "single_source_all_shortest_paths" and "all_pairs_all_shortest_paths"

The time complexity of "single_source_all_shortest_paths" is O((E+VlogV) + V*(V+E)), the first terms comes from the dijkstra search which produces the predecessor tree, and the second terms comes from the construction of the paths using a tree search in predecessor tree. This is because the multiple paths (but only one path) are not storaged in the lowest-layer dijkstra algorithm in networkx.

But in the context of HPC networkx, and the Nexullance problem, the second step of tree search is **probably** marginal, as only a small part of the predecessor tree should be explored. (low diameter graphs)

The time complexity of "all_pairs_all_shortest_paths" is simply V times the time complexity of "single_source_all_shortest_paths", which is O(V*((E+VlogV) + V*(V+E))).

https://networkx.org/documentation/stable/_modules/networkx/algorithms/shortest_paths/generic.html#all_shortest_paths

Bayesian Optimization: 
https://github.com/bayesian-optimization/BayesianOptimization
