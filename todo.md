# Features
- [ ] FIX
- [ ] CLI
- [ ] meta-controleur
- [ ] controlers

## CLI
enable user to modulate the network
- [ ] show topology
- [ ] set topology

## meta-controleur
attend la reception de nouveaux YML et applique les différance

connais tout du réseaux et peut lancer des controler sur des switch

- [ ] network knowlege
- [ ] lunch controler

## controler
*L’instanciation d’un contrôleur démarrera donc par l’ouverture d’une
connexion Thrift, une réinitialisation des états présents sur le switch, et l’upload du nouveau data-plane
compilé.*

- add link
- remove link
- show topo
- swap
- filters
- load 
- tuneled

**flow** => *IP source, IP dst, protocole, port source, port destination*

cerveaux qui va driver un équipement:
- [ ] router
- [ ] load-balancer
- [ ] firewall

### Firewall
- possède 2 port IN => OUT.
- add_fw_rule <flow>
- compte les packet filtrée et recus

### Load balancer
déja fait en tp

- 1:N Une entrée Plusieur sortie
- choix hash de du flux pour la sortie
- limite ``set_rate_lb <pkt/s> (voir choise)``
- nombre packet recus

### Router
- propose segment routing
- ajouter point de passage ``add_encap_node <flow> <node or link>``
- compte nombre de packet reçus total



lunch cursedgrpc.bash