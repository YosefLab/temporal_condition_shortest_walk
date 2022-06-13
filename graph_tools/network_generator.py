"""
This file generates a random TCSW instance w/ a source destination pair
"""

import networkx
import random

def generate_graph(graph, time_count=10,  node_active_prob=0.25, k = 1):
    """
    Method which given a graph returns an instance of TCSW whereby a feasible exists between randomly generated source and target nodes

    :param num_nodes: number of nodes in graph
    :param edge_connectivity: the probability there exists an edge between two vertices edge_connectivity*100%
    :param active_time_percent: the probability a vertex v is active at timepoint t active_time_percent*100%
    :param weight_distribution: range for random weighst
    :return: graph, existence_for_node_time (dictionary: V x T -> 1/0), connectivity_demand (source, destination)
    """
    
    
    existence_for_node_time = {(node,time): 0 if random.uniform(0,1) > node_active_prob else 1 for node in graph.nodes() for time in range(time_count)}

    # List of connectivity demands in the form (source, target, time)

    # Sample a tree at each time point
    nodes = graph.nodes()
    #time_zero_nodes = [node for node in nodes if existence_for_node_time[(node, 0)] == 1]
    #time_T_nodes = [node for node in nodes if existence_for_node_time[(node, time_count-1)] == 1]


    print("hypernetwork building")    
    test_network = networkx.DiGraph()
    for e in graph.edges():
        for t in range(0, time_count):
            for step in range(0, k+1):
                if t + step < time_count and existence_for_node_time[(e[0], t)] == 1 and existence_for_node_time[(e[1], t+step)] == 1:
                    test_network.add_edge(e[0] + "~" + str(t), e[1] + "~" + str(t+step))

    print("hypernetwork built")
    time_zero_nodes = [node for node in test_network if '~0' in node]
    time_T_nodes = [node for node in test_network if '~'+str(time_count-1) in node]
    print(len(time_zero_nodes), len(time_T_nodes))
    source, destination = random.choice(time_zero_nodes), random.choice(time_T_nodes)
    while source == destination or not networkx.has_path(test_network, source , destination ):
        source, destination = random.choice(time_zero_nodes), random.choice(time_T_nodes)
    source = source.split('~')[0]
    destination = destination.split('~')[0]    
    return graph, existence_for_node_time, (source, destination)


def generate_nodes(num_nodes=100):
    """
    Returns a list from {1,...,num_nodes}

    :param num_nodes: length of list
    :return:
    """
    return list(range(1,num_nodes+1))

