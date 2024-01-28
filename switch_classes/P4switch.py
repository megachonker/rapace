from LogicTopo import LogicTopo, load_logictopo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
from collections import namedtuple
import p4utils

class NodeInfo:
    """ Contains inforamtion about a node ip mac port
    it is relative about another node (especially for the port)"""
    
    def __init__(self,base_node : str ,node_name : str, topo : LogicTopo) :
        """ base_node is the name of the node from the info are taken node_name is the name
        of the node that's  info will be taken.
        """
        self.name = node_name
        self.mac = topo.node_to_node_mac(node_name,base_node)
        # self.ip = topo.node_to_node_interface_ip(node_name,base_node).split('/')[0]
        self.port = topo.node_to_node_port_num(base_node,node_name)
        

class P4switch:
    def __init__(self,name : str,connect,topo : LogicTopo ) -> None:
        self.name = name
        self.topo = topo
        self.connect = []
        for c in connect:
            self.connect.append(NodeInfo(name,c,topo))
        
        self.api = SimpleSwitchThriftAPI(self.topo.get_thrift_port(name))


        
    def compile_and_push(self,p4_src : str, json_src : str):
        source = P4C(p4_src, "/usr/local/bin/p4c")
        source.compile()
        self.api.load_new_config_file(json_src)
        self.api.swap_configs()
        
    def init_table(self):
        pass
    
    def clear_table(self):
        pass
    
    def mininet_update(self):
        self.api.switch_info.load_json_config(self.api.client)
        self.api.table_entries_match_to_handle = self.api.create_match_to_handle_dict()
        self.api.load_table_entries_match_to_handle()
        
    def add_link(self,new_neigh,attribute):
        """ Need to be overwrite do nothing. 
        If attribute is not necessary or not correct it is just ignore"""
        pass
    
    def can_remove_link(self,neighboor:str):
        """ Need to be overwride """
        pass
    
    def remove_link(self,neighboor:str):
        """ Need to be overwride """
        pass