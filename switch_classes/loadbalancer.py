
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
from switch_classes.P4switch import P4switch,NodeInfo



class LoadBalancer(P4switch):
    
    
    
    def __init__(self, name :str,thrif:SimpleSwitchThriftAPI, in_ : str, out : list ):
        super().__init__(name)
        self.thrif = thrif
        self.in_info = NodeInfo(name,in_,self.topo)
        
        self.out_info = []
        for o in out:
            self.out_info.append(NodeInfo(name,o,self.topo))
        
        
        
        self.compile_and_push("P4src/loadbalancer.p4","P4src/loadbalancer.json")
        
        self.init_table()
        
        
        self.mininet_update()
        
        
        # Need to setup meter ....
        #self.meter ....
        
    
    def init_table(self):
        self.api.table_set_default("ipv4_lpm","drop",[])
        self.api.table_set_default("ecmp_group_to_nhop","drop",[])
       
        for out in self.out_info:
            self.api.table_add("ipv4_lpm","set_nhop",[str(out.port)],[str(self.in_info.mac),str(self.in_info.port)])
        
        self.api.table_add("ipv4_lpm","ecmp_group",[str(self.in_info.port)],[str(len(self.out_info))])
        
        
        for i in range(len(self.out_info)):
            self.api.table_add("ecmp_group_to_nhop","set_nhop",[str(i)],[str(self.out_info[i].mac),str(self.out_info[i].port)])
            
            
        self.api.table_add("filter", "drop", [str(2)], [])
        self.api.table_add("filter", "advertise", [str(1)], [])
        self.api.table_add("filter", "NoAction", [str(0)], [])
        
    # controler function
    def stat(self):
        print(f"stat du switch {self.name}")    
        self.thrif.counter_read('total_packet', 0)

    def reset(self):
        print(f"reset du switch {self.name}")
        self.init_table()