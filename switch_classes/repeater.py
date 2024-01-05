from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import *

from switch_classes.P4switch import P4switch 


class Repeater(P4switch):
    def __init__(self,name :str,thrif:SimpleSwitchThriftAPI,peer1 : str,peer2 : str ):
        super().__init__(name)
        self.thrif = thrif
        self.peer_port = [self.topo.node_to_node_port_num(name,peer1),
                          self.topo.node_to_node_port_num(name,peer2)]
        
        self.compile_and_push("P4src/repeater_with_table.p4","P4src/repeater_with_table.json")
        self.init_table()
        self.mininet_update()
        
        
        
    def init_table(self):
        self.api.table_set_default("repeater","drop",[])
        
        self.api.table_add("repeater","forward",[str(self.peer_port[0])],[str(self.peer_port[1])])
        self.api.table_add("repeater","forward",[str(self.peer_port[1])],[str(self.peer_port[0])])
        
    # controler function
    def stat(self):
        print(f"stat du switch {self.name}")    
        self.thrif.counter_read('total_packet', 0)

    def reset(self):
        print(f"reset du switch {self.name}")
        self.init_table()