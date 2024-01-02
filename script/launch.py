import yaml

import sys
sys.path.append('.')

from switch_classes.repeater import Repeater
from switch_classes.firewall import Firewall,Flow

import network

network.main(Cli=False)

# Charger le fichier YAML (remplacer 'your_file.yaml' par le chemin de votre fichier)
with open('conf.yaml', 'r') as file:
    data = yaml.safe_load(file)

# Création d'une liste pour stocker les instances de Repeater
repeaters = []

# Parcourir les éléments du fichier YAML pour créer des instances de Repeater
for switch in data['switchs']:
    name = switch['nom']
    role = switch['role']
    connections = switch['connect']
    
    if role == "Repeater":
        Repeater(name, *connections)
    elif role == "Firewall":
        fire = Firewall(name, *connections)
        if 'rules' in switch:
            for rule in switch['rules']:
                rule = Flow(rule['source_ip'], rule['dest_ip'], rule['protocol'], rule['source_port'], rule['dest_port'])
                fire.add_drop_rule(rule)
                
        else:
            print(f"Warning: No rule defined for Firewall {name}")
        
    else:
        print(f"Warning: Unknown role {role} for switch {name}")
        
        
input("Enter to quit")
network.quit()