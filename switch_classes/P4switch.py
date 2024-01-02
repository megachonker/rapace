from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
from collections import namedtuple


class P4switch:
    def __init__(self,name : str, ) -> None:
        self.name = name
        self.topo = load_topo("topology.json")

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