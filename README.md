# Carto Editor

> Outil de création de plan de survol pour transmettre la demande de survol au Parc National du Mercantour

- [Carto Editor](#carto-editor)
  - [Installation](#installation)
    - [Note](#note)
  - [Configuration de l'application (obligatoire)](#configuration-de-lapplication-obligatoire)
    - [Description des variables](#description-des-variables)
  - [Lancement](#lancement)
    - [Pour un lancement en mode développement sur le réseau local](#pour-un-lancement-en-mode-développement-sur-le-réseau-local)
    - [Pour un lancement en mode production (ou sans le mode débug, ou avec un host ou un port différent)](#pour-un-lancement-en-mode-production-ou-sans-le-mode-débug-ou-avec-un-host-ou-un-port-différent)
  - [Pour aller plus loin dans le paramétrage](#pour-aller-plus-loin-dans-le-paramétrage)
    - [Description des variables](#description-des-variables-1)


Cet outil est adaptable à d'autres instances, avec quelques modifications au niveau du schéma de la base de données.(Ref sql/schema.sql pour comprendre comment la base de données est structurée). Pour ce qui est du reste (Démarches simplifiées, génération  du plan de vol), tout est paramétrable dans le fichier config.json (à la racine du projet).

## Installation

```sh
git clone https://github.com/PnMercantour/demarches.git
cd demarches
pip install -r requirements.txt
```

### Note 
Cet outil dépends de deux packages qui ne sont pas disponibles sur PyPi, le fichier 'requirements.txt' contient l'url vers le dépôt. Normalement, pip devrait pouvoir les installer sans problème.

#### Diagramme UX
[Diagramme](https://github.com/PnMercantour/demarches/blob/main/assets/Diagramm%20Authorisation%20Survol%20Final.png)

## Configuration de l'application (obligatoire)

> Dupliquer le fichier `config-template.json` et le renommer `config.json` les paramètres de base permettrons de lancer l'application. Voir [Pour aller plus loin dans le paramétrage](#pour-aller-plus-loin-dans-le-paramétrage) pour plus d'informations sur les paramètres disponibles.


> Créer un fichier `.env` et le remplir avec les informations suivantes:

```plain
# General
IGN_KEY=decouverte
DS_KEY='OGM3NDUzNjAtZDM2MS00NGY4LWEyNTAtOTUyY2FjZmM1MTU1O2VNTnVKb3hnMWVCQXRtSENNdlVIRXJ4Yw=='
DB_CONNECTION=""
DEMARCHE_NUMBER=77818
BASEMAP_PATH="./raster/scan25.tif"
VERBOSE=0
VERBOSE_SQL=0
HOST="http://localhost:8050"

# Mail
SMTP_SERVER='ssl0.ovh.net'
SENDER_EMAIL='no_reply@ext.com'
SENDER_PASSWORD='123456'
```

### Description des variables

| Variable          | Description                                                                                                                                        |
| ----------------- | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| `IGN_KEY`         | Clé d'API pour l'API Géoportail(laisser decouverte si vous n'avez pas de clé)                                                                      |
| `DS_KEY`          | Clé d'API pour l'API Démarches Simplifiées (générable depuis le site avec un compte administrateur)                                                |
| `DB_CONNECTION`   | Connection string pour la base de données (voir [ici](https://docs.sqlalchemy.org/en/13/core/engines.html#database-urls) pour plus d'informations) |
| `DEMARCHE_NUMBER` | Numéro de la démarche simplifiée (trouvable sur le dashboard de démarches simplifiées (en mode administrateur ou en instructeur))                  |
| `BASEMAP_PATH`    | Chemin vers le fichier raster servant de fond de carte                                                                                             |
| `VERBOSE`         | Affiche les logs de l'application                                                                                                                  |
| `VERBOSE_SQL`     | Affiche le détail des requêtes SQL                                                                                                                 |
| `HOST`            | URL de l'application (Uniquement pour la creation de lien dans les mails, la vrai root se fait au lancement de l'application)                      |
| `SENDER_EMAIL`    | Adresse mail de l'expéditeur des mails                                                                                                             |
| `SENDER_PASSWORD` | Mot de passe de l'expéditeur des mails                                                                                                             |
| `SMTP_SERVER`     | Serveur SMTP pour l'envoi des mails                                                                                                                |


## Lancement

### Pour un lancement en mode développement sur le réseau local

```sh
python app.py
```

### Pour un lancement en mode production (ou sans le mode débug, ou avec un host ou un port différent)

> Créer un fichier `run.py` (à la racine du projet, le nom importe peu (run.py déjà ajouté au .gitignore)) et y mettre le code suivant:

```python
from app import app

if __name__ == "__main__":
    app.run(host='custom', port=custom, debug=False)
```

Remplacer `custom` et `custom` par les valeurs souhaitées


## Pour aller plus loin dans le paramétrage

> `config.json` contient les paramètres de l'application, il est possible de le modifier pour adapter l'application à vos besoins.

```json
{
    "email-route":{
        "Ubaye Verdon" : [],
        "Haut Var Cians" : [],
        "Vésubie" : [],
        "Tinée" : [],
        "Roya Bevera" : [],
        "default" : []
    },
    "admin-emails" : [],
    "email-templates": {
        "st-requesting": {
            "subject": "Validation ST dossier n°{dossier_number}",
            "body-path": "./email-templates/st-requesting.txt"
        },
        "st-prescription":{
            "subject": "Prescription ST dossier n°{dossier_number}",
            "body-path": "./email-templates/st-prescription.txt"
        },
        "dossier-admin": {
            "subject": "Dossier n°{dossier_number} inspection",
            "body-path": "./email-templates/dossier-admin.txt"
        }
    },
    "pdf" : {
        "pdf-template":"vol_mercantour",
        "title" : "Annexe",
        "subtitle" : "Plan de vol",
        "pdf-fields": []
    },
    "label-field":{
        "st-prescription": "st-prescription",
        "security-token" : "security-token",
        "instructor-url" : "url-instructeur",
        "flight-pdf-url" : "plan-de-vol",
        "user-edit-link" : "user-edit-link"
    },
    "info-panel-fields":[]
}
```

### Description des variables

| Variable            | Description                                                                                                                                                                                                                                                 |
| ------------------- | ----------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `email-route`       | Liste des adresses mail des instructeurs pour chaque région, le nom des régions peuvents être changé et corresponde à la colonne region dans la base de données, mettre dans `default` si il n'y a pas de route                                             |
| `email-templates`   | Liste des templates de mail, `subject` correspond au sujet du mail, `body-path` correspond au chemin vers le fichier contenant le corps du mail, vous pouvez personnalisé vos mails avec des variables en respectant la syntaxe (voir les mails par défaut) |
| `label-field`       | Liste des nom des variables des champs et annotations de démarches simplifiées requis par l'application (propre à la démarche)                                                                                                                              |
| `info-panel-fields` | Liste des champs démarches simplifiées à afficher dans le panel information                                                                                                                                                                                 |
| `pdf-fields`        | Liste des champs démarches simplifiées à afficher dans le pdf de survol final                                                                                                                                                                               |
| `pdf-template`      | Nom du template de pdf à utiliser qui est le nom du fichier html et css présent dans le dossier `pdf-templates`, pour rajouter votre propre squelette, rajouter les dans ce dossier avec le même nom pour le css et html                                    |
| `title`             | Titre du pdf                          (peut être formatté)                                                                                                                                                                                                  |
| `subtitle`          | Sous-titre du pdf (peut être formatté )                                                                                                                                                                                                                     |
| `admin-emails`      |  Liste des adresses mail dont le mail d'inspection par la direction sera envoyé à.                                                                                                                                                                                        |


