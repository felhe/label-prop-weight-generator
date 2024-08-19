import random

import networkit as nk
import numpy as np
from networkit import vizbridges

PERCENTAGE_ZERO = 0.05
PERCENTAGE_NONZERO = 0.02
DISCRETE_RANGE = 10
ITERATIONS = 200
ALPHA = 0.8


def load_nk_graph(graph_name: str, instance_dir: str) -> nk.Graph:
    return nk.readGraph(f"{instance_dir}/{graph_name}.nkb", nk.Format.NetworkitBinary)


def label_propagation(graph: nk.Graph, max_iterations: int) -> nk.Graph:
    # assign initial labels
    state_probs = {graph.edgeId(*edge): np.zeros(DISCRETE_RANGE) for edge in graph.iterEdges()}
    state = graph.attachEdgeAttribute("state", int)
    unlabelled = {edge: False for edge in graph.iterEdges()}
    for edge in graph.iterEdges():
        vec = np.zeros(DISCRETE_RANGE)
        if random.random() < PERCENTAGE_ZERO:
            vec[0] = 1.0 - ALPHA
        else:
            if random.random() < PERCENTAGE_NONZERO:
                random_state = random.randint(1, DISCRETE_RANGE - 1)
                vec[random_state] = 1.0
            else:
                unlabelled[edge] = True
        state_probs[graph.edgeId(*edge)] = vec

    for i in range(max_iterations):
        print(f"Iteration {i}")
        prev_vecs = [state_probs[graph.edgeId(*edge)].copy() for edge in graph.iterEdges()]
        for edge, value in unlabelled.items():
            if value:
                u = edge[0]
                v = edge[1]
                incident_edges = [(u, i) for i in graph.iterNeighbors(u)] + [(v, i) for i in graph.iterNeighbors(v)]
                incident_vecs = [prev_vecs[graph.edgeId(*incident_edge)] for incident_edge in incident_edges]
                mean = np.mean(incident_vecs, axis=0)
                softmax = np.exp(mean) / np.sum(np.exp(mean))
                state_probs[graph.edgeId(*edge)] = softmax

    for edge in graph.iterEdges():
        state[edge] = int(np.argmax(state_probs[graph.edgeId(*edge)]))


if __name__ == "__main__":
    graph: nk.Graph = load_nk_graph("Bergedorf-Hamburg-Germany", "instances")
    print(nk.overview(graph))
    graph.indexEdges()
    label_propagation(graph, ITERATIONS)
    nk.vizbridges.widgetFromGraph(graph, dimension=nk.vizbridges.Dimension.TwoForcePlotly,
                                  edgeAttributes=[("state", int)]).show()
