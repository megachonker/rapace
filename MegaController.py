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
        
        
        self.save_topo()
        
    

    def save_topo(self):
        self.logic_topo.save_topo(self.logic_topo_path)
    
    
    


if __name__ == '__main__':
    import sys 
    if len(sys.argv) >1:
        mg = MegaController(conf_path=sys.argv[1])
    else:
        mg = MegaController()



# # network.stop()