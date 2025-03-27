# Calculateur de Carrière ESG Simplifié

Un outil minimaliste permettant d'explorer les perspectives de carrière dans les métiers ESG (Environnement, Social et Gouvernance).

## Présentation

Cette version simplifiée du calculateur de carrière ESG a été conçue pour offrir une expérience utilisateur épurée avec un parcours linéaire clair, tout en capturant des leads intéressés par les métiers de l'économie durable.

## Fonctionnalités

- **Exploration des métiers ESG** par secteur
- **Visualisation des perspectives salariales** selon l'expérience
- **Aperçu des compétences clés** pour chaque métier
- **Formulaire simplifié** pour la collecte de leads

## Installation

1. Cloner le dépôt
```bash
git clone https://github.com/ArthurBrunswick/ESG-calculator.git
cd ESG-calculator
```

2. Créer un environnement virtuel (recommandé)
```bash
python -m venv venv
source venv/bin/activate  # Sur Windows: venv\Scripts\activate
```

3. Installer les dépendances
```bash
pip install -r requirements.txt
```

## Utilisation

Lancer l'application:
```bash
streamlit run calculateur_esg.py
```

## Structure des données

L'application utilise un fichier Excel (`data/IED _ esg_calculator data.xlsx`) contenant les données suivantes:
- `salaire`: Données salariales des métiers ESG par niveau d'expérience
- `competences_cles`: Compétences requises pour chaque métier

## Développé par

Institut d'Économie Durable (IED)