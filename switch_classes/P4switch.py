from ExtendedTopology import load_etopo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
from collections import namedtuple
import p4utils

class NodeInfo:
    """ Contains inforamtion about a node ip mac port
    it is relative about another node (especially for the port)"""
    
    def __init__(self,base_node : str ,node_name : str, topo : p4utils.utils.topology) :
        """ base_node is the name of the node from the info are taken node_name is the name
        of the node that's  info will be taken.
        """
        self.name = node_name
        self.mac = topo.node_to_node_mac(node_name,base_node)
        # self.ip = topo.node_to_node_interface_ip(node_name,base_node).split('/')[0]
        self.port = topo.node_to_node_port_num(base_node,node_name)
        
        


class P4switch:
    def __init__(self,name : str, ) -> None:
        self.name = name
        self.topo = load_etopo("ext_topology.json")

        self.api = SimpleSwitchThriftAPI(self.topo.get_thrift_port(name))


        
    def compile_and_push(self,p4_src : str, json_src : str):
        source = P4C(p4_src, "/usr/local/bin/p4c")
        source.compile()
        self.api.load_new_config_file(json_src)
        self.api.swap_configs()
        
    def init_table(self):
        pass
    
    def mininet_update(self):
        self.api.switch_info.load_json_config(self.api.client)
        self.api.table_entries_match_to_handle = self.api.create_match_to_handle_dict()
        self.api.load_table_entries_match_to_handle()