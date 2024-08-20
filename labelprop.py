import random

import networkit as nk
import numpy as np
from geopandas import GeoDataFrame
from networkit import vizbridges
from shapely import wkt
from tqdm import tqdm

PERCENTAGE_ZERO = 0.05
PERCENTAGE_NONZERO = 0.01
DISCRETE_RANGE = 10
ITERATIONS = 200
ALPHA = 0.8


def load_nk_graph(graph_name: str, instance_dir: str) -> nk.Graph:
    return nk.readGraph(f"{instance_dir}/{graph_name}.nkb", nk.Format.NetworkitBinary)


def load_geometry(graph: nk.Graph, graph_name: str, instance_dir: str):
    geom = graph.attachEdgeAttribute("geometry", str)
    geom.read(f"{instance_dir}/{graph_name}.geometry")


def plot_graph(graph: nk.Graph):
    df = GeoDataFrame({"geometry": [], "id": [], "state": []})
    geom = graph.getEdgeAttribute("geometry", str)
    state = graph.getEdgeAttribute("state", int)
    for edge in graph.iterEdges():
        id = graph.edgeId(*edge)
        df = df._append({"geometry": geom[edge], "id": int(id), "state": state[edge]}, ignore_index=True)
    df.geometry = df.geometry.apply(wkt.loads)
    gdf = GeoDataFrame(df, geometry="geometry", crs="EPSG:3857")
    # to epsg 4326
    gdf = gdf.to_crs(epsg=4326)
    return gdf


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

    for i in tqdm(range(max_iterations)):
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


def run(graph_name: str, instance_dir: str):
    graph: nk.Graph = load_nk_graph(graph_name, instance_dir)
    load_geometry(graph, graph_name, instance_dir)
    graph.indexEdges()
    label_propagation(graph, ITERATIONS)
    plot_graph(graph).plot(column="state", legend=True).get_figure().show()
    # make lines thicker
    (plot_graph(graph).explore(column="state", tiles="CartoDB Positron", style_kwds={"weight": 5}).show_in_browser())


if __name__ == "__main__":
    # run("Bergedorf-Hamburg-Germany", "instances")
    run("Spandau-Berlin-Germany", "instances")
