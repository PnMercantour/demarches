# Managers
---
## Data Manager (data_manager.py)

Le DataManager est un object global qui est instancié au lancement de l'application. Et qui est partagé par tout les clients. Il permet de gerer l'accès aux données que ce soit les dossiers via le package de démarches simplifiées ou les données des vols sur la base de données du parcs. Il gère aussi la mise en cache des ressources

## ISecurity Manager (interfaces.py)

Cette interface permet de gerer la sécurité au sein de l'application,
Trois versions de cette interface sont implémentées:
- AdminSecurity : Qui va vérifier si le mail et le mot de passe sont corrects
- STSecurity : Va vérifier si le st_token est correct
- UserSecurity : Va vérifier si le security token est valide
(security_manager.py)

## Manager (manager.py)

Ce manager est en réalité un composant dash (dcc.Store) mais qui est en réalité utilisé uniquement pour instancier un security manager propre à la sessions (pour éviter les conflits entre les sessions), il gère aussi 
l'object PageConfig qui permet de partager la configuration d'une page à tout les autres composants (l'interface IBaseComponent que chaque base_component (tout les composants dans ce dossier) implémente possède un attribut config qui est un object PageConfig instancié par le manager propre à chaque session)
