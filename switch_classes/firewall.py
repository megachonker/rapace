from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
from collections import namedtuple
from LogicTopo import LogicTopo
from queue import LifoQueue


from switch_classes.P4switch import P4switch, NodeInfo


Flow = namedtuple('Flow', ['source_ip', 'dest_ip', 'protocol', 'source_port', 'dest_port'])

class Firewall(P4switch):
    def __init__(self,name :str,peer1 : str,peer2 : str,topo : LogicTopo):
        super().__init__(name,topo)
        self.role = "Firewall"
        self.peer_info = [NodeInfo(name,peer1,topo),
                          NodeInfo(name,peer2,topo)]
        self.next_link = LifoQueue()  # A lifo queue to permit switch link for firewall (because firewall always need 2 peer)

        self.compile_and_push("P4src/firewall_with_table.p4","P4src/firewall_with_table.json")
        self.init_table()
        self.mininet_update()

    

    def init_table(self):
        
        self.api.table_clear("rule")
        self.api.table_clear("route")

        
        self.api.table_set_default("rule","allow",[])
        self.api.table_set_default("route","drop",[])
        self.api.table_add("route","forward",[str(self.peer_info[0].port)],[str(self.peer_info[1].port)])
        self.api.table_add("route","forward",[str(self.peer_info[1].port)],[str(self.peer_info[0].port)])

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

    def add_link(self,new_neigh,attribute):
        self.next_link.put(new_neigh)
        return f"[{self.name}] the new  link is store, delete a curent link to aplly it (firewall can only have to link)"

    def can_remove_link(self,neighboor:str):
        return not self.next_link.empty()
    
    def remove_link(self,neighboor:str):
        for n in self.peer_info:
            if n.name == neighboor:
                self.peer_info.remove(n)        #Remove the link
                self.peer_info.append(NodeInfo(self.name,self.next_link.get(),self.topo)) #Replace by the link previously save (with add_link)
                self.reset()
                return
        raise Exception("Neighboor not found")
            