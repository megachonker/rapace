
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import * 
from switch_classes.P4switch import P4switch,NodeInfo

SEC_METER = 0.000001

class LoadBalancer(P4switch):
    
    
    
    def __init__(self, name :str, in_ : str, out : list ):
        super().__init__(name)
        
        self.in_info = NodeInfo(name,in_,self.topo)
        
        
        self.rates_max = 1* SEC_METER #1 sec
        
        self.out_info = []
        for o in out:
            self.out_info.append(NodeInfo(name,o,self.topo))
        
        
        
        self.compile_and_push("P4src/loadbalancer.p4","P4src/loadbalancer.json")
        
        self.init_table()
        
        self.init_conter_and_co()
        
        
        self.mininet_update()
        
        
        
        
    
    def init_table(self):
        self.api.table_set_default("ipv4_lpm","drop",[])
        self.api.table_set_default("ecmp_group_to_nhop","drop",[])
        self.api.table_set("filter", "drop", [])
        
       
        for out in self.out_info:
            self.api.table_add("ipv4_lpm","set_nhop_out_in",[str(out.port)],[str(self.in_info.mac),str(self.in_info.port)])
        
        self.api.table_add("ipv4_lpm","ecmp_group",[str(self.in_info.port)],[str(len(self.out_info))])
        
        
        for i in range(len(self.out_info)):
            self.api.table_add("ecmp_group_to_nhop","set_nhop_in_out",[str(i)],[str(self.out_info[i].mac),str(self.out_info[i].port)])
            
            
        self.api.table_add("filter", "drop", [str(2)], [])
        self.api.table_add("filter", "advertise", [str(1)], [])
        self.api.table_add("filter", "NoAction", [str(0)], [])
        
    def init_conter_and_co(self):
        self.api.meter_array_set_rates("the_meter",[(self.rates_max/2,1),(self.rates_max,1)])
        
    def set_rates_lb(self,pktps):
        self.rates_max = pktps * SEC_METER
        self.api.meter_array_set_rates("the_meter",[(self.rates_max/2,1),(self.rates_max,1)])
        
        
        
        