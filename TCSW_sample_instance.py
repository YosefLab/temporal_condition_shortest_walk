import gurobipy
from ILP_solver.ILP_solver import *
import matplotlib.pyplot as pyplot
import pickle
from graph_tools.network_generator import *


def test_solve_path_instance(feasible=True, detailed_output=False):
	"""
	Tests the TCSW ILP solver on a simple path at four time points.
	"""
	#print 'Testing path instance, should be ' + ('feasible' if feasible else 'infeasible')

	graph = networkx.DiGraph()

	graph.add_path([1,2,3,4])
	for u,v in graph.edges():
		graph[u][v]['weight'] = 1
	
	existence_for_node_time = {
		(1,0): 1,
		(2,0): 1,
		(3,0): 1,
		(4,0): 1,
		(1,1): 1,
		(2,1): 1,
		(3,1): 1,
		(4,1): 1,
		(1,2): 1,
		(2,2): 1,
		(3,2): 1,
		(4,2): 1,
		(1,3): 1,
		(2,3): 1,
		(3,3): 1,
		(4,3): 1 if feasible else 0
	}

	source_target = (1,4)

	subgraph = generate_kTCSW_model(graph, existence_for_node_time, source_target, k=1)

test_solve_path_instance()
