# Temporal Condition Shortest Walk

This project implements an algorithm for solving the Temporal Condition Shortest Walk problem in time condition-varying graphs. It also contains tools for generating interesting instances of the problem to test the feasibility of the algorithm in practice. 


#### Problem Statement

Formally, the __Temporal Condition Shortest Walk__ problem is the following: we are given

1. A series of directed networks {G<sub>t</sub> = (V<sub>t</sub>, E)}<sub>t ∈ [T]</sub> each corresponding to a time condition t. Edges are positively weighted. Note that we denote V as the union of  V<sub>t</sub>. We denote a node v ∈ V<sub>T</sub> as v<sub>t</sub>

2. A pair of nodes (a<sub>1</sub>, b<sub>T</sub>) s.t. a<sub>1</sub> ∈ V<sub>1</sub> and b<sub>T</sub> ∈ V<sub>T</sub> which we wish to connect via a walk through G<sub>1</sub>,..., G<sub>T</sub>

Our goal is to find an a-b walk from G<sub>1</sub> to G<SUB>T</SUB>. We denote a walk W in the form W = {...,(v<sub>i</sub>, w<sub>j</sub>), ...}, where (v<sub>i</sub>, w<sub>j</sub>) is a valid edge if v ∈ V<sub>i</sub>, w ∈ V<sub>j</sub> and i = j or i = j+1, and (v,w) ∈ E or v = w. We denote this "jump" constraint from G<sub>i</sub> to G<sub>i+1</sub> as the <bold>temporal walk constraint</bold>. The walk begins at a<sub>1</sub> and ends at b<sub>T</sub>.

Theoretical aspects of this problem, as well as our algorithm, will be detailed in a forthcoming paper.


---
### Solving Temporal Condition Shortest Walk Instances

The main TCSW solver is invoked by calling the following function in `/ILP_solver/ILP_solver.py`:

```python
# In the following, G is a NetworkX DiGraph, rho is a dictionary corresponding to whether v is in V_t, and pair is a (source,target) tuple. See the docstring for details. Subnetwork returns the subnetwork traversed by the walk

subnetwork = generate_TCSW_model(graph=G, existence_for_node_time=rho, connectivity_demands=pair)
```

The kTCSW solver is invoked similarly, by calling the following function in `/ILP_solver/ILP_solver.py`:

```python
 In the following, G is a NetworkX DiGraph, rho is a dictionary corresponding to whether v is in V_t, pair is a (source,target) tuple, step_size), and step_size is the max allowable step size. See the docstring for details. Subnetwork returns the subnetwork traversed by the walk

subnetwork = generate_kTCSW_model(graph=G, existence_for_node_time=rho, connectivity_demands=pair, k = step_size)
```


_Note_: This function works by modeling the instance as an integer linear program (ILP), then solving using the Gurobi optimization library.



### Generating Artificial Instances

We implement the following procedure for generating highly-structured random kTCSW instances given a network G:

1. Give an underlying graph G

2. For every node, timepoint in the network, set v to be included in V<sub>t</sub> with probability _p_

3. Sample a random source, target pair 

4. See if the target can be reached by the source given the maximum allowed step size k, if not return to 3.


This procedure is implemented in the following function in `/graph_tools/network_generator.py`:

```python
generate_graph(graph, time_count=10, node_active_prob=.25, k=1)
```

To view example instances and run the algorithm, please view `TCSW_sample_instance.py`:
