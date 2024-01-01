import yaml
from repeater import Repeater

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
        # Créer une instance de Repeater avec le nom et les connexions
        repeater = Repeater(name, *connections)
    