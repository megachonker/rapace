
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import *
from LogicTopo import LogicTopo 
from switch_classes.P4switch import P4switch,NodeInfo
from queue import Queue

SEC_METER = 0.000001

class LoadBalancer(P4switch):
    
    
    
    def __init__(self, name :str, in_ : str, out : list,topo : LogicTopo ):
        super().__init__(name,out + [in_],topo)
        self.role = "LoadBalancer"
        
        self.rates_max = 1* SEC_METER #1 sec
        
        self.next_in = Queue()  #Use when swap node/link to store potential next in
        # out_backup is not needed because we can put inifinit output port
        
        self.out_info = []
        for o in self.connect:
            if o.name == in_:
                self.in_info = o
            else:
                self.out_info.append(o)
        
        
        self.compile_and_push("P4src/loadbalancer.p4","P4src/loadbalancer.json")
        self.init_table()
        self.init_conter_and_co()
        self.mininet_update()

        
    def clear_table(self):
        self.api.table_clear("traffic_type")
        self.api.table_clear("loadbalance")
        self.api.table_clear("filter")
        
        #Normally the default is not clear but ... :
        self.api.table_set_default("traffic_type","drop",[])
        self.api.table_set_default("loadbalance","drop",[])
        self.api.table_set_default("filter", "drop", [])
    
    def init_table(self):
        self.clear_table()
        
        for out in self.out_info:
            self.api.table_add("traffic_type","set_nhop_out_in",[str(out.port)],[str(self.in_info.mac),str(self.in_info.port)])
        
        self.api.table_add("traffic_type","hash_calcule",[str(self.in_info.port)],[str(len(self.out_info))])
        
        for i in range(len(self.out_info)):
            self.api.table_add("loadbalance","set_nhop_in_out",[str(i)],[str(self.out_info[i].mac),str(self.out_info[i].port)])
            
        self.api.table_add("filter", "drop", [str(2)], [])
        self.api.table_add("filter", "advertise", [str(1)], [])
        self.api.table_add("filter", "NoAction", [str(0)], [])
        

    # controler function
    def stat(self):
        print(f"stat du switch {self.name}")    
        return [self.api.counter_read('total_packet', 0)]

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
        
    def add_link(self,new_neigh,attribute):
        if attribute =='in':
            self.next_in.put(new_neigh)
            return f"[{self.name}] the new in link is store, delete the previous one the aplly it"
        else:
            self.out_info.append(NodeInfo(self.name,new_neigh,self.topo))
            self.init_table()  #Refill the tables
            return f"[{self.name}] new outup added"
        
    def can_remove_link(self,neighboor:str):
        if self.in_info.name == neighboor : 
            return not self.next_in.empty()
        return len(self.out_info)>1
    
    def remove_link(self,neighboor:str):
        if self.in_info.name == neighboor :
            self.in_info = NodeInfo(self.name,self.next_in.get(),self.topo)
        else:
            for n in self.out_info:
                if n.name == neighboor:
                    self.out_info.remove(n)
        
        self.reset()
            
