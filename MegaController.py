import yaml

from switch_classes.repeater import Repeater
from switch_classes.router import Router
from switch_classes.loadbalancer import LoadBalancer
from switch_classes.firewall import Firewall,Flow
from p4utils.utils.helper import load_topo

from LogicTopo import LogicTopo



class MegaController:
    def __init__(self,conf_path='topo_conf/conf.yaml',logic_topo_path='logic_topology.json') :
        self.switchs={}
        self.logic_topo=LogicTopo()
        self.logic_topo_path = logic_topo_path
        
        self.init_switch(conf_path)
        



    def init_switch(self,conf_path='topo_conf/conf.yaml'):
        with open(conf_path, 'r') as file:
            data = yaml.safe_load(file)
        # Load la topo pour avoir les interface thrift


        physic_topo  = load_topo("topology.json")
        self.logic_topo = LogicTopo(physic_topo)

        self.logic_topo.undo_physic_links(physic_topo)




        self.switchs =  {}
        # Parcourir les éléments du fichier YAML pour créer des instances de Repeater
        for switch in data['switchs']:
            """ Iter a first time because P4switchs need a complete topology to start (especially router) """
            name = switch['name']
            role = switch['role']
            connections = switch['connect']   
            self.logic_topo.switch_info(name,role,connections)


        for switch in data['switchs']:
            name = switch['name']
            role = switch['role']
            connections = switch['connect']

            if role == "Repeater":
                self.switchs[name]=Repeater(name, *connections,self.logic_topo)
            elif role == "Firewall":
                fire = Firewall(name, *connections,self.logic_topo)
                if 'rules' in switch:
                    #association table 
                    translate = {
                        'TCP':6,
                        'UDP':17,
                        'ICMP':1,
                    }
                    for rule in switch['rules']: 
                        if rule['protocol'] == 'ICMP':
                            rule = Flow(rule['source_ip'], rule['dest_ip'],  translate.get(rule['protocol']), 0, 0)
                        else:
                            rule = Flow(rule['source_ip'], rule['dest_ip'],  translate.get(rule['protocol']), rule['source_port'], rule['dest_port'])
                        fire.add_drop_rule(rule)
                else:
                    print(f"Warning: No rule defined for Firewall {name}")
                self.switchs[name]=fire

            elif role == 'LoadBalancer':
                in_ = str(switch['in'])
                out = switch['connect']
                if not in_ in out :
                    raise Exception("in not present in connect list")
                out.remove(in_)

                load = LoadBalancer(name,in_,out,self.logic_topo)
                self.switchs[name]=load
                print(f"Load Balancer lauch on {name}, his input is {in_} and output {out}")

            elif role == 'Router':
                self.switchs[name] = Router(name, connections,self.logic_topo)

            else:
                print(f"Warning: Unknown role {role} for switch {name}")

        self.save_topo()
        return self.switchs



    def change_weight(self,link : (str,str), weight : int):
        if not self.logic_topo.are_neighbors(link[0],link[1]):
            return f"{link[0]} and {link[1]} are not neighbors"
        self.logic_topo.edges[link]['weight'] = weight
        
        self.newtopo_router()
        
        self.save_topo()
        
        return f"Ok"
        
    

    def save_topo(self):
        self.logic_topo.save_topo(self.logic_topo_path)
        
    def newtopo_router(self):
        """ Reload the router pass the new topo to the switch (and recalculate route) """
        for _,switch in self.switchs.items():
            if switch.role == "Router":
                switch.newtopo_recalculate(self.logic_topo)
    
    def add_link(self,link : (str,str),attribute=('','')):
        """ Add link to the topo and updtae the switch. 
            Attributes is for example in for a loadbalancer"""
        if self.logic_topo.are_neighbors(link[0],link[1]):
            return f"There is already a link between {link[0]} and {link[1]}"

        if self.logic_topo.isHost(link[0]) and self.logic_topo.isHost(link[1]):
            return f"Error can not link to host"
        
        if (not self.logic_topo.isHost(link[0])) and self.switchs.get(link[0]) is None:
            return f"{link[0] } has no role, link can not be added to it"
        
        if (not self.logic_topo.isHost(link[1])) and self.switchs.get(link[1]) is None:
            return f"{link[1] } has no role, link can not be added to it"
            
        reponses =[]
        if not self.logic_topo.isHost(link[0]):
            reponses.append(self.switchs[link[0]].add_link(link[1],attribute[0]))
        if not self.logic_topo.isHost(link[1]):
            reponses.append(self.switchs[link[1]].add_link(link[0],attribute[1]))
        self.logic_topo.add_link(link[0],link[1])
        
        self.newtopo_router()
        
        return reponses
        
    def remove_link(self, link : (str,str)):
        if not self.logic_topo.are_neighbors(link[0],link[1]):
            return f"There is any link between {link[0]} and {link[1]}"
        isswitch0 = self.logic_topo.isSwitch(link[0])
        isswitch1 = self.logic_topo.isSwitch(link[1])
        
        if  isswitch0 and ( not self.switchs[link[0]].can_remove_link(link[1]) ):
            return f"{link[0]} can not remove his link"

        if  isswitch1 and (not self.switchs[link[1]].can_remove_link(link[0])) :
            return f"{link[1]} can not remove his link"
        
        if isswitch0 :
            self.switchs[link[0]].remove_link(link[1])
        if isswitch1:
            self.switchs[link[1]].remove_link(link[0])
        
        self.logic_topo.remove_edge(link[0],link[1])
        
        self.newtopo_router()
        
        return f"Link remove succefully"
        
        
        
        
        
                
    
    


if __name__ == '__main__':
    import sys 
    if len(sys.argv) >1:
        mg = MegaController(conf_path=sys.argv[1])
    else:
        mg = MegaController()

    input("remove link2")
    print(mg.remove_link(('s3','s1')))
    

    
 


# # network.stop()