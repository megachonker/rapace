
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
topo = load_topo("topology.json")



class LoadBalancer:
    
    
    
    def __init__(self, name :str, in_ : str, out : list ):
        self.api = SimpleSwitchThriftAPI(topo.get_thrift_port(name))
        self.name = name
        self.in_ = in_
        self.out= out
        
        self.compile_and_push()
        self.init_table()
        
        
        
        self.api.switch_info.load_json_config(self.api.client)
        self.api.table_entries_match_to_handle = self.api.create_match_to_handle_dict()
        self.api.load_table_entries_match_to_handle()
        
    def compile_and_push(self):
        source = P4C("P4src/loadbalancer.p4", "/usr/local/bin/p4c")
        source.compile()
        self.api.load_new_config_file("P4src/loadbalancer.json")
        self.api.swap_configs()
        
        
        
    def init_table(self):
        qsdqsd