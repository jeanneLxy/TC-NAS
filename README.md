# TC-NAS
Github for the NAS project

But : automatiser le déploiement de BGP/MPLS VPN
=> Il faut rajouter MPLS et quelques features de BGP sur notre code GNS existant
et Adaptation en IPv4 au lieu de IPv6 => addresses et ospfv2

## Phase 0 : setup
Faire des groupes de 5 ou 6
4 routeurs à la suite : PE1 – P1 – P2 – PE2
Addressage : interfaces IPv4 et IPv4 loopback
Pas de RIP
Routage en OSPFv2
Router les loopback
Valider le routage et le forwarding (show ip route et pings)

## Phase 1 : core MPLS routing

###Partie A :
Activer LDP sur les interfaces (juste 2 lignes à rajouter)
Valider LDP : MPLS bien transporté + penultimatum popping

###Partie B : automatisation
Addressage, OSPF et LDP


## Phase 2 : core BGP/MPLS routing

###Partie A : documentation
Chercher sur google “Cisco IOS Basic BGP/MPLS VPN” 
attention ils utilisent un route reflector au lieu de full mesh
attention ils utilisent IS-IS au lieu de OSPF	

###Partie B : configuration
configurer iBGP for VPNv4 address family
loopback to loopback iBGP

###Partie C : automatisation
Addressage, OSPF, MPLS, BGP/MPLS



##Phase 3 : ajout de clients

###Partie A :
Ajouter 4 routeurs CE (pour 2 clients de chaque côté)
configurer VRF
et route target

###Partie B :
Configurer eBGP entre PE-CE :
- Normal BGP sur le CE
- Normal BGP dans le VRF sur le PE
Validation routage

###Partie C : automatiser
configuration automatique VRF

##Phase 4 : “aller plus loin”

###Partie A : manageability
Se souvenir ce qu’on a configuré sur le réseau
Pouvoir changer le json et un effet direct sans : routeur reload, cfg wipe ni config ghosting
Pouvoir add, delete, update

###Partie B : plus de services
Faire que les clients puisse dialoguer comme ils veulent entre clients et sites
Ajouter services Internet : VPN et internet normal PAR CONTRE ISOLÉS 
Traffic engineering entrant, faire que les clients puisse choisir par où le traffic doit passer
Ajouter RSVP

# Choix

## Convention retenue pour le nommage
Exemple pour un réseau 10.10.10.??/24

Routeur 1 :
10.10.10.0/30 network
10.10.10.1/30 interface 0
10.10.10.2/30 interface 1
10.10.10.3/30 broadcast

Routeur 2 :
10.10.10.4/30 network
10.10.10.5/30 interface 0
10.10.10.6/30 interface 1
10.10.10.7/30 broadcast
