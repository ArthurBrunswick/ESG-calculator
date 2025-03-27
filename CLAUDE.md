# Guide de Développement - Calculateur ESG

## Commandes importantes
- **Lancer l'application**: `streamlit run calculateur_esg.py`
- **Installer les dépendances**: `pip install -r requirements.txt`
- **Créer l'environnement virtuel**: `python -m venv venv`
- **Activer l'environnement** (macOS/Linux): `source venv/bin/activate`
- **Vérifier le format du code**: `pycodestyle calculateur_esg.py`
- **Linter le code**: `pylint calculateur_esg.py`
- **Tests unitaires**: `python -m pytest tests/test_calculateur_esg.py`
- **Tester une fonction spécifique**: `python -m pytest tests/test_calculateur_esg.py::test_nom_fonction`
- **Rapport de couverture**: `python -m pytest --cov=. --cov-report=html`
- **Débogage**: `streamlit run calculateur_esg.py --logger.level=debug`

## Structure des données
Le projet utilise un fichier Excel (`data/IED _ esg_calculator data.xlsx`) avec 4 onglets:
- `salaire`: données salariales des métiers ESG
- `competences_cles`: compétences requises par métier
- `formations_IED`: formations proposées par l'institut
- `tendances_marche`: tendances d'évolution des métiers

## Conventions de code
- **Style**: Respecter PEP 8 (lignes max 88 caractères, 4 espaces d'indentation)
- **Imports**: Grouper par (1) stdlib, (2) third-party, (3) local, alphabétiquement
- **Fonctions**: Docstrings format Google, description + Args/Returns/Raises
- **Types**: Utiliser les annotations de type (PEP 484) sur toutes les fonctions
- **Nommage**: Variables/fonctions en snake_case, Classes en PascalCase, CONSTANTES en MAJUSCULES
- **UI Streamlit**: Une fonction par page, séquencer les éléments logiquement
- **Gestion d'état**: Utiliser st.session_state avec des clés cohérentes et bien documentées
- **Gestion d'erreurs**: try/except avec messages utilisateur clairs et logs détaillés
- **Visualisations**: Standardiser les couleurs avec les variables dans st.session_state.colors
- **Langue**: Utiliser des noms explicites en français pour toutes les variables et fonctions