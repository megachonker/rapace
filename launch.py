import yaml

from switch_classes.repeater import Repeater
from switch_classes.router import Router
from switch_classes.loadbalancer import LoadBalancer
from switch_classes.firewall import Firewall,Flow
from p4utils.utils.helper import load_topo

from LogicTopo import LogicTopo



def init_switch():
    with open('conf.yaml', 'r') as file:
        data = yaml.safe_load(file)
    # Load la topo pour avoir les interface thrift


    topo  = load_topo("topology.json")
    logic_topo = LogicTopo(topo)
    
    logic_topo.undo_physic_links(topo)
    
    
    
    
    switchs =  {}
    # Parcourir les éléments du fichier YAML pour créer des instances de Repeater
    for switch in data['switchs']:
        """ Iter a first time because P4switchs need a complete topology to start (especially router) """
        name = switch['name']
        role = switch['role']
        connections = switch['connect']   
        logic_topo.switch_info(name,role,connections)


    for switch in data['switchs']:
        name = switch['name']
        role = switch['role']
        connections = switch['connect']
        
        if role == "Repeater":
            switchs[name]=Repeater(name, *connections,logic_topo)
        elif role == "Firewall":
            fire = Firewall(name, *connections,logic_topo)
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
            switchs[name]=fire
        
        elif role == 'LoadBalancer':
            in_ = str(switch['in'])
            out = switch['connect']
            if not in_ in out :
                raise Exception("in not present in connect list")
            out.remove(in_)

            load = LoadBalancer(name,in_,out,logic_topo)
            switchs[name]=load
            print(f"Load Balancer lauch on {name}, his input is {in_} and output {out}")
        
        elif role == 'Router':
            switch[name] = Router(name, connections,logic_topo)
            
        else:
            print(f"Warning: Unknown role {role} for switch {name}")
            
    logic_topo.save_topo("logic_topology.json")
    return switchs

init_switch()



# # network.stop()