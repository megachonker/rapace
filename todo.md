# Features
- [x] CLI
- [x] meta-controleur
- [x] controlers

## CLI
enable user to modulate the network
- [x] show topology
- [x] set topology

## meta-controleur
attend la reception de nouveaux YML et applique les différance

connais tout du réseaux et peut lancer des controler sur des switch

- [x] network knowlege
- [x] lunch controler

## controler
*L’instanciation d’un contrôleur démarrera donc par l’ouverture d’une
connexion Thrift, une réinitialisation des états présents sur le switch, et l’upload du nouveau data-plane
compilé.*

- [x] add link
- [x] remove link
- [x] show topo
- [x] swap
- [x] filters

**flow** => *IP source, IP dst, protocole, port source, port destination*

controler :
- [x] router
- [x] load-balancer
- [x] firewall
- [x] repeter

### Firewall
- possède 2 port IN => OUT.
- add_fw_rule <flow>
- compte les packet filtrée et recus

### Load balancer

- 1:N Une entrée Plusieur sortie
- choix hash de du flux pour la sortie
- limite ``set_rate_lb <pkt/s> (voir choise)``
- nombre packet recus

### Router
- propose segment routing
- ajouter point de passage ``add_encap_node <flow> <node or link>``
- compte nombre de packet reçus total
