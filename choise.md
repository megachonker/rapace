## Configuration

L'usage d'un fichier pour l'initialisation est judicieux (CI/CD) et simplifie les tests comparativement à la mémorisation de commandes.
utiliser un format standare est meilleur:

- **YAML** : Idéal pour la lisibilité humaine, offre davantage de fonctionnalités mais moins performant.
- **JSON** : Bon équilibre entre lisibilité et performance.
- **XML** : Peu agréable pour l'humain, mais très performant.

Privilégier un style déclaratif pour plus de clarté.

Notre objectif n'est pas l'efficacité à tout prix, mais une clarté maximale.

### exemple:
```yaml
switchs:
  - nom: A
    role: load_balancer
  - nom: B
    role: switch
  - nom: C
    role: switch
  - nom: D
    role: switch
  - nom: E
    role: firewall

connexions:
  - entre: [A, B]
  - entre: [A, C]
  - entre: [B, E]
  - entre: [C, E]

```
Utilisation de YAML:
- Le fichier YAML reste **petit et simple**, contenant les informations essentielles sur la topologie réseau.
- Sert de **source de vérité** pour les configurations du réseau.

**Question ouverte** : Comment intégrer la topologie Mininet avec le YAML ?


## communication CLI -> meta-controler
### Transmission du Fichier YAML Complet:
- Le fichier YAML entier est envoyé à chaque modification.
- Convient aux configurations **légères** et réduit la complexité.

Rôles Délimités:
- La CLI gère les **interactions utilisateur**.
- Un serveur séparé gère la **logique de contrôle** basée sur le YAML.

### Comparaison avec d'Autres Approches
gRPC vs Protocole Personnalisé vs CRUD:
- **gRPC** : Efficace mais nécessite une API et une gestion des communications plus **complexe**.
- **Protocole Personnalisé** : Offre une flexibilité totale mais augmente la **complexité de développement** et de maintenance.
- **CRUD** : Commun pour les API web, exige une structure d'API bien définie, pouvant devenir **complexe** avec l'évolution des besoins.


# controler
## Load balancer
### limitation du débit
- [controlplane exemple](https://github.com/nsg-ethz/p4-learning/blob/0ddba187f207e24a8a614f5d1abf8bc11998c9d3/exercises/04-RSVP/thrift/solution/rsvp_controller.py#L276)
- [exemple rate limiting](https://github.com/nsg-ethz/p4-learning/tree/master/exercises/04-RSVP/thrift#part-2-rate-limiting-and-priorities)
- RFC [trTCM](https://datatracker.ietf.org/doc/html/rfc2698#section-1) tag du packet en fonction du débit 