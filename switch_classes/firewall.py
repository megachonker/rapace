from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
from collections import namedtuple
from LogicTopo import LogicTopo

from switch_classes.P4switch import P4switch


Flow = namedtuple('Flow', ['source_ip', 'dest_ip', 'protocol', 'source_port', 'dest_port'])

class Firewall(P4switch):
    def __init__(self,name :str,peer1 : str,peer2 : str,topo : LogicTopo):
        super().__init__(name,topo)
        self.peer_port = [self.topo.node_to_node_port_num(name,peer1),
                          self.topo.node_to_node_port_num(name,peer2)]

        self.compile_and_push("P4src/firewall_with_table.p4","P4src/firewall_with_table.json")
        self.init_table()
        self.mininet_update()

    

    def init_table(self):
        
        self.api.table_clear("rule")
        self.api.table_clear("route")

        
        self.api.table_set_default("rule","allow",[])
        self.api.table_set_default("route","drop",[])
        self.api.table_add("route","forward",[str(self.peer_port[0])],[str(self.peer_port[1])])
        self.api.table_add("route","forward",[str(self.peer_port[1])],[str(self.peer_port[0])])

    # controler function --> put in P4switchs No ? 
    def stat(self):
        print(f"stat du switch {self.name} Firewall")    
        return [self.api.counter_read('total_packet', 0),self.api.counter_read('filter_hit', 0)]

    def reset(self):
        print(f"reset du switch {self.name}")
        self.init_table()


    # firewall function
    def add_drop_rule(self,rule:Flow):
        self.api.table_add("rule","drop",[str(rule.source_ip),str(rule.dest_ip),str(rule.protocol),str(rule.source_port),str(rule.dest_port)],[])
