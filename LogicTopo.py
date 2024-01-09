import json
import networkx as nx
from networkx.readwrite import json_graph
from p4utils.utils.topology import NetworkGraph
from p4utils.utils.helper import load_topo


def load_logictopo(json_path):
    """Load the topology from the path provided.

    Args:
        json_path (string): path of the JSON file to load

    Returns:
        ExtendedTopology : the topology graph extented for the TP.
    """
    
    return LogicTopo(load_topo(json_path))
        
        
class LogicTopo(NetworkGraph):
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.physic_edges =[]
    
    
    def get_switch_loopback(self,name):
        if self.isSwitch(name):
            ip = self.get_nodes()[name].get('loopback')
            if ip is not None: 
                return ip.split("/")[0]
            else:
                return None
        else:
            raise TypeError('{} is not a switch.'.format(name))
        
    def from_physic(self,topo : NetworkGraph):
        """ Return a Logic graph with the node of the pysic graph and with loopback for switchs """
        nodes =[]
    
        for n in topo.nodes:
            dico=topo.nodes[n]
            if dico.get("isSwitch") is not None:
                dico["loopback"] ="127.0.0."+n.split("s")[1]
            nodes.append((n,dico))

        self.add_nodes_from(nodes)    
        for e in topo.edges:
            self.physic_edges.append((e,topo.edges[e]))
        
    def switch_info(self,name:str, role : str, connections : list):
        """ Update the swotch info : put a role label and put the edges of the logic network """
        self.nodes[name]['role']=role
        for neig in connections:
            physic_edge = self.shearch_edges(name,neig)
            physic_edge = (physic_edge[0][0], physic_edge[0][1],physic_edge[1])   #Python ...
            self.add_edges_from([physic_edge])
            
    def shearch_edges(self,src:str, dst:str):
        for (k,v) in self.physic_edges:
            if k[0] == src and k[1] == dst:
                return (k,v)
            elif k[1] == src and k[0] == dst:
                return (k,v)
        return None
    
    
    
    def save_topo(self,path : str):
        graph_dict = json_graph.node_link_data(self)
        with open(path,"w") as f:
            json.dump(graph_dict,f,indent=2)

    