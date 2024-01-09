
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import *
from LogicTopo import LogicTopo 
from switch_classes.P4switch import P4switch,NodeInfo

SEC_METER = 0.000001

class LoadBalancer(P4switch):
    
    
    
    def __init__(self, name :str, in_ : str, out : list,topo : LogicTopo ):
        super().__init__(name,topo)
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
        
        
        self.api.table_clear("traffic_type")
        self.api.table_clear("ecmp_group_to_nhop")
        self.api.table_clear("filter")
        
        #Normally the default is not clear but ... :
        self.api.table_set_default("traffic_type","drop",[])
        self.api.table_set_default("ecmp_group_to_nhop","drop",[])
        self.api.table_set_default("filter", "drop", [])
        
       
        for out in self.out_info:
            self.api.table_add("traffic_type","set_nhop_out_in",[str(out.port)],[str(self.in_info.mac),str(self.in_info.port)])
        
        self.api.table_add("traffic_type","ecmp_group",[str(self.in_info.port)],[str(len(self.out_info))])
        
        
        for i in range(len(self.out_info)):
            self.api.table_add("ecmp_group_to_nhop","set_nhop_in_out",[str(i)],[str(self.out_info[i].mac),str(self.out_info[i].port)])
            
            
        self.api.table_add("filter", "drop", [str(2)], [])
        self.api.table_add("filter", "advertise", [str(1)], [])
        self.api.table_add("filter", "NoAction", [str(0)], [])
        

        
        
    # controler function
    def stat(self):
        print(f"stat du switch {self.name}")    
        return self.api.counter_read('total_packet', 0)

    def reset(self):
        print(f"reset du switch {self.name}")
        self.rates_max = 1* SEC_METER
        self.init_table()
        self.init_conter_and_co()
    # dedicated
    def init_conter_and_co(self):
        self.api.meter_array_set_rates("the_meter",[(self.rates_max/2,1),(self.rates_max,1)])
        
    def set_rates_lb(self,pktps):
        self.rates_max = pktps * SEC_METER
        print(f"new rate set to {self.rates_max}")
        self.api.meter_array_set_rates("the_meter",[(self.rates_max/2,1),(self.rates_max,1)])
        return f"new rate set to {self.rates_max}"
        
        