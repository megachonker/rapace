
from p4utils.utils.helper import load_topo
from p4utils.utils.sswitch_thrift_API import SimpleSwitchThriftAPI
from p4utils.utils.compiler import *
from LogicTopo import LogicTopo 
from switch_classes.P4switch import P4switch,NodeInfo


class Router(P4switch):
    
    
    
    def __init__(self, name :str, connexion : list,topo : LogicTopo ):
        super().__init__(name,topo)
        
        
        self.port_info = []
        for connex in connexion:
            self.port_info.append(NodeInfo(name,connex,self.topo))

        self.compile_and_push("P4src/router.p4","P4src/router.json")
        self.init_table()
        self.mininet_update()
        
    def routes(self):
        #Route for switchs loopback (and host inside)
        for sw_dst in self.topo.get_p4switches():
            next_hop = None
            if sw_dst == self.name:
                #For the moment ignore -> decaplusalte in the future
                pass
            else:
                try:
                    paths = self.topo.get_shortest_paths_between_nodes(self.name, sw_dst)
                except:
                    continue #the two switch are no connected

                ip = self.topo.get_switch_loopback(sw_dst)
                if len(paths) >=1:
                    next_hop = paths[0][1]
                    port = self.topo.node_to_node_port_num(self.name,next_hop)
                    mac = self.topo.node_to_node_mac(next_hop,self.name)
                    print("add entry :", "ipv4_lpm","forward",[str(ip)],[mac,str(port)])
                    self.api.table_add("ipv4_lpm","forward",[str(ip)],[mac,str(port)])
                    
            #host linked to this switchs
            for host in self.topo.get_hosts_connected_to(sw_dst):
                ip = self.topo.get_host_ip(host)
                if next_hop:
                    print("add entry :","ipv4_lpm","forward",[str(ip)],[mac,str(port)])
                    self.api.table_add("ipv4_lpm","forward",[str(ip)],[mac,str(port)]) #mac and port already setup 

                elif sw_dst == self.name: #host directly connect to this switch
                    port = self.topo.node_to_node_port_num(self.name,host)
                    mac = self.topo.node_to_node_mac(host,self.name)
                    print("add entry :","ipv4_lpm","forward",[str(ip)],[mac,str(port)] )
                    self.api.table_add("ipv4_lpm","forward",[str(ip)],[mac,str(port)])


    def init_table(self):
        self.api.table_clear("ipv4_lpm")
        self.api.table_set_default("ipv4_lpm","drop",[])
        self.routes()
    
    def add_encap(self,ip,dst):
        ip_dst_loopback = self.topo.get_switch_loopback(dst)
        #azerazer
        print(f"déviation de {ip} qui doit passer par {ip_dst_loopback}")

    # controler function
    def stat(self):
        print(f"stat du switch {self.name} router")    
        return self.api.counter_read('total_packet', 0)

    def reset(self):
        print(f"reset du switch {self.name}")
        self.init_table()