from gurobipy import *
import networkx
import time as python_time
sys.path.append("..")

epsilon = 0.000000001

def solve_TCSW_instance(model, graph, edge_variables, detailed_output=True, time_output=False):

    """
    Given a simple TCSW problem instance, returns a minimum weight subgraph that satisfies the demand.

    :param graph: a directed graph with attribute 'weight' on all edges
    :param model: a Gurobi model to be optimized
    :param edge_variables: a dictionary of variables corresponding to the variables d_v,w
    :param detailed_output: flag which when True will print the edges in the optimal subgraph
    :param time_output: flag which when True will return the time taken to obtain result rather than the optimal subgraph
    :return: a optimal subgraph containing the path if the solution is Optimal, else None
    """

    start_time = python_time.time()


    # SOLVE AND RECOVER SOLUTION
    print('-----------------------------------------------------------------------')
    model.optimize()
    print "Solution Count: " + str(model.SolCount)
    subgraph = retreive_and_print_subgraph(model, graph, edge_variables, detailed_output)

    end_time = python_time.time()
    days, hours, minutes, seconds = execution_time(start_time, end_time)
    print('sDCP solving took %s days, %s hours, %s minutes, %s seconds' % (days, hours, minutes, seconds))

    # Return solution iff found
    if time_output:
        return end_time - start_time

    return subgraph if model.status == GRB.status.OPTIMAL else None

def solve_kTCSW_instance(model, graph, edge_variables, k=1, detailed_output=True, time_output=False):

    """
    Given a k-TCSW problem instance, returns a minimum weight subgraph that satisfies the demand.

    :param graph: a directed graph with attribute 'weight' on all edges
    :param model: a Gurobi model to be optimized
    :param edge_variables: a dictionary of variables corresponding to the variables d_v,w
    :param detailed_output: flag which when True will print the edges in the optimal subgraph
    :param time_output: flag which when True will return the time taken to obtain result rather than the optimal subgraph
    :return: a optimal subgraph containing the path if the solution is Optimal, else None
    """

    start_time = python_time.time()


    # SOLVE AND RECOVER SOLUTION
    print('-----------------------------------------------------------------------')
    model.optimize()
    print "Solution Count: " + str(model.SolCount)
    subgraph = retreive_and_print_subgraph(model, graph, edge_variables, detailed_output)

    end_time = python_time.time()
    days, hours, minutes, seconds = execution_time(start_time, end_time)
    print('sDCP solving took %s days, %s hours, %s minutes, %s seconds' % (days, hours, minutes, seconds))

    # Return solution iff found
    if time_output:
        return end_time - start_time

    return subgraph if model.status == GRB.status.OPTIMAL else None

def solve_multi_destination_TCSW_instance(model, graph, edge_variables, detailed_output=True, time_output=False):
    """
    Given a multi-destination TCSW problem instance, returns a minimum weight subgraph that satisfies the demand.

    :param graph: a directed graph with attribute 'weight' on all edges
    :param model: a Gurobi model to be optimized
    :param edge_variables: a dictionary of variables corresponding to the variables d_v,w
    :param detailed_output: flag which when True will print the edges in the optimal subgraph
    :param time_output: flag which when True will return the time taken to obtain result rather than the optimal subgraph
    :return: a optimal subgraph containing the path(s) if the solution is Optimal, else None
    """
    start_time = python_time.time()


    # SOLVE AND RECOVER SOLUTION
    print('-----------------------------------------------------------------------')
    model.optimize()

    # Recover minimal subgraph
    subgraph = retreive_and_print_subgraph(model, graph, edge_variables, detailed_output)


    end_time = python_time.time()
    days, hours, minutes, seconds = execution_time(start_time, end_time)
    print('sDCP solving took %s days, %s hours, %s minutes, %s seconds' % (days, hours, minutes, seconds))

    # Return solution iff found
    if time_output:
        return end_time - start_time
    return subgraph if model.status == GRB.status.OPTIMAL else None

def generate_TCSW_model(graph, existence_for_node_time, connectivity_demand):
    """

    :param graph: a directed graph with attribute 'weight' on all edges
    :param existence_for_node_time: a dictionary from (node, time) to existence {True, False}
    :param connectivity_demand: a connectivity demand (source, demand)
    :return: a Gurobi model pertaining to the TCSW instance, and the edge_variables involved
    """
    
    
    start_time = python_time.time()


   
    # MODEL SETUP
    # Infer a list of times
    times = list(set([node_time[1] for node_time in existence_for_node_time.keys()]))

    # Sources get +1 sourceflow, destinations get -1, other nodes 0
    sourceflow = {(v, t): 0 for v in graph.nodes() for t in times}
    source, destination = connectivity_demand
    sourceflow[source, 0] = 1
    sourceflow[destination, max(times)] = -1

    model = Model('temporal_connectivity')

    # Create variables d_{uvtt'}
    edge_time_variables = {}
    for t in times:
        for t_prime in times:
            for u, v in graph.edges():
                edge_time_variables[u, v, t, t_prime] = model.addVar(vtype=GRB.BINARY,
                                                                     name='edge_time_%s_%s_%s_%s' % (u, v, t, t_prime))

    # Create variables d_{uv}
    edge_variables = {}
    for u, v in graph.edges():
        edge_variables[u, v] = model.addVar(vtype=GRB.BINARY, name='edge_%s_%s' % (u, v))

    model.update()

    # CONSTRAINTS
    # Edge decision constraints (an edge is chosen if it is chosen at any time)
    for t in times:
        for t_prime in times:
            for u, v in graph.edges():
                model.addConstr(edge_variables[u, v] >= edge_time_variables[u, v, t, t_prime])

    # Existence constraints (can only route flow through active nodes)
    for t in times:
        for t_prime in times:
            for u, v in graph.edges():
                model.addConstr(edge_time_variables[u, v, t, t_prime] <= existence_for_node_time[u, t])
                model.addConstr(edge_time_variables[u, v, t, t_prime] <= existence_for_node_time[v, t_prime])

    for t in times:
        for t_prime in times:
            if t != t_prime and t + 1 != t_prime:
                model.addConstr(edge_time_variables[u, v, t, t_prime] == 0)

    # Flow conservation constraints
    for t in times:
        for v in graph.nodes():
            if t != 0 and t != max(times):
                model.addConstr(
                    quicksum(edge_time_variables[u, v, t - 1, t] for u in graph.predecessors_iter(v)) +
                    quicksum(edge_time_variables[u, v, t, t] for u in graph.predecessors_iter(v)) +
                    sourceflow[v, t] ==
                    quicksum(edge_time_variables[v, w, t, t] for w in graph.successors_iter(v)) +
                    quicksum(edge_time_variables[v, w, t, t + 1] for w in graph.successors_iter(v))
                )
            if t == 0:
                model.addConstr(
                    quicksum(edge_time_variables[u, v, t, t] for u in graph.predecessors_iter(v)) +
                    sourceflow[v, t] ==
                    quicksum(edge_time_variables[v, w, t, t] for w in graph.successors_iter(v)) +
                    quicksum(edge_time_variables[v, w, t, t + 1] for w in graph.successors_iter(v))
                )
            if t == max(times):
                model.addConstr(
                    quicksum(edge_time_variables[u, v, t - 1, t] for u in graph.predecessors_iter(v)) +
                    quicksum(edge_time_variables[u, v, t, t] for u in graph.predecessors_iter(v)) +
                    sourceflow[v, t] ==
                    quicksum(edge_time_variables[v, w, t, t] for w in graph.successors_iter(v))
                )

    # OBJECTIVE
    # Minimize total path weight
    objective_expression = quicksum(edge_variables[u, v] * graph[u][v]['weight'] for u, v in graph.edges())
    model.setObjective(objective_expression, GRB.MINIMIZE)

    
     # SOLVE AND RECOVER SOLUTION
    print('-----------------------------------------------------------------------')
    model.optimize()
    print "Solution Count: " + str(model.SolCount)
    subgraph = retreive_and_print_subgraph(model, graph, edge_variables, detailed_output)

    end_time = python_time.time()
    days, hours, minutes, seconds = execution_time(start_time, end_time)
    print('kTCSW solving took %s days, %s hours, %s minutes, %s seconds' % (days, hours, minutes, seconds))

    # Return solution iff found
    if time_output:
        return end_time - start_time

    return subgraph if model.status == GRB.status.OPTIMAL else None

    #return model, edge_variables


def generate_kTCSW_model(graph, existence_for_node_time, connectivity_demand, k = 1):
    """

    :param graph: a directed graph with attribute 'weight' on all edges
    :param existence_for_node_time: a dictionary from (node, time) to existence {True, False}
    :param connectivity_demand: a connectivity demand (source, demand)
    :return: a Gurobi model pertaining to the TCSW instance, and the edge_variables involved
    """
    # MODEL SETUP
    # Infer a list of times
    
    start_time = python_time.time()

    
    times = list(set([node_time[1] for node_time in existence_for_node_time.keys()]))

    # Sources get +1 sourceflow, destinations get -1, other nodes 0
    sourceflow = {(v, t): 0 for v in graph.nodes() for t in times}
    source, destination = connectivity_demand
    sourceflow[source, 0] = 1
    sourceflow[destination, max(times)] = -1
    edges = graph.edges()
    model = Model('temporal_connectivity')

    # Create variables d_{uvtt'}
    edge_time_variables = {}
    for t in times:
        for t_prime in range(t, min(t+k, max(times))+1):
            for u, v in edges:
                edge_time_variables[u, v, t, t_prime] = model.addVar(vtype=GRB.BINARY,
                                                                     name='edge_time_%s_%s_%s_%s' % (u, v, t, t_prime))
    # Create variables d_{uv}
    edge_variables = {}
    for u, v in edges:
        edge_variables[u, v] = model.addVar(vtype=GRB.BINARY, name='edge_%s_%s' % (u, v))

    model.update()

    # CONSTRAINTS
    # Edge decision constraints (an edge is chosen if it is chosen at any time)
    for t in times:
        for t_prime in range(t, min(t+k, max(times))+1):
            for u, v in edges:
                model.addConstr(edge_variables[u, v] >= edge_time_variables[u, v, t, t_prime])

    # Existence constraints (can only route flow through active nodes)
    for t in times:
        for t_prime in range(t, min(t+k, max(times))+1):
            for u, v in edges:
                model.addConstr(edge_time_variables[u, v, t, t_prime] <= existence_for_node_time[u, t])
                model.addConstr(edge_time_variables[u, v, t, t_prime] <= existence_for_node_time[v, t_prime])

    for t in times:
        for t_prime in range(t, min(t+k, max(times))+1):
            if not (t_prime >= t and t_prime <= t + k):
                model.addConstr(edge_time_variables[u, v, t, t_prime] == 0)

    # Flow conservation constraints
    for t in times:
        for v in graph.nodes():
            sell_side = 0
            for modifier in range(t, min(max(times), t + k)+1):
                sell_side += quicksum(edge_time_variables[v, w, t, modifier] for w in graph.successors(v))
            buy_side = sourceflow[v, t]
            for modifier in range(max(0, t - k), t+1):
                buy_side += quicksum(edge_time_variables[u, v, modifier, t] for u in graph.predecessors(v))
            model.addConstr(buy_side == sell_side)

    # OBJECTIVE
    # Minimize total path weight
    objective_expression = quicksum(edge_variables[u, v] * graph[u][v]['weight'] for u, v in edges)
    #objective_expression = quicksum(edge_variables[u, v]  for u, v in edges)
    model.setObjective(objective_expression, GRB.MINIMIZE)

    
    # SOLVE AND RECOVER SOLUTION
    print('-----------------------------------------------------------------------')
    model.Params.timelimit=1200
    model.optimize()
    print "Solution Count: " + str(model.SolCount)
    subgraph = retreive_and_print_subgraph(model, graph, edge_variables, False)

    end_time = python_time.time()
    days, hours, minutes, seconds = execution_time(start_time, end_time)
    print('kTCSW solving took %s days, %s hours, %s minutes, %s seconds' % (days, hours, minutes, seconds))

    # Return solution iff found

    return subgraph if model.status == GRB.status.OPTIMAL else None

    #return model, edge_variables

def generate_mTCSW_model(graph, existence_for_node_time, source, destinations):
    """
    :param graph: a directed graph with attribute 'weight' on all edges
    :param existence_for_node_time: a dictionary from (node, time) to existence {True, False}
    :param source: a source node
    :param destinations: a list of target nodes
    :return: a Gurobi model pertaining to the mTCSW instance, and the edge_variables involved
    """
    # Infer a list of times
    times = list(set([node_time[1] for node_time in existence_for_node_time.keys()]))

    # Source get +len(destination) sourceflow, destinations get -1, other nodes 0
    sourceflow = {(v, t): 0 for v in graph.nodes() for t in times}
    sourceflow[source, 0] = len(destinations)
    for destination in destinations:
        sourceflow[destination, max(times)] = -1

    # Create empty optimization model
    model = Model('temporal_connectivity')

    # Create variables d_{uvtt'}
    edge_time_variables = {}
    for t in times:
        for t_prime in times:
            for u, v in graph.edges():
                edge_time_variables[u, v, t, t_prime] = model.addVar(vtype=GRB.INTEGER, lb=0, ub=len(destinations), name='edge_time_%s_%s_%s_%s' % (u, v, t, t_prime))

    # Create variables d_{uv}
    edge_variables = {}
    for u, v in graph.edges():
        edge_variables[u, v] = model.addVar(vtype=GRB.BINARY, name='edge_%s_%s' % (u, v))

    model.update()

    # CONSTRAINTS
    # Edge decision constraints (an edge is chosen if it is chosen at any time)
    for t in times:
        for t_prime in times:
            for u, v in graph.edges():
                model.addConstr(edge_variables[u, v] >= edge_time_variables[u, v, t, t_prime]/len(destinations)) #*******

    # Existence constraints (can only route flow through active nodes)
    for t in times:
        for t_prime in times:
            for u, v in graph.edges():
                model.addConstr(edge_time_variables[u, v, t, t_prime] <= len(destinations) * existence_for_node_time[u, t])
                model.addConstr(edge_time_variables[u, v, t, t_prime] <= len(destinations) * existence_for_node_time[v, t_prime])

    for t in times:
        for t_prime in times:
            if t != t_prime and t+1 != t_prime:
                model.addConstr(edge_time_variables[u, v, t, t_prime] == 0)

    # Flow conservation constraints
    for t in times:
        for v in graph.nodes():
            if t != 0 and t != max(times):
                model.addConstr(
                    quicksum(edge_time_variables[u, v, t-1, t] for u in graph.predecessors_iter(v)) +
                    quicksum(edge_time_variables[u, v, t, t] for u in graph.predecessors_iter(v)) +
                    sourceflow[v, t] ==
                    quicksum(edge_time_variables[v, w, t, t] for w in graph.successors_iter(v)) +
                    quicksum(edge_time_variables[v, w, t, t+1] for w in graph.successors_iter(v))
                )
            if t == 0:
                model.addConstr(
                    quicksum(edge_time_variables[u, v, t, t] for u in graph.predecessors_iter(v)) +
                    sourceflow[v, t] ==
                    quicksum(edge_time_variables[v, w, t, t] for w in graph.successors_iter(v)) +
                    quicksum(edge_time_variables[v, w, t, t + 1] for w in graph.successors_iter(v))
                )
            if t == max(times):
                model.addConstr(
                    quicksum(edge_time_variables[u, v, t - 1, t] for u in graph.predecessors_iter(v)) +
                    quicksum(edge_time_variables[u, v, t, t] for u in graph.predecessors_iter(v)) +
                    sourceflow[v, t] ==
                    quicksum(edge_time_variables[v, w, t, t] for w in graph.successors_iter(v))
                )


    # OBJECTIVE
    # Minimize total path weight
    objective_expression = quicksum(edge_variables[u, v] * graph[u][v]['weight'] for u, v in graph.edges())
    model.setObjective(objective_expression, GRB.MINIMIZE)

    return model, edge_variables



def retreive_and_print_subgraph(model, graph, edge_variables, detailed_output):
    """

    :param model: an optimized gurobi model
    :param graph: a directed graph with attribute 'weight' on all edges
    :param edge_variables: a dictionary of variables corresponding to the variables d_v,w
    :param detailed_output: flag which when True will print the edges in the optimal subgraph
    """
    # Recover minimal subgraph
    subgraph = networkx.DiGraph()
    if model.status == GRB.status.OPTIMAL:
        value_for_edge = model.getAttr('x', edge_variables)
        for u,v in graph.edges():
            if value_for_edge[u,v] > 0:
                subgraph.add_edge(u, v, weight=graph[u][v]['weight'])

        # Print solution
        print('-----------------------------------------------------------------------')
        print('Solved sDCP instance. Optimal Solution costs ' + str(model.objVal))
        if detailed_output:
            print('Edges in minimal subgraph:')
            print_edges_in_graph(subgraph)
        return subgraph

import datetime


def execution_time(start_time, end_time):
    """
    Returns the time of execution in days, hours, minutes, and seconds

    :param start_time: the start time of execution
    :param end_time: the end time of execution
    :return:
    """
    execution_delta = datetime.timedelta(seconds=end_time - start_time)
    return execution_delta.days, execution_delta.seconds // 3600, (execution_delta.seconds // 60) % 60, execution_delta.seconds % 60


def print_edges_in_graph(graph, edges_per_line=5):
    """
    Given a graph, prints all edges

    :param graph: a directed graph with attribute 'weight' on all edges
    :param edges_per_line: number of edges to print per line
    :return:
    """
    edges_string = ''
    edges_printed_in_line = 0

    for u,v in graph.edges():
        edges_string += '%s -> %s        ' % (u, v)
        edges_printed_in_line += 1
        if edges_printed_in_line >= edges_per_line:
            edges_printed_in_line = 0
            edges_string += '\n'

    print edges_string
