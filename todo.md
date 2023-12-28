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
flow => *IP source, IP dst, protocole, port source, port destination*

cerveaux qui va driver un équipement:
- [ ] router
- [ ] load-balancer
- [ ] firewall

### Firewall
(IP source, IP dst, protocole, port source, port destination)

- possède 2 port IN => OUT.
- add_fw_rule <flow>
- compte les packet filtrée et recus

### Load balancer
- 1:N Une entrée Plusieur sortie
- hash de du flux pour la sortie
- limite set_rate_lb <pkt/s>