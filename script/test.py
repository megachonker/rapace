import json
import networkx as nx
from networkx.readwrite import json_graph
from p4utils.utils.topology import NetworkGraph

def load_topo(json_path):
    """Load the topology from the path provided.

    Args:
        json_path (string): path of the JSON file to load

    Returns:
        p4utils.utils.topology.NetworkGraph: the topology graph.
    """
    with open(json_path, 'r') as f:
        graph_dict = json.load(f)
        graph = json_graph.node_link_graph(graph_dict)
    return NetworkGraph(graph)

def save_topo(graph, json_path):
    """Save the topology to the specified JSON file.

    Args:
        graph (p4utils.utils.topology.NetworkGraph): the topology graph
        json_path (string): path of the JSON file to save
    """
    graph_dict = json_graph.node_link_data(graph)
    with open(json_path, 'w') as f:
        json.dump(graph_dict, f, indent=2)

# Example usage:
# Load the topology
topology = load_topo('topology.json')

# Make some modifications to the topology if needed

# Save the modified topology



topology.nodes['s1']['ip'] = "10.0.1.0.0"

print(json_graph.node_link_data(topology))
save_topo(topology, 'modified_topology.json')
