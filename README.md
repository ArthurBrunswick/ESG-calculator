# Calculateur de Carrière ESG - Institut d'Économie Durable (IED)

## Description
Le calculateur de carrière ESG est un outil interactif qui permet aux utilisateurs de visualiser les perspectives salariales et d'évolution dans les métiers de la transition écologique et sociale. Destiné aux étudiants intéressés par une carrière dans le secteur de la durabilité, cet outil aide à la prise de décision concernant leur orientation professionnelle.

## Fonctionnalités
- Parcours utilisateur en 3 étapes (profil, métier, résultats)
- Base de données de métiers ESG avec salaires par niveau d'expérience
- Visualisation graphique des évolutions salariales
- Capture de leads qualifiés avec formulaire RGPD
- Système de sessions pour conserver les données entre les étapes
- Barre de progression interactive

## Installation et démarrage

### Prérequis
- Python 3.7+
- pip (gestionnaire de paquets Python)

### Installation
1. Clonez ce dépôt :
```bash
git clone https://github.com/votre-compte/calculateur-esg.git
cd calculateur-esg
```

2. Installez les dépendances :
```bash
pip install -r requirements.txt
```

### Lancement de l'application
```bash
streamlit run calculateur_esg.py
```

L'application sera accessible dans votre navigateur à l'adresse : http://localhost:8501

## Structure des données
Les données des métiers ESG sont stockées dans le fichier CSV `data/metiers_esg.csv` avec la structure suivante :
- Métier : nom du métier
- Secteur : secteur d'activité
- Expérience : tranche d'expérience
- Salaire_Min : salaire minimum pour cette tranche
- Salaire_Max : salaire maximum pour cette tranche
- Salaire_Moyen : salaire moyen pour cette tranche
- Description : description du métier

Pour ajouter ou modifier des métiers, vous pouvez éditer directement ce fichier CSV.

## Personnalisation
- Les couleurs principales de l'interface sont définies en haut du fichier `calculateur_esg.py`
- Le CSS personnalisé peut être modifié dans la fonction `load_custom_css()`
- Les textes explicatifs peuvent être adaptés dans les fonctions `page_...`

## Contact
Pour toute question ou suggestion concernant cette application, contactez l'Institut d'Économie Durable.

## Licence
Ce projet est sous licence MIT.