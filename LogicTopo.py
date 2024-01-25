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
        
        #append loopback
        nodes =[]
        for n in self.nodes:
            dico=self.nodes[n]
            if dico.get("isSwitch") is not None:
                dico["loopback"] ="127.0.0."+n.split("s")[1]
            nodes.append((n,dico))

        self.add_nodes_from(nodes)   
        
    def undo_physic_links(self,topo : NetworkGraph):
        self.clear_edges()
        for e in topo.edges:
            self.physic_edges.append((e,topo.edges[e]))
        
        
    def get_switch_loopback(self,name):
        if self.isSwitch(name):
            ip = self.get_nodes()[name].get('loopback')
            if ip is not None: 
                return ip.split("/")[0]
            else:
                return None
        else:
            raise TypeError('{} is not a switch.'.format(name))
        
        
    def switch_info(self,name:str, role : str, connections : list):
        """ Update the swotch info : put a role label and put the edges of the logic network """
        self.nodes[name]['role']=role
        for neig in connections:
            self.add_link(name,neig)
            
    def shearch_edges(self,src:str, dst:str):
        for (k,v) in self.physic_edges:
            if k[0] == src and k[1] == dst:
                return (k,v)
            elif k[1] == src and k[0] == dst:
                return (k,v)
        return None
    
    def add_link(self,node1:str,node2:str):
        """ Add a logic link, use the physical link """
        physic_edge = self.shearch_edges(node1,node2)

        physic_edge = (physic_edge[0][0], physic_edge[0][1],physic_edge[1])   #Python ...
        self.add_edges_from([physic_edge])
    
    
    
    def save_topo(self,path : str):
        graph_dict = json_graph.node_link_data(self)
        with open(path,"w") as f:
            json.dump(graph_dict,f,indent=2)
            
    def get_hosts_connected_to(self, name):
        """ Rewrite this one because we delete some link from the physical topo where
        there are still present in this function. 
        We just check if the hsot is logically connect to the node"""
        
        hosts = super().get_hosts_connected_to(name)
        
        
        return [host for host in hosts if self.has_edge(host,name)]
    
    def are_neighbors(self, node1, node2):
        """ Same idea, need to rewrite this one because it take physical topology not to logic  """
        
        return super().are_neighbors(node1,node2) and self.has_edge(node1,node2)

    