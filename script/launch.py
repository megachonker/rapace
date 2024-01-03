import yaml

import sys
sys.path.append('.')

from switch_classes.repeater import Repeater
from switch_classes.loadbalancer import LoadBalancer
from switch_classes.firewall import Firewall,Flow

import network
# network.main(Cli=False)

# Charger le fichier YAML (remplacer 'your_file.yaml' par le chemin de votre fichier)
with open('conf.yaml', 'r') as file:
    data = yaml.safe_load(file)

# Création d'une liste pour stocker les instances de Repeater
repeaters = []

# Parcourir les éléments du fichier YAML pour créer des instances de Repeater
for switch in data['switchs']:
    name = switch['name']
    role = switch['role']
    connections = switch['connect']
    
    if role == "Repeater":
        Repeater(name, *connections)
    elif role == "Firewall":
        fire = Firewall(name, *connections)
        if 'rules' in switch:
            #association table 
            translate = {
                'TCP':6,
                'UDP':17,
            }
            for rule in switch['rules']: 
                rule = Flow(rule['source_ip'], rule['dest_ip'],  translate.get(rule['protocol']), rule['source_port'], rule['dest_port'])
                fire.add_drop_rule(rule)
                
        else:
            print(f"Warning: No rule defined for Firewall {name}")
    
    elif role == 'LoadBalancer':
        in_ = str(switch['in'])
        out = switch['connect']
        if not in_ in out :
            raise Exception("in not present in connect list")
        out.remove(in_)

        load = LoadBalancer(name,in_,out)
        print(f"Load Balancer lauch on {name}, his input is {in_} and output {out}")
        
    else:
        print(f"Warning: Unknown role {role} for switch {name}")
        
        
# input("Enter to quit")
# network.stop()