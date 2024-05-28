# topology-research

# required python packages:
numpy, networkx, galois
, (matplotlib), if you want to plot
, (joblib (for multi-thread cpu algorithms)), if you want to launch parallel algorithms (for slimfly), gurobipy, (pynauty)

# classes in folder "topolgies/":
Slimfly, RRG and Equality are implemented as child classes of "HPC_topo" which are based on undiretional graphs.
While GDBG is implemented separately because of its di-graph nature.


# Definitions and Notations for flow-level modeling:

$R$ denotes the total number of routers in the network. $EPR$ denotes the number of network EndPoints (EP) per router, assume there are a same number of EPs on every router.

Define a **'remote link'** to be a link between two routers, and a **'local link'** as a link between a router and an EP.
Denote the remote link from router x to router y as $l_{x,y}$.

Define **Flow** [Gbps]: The data rate of a data stream. A flow originates from an EP and ends up in another EP. The aggregated flow on a link is defined as the summation of data rates of flow that passes by the link.

Define **Link capacity** [Gbps]: The maximum data rate (aggregated flow) on a link, that is supported by the technology used in the link.

Define **Link load** (unit-less): the utilization of link bandwidth, equals to the aggregated flow on the link over the link capacity. The load can be higher than 1, meaning the link capacity is not able to support the flow and therefore will lead to network congestion and therefore high packet latencies in real scenarios.

Denote $C^{remote}$ and $C^{local}$  to be the uniform (by assumption) link capacities on remote links and local links, respectively. Denote $f^{remote}_{x,y}$ to be the aggregated flow on remote link $l_{x,y}$, $f^{in}_i$ as the aggregated flow on the ingress local link to EP $i$, and $f^{out}_i$ as the aggregated flow on the egress local link from EP $i$. Similarly, denote $L^{remote}_{x,y} = f^{remote}_{x,y}/C^{remote}$ to be the load on remote link $l_{x,y}$, $L^{in}_i = f^{in}_i/C^{local}$ as the load on ingress local link to EP $i$, and $L^{out}_i= f^{out}_i/C^{local}$ as the load on the egress local link from EP $i$. 

Define **Inter-EP Traffic demand matrix** ($M^{EP}$) (2-D matrix, every entry has uint of [Gbps]): the flows among src and dest EPs

Define **Inter-router Traffic demand matrix** ($M^{R}$) (2-D matrix, every entry has uint of [Gbps]): the aggregated flows between the src and dest routers

By flow-level modeling, the flows and loads on links can be calculated:
The aggregated flow on a remote link $f^{remote}_{x, y} = F(M^R)$. F() is defined in the specific flow-level modeling, mainly depends on routing algorithm.
The aggregated flow ingress to an EP $f^{in}_{i} = \sum_j(M^{EP}_{i,j})$. 
The aggregated flow egress from an EP $f^{out}_{i} = \sum_j(M^{EP}_{j,i})$.

Define the **Local-Remote ratio** $\mu = MAX(\{L^{in}_i\} \cup \{L^{out}_i\})/MAX(\{L^{remote}_{x,y}\})$ to indicate whether the local links or remote links are more prone to be bottlenecks. 
In terms of synthetic traffic patterns in a flit-level network simulation, the traffic pattern is equivalent to $M^{EP}$ with a certain scalar scaling factor. When $ \mu <=1$, the value of $ \mu $ is somehow (if link saturation is the only source of network congestion) equivalent to the "saturation injection rate" in a flit-level simulation with synthetic traffic patterns.

Define **network total capacity** ($\Phi_{max}$) as the maximum total aggregated flow at all EPs in a network, $\Phi_{max} = C^{local}*EPR*R$.

Define **network total throughput** ($\Phi$) as the total aggregated flow at all EPs under a certain traffic demand matrix (as a function of: link capacties, routing, network configurations, etc.). 


The definition of $\Phi$ splits into two cases:
1.  When there is no link saturation ( $\forall i, L^{in}_i < 1; L^{out}_i<1; L^{remote}_{x,y}<1 $ ), meaning that the network is ***under-supplied***,
$\Phi = \sum_{i,j} M^{EP}_{i,j}$. 

2.  When there exits link saturation (meaning that the network is ***over-supplied***), a realistic traffic demand matrix is likely to be deformed due to possible flow dependencies. However, flow dependencies are not modeled in flow-level or flit-level simulations. Flit-level simulation tools handle network saturations depending on their implementation: booksim2 use an 'infinite injection queue' to keep the traffic demand matrix the same when network congestion happens; while SST-Merlin simply 'drop' packets and thus deforms the traffic demand matrix when network congestion happens.

    Therefore, we consider two scenarios for the flow-level simulations to handle network congestion:

    ***Scenario $\textcircled{1}$***: Assume the flows in the network are all independent, so their arrival have equivalent impact on the application (image a traffic network without any ambulances or police cars.). In this case, $\Phi$ depends on which flows are chosen to be served in the network, an optimization goal could be to fill all local links as full as possible. An upper-bound on $\Phi$ equals to the total aggregated bandwidth of local links in the network: $\Phi^{ub} = C^{local}*EPR*R$, the tightness of this upper-bound depends on the network topology and configurations.


    ***Scenario $\textcircled{2}$***: Assume that the flows have certain depencies to each other, such that the traffic demand matrix can only be scaled with a scalar factor. (Note that this assumption is not based on observation from real applications, but just a hypothesis and an advocator for the definition of "traffic demand matrix".) In this case, $\Phi$ is defined as the total aggregated flow with a down-scaled (scalar factor) traffic demand matrix such that the maximum load on local or remote links equals to 1.0. 
    $\Phi = \lambda*\sum_{i,j} M^{EP}_{i,j} $, where $\lambda \in (0,1)$ is the scalar scaling factor on the traffic demand matrix so that the maximum load on local or remote links equals to 1.0.
    * when $\mu < 1$, meaning $MAX(\{ L^{in}_i\} \cup \{L^{out}_i\}) < MAX(\{L^{remote}_{x,y}\})$, 
            $\lambda = C^{remote} / MAX(\{ f^{remote}_{x,y}\}) = 1 / MAX(\{ L^{remote}_{x,y}\}) \\ \; \; \;  = \mu/MAX(\{ L^{in}_i\} \cup \{L^{out}_i\})$
    * when $\mu > 1$, meaning $MAX(\{ L^{in}_i\} \cup \{L^{out}_i\}) > MAX(\{L^{remote}_{x,y}\})$, 
            $\lambda = C^{local} / MAX(\{ f^{in}_i\} \cup \{f^{out}_i\}) = 1/MAX(\{ L^{in}_i\} \cup \{L^{out}_i\})$

    Therefore, in summary, $\lambda = \frac{1}{max(MAX(\{ L^{remote}_{x,y}\}), MAX(\{ L^{in}_i\} \cup \{L^{out}_i\}))} $, and $\Phi = \frac{\sum_{i,j} M^{EP}_{i,j}}{max(MAX(\{ L^{remote}_{x,y}\}), MAX(\{ L^{in}_i\} \cup \{L^{out}_i\}))} $.
        
    
    ***Scenario $\textcircled{1}$*** is not very realistic in the context of HPC networks where consecutive data streams usually have strong dependencies. Therefore, we focus on ***Scenario $\textcircled{2}$***, although it is also not accurate in reflecting flow dependencies.

# Nexullance:

Nexullance is an flow-level optimization technique that applies to Scenario $\textcircled{2}$, where a specific over-supplied traffic demand matrix leads to $\mu < 1$. The objective of the Nexullance method is to maximize the **network total throughput** $\Phi = \lambda*\sum_{i,j} M^{EP}_{i,j} = (\sum_{i,j} M^{EP}_{i,j})/MAX(\{ L^{remote}_{x,y}\})$. Therefore, the objective is equivalent to minimizing the maximum load among remote links in the network, given a traffic demand matrix. We achieve this optimization by alternating the routing tables (traffic-agnostic routing scheme) in the routers such that the loads on remote links are more balanced.

Nexullance will be a bit slow when the network is large,
but based on the statements from Axel, the traffic could be stably uniform-random, which was why we started to investigate this technique from the first place.

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
Nexullance_IT: a heuristic to be developed


# TODOs: 

Optimize alpha and beta for a set of traffic demand matrices together.
Optimize the routing table (Nexullance) for a set of traffic demand matrices together.(?)


Bayesian Optimization: 
https://github.com/bayesian-optimization/BayesianOptimization
