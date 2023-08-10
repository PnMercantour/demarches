# Actions

> Les actions sont des objects permettant de réaliser une action de back-end précise, elles sont utilisées par admin_panel.py, flight_saver.py en majorité. Elle implémentent l'interface IAction (interfaces.py) qui permet de définir un niveau de sécurité pour chaque action.

## PackedActions (action_manager.py)
Implémente l'interface IAction et est donc considéré comme une action, et permet de prendre en compte plusieurs actions en une seule. Elle est utilisée par admin_panel.py pour réaliser plusieurs actions en une seule et permet de facilement ajouter des actions entre deux autres, permet transmettre un résultat d'une action à une autre. La liste des actions doivent être des actions héritant non pas de IAction mais de IPackedAction (interfaces.py) qui permet de définir une action qui peut être packée (et donc prendre des arguments **kwargs dans sa fonction perform contrairement à une IAction simple qui prend ses paramètres dans le constructeur)


## Liste des actions implémentées (action_manager.py)

- FeatureFetching : Action sans sécurité qui permet de récupérer des données à partir d'une requête SQL dans un fichier feature (spécifique à l'obtentions des limites, zones sensibles, etc...)
- GenerateSTToken : Permet de générer un token pour le st stocké dans la base de données
- SaveFlight : Permet de sauvegarder un vol dans la base de données
- SendMailTo : Permet d'envoyer un mail à une adresse mail et de formater le message avec différents arguments
- DeleteSTToken : Permet de supprimer un token pour le st stocké dans la base de données
- ChangeDossieState : Permet de changer l'état d'un dossier (accepté, refusé, etc...)
- BuildPdf : Permet de construire un pdf contenant les informations de survol
- Create Prefilled Dossier : Permet de construire un dossier pré-rempli sur démarches simplifiées
- UpdateFlightDossier : Permet de mettre à jour un vol sur la base de données à partir d'un dossier
- SaveNewTemplate : Sauvegarde un vol en tant que template