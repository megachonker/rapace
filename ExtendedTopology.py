import json
import networkx as nx
from networkx.readwrite import json_graph
from p4utils.utils.topology import NetworkGraph
from p4utils.utils.helper import load_topo



def extendtopology(current : str , new : str):
    topo = load_topo(current)
    
    for i,sw in enumerate(topo.get_switches()):
        print(i)
        topo.nodes[sw]['loopback'] = "192.168.0."+str(i)+"/16"  
        
        
    graph_dict = json_graph.node_link_data(topo)
    with open(new,"w") as f:
        json.dump(graph_dict,f,indent=2)
        
def load_etopo(json_path):
    """Load the topology from the path provided.

    Args:
        json_path (string): path of the JSON file to load

    Returns:
        ExtendedTopology : the topology graph extented for the TP.
    """
    
    return ExtendedTopology(load_topo(json_path))
        
        
class ExtendedTopology(NetworkGraph):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
    
    
    def get_switch_loopback(self,name):
        if self.isSwitch(name):
            ip = self.get_nodes()[name].get('loopback')
            if ip is not None: 
                return ip.split("/")[0]
            else:
                return None
        else:
            raise TypeError('{} is not a switch.'.format(name))
    
    

if __name__ == '__main__':
    extendtopology("topology.json","ext_topology.json")