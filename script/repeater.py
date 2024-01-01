from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
topo = load_topo("topology.json")


class Repeater:
    def __init__(self,name :str,peer1 : str,peer2 : str ):
        self.api = SimpleSwitchThriftAPI(topo.get_thrift_port(name))
        self.name = name
        self.peer_port = [topo.node_to_node_port_num(name,peer1),
                          topo.node_to_node_port_num(name,peer2)]
        
        self.compile_and_push()
        self.init_table()
        
        
        self.api.switch_info.load_json_config(self.api.client)
        self.api.table_entries_match_to_handle = self.api.create_match_to_handle_dict()
        self.api.load_table_entries_match_to_handle()
        
        
    def compile_and_push(self):
        source = P4C("P4src/repeater_with_table.p4", "/usr/local/bin/p4c")
        source.compile()
        self.api.load_new_config_file("P4src/repeater_with_table.json")
        self.api.swap_configs()
        
    def init_table(self):
        self.api.table_set_default("repeater","drop",[])
        
        self.api.table_add("repeater","forward",[str(self.peer_port[0])],[str(self.peer_port[1])])
        self.api.table_add("repeater","forward",[str(self.peer_port[1])],[str(self.peer_port[0])])
        
        