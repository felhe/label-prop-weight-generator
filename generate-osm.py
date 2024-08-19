import networkit as nk
import momepy
import osmnx as ox
import networkx as nx

from osmnx import settings


def load_and_save_graph(city: str, country: str, instance_dir: str):
    location = f"{city}, {country}"
    # download location with OSMnx
    G = ox.graph_from_place(
        location,
        network_type="drive",
        custom_filter='["highway"]["highway"!~"footway|bridleway|path|service|track|steps"]',
    )

    G.remove_edges_from(nx.selfloop_edges(G))

    # graph to gdf
    gdf = ox.graph_to_gdfs(G, nodes=False, edges=True)

    # clean up dataframe
    gdf = gdf.rename(
        columns={"osmid": "wayid", "geometry": "geometry"}
    )
    gdf = gdf.reset_index()
    gdf = gdf[["wayid", "geometry", "u", "v"]]
    gdf.wayid = gdf.wayid.apply(lambda x: x if type(x) == list else [x])
    gdf = gdf.to_crs(3857)

    # convert to networkx graph using momepy and set name of length
    nx_graph = momepy.gdf_to_nx(gdf, length="length", multigraph=False)

    nk_graph = nk.nxadapter.nx2nk(
        nx_graph, data=True, typeMap={"wayid": str, "u": str, "v": str, "geometry": str}
    )

    cost = nk_graph.getEdgeAttribute("length", float)
    wayids = nk_graph.getEdgeAttribute("wayid", str)
    geometry = nk_graph.getEdgeAttribute("geometry", str)
    u = nk_graph.getEdgeAttribute("u", str)
    v = nk_graph.getEdgeAttribute("v", str)

    instance_name = location.replace(",", "-").replace(" ", "")
    geometry.write(f"{instance_dir}/{instance_name}.geometry")
    cost.write(f"{instance_dir}/{instance_name}.cost")
    wayids.write(f"{instance_dir}/{instance_name}.wayids")
    u.write(f"{instance_dir}/{instance_name}.sourceid")
    v.write(f"{instance_dir}/{instance_name}.destid")
    nk.writeGraph(
        nk_graph, f"{instance_dir}/{instance_name}.nkb", nk.Format.NetworkitBinary
    )


if __name__ == "__main__":
    instance_dir = "./instances"
    # generate graph for 20 cities in Germany in various sizes
    german = [
        #"Berlin",
        # "Hamburg",
        # "Munich",
        # "Cologne",
        # "Frankfurt",
        # "Stuttgart",
        # "Düsseldorf",
        # "Dortmund",
        # "Essen",
        # "Leipzig",
        # "Bremen",
        # "Dresden",
        # "Hanover",
        # "Nuremberg",
        # "Duisburg",
        # "Bochum",
        # "Wuppertal",
        # "Bielefeld",
        # "Bonn",
        # "Münster",
    ]

    # add Berlin boroughs
    berlin = [
        #     "Mitte",
        #     "Friedrichshain-Kreuzberg",
        #     "Pankow",
        #     "Charlottenburg-Wilmersdorf",
            "Spandau",
        #     "Steglitz-Zehlendorf",
        #     "Tempelhof-Schöneberg",
        #     "Neukölln",
        #     "Treptow-Köpenick",
        #     "Marzahn-Hellersdorf",
        #     "Lichtenberg",
        #     "Reinickendorf",
    ]

    # add Hamburg boroughs
    hamburg = [
        #     "Hamburg-Mitte",
        #     "Altona",numpy
        #     "Eimsbüttel",
        #     "Hamburg-Nord",
        #     "Wandsbek",
             "Bergedorf",
        #     "Harburg",
    ]

    for city in german:
        load_and_save_graph(city, "Germany", instance_dir)

    for borough in berlin:
        load_and_save_graph(borough, "Berlin, Germany", instance_dir)

    for borough in hamburg:
        load_and_save_graph(borough, "Hamburg, Germany", instance_dir)

    # same for some other cities in Europe
    # load_and_save_graph("Paris", "France", instance_dir)
    # load_and_save_graph("London", "United Kingdom", instance_dir)
    # load_and_save_graph("Madrid", "Spain", instance_dir)
