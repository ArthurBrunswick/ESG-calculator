"""
Calculateur de Carrière ESG - Institut d'Économie Durable
Application Streamlit pour l'orientation professionnelle dans les métiers de l'ESG
Version MVP 2.0 - Refonte avec sélection par tags
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import requests
import json
import hubspot
import numpy as np
from hubspot.crm.contacts import SimplePublicObjectInputForCreate, SimplePublicObjectInput, ApiException

# ----- CONFIGURATION DE L'APPLICATION -----
def configure_app():
    """Configure l'application Streamlit avec les paramètres de base."""
    st.set_page_config(
        page_title="Calculateur ESG - Institut d'Économie Durable",
        page_icon="🌱",
        layout="wide"
    )
    
    # Ajouter un script JavaScript pour scroller en haut de la page si nécessaire
    if st.session_state.get('scroll_to_top', False):
        st.session_state.scroll_to_top = False  # Réinitialiser le flag
        js = '''
        <script>
            // Solution plus robuste pour le défilement
            window.addEventListener('load', function() {
                window.scrollTo(0, 0);
                // Méthode alternative pour Safari et certains navigateurs
                document.body.scrollTop = 0;
                document.documentElement.scrollTop = 0;
            });
            // Exécuter immédiatement aussi
            window.scrollTo({top: 0, behavior: 'auto'});
            document.body.scrollTop = 0;
            document.documentElement.scrollTop = 0;
        </script>
        '''
        st.markdown(js, unsafe_allow_html=True)
    
    # Définition des couleurs
    st.session_state.setdefault('colors', {
        'primary': "#0356A5",     # Bleu foncé
        'secondary': "#FFE548",   # Jaune
        'green': "#00916E",       # Vert
        'background': "#f7f7f5"   # Fond gris
    })
    
    # CSS amélioré
    colors = st.session_state.colors
    st.markdown(f"""
    <style>
    .main {{
        background-color: {colors['background']};
    }}
    .stButton>button {{
        background-color: {colors['secondary']};
        color: #003366;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        transition: all 0.3s ease;
    }}
    .stButton>button:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }}
    .progress-bar {{
        height: 10px;
        background-color: #E0E0E0;
        border-radius: 5px;
        margin-bottom: 20px;
    }}
    .progress-bar-fill {{
        height: 100%;
        background-color: {colors['secondary']};
        border-radius: 5px;
    }}
    .highlight-box {{
        padding: 20px;
        border-radius: 10px;
        background-color: white;
        color: #333333;
        border-left: 5px solid {colors['primary']};
        margin: 20px 0;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
    }}
    .feature-card {{
        padding: 15px;
        border-radius: 10px;
        background-color: white;
        color: #333333;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-top: 3px solid {colors['secondary']};
    }}
    .tag-selector {{
        display: inline-block;
        margin: 5px;
        padding: 8px 15px;
        background-color: white;
        border: 1px solid #ddd;
        border-radius: 20px;
        cursor: pointer;
        transition: all 0.2s;
    }}
    .tag-selector:hover {{
        border-color: {colors['primary']};
    }}
    .tag-selected {{
        background-color: {colors['primary']};
        color: white;
        border-color: {colors['primary']};
    }}
    div[data-testid="stCheckbox"] {{
        background-color: white;
        border-radius: 8px;
        padding: 2px 10px;
        margin: 4px;
        border: 1px solid #e6e6e6;
        box-shadow: 0 1px 2px rgba(0,0,0,0.05);
        transition: all 0.2s;
    }}
    div[data-testid="stCheckbox"]:hover {{
        border-color: {colors['primary']};
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }}
    div[data-testid="stCheckbox"] > label > div[data-testid="stMarkdownContainer"] {{
        font-size: 15px;
    }}
    /* Pour les cases cochées */
    div[data-testid="stCheckbox"] label:has(input:checked) {{
        font-weight: 600;
        color: {colors['primary']};
    }}
    .metier-card {{
        padding: 15px;
        border-radius: 10px;
        background-color: white;
        margin-bottom: 15px;
        box-shadow: 0 2px 5px rgba(0,0,0,0.05);
        border-left: 3px solid {colors['primary']};
        cursor: pointer;
        transition: all 0.2s;
    }}
    .metier-card:hover {{
        transform: translateY(-2px);
        box-shadow: 0 4px 10px rgba(0,0,0,0.1);
    }}
    h1, h2, h3 {{
        color: {colors['primary']};
    }}
    /* Fix pour le mode dark */
    .dark .highlight-box, .dark .feature-card, .dark .metier-card, .dark .tag-selector, .dark .interest-tag {{
        background-color: rgba(255, 255, 255, 0.1);
        color: #FFFFFF;
    }}
    .dark .interest-tag.selected {{
        background-color: rgba(3, 86, 165, 0.3);
    }}
    [data-testid="stMarkdownContainer"] {{
        color: currentColor;
    }}
    </style>
    """, unsafe_allow_html=True)

# ----- GESTION DE L'ÉTAT DE L'APPLICATION -----
def initialize_session_state():
    """Initialise l'état de la session avec les valeurs par défaut."""
    default_values = {
        'page': 'accueil',        # Page actuelle
        'user_data': {            # Données utilisateur minimales
            'prenom': "",
            'nom': "",
            'email': "",
            'telephone': "",
            'opt_in': True,
            'tags': [],           # Tags d'intérêt sélectionnés
            'entreprises': [],    # Types d'entreprises sélectionnés
            'metiers_matches': [], # Métiers correspondant aux tags
            'metier_selectionne': "", # Métier sélectionné pour la page détaillée
            'hubspot_submitted': False  # Indicateur d'envoi à Hubspot
        },
        'data_loaded': False,     # Indicateur de chargement des données
        'data': {},               # Données chargées
        'selected_tags': [],      # Tags sélectionnés
        'selected_entreprises': [], # Types d'entreprises sélectionnés
        'email_submitted': False,  # Indicateur de soumission d'email
        'scroll_to_top': True     # Indicateur de défilement automatique vers le haut (activé par défaut)
    }
    
    # Initialiser les valeurs manquantes uniquement
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value
            
    # S'assurer que tous les champs user_data existent
    if 'user_data' in st.session_state:
        for field, default in default_values['user_data'].items():
            if field not in st.session_state.user_data:
                st.session_state.user_data[field] = default

def change_page(page_name):
    """Change la page actuelle et force le rechargement."""
    # La solution la plus simple: stocker un flag pour dire à la nouvelle page de scroller en haut
    st.session_state.page = page_name
    st.session_state.scroll_to_top = True
    st.rerun()

# ----- INTÉGRATION HUBSPOT -----
def send_data_to_hubspot(user_data):
    """
    Envoie les données utilisateur à Hubspot via l'API.
    
    Args:
        user_data: Dictionnaire contenant les données de l'utilisateur
    
    Returns:
        bool: True si l'envoi est réussi, sinon lève une exception
    """
    try:
        # Récupérer la clé API depuis les secrets
        api_key = st.secrets["hubspot"]["api_key"]
        
        # Initialiser le client Hubspot avec token d'accès
        client = hubspot.Client.create(access_token=api_key)
        
        # Préparer les propriétés pour l'API Hubspot (UNIQUEMENT les informations de base)
        properties = {
            "firstname": user_data.get('prenom', ''),
            "lastname": user_data.get('nom', ''), 
            "email": user_data.get('email', ''),
            "phone": user_data.get('telephone', ''),
            "hs_marketable_status": True  # Opt-in est toujours à True car obligatoire
        }
        
        # NE PAS envoyer les tags ni le métier sélectionné à Hubspot
        
        # Rechercher si le contact existe déjà
        existing_contact = None
        try:
            # Utiliser l'API pour rechercher par email
            filter_groups = [{"filters": [{"propertyName": "email", "operator": "EQ", "value": user_data.get('email')}]}]
            public_object_search_request = {"filterGroups": filter_groups}
            contact_search_results = client.crm.contacts.search_api.do_search(public_object_search_request=public_object_search_request)
            
            # Vérifier s'il y a des résultats
            if contact_search_results.results and len(contact_search_results.results) > 0:
                existing_contact = contact_search_results.results[0]
        except Exception as search_error:
            # Si la recherche échoue, continuer pour créer un nouveau contact
            print(f"Erreur de recherche contact: {str(search_error)}")
            pass

        # Mettre à jour le contact existant ou en créer un nouveau
        if existing_contact:
            # Mettre à jour le contact existant
            contact_id = existing_contact.id
            simple_public_object_input = SimplePublicObjectInput(properties=properties)
            api_response = client.crm.contacts.basic_api.update(contact_id=contact_id, simple_public_object_input=simple_public_object_input)
            print(f"Contact mis à jour dans Hubspot: {contact_id}")
        else:
            # Créer un nouveau contact
            simple_public_object_input_for_create = SimplePublicObjectInputForCreate(properties=properties)
            api_response = client.crm.contacts.basic_api.create(simple_public_object_input_for_create=simple_public_object_input_for_create)
            print(f"Nouveau contact créé dans Hubspot: {api_response.id}")
        
        return True
    except Exception as e:
        # Journaliser l'erreur mais la remonter pour gestion
        print(f"Erreur lors de l'envoi des données à Hubspot: {str(e)}")
        raise e

# ----- GESTION DES DONNÉES -----
def load_data():
    """Charge les données depuis le fichier Excel."""
    if st.session_state.data_loaded:
        return st.session_state.data
    
    try:
        file_path = 'data/IED _ esg_calculator data.xlsx'
        
        # Charger toutes les feuilles directement avec leurs noms standardisés
        df_metiers = pd.read_excel(file_path, sheet_name='metier')
        df_salaire = pd.read_excel(file_path, sheet_name='salaire')
        df_competences = pd.read_excel(file_path, sheet_name='competences_cles')
        df_formations = pd.read_excel(file_path, sheet_name='formations_IED')
        df_tendances = pd.read_excel(file_path, sheet_name='tendances_marche')
        
        print("Colonnes disponibles dans la feuille métier:", df_metiers.columns.tolist())
        
        # Stocker les données dans l'état de la session
        st.session_state.data = {
            'salaire': df_salaire,
            'competences': df_competences,
            'metiers': df_metiers,
            'formations': df_formations,
            'tendances': df_tendances
        }
        st.session_state.data_loaded = True
        print("Toutes les données ont été chargées avec succès.")
        return st.session_state.data
    except Exception as e:
        print(f"Erreur critique lors du chargement des données: {str(e)}")
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return {
            'salaire': pd.DataFrame(),
            'competences': pd.DataFrame(),
            'metiers': pd.DataFrame(),
            'formations': pd.DataFrame(),
            'tendances': pd.DataFrame()
        }

def get_all_tags():
    """Récupère tous les tags disponibles depuis la feuille métier."""
    data = load_data()
    df_metiers = data.get('metiers', pd.DataFrame())
    
    # Vérifier si le DataFrame est vide
    if df_metiers.empty:
        print("La feuille métier est vide ou n'existe pas")
        # En cas d'échec, fournir une liste par défaut pour le MVP
        return ["Finance durable", "ESG", "Data/Analytics", "Reporting", "Conseil", "Investissement", 
                "Développement durable", "RSE", "Audit", "Conformité", "Risk Management"]
    
    # Vérifier si la colonne Tags existe
    if 'Tags' not in df_metiers.columns:
        print("Colonne 'Tags' non trouvée dans la feuille métier")
        return ["Finance durable", "ESG", "Data/Analytics", "Reporting", "Conseil", "Investissement", 
                "Développement durable", "RSE", "Audit", "Conformité", "Risk Management"]
    
    # Extraire et dédupliquer tous les tags
    all_tags = []
    for tags_str in df_metiers['Tags'].dropna():
        # Vérifier le type de données pour éviter les erreurs
        if isinstance(tags_str, str):
            tags = [tag.strip() for tag in tags_str.split(',')]
            all_tags.extend(tags)
    
    # Si aucun tag n'a été trouvé, utiliser des valeurs par défaut
    if not all_tags:
        print("Aucun tag trouvé dans les données, utilisation de valeurs par défaut")
        return ["Finance durable", "ESG", "Data/Analytics", "Reporting", "Conseil", "Investissement", 
                "Développement durable", "RSE", "Audit", "Conformité", "Risk Management"]
    
    # Retourner la liste unique triée
    return sorted(list(set(all_tags)))

def get_all_entreprises():
    """Récupère tous les types d'entreprises disponibles."""
    # Dans cette version MVP, nous fournissons une liste prédéfinie
    return [
        "Grandes entreprises", 
        "PME/ETI", 
        "Startups", 
        "Secteur public", 
        "ONG/Associations",
        "Cabinet de conseil"
    ]

def filter_metiers_by_tags(selected_tags):
    """Filtre les métiers selon les tags sélectionnés."""
    data = load_data()
    df_metiers = data.get('metiers', pd.DataFrame())
    df_salaire = data.get('salaire', pd.DataFrame())
    
    # Si les données métier sont vides ou si aucun tag n'est sélectionné, utiliser les données salaire comme fallback
    if df_metiers.empty or not selected_tags:
        if df_salaire.empty:
            # Aucune donnée disponible
            return []
        else:
            # Utiliser les données de salaire pour créer une liste de métiers avec minimum d'information
            print("Utilisation des données de salaire comme fallback pour les métiers")
            # Prendre jusqu'à 5 métiers de la table salaire
            fallback_metiers = []
            for i, (_, row) in enumerate(df_salaire.iterrows()):
                if i >= 5:  # Limiter à 5 métiers pour le fallback
                    break
                    
                metier_info = {
                    'Metier': row['Métier'],
                    'Secteur': row['Secteur'] if 'Secteur' in row else 'Non spécifié',
                    'Description': row.get('Description', 'Information non disponible'),
                    'Tags': [],
                    'match_score': 1  # Score arbitraire
                }
                fallback_metiers.append(metier_info)
            return fallback_metiers
    
    # Maintenant nous savons que la colonne Tags existe dans le fichier reformaté
    tag_column = 'Tags'
    
    # Filtrer les métiers qui contiennent au moins un des tags sélectionnés
    matching_metiers = []
    
    for _, row in df_metiers.iterrows():
        if pd.isna(row[tag_column]):
            continue
            
        # Vérifier que c'est bien une chaîne de caractères
        if not isinstance(row[tag_column], str):
            continue
            
        metier_tags = [tag.strip() for tag in row[tag_column].split(',')]
        
        # Vérifier si au moins un tag sélectionné est présent
        if any(tag in metier_tags for tag in selected_tags):
            # Calculer un score de correspondance (nombre de tags correspondants)
            match_score = sum(1 for tag in selected_tags if tag in metier_tags)
            
            # Récupérer les informations du métier
            # Chercher le secteur dans la table des salaires si disponible
            secteur = 'Non spécifié'
            if not df_salaire.empty:
                salaire_row = df_salaire[df_salaire['Métier'] == row['Métier']]
                if not salaire_row.empty and 'Secteur' in salaire_row.columns:
                    secteur = salaire_row['Secteur'].iloc[0]
            
            matching_metiers.append({
                'Metier': row['Métier'],
                'Secteur': secteur,  # Utiliser le secteur trouvé dans la table des salaires
                'Description': row.get('Description', 'Information non disponible'),
                'Tags': metier_tags,
                'match_score': match_score
            })
    
    # Si aucun métier ne correspond, utiliser quelques métiers par défaut de la table salaire
    if not matching_metiers and not df_salaire.empty:
        print("Aucun métier correspondant aux tags, utilisation de données de fallback")
        # Prendre jusqu'à 3 métiers de la table salaire
        for i, (_, row) in enumerate(df_salaire.iterrows()):
            if i >= 3:  # Limiter à 3 métiers pour le fallback
                break
                
            metier_info = {
                'Metier': row['Métier'],
                'Secteur': row['Secteur'] if 'Secteur' in row else 'Non spécifié',
                'Description': row.get('Description', f"Métier en rapport avec les thématiques: {', '.join(selected_tags)}"),
                'Tags': selected_tags,  # Associer les tags sélectionnés
                'match_score': 1  # Score arbitraire
            }
            matching_metiers.append(metier_info)
    
    # Trier par score de correspondance décroissant
    matching_metiers.sort(key=lambda x: x['match_score'], reverse=True)
    
    return matching_metiers

def get_metier_details(metier_nom):
    """Récupère toutes les informations pour un métier donné."""
    data = load_data()
    
    # Récupérer les informations de base du métier
    df_metiers = data.get('metiers', pd.DataFrame())
    metier_info = df_metiers[df_metiers['Métier'] == metier_nom].to_dict('records')
    
    if not metier_info:
        print(f"Aucune information de base trouvée pour le métier: {metier_nom}")
        # Créer une entrée minimale pour éviter de retourner None
        metier_data = {'Métier': metier_nom}
    else:
        metier_data = metier_info[0]
    
    # Ajouter les données salariales
    df_salaire = data.get('salaire', pd.DataFrame())
    salaire_info = df_salaire[df_salaire['Métier'] == metier_nom]
    
    if not salaire_info.empty:
        print(f"Données salariales trouvées pour {metier_nom}")
        # Récupérer la description du métier à partir de la feuille salaire
        if 'Description' in salaire_info.columns and not metier_data.get('Description'):
            desc = salaire_info['Description'].iloc[0]
            if pd.notna(desc) and desc:
                metier_data['Description'] = desc
        
        metier_data['salaire'] = salaire_info.to_dict('records')
    else:
        print(f"Aucune donnée salariale trouvée pour {metier_nom}")
    
    # Ajouter les compétences
    df_competences = data.get('competences', pd.DataFrame())
    competences_filtered = get_competences_par_metier(df_competences, metier_nom)
    
    if not competences_filtered.empty:
        print(f"Compétences trouvées pour {metier_nom}")
        metier_data['competences'] = competences_filtered.to_dict('records')
    else:
        print(f"Aucune compétence trouvée pour {metier_nom}")
    
    # Ajouter les formations
    df_formations = data.get('formations', pd.DataFrame())
    formations_filtered = get_formations_par_metier(df_formations, metier_nom)
    
    if not formations_filtered.empty:
        print(f"Formations trouvées pour {metier_nom}")
        metier_data['formations'] = formations_filtered.to_dict('records')
    else:
        print(f"Aucune formation trouvée pour {metier_nom}")
    
    # Ajouter les tendances du marché
    df_tendances = data.get('tendances', pd.DataFrame())
    # Imprimer les colonnes du DataFrame pour débogage
    print(f"Colonnes dans df_tendances: {df_tendances.columns.tolist()}")
    print(f"Valeurs uniques de métiers dans df_tendances: {df_tendances['Métier'].unique().tolist() if 'Métier' in df_tendances.columns else 'Aucune colonne Métier'}")
    
    tendances_filtered = df_tendances[df_tendances['Métier'] == metier_nom]
    
    if not tendances_filtered.empty:
        print(f"Tendances trouvées pour {metier_nom}")
        metier_data['tendances'] = tendances_filtered.to_dict('records')
    else:
        print(f"Aucune tendance trouvée pour {metier_nom}")
    
    # Convertir les types de données à des formes sérialisables si nécessaire
    for key, value in metier_data.items():
        if isinstance(value, pd.Series):
            metier_data[key] = value.to_dict()
        elif isinstance(value, np.ndarray):
            metier_data[key] = value.tolist()
        elif isinstance(value, np.integer):
            metier_data[key] = int(value)
        elif isinstance(value, np.floating):
            metier_data[key] = float(value)
    
    return metier_data

def get_competences_par_metier(df_competences, metier):
    """Retourne les compétences pour un métier donné."""
    if df_competences.empty or 'Métier' not in df_competences.columns:
        return pd.DataFrame()
    
    # Filtrer pour le métier spécifique
    df_filtered = df_competences[df_competences['Métier'] == metier]
    
    if df_filtered.empty:
        return pd.DataFrame()
    
    # Chercher toutes les colonnes potentielles de compétences avec différentes orthographes possibles
    competence_patterns = ['Compétence', 'Competence', 'compétence', 'competence']
    
    # Récupérer toutes les colonnes qui pourraient contenir des compétences
    competence_cols = []
    for pattern in competence_patterns:
        # Chercher les colonnes qui commencent par ce motif
        pattern_cols = [col for col in df_filtered.columns if str(col).startswith(pattern)]
        competence_cols.extend(pattern_cols)
    
    # Supprimer les doublons
    competence_cols = list(set(competence_cols))
    
    # Si aucune colonne de compétences trouvée, essayer de trouver des colonnes numériques (Compétence1, Compétence2...)
    if not competence_cols:
        # Essayer de trouver des colonnes qui contiennent des chiffres et qui pourraient être des compétences
        competence_cols = [col for col in df_filtered.columns if any(p in str(col) for p in competence_patterns) or 
                          (any(c.isdigit() for c in str(col)) and len(str(col)) <= 15)]
    
    # Trier les colonnes pour avoir un ordre cohérent
    competence_cols.sort()
    
    print(f"Colonnes de compétences trouvées: {competence_cols}")
    
    if competence_cols:
        # Créer un nouveau DataFrame pour stocker les compétences
        competences_list = []
        
        for _, row in df_filtered.iterrows():
            # Pour chaque colonne de compétence, créer une ligne
            for i, col in enumerate(competence_cols, 1):
                if pd.notna(row[col]) and row[col]:
                    competence_entry = {
                        'Compétence': row[col],
                        'Importance': 6-min(i, 5)  # Importance décroissante basée sur l'ordre (max 5)
                    }
                    competences_list.append(competence_entry)
        
        # Créer un DataFrame à partir de la liste
        if competences_list:
            return pd.DataFrame(competences_list).sort_values(by='Importance', ascending=False)
    
    # Si aucun format ne correspond, retourner un DataFrame vide
    return pd.DataFrame(columns=['Compétence', 'Importance'])

def get_formations_par_metier(df_formations, metier):
    """Retourne les formations recommandées pour un métier donné."""
    if df_formations.empty or 'Métier' not in df_formations.columns:
        return pd.DataFrame()
    
    # Filtrer pour le métier spécifique
    df_filtered = df_formations[df_formations['Métier'] == metier]
    
    if df_filtered.empty:
        return pd.DataFrame()
    
    # Créer une copie explicite du DataFrame pour éviter les SettingWithCopyWarning
    df_result = df_filtered.copy()
    
    # Ajouter une colonne Formation si elle n'existe pas déjà
    if 'Formation' not in df_result.columns:
        # Utiliser Programme_Principal comme Formation si disponible
        if 'Programme_Principal' in df_result.columns:
            df_result['Formation'] = df_result['Programme_Principal']
    
    # Ajouter d'autres colonnes nécessaires pour l'affichage
    if 'Description' not in df_result.columns and 'Modules_Clés' in df_result.columns:
        df_result['Description'] = df_result['Modules_Clés']
    
    if 'Durée' not in df_result.columns and 'Durée_Formation' in df_result.columns:
        df_result['Durée'] = df_result['Durée_Formation']
        
    if 'Niveau' not in df_result.columns and 'Prérequis' in df_result.columns:
        df_result['Niveau'] = df_result['Prérequis']
    
    return df_result

# ----- VISUALISATIONS -----
def create_salary_chart(df_filtered, small_version=False):
    """Crée un graphique d'évolution salariale.
    
    Args:
        df_filtered: DataFrame des données filtrées
        small_version: Si True, crée une version plus petite pour l'aperçu
    """
    colors = st.session_state.colors
    
    # Vérifier et normaliser les colonnes obligatoires (avec ou sans accent)
    column_mapping = {
        'Expérience': ['Expérience', 'Experience'],
        'Salaire_Min': ['Salaire_Min', 'Salaire_min'],
        'Salaire_Max': ['Salaire_Max', 'Salaire_max'],
        'Salaire_Moyen': ['Salaire_Moyen', 'Salaire_moyen']
    }
    
    # Normaliser les colonnes du DataFrame
    for expected_col, possible_cols in column_mapping.items():
        for actual_col in possible_cols:
            if actual_col in df_filtered.columns and expected_col != actual_col:
                df_filtered.rename(columns={actual_col: expected_col}, inplace=True)
    
    # Vérifier les colonnes après normalisation
    required_columns = ['Expérience', 'Salaire_Min', 'Salaire_Max', 'Salaire_Moyen']
    missing_columns = [col for col in required_columns if col not in df_filtered.columns]
    
    if missing_columns:
        # Colonnes manquantes - créer un graphique simple avec message d'erreur
        fig, ax = plt.subplots(figsize=(7, 4) if not small_version else (3.5, 2.5))
        ax.text(0.5, 0.5, f"Données salariales incomplètes\nColonnes manquantes: {', '.join(missing_columns)}", 
                ha='center', va='center', transform=ax.transAxes, fontsize=12)
        ax.set_axis_off()
        return fig
    
    # Choisir la taille en fonction du contexte
    if small_version:
        # Version compact pour l'aperçu
        fig, ax = plt.subplots(figsize=(3.5, 2.5))
    else:
        # Version normale pour les résultats détaillés
        fig, ax = plt.subplots(figsize=(7, 4))
    
    # Créer des données pour le graphique
    experience = df_filtered['Expérience'].tolist()
    min_salary = df_filtered['Salaire_Min'].tolist()
    max_salary = df_filtered['Salaire_Max'].tolist()
    avg_salary = df_filtered['Salaire_Moyen'].tolist()
    
    # Tracer les lignes et l'aire entre min et max
    x = range(len(experience))
    ax.plot(x, avg_salary, marker='o', linestyle='-', color=colors['primary'], linewidth=2, label='Salaire moyen')
    ax.fill_between(x, min_salary, max_salary, alpha=0.2, color=colors['primary'], label='Fourchette salariale')
    
    # Personnaliser le graphique
    ax.set_ylabel('Salaire annuel brut (€)', fontsize=10)
    ax.set_xlabel('Expérience', fontsize=10)
    ax.set_xticks(x)
    ax.set_xticklabels(experience, fontsize=8)
    ax.grid(True, linestyle='--', alpha=0.7)
    
    # Réduire la taille de la légende si version compacte
    if small_version:
        ax.legend(fontsize=7, loc='upper left')
    else:
        ax.legend(fontsize=8)
    
    # Ajouter les valeurs
    for i, avg_val in enumerate(avg_salary):
        font_size = 7 if small_version else 8
        y_offset = 8 if small_version else 10
        ax.annotate(f"{avg_val}€", (i, avg_val), textcoords="offset points", 
                    xytext=(0, y_offset), ha='center', fontweight='bold', fontsize=font_size)
    
    plt.tight_layout()
    return fig

# ----- COMPOSANTS D'INTERFACE -----
def display_header():
    """Affiche l'en-tête avec le logo."""
    col1, col2 = st.columns([1, 5])
    
    with col1:
        # Afficher le logo IED
        st.image("assets/logo_ied_low.png", width=150)
    
    with col2:
        st.markdown("<h1>Calculateur de Carrière ESG</h1>", unsafe_allow_html=True)

def display_contact_form():
    """Affiche un formulaire de contact pour collecte des informations."""
    st.markdown("### Pour accéder à l'analyse détaillée")
    st.markdown("Recevez gratuitement votre analyse personnalisée et des informations sur nos formations.")
    
    with st.form(key="contact_form"):
        col1, col2 = st.columns(2)
        with col1:
            prenom = st.text_input("Prénom*", value=st.session_state.user_data.get('prenom', ''))
            email = st.text_input("Email professionnel*", value=st.session_state.user_data.get('email', ''), 
                                placeholder="nom@entreprise.com")
        with col2:
            nom = st.text_input("Nom*", value=st.session_state.user_data.get('nom', ''))
            telephone = st.text_input("Téléphone*", value=st.session_state.user_data.get('telephone', ''), 
                                     placeholder="06XXXXXXXX")
        
        opt_in = st.checkbox("J'accepte de recevoir des informations de l'Institut d'Économie Durable", 
                            value=st.session_state.user_data.get('opt_in', True))
        
        st.markdown("*Champs obligatoires")
        
        submit = st.form_submit_button("Recevoir mon analyse détaillée", use_container_width=True)
        
        if submit:
            errors = []
            
            # Validation basique
            if not prenom:
                errors.append("Veuillez entrer votre prénom.")
            if not nom:
                errors.append("Veuillez entrer votre nom.")
            if not email or "@" not in email or "." not in email:
                errors.append("Veuillez entrer une adresse email valide.")
            if not telephone or len(''.join(c for c in telephone if c.isdigit())) < 10:
                errors.append("Veuillez entrer un numéro de téléphone valide (minimum 10 chiffres).")
            
            if errors:
                for error in errors:
                    st.error(error)
                return False
            
            # Enregistrer les coordonnées
            st.session_state.user_data.update({
                'prenom': prenom,
                'nom': nom,
                'email': email,
                'telephone': telephone,
                'opt_in': opt_in
            })
            
            # Envoyer les données à Hubspot
            try:
                send_data_to_hubspot(st.session_state.user_data)
                # Marquer comme soumis pour éviter les doublons
                st.session_state.user_data['hubspot_submitted'] = True
                st.session_state.email_submitted = True
                
                # Message de succès et redirection
                st.success("Vos informations ont été enregistrées avec succès.")
                
                # Changer de page (doit être fait après le context du formulaire)
                st.session_state.scroll_to_top = True  # Activer le défilement vers le haut
                st.rerun()
                return True
            except ApiException as e:
                # Traitement spécifique des erreurs d'API Hubspot
                if "email provided is invalid" in str(e).lower():
                    st.error("L'adresse email fournie n'est pas valide. Veuillez entrer une adresse email professionnelle correcte.")
                elif "rate limit" in str(e).lower():
                    st.error("Trop de requêtes en cours. Veuillez réessayer dans quelques instants.")
                else:
                    st.error(f"Erreur de validation des données: {str(e)}")
                print(f"Erreur Hubspot API: {str(e)}")
                return False
            except Exception as e:
                # Gestion des autres types d'erreurs
                st.error("Une erreur est survenue lors de l'enregistrement de vos données. Veuillez vérifier vos informations.")
                print(f"Erreur Hubspot générale: {str(e)}")
                return False
    
    return False

# Fonctions de sélection simplifiées - utilisons désormais directement les composants natifs

# ----- PAGES DE L'APPLICATION -----
def page_accueil():
    """Affiche la page d'accueil avec entrée immédiate dans l'expérience."""
    display_header()
    
    # Introduction avec mise en valeur
    st.markdown("""
    <div class='highlight-box'>
    <h2 style='text-align: center; margin-bottom: 20px;'>Découvrez les métiers ESG qui correspondent à vos intérêts</h2>
    <p style='text-align: center; font-size: 1.2em;'>Trouvez votre voie professionnelle dans l'économie durable en quelques clics</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Chiffres clés en colonnes
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='text-align: center'>🚀 +20%</h3>
        <p style='text-align: center'>Croissance annuelle des métiers ESG</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='text-align: center'>💼 +300</h3>
        <p style='text-align: center'>Métiers en développement</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col3:
        st.markdown("""
        <div class='feature-card'>
        <h3 style='text-align: center'>💰 50-120k€</h3>
        <p style='text-align: center'>Fourchette salariale</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Bouton d'action pour commencer
    st.markdown("<div style='padding: 20px;'></div>", unsafe_allow_html=True)
    
    if st.button("Commencer", use_container_width=True, type="primary"):
        change_page("interests")

def page_interests():
    """Affiche la page de sélection des intérêts."""
    display_header()
    
    # Titre principal avec style amélioré
    st.markdown("""
    <div style='padding: 20px; background-color: white; border-radius: 10px; margin-bottom: 20px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
        <h2 style='text-align: center; color: #0356A5;'>Découvrez les métiers ESG qui correspondent à votre profil</h2>
        <p style='text-align: center; font-size: 1.1em;'>Quelques clics pour trouver votre voie dans l'économie durable</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Charger les données
    tags = get_all_tags()
    entreprises = get_all_entreprises()
    
    # Récupérer et initialiser les sélections existantes dans la session state
    if 'selected_tags' not in st.session_state:
        st.session_state.selected_tags = []
    
    # 1. Section objectif professionnel
    st.markdown("""
    <div style='padding: 15px 20px; background-color: #e6f7f2; border-left: 4px solid #00916E; border-radius: 5px; margin-bottom: 25px;'>
        <h3 style='color: #00916E;'>Votre objectif professionnel</h3>
        <p>Quelle est votre situation actuelle ?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Options d'objectif professionnel avec radio buttons
    objectifs = [
        "Débuter ma carrière", 
        "Évoluer dans mon secteur actuel", 
        "Me reconvertir complètement",
        "Explorer de nouvelles opportunités",
        "Autre"
    ]
    
    # Stocker l'objectif sélectionné temporairement (pas sauvegardé dans user_data)
    selected_objectif = st.radio(
        label="Sélectionnez votre objectif",
        options=objectifs,
        horizontal=False,
        label_visibility="collapsed"
    )
    
    # Séparateur visuel entre les sections
    st.markdown("<hr style='margin: 30px 0; border: none; height: 1px; background-color: #ddd;'>", unsafe_allow_html=True)
    
    # 2. Section domaines d'intérêt - présentation simple et efficace
    st.markdown("""
    <div style='padding: 15px 20px; background-color: #f0f7ff; border-left: 4px solid #0356A5; border-radius: 5px; margin-bottom: 15px;'>
        <h3 style='color: #0356A5;'>Vos domaines d'intérêt</h3>
        <p>Sélectionnez les domaines qui vous intéressent :</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Créer des colonnes pour organiser les checkboxes
    col1, col2, col3 = st.columns(3)
    
    # Distribuer les tags de manière équilibrée entre les colonnes
    tags_per_column = (len(tags) + 2) // 3
    
    # Afficher les checkboxes dans chaque colonne
    for i, col in enumerate([col1, col2, col3]):
        start_idx = i * tags_per_column
        end_idx = min(start_idx + tags_per_column, len(tags))
        
        with col:
            for tag in tags[start_idx:end_idx]:
                # Vérifier si ce tag est déjà sélectionné
                is_selected = tag in st.session_state.selected_tags
                
                # Checkbox avec style amélioré
                if st.checkbox(tag, value=is_selected, key=f"tag_{tag}"):
                    if tag not in st.session_state.selected_tags:
                        st.session_state.selected_tags.append(tag)
                else:
                    if tag in st.session_state.selected_tags:
                        st.session_state.selected_tags.remove(tag)
    
    # Afficher un résumé des tags sélectionnés pour un feedback clair
    if st.session_state.selected_tags:
        st.markdown(f"""
        <div style='padding: 12px 18px; background-color: #eef7ff; border-radius: 8px; margin: 15px 0; border: 1px solid #0356A5;'>
            <p><strong>🔍 Domaines sélectionnés ({len(st.session_state.selected_tags)}) :</strong> {', '.join(st.session_state.selected_tags)}</p>
        </div>
        """, unsafe_allow_html=True)
    
    # Séparateur visuel entre les sections
    st.markdown("<hr style='margin: 30px 0; border: none; height: 1px; background-color: #ddd;'>", unsafe_allow_html=True)
    
    # 3. Section types d'entreprises - avec multiselect au lieu de toggles
    st.markdown("""
    <div style='padding: 15px 20px; background-color: #fffaf0; border-left: 4px solid #FFE548; border-radius: 5px; margin-bottom: 15px;'>
        <h3 style='color: #333;'>Types d'entreprises</h3>
        <p>Sélectionnez les types d'entreprises qui vous intéressent :</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Utiliser un multiselect pour une meilleure expérience utilisateur
    selected_entreprises = st.multiselect(
        label="Choisissez un ou plusieurs types d'entreprises",
        options=entreprises,
        default=[],
        label_visibility="collapsed"
    )
    
    # Espacement avant les boutons d'action
    st.markdown("<div style='padding: 20px;'></div>", unsafe_allow_html=True)
    
    # Bouton d'action principal avec style amélioré
    st.markdown("""
    <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); text-align: center;'>
        <p style='font-weight: bold; font-size: 1.1em;'>Prêt à découvrir les métiers qui correspondent à votre profil ?</p>
    </div>
    """, unsafe_allow_html=True)
    
    # Boutons de navigation améliorés
    col1, col2 = st.columns([1, 3])
    
    with col1:
        if st.button("← Retour", use_container_width=True):
            change_page("accueil")
    
    with col2:
        if st.button("Découvrir mes métiers →", use_container_width=True, type="primary"):
            if st.session_state.selected_tags:
                # Sauvegarder les tags sélectionnés dans les données utilisateur
                st.session_state.user_data['tags'] = st.session_state.selected_tags
                
                # Exécuter la recherche des métiers correspondants
                metiers_matches = filter_metiers_by_tags(st.session_state.selected_tags)
                st.session_state.user_data['metiers_matches'] = metiers_matches
                
                # Aller à la page de résultats
                change_page("resultats")
            else:
                st.error("Veuillez sélectionner au moins un domaine d'intérêt pour continuer.")

def page_resultats():
    """Affiche la page des résultats avec les métiers correspondants."""
    display_header()
    
    # Récupérer les métiers correspondants aux tags sélectionnés
    if not st.session_state.user_data.get('metiers_matches'):
        # Si pas de résultats, exécuter la recherche
        selected_tags = st.session_state.selected_tags
        if not selected_tags:
            st.warning("Veuillez d'abord sélectionner vos domaines d'intérêt.")
            change_page("interests")
            return
            
        metiers_matches = filter_metiers_by_tags(selected_tags)
        st.session_state.user_data['metiers_matches'] = metiers_matches
    else:
        # Utiliser les résultats existants
        metiers_matches = st.session_state.user_data.get('metiers_matches')
    
    # Afficher les résultats
    if not metiers_matches:
        st.warning("Aucun métier ne correspond à vos critères de recherche.")
        if st.button("Modifier mes critères"):
            change_page("interests")
        return
    
    # En-tête de la page
    st.markdown("""
    <div class='highlight-box'>
    <h2 style='text-align: center;'>Voici les métiers ESG qui vous correspondent</h2>
    </div>
    """, unsafe_allow_html=True)
    
    # Afficher le nombre de métiers trouvés
    st.markdown(f"### Top 3 des métiers ESG basés sur vos intérêts")
    st.markdown(f"**Vos domaines sélectionnés :** *{', '.join(st.session_state.selected_tags)}*")
    
    # Afficher les 3 premiers métiers
    top_metiers = metiers_matches[:3]
    
    # Utiliser des colonnes pour une meilleure présentation sur grand écran
    cols = st.columns(min(len(top_metiers), 3))
    
    for i, metier in enumerate(top_metiers):
        metier_nom = metier['Metier']
        secteur = metier.get('Secteur', 'Non spécifié')
        description = metier.get('Description', 'Information non disponible')
        
        # Enrichir les données si nécessaire
        if secteur == 'Non spécifié':
            # Tenter de trouver le secteur dans les données de salaire
            data = load_data()
            df_salaire = data.get('salaire', pd.DataFrame())
            if not df_salaire.empty:
                secteur_info = df_salaire[df_salaire['Métier'] == metier_nom]
                if not secteur_info.empty and 'Secteur' in secteur_info.columns:
                    secteur = secteur_info['Secteur'].iloc[0]
        
        # Faire un log pour le débogage
        print(f"Affichage du métier: {metier_nom}, Secteur: {secteur}")
        
        with cols[i]:
            # Utiliser une carte pour chaque métier sans description
            st.markdown(f"""
            <div class='metier-card'>
                <h3>{metier_nom}</h3>
                <p><strong>Secteur :</strong> {secteur}</p>
            </div>
            """, unsafe_allow_html=True)
            
            # Bouton pour voir les détails du métier (solution native Streamlit)
            if st.button(f"Voir détails", key=f"detail_{i}"):
                st.session_state.user_data['metier_selectionne'] = metier_nom
                # Si déjà soumis, aller directement aux détails, sinon au formulaire
                if st.session_state.email_submitted:
                    change_page("metier_detail")
                else:
                    change_page("contact")
    
    # Formulaire de contact intégré
    st.markdown("---")
    st.markdown("### Accédez à l'analyse détaillée de ces métiers")
    
    if not st.session_state.email_submitted:
        display_contact_form()
    else:
        if st.button("Voir l'analyse détaillée", type="primary", use_container_width=True):
            # Aller directement à la page détaillée du métier sélectionné
            if st.session_state.user_data.get('metier_selectionne'):
                change_page("metier_detail")
            else:
                # Sélectionner le premier métier par défaut
                st.session_state.user_data['metier_selectionne'] = top_metiers[0]['Metier']
                change_page("metier_detail")
    
    # Option pour modifier les intérêts
    if st.button("Modifier mes centres d'intérêt"):
        change_page("interests")

def page_contact():
    """Page dédiée au formulaire de contact."""
    display_header()
    
    # Afficher les informations sur le métier sélectionné
    metier_selectionne = st.session_state.user_data.get('metier_selectionne', '')
    
    if metier_selectionne:
        st.markdown(f"## Analyse détaillée : {metier_selectionne}")
        st.markdown("Pour accéder à l'analyse complète et recevoir des informations personnalisées sur ce métier, veuillez compléter le formulaire ci-dessous.")
    else:
        st.markdown("## Analyse détaillée des métiers ESG")
        st.markdown("Pour accéder à l'analyse complète des métiers correspondant à vos intérêts, veuillez compléter le formulaire ci-dessous.")
    
    # Afficher le formulaire de contact
    if not st.session_state.email_submitted:
        if display_contact_form():
            # Si le formulaire est soumis avec succès, passer à la page détaillée
            change_page("metier_detail")
    else:
        # Si l'utilisateur a déjà soumis ses coordonnées, rediriger directement
        change_page("metier_detail")
    
    # Option pour revenir aux résultats
    if st.button("Retour aux résultats"):
        change_page("resultats")

def page_metier_detail():
    """Affiche la page détaillée d'un métier."""
    display_header()
    
    # Vérifier que les coordonnées ont été soumises
    if not st.session_state.email_submitted:
        st.warning("Veuillez d'abord fournir vos coordonnées.")
        change_page("contact")
        return
    
    # Récupérer le métier sélectionné
    metier_nom = st.session_state.user_data.get('metier_selectionne', '')
    
    if not metier_nom:
        st.warning("Aucun métier sélectionné.")
        change_page("resultats")
        return
    
    # Récupérer les détails du métier
    metier_details = get_metier_details(metier_nom)
    
    if not metier_details:
        st.warning(f"Données non disponibles pour le métier : {metier_nom}")
        if st.button("Retour aux résultats"):
            change_page("resultats")
        return
        
    # Pour le débogage des données disponibles
    # Décommenter cette ligne pour voir les clés disponibles dans metier_details
    # st.write("Données disponibles:", list(metier_details.keys()))
    
    # Afficher les détails du métier
    st.markdown(f"# {metier_nom}")
    
    # Secteur
    if 'Secteur' in metier_details:
        st.caption(f"Secteur: **{metier_details['Secteur']}**")
    
    st.divider()
    
    # Description du métier
    st.markdown("## 📋 Description du métier")
    if 'Description' in metier_details and metier_details['Description']:
        st.markdown(metier_details['Description'])
    else:
        st.info(f"Aucune description disponible pour le métier de {metier_nom}.")
    
    st.divider()
    
    # Salaires
    st.markdown("## 💰 Perspectives salariales")
    if 'salaire' in metier_details and metier_details['salaire']:
        # S'assurer que nous avons des données salariales valides
        try:
            # Convertir en DataFrame
            salaire_data = pd.DataFrame(metier_details['salaire'])
            
            # Afficher ce que nous avons comme données salariales pour le débogage
            print(f"Colonnes des données salariales: {salaire_data.columns.tolist()}")
            
            # Vérifier si les colonnes essentielles existent (avec ou sans accent)
            # Mapping des colonnes possibles (avec et sans accent)
            column_mapping = {
                'Expérience': ['Expérience', 'Experience'],
                'Salaire_Min': ['Salaire_Min', 'Salaire_min'],
                'Salaire_Max': ['Salaire_Max', 'Salaire_max'],
                'Salaire_Moyen': ['Salaire_Moyen', 'Salaire_moyen']
            }
            
            # Normaliser les colonnes du DataFrame (renommer pour correspondre à ce que le code attend)
            for expected_col, possible_cols in column_mapping.items():
                for actual_col in possible_cols:
                    if actual_col in salaire_data.columns and expected_col != actual_col:
                        salaire_data.rename(columns={actual_col: expected_col}, inplace=True)
            
            # Vérifier maintenant si les colonnes attendues existent
            salary_columns = ['Expérience', 'Salaire_Min', 'Salaire_Max', 'Salaire_Moyen']
            has_salary_columns = all(col in salaire_data.columns for col in salary_columns)
            
            if not has_salary_columns:
                print(f"Colonnes manquantes dans les données salariales")
                st.info("Données salariales complètes non disponibles pour ce métier.")
                
                # Afficher quand même les données disponibles dans une table simple
                st.dataframe(salaire_data, hide_index=True, use_container_width=True)
            else:
                # Si nous avons toutes les colonnes, afficher le graphique et la table
                col1, col2 = st.columns([3, 2])
                
                with col1:
                    # Graphique des salaires
                    fig_salary = create_salary_chart(salaire_data, small_version=False)
                    st.pyplot(fig_salary)
                
                with col2:
                    # Afficher un tableau de salaires avec mise en forme
                    st.markdown("### Détail des salaires")
                    
                    # Créer un dictionnaire pour renommer les colonnes
                    rename_dict = {
                        'Salaire_Min': 'Minimum (€)',
                        'Salaire_Max': 'Maximum (€)',
                        'Salaire_Moyen': 'Moyen (€)'
                    }
                    
                    # Afficher les colonnes disponibles
                    st.dataframe(
                        salaire_data[salary_columns].rename(columns=rename_dict),
                        hide_index=True,
                        use_container_width=True
                    )
                    
                    # Ajouter les informations de croissance si disponibles
                    if 'Croissance_Salaire' in salaire_data.columns:
                        croissance = salaire_data['Croissance_Salaire'].iloc[0]
                        if pd.notna(croissance):
                            st.metric("Croissance annuelle moyenne", f"{croissance}%")
        
        except Exception as e:
            # En cas d'erreur, afficher un message informatif
            st.info("Impossible d'afficher les données salariales détaillées")
            print(f"Erreur lors de l'affichage des salaires: {str(e)}")
    else:
        # Aucune donnée salariale disponible
        st.info("Aucune information salariale disponible pour ce métier.")
    
    st.divider()
    
    # Compétences clés
    st.markdown("## 🔑 Compétences clés")
    if 'competences' in metier_details and metier_details['competences']:
        # Utiliser des colonnes pour organiser les compétences
        competences_cols = st.columns(2)
        
        # Préparer la liste complète des compétences
        competences_list = sorted(metier_details['competences'], key=lambda x: x['Importance'], reverse=True)
        
        # Utiliser une boucle pour ajouter les compétences aux colonnes
        for i, comp in enumerate(competences_list):
            col_index = i % 2  # Alterner entre les deux colonnes
            with competences_cols[col_index]:
                importance = comp['Importance']
                emoji = "🔴" if importance >= 4 else "🟠" if importance >= 2 else "🟡"
                st.markdown(f"{emoji} **{comp['Compétence']}**")
    else:
        st.info("Aucune information sur les compétences n'est disponible pour ce métier.")
    
    st.divider()
    
    # Formations recommandées
    st.markdown("## 🎓 Formations recommandées")
    if 'formations' in metier_details and metier_details['formations']:
        # Créer un conteneur pour les formations
        formations_container = st.container()
        
        with formations_container:
            st.markdown("Formations recommandées par l'Institut pour développer vos compétences dans ce métier :")
            # Afficher chaque formation dans un expander avec détails et style amélioré
            for i, formation in enumerate(metier_details['formations']):
                formation_name = formation.get('Formation', f"Formation {i+1}")
                with st.expander(formation_name):
                    # Afficher les détails de la formation avec une présentation améliorée
                    col1, col2 = st.columns([3, 2])
                    
                    with col1:
                        if 'Description' in formation and formation['Description']:
                            st.markdown(formation['Description'])
                        else:
                            st.markdown("*Description non disponible*")
                    
                    with col2:
                        # Créer un bloc d'informations clés avec badges colorés
                        info_html = ""
                        
                        if 'Durée' in formation and formation['Durée']:
                            info_html += f"<div style='margin-bottom:10px;'><span style='background-color:{st.session_state.colors['primary']}; color:white; padding:3px 8px; border-radius:10px; font-size:0.8em;'>⏱️ {formation['Durée']}</span></div>"
                        
                        if 'Niveau' in formation and formation['Niveau']:
                            info_html += f"<div style='margin-bottom:10px;'><span style='background-color:{st.session_state.colors['green']}; color:white; padding:3px 8px; border-radius:10px; font-size:0.8em;'>🎯 Niveau {formation['Niveau']}</span></div>"
                        
                        if 'Prix' in formation and formation['Prix']:
                            info_html += f"<div style='margin-bottom:10px;'><span style='background-color:{st.session_state.colors['secondary']}; color:#333; padding:3px 8px; border-radius:10px; font-size:0.8em;'>💰 {formation['Prix']}€</span></div>"
                        
                        st.markdown(info_html, unsafe_allow_html=True)
                        
                        if 'Lien' in formation and formation['Lien']:
                            st.markdown(f"<a href='{formation['Lien']}' target='_blank' style='display:inline-block; margin-top:10px; background-color:{st.session_state.colors['primary']}; color:white; padding:5px 15px; border-radius:5px; text-decoration:none; font-size:0.9em;'>En savoir plus</a>", unsafe_allow_html=True)
    else:
        st.info("Aucune formation spécifique n'est disponible pour ce métier.")
        st.markdown("""
        L'Institut d'Économie Durable propose néanmoins plusieurs formations généralistes 
        qui peuvent vous aider à développer vos compétences dans le domaine ESG.
        """)
    
    # Tendances du marché
    if 'tendances' in metier_details and metier_details['tendances']:
        st.divider()
        st.markdown("## 📈 Tendances du marché")
        
        tendances = metier_details['tendances'][0]
        
        # Créer un affichage plus visuel avec une mise en page en colonnes
        col1, col2 = st.columns([2, 3])
        
        with col1:
            # Croissance annuelle avec indicateur visuel
            if 'Croissance_Annuelle' in tendances:
                tendance = tendances['Croissance_Annuelle']
                if pd.notna(tendance):
                    # Déterminer l'émoji selon la tendance
                    tendance_str = str(tendance).lower()
                    tendance_emoji = "🚀" if "hausse" in tendance_str or "forte" in tendance_str or "+" in tendance_str else "📈" if "croissance" in tendance_str or "positive" in tendance_str else "➡️" if "stable" in tendance_str else "📉" if "baisse" in tendance_str or "déclin" in tendance_str or "-" in tendance_str else "📊"
                    
                    # Créer un style visuel pour la tendance
                    tendance_color = f"{st.session_state.colors['green']}" if "hausse" in tendance_str or "croissance" in tendance_str or "positive" in tendance_str or "+" in tendance_str else f"{st.session_state.colors['primary']}" if "stable" in tendance_str else "#e74c3c"
                    
                    st.markdown(f"""
                    <div style='background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05);'>
                        <h4 style='margin-top: 0; color: {tendance_color};'>{tendance_emoji} Croissance annuelle</h4>
                        <p style='font-size: 1.1em;'>{tendance}</p>
                    </div>
                    """, unsafe_allow_html=True)
            
            # Ajouter demande marché comme métrique supplémentaire
            if 'Demande_Marché' in tendances:
                demande = tendances['Demande_Marché']
                if pd.notna(demande):
                    st.markdown(f"""
                    <div style='background-color: white; padding: 15px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); margin-top: 15px;'>
                        <h4 style='margin-top: 0;'>🔍 Demande du marché</h4>
                        <p style='font-size: 1.1em;'>{demande}</p>
                    </div>
                    """, unsafe_allow_html=True)
        
        with col2:
            # Tendance salariale et secteurs recruteurs dans un bloc
            tendance_salariale = ""
            if 'Salaire_Tendance' in tendances:
                sal_tendance = tendances['Salaire_Tendance']
                if pd.notna(sal_tendance):
                    tendance_salariale = f"<p><strong>💰 Tendance salariale:</strong> {sal_tendance}</p>"
            
            secteurs_recruteurs = ""
            if 'Secteurs_Recruteurs' in tendances:
                secteurs = tendances['Secteurs_Recruteurs']
                if pd.notna(secteurs):
                    secteurs_recruteurs = f"<p><strong>🏢 Principaux secteurs recruteurs:</strong> {secteurs}</p>"
            
            # Afficher le bloc combiné s'il contient des données
            if tendance_salariale or secteurs_recruteurs:
                st.markdown(f"""
                <div style='background-color: white; padding: 20px; border-radius: 10px; box-shadow: 0 2px 5px rgba(0,0,0,0.05); height: 100%;'>
                    <h4 style='margin-top: 0;'>🔮 Perspectives d'évolution</h4>
                    {tendance_salariale}
                    {secteurs_recruteurs}
                </div>
                """, unsafe_allow_html=True)
    
    # Navigation
    st.divider()
    
    # Option pour voir d'autres métiers
    col1, col2 = st.columns(2)
    with col1:
        if st.button("Retour aux résultats", use_container_width=True):
            change_page("resultats")
    with col2:
        if st.button("Modifier mes centres d'intérêt", use_container_width=True):
            change_page("interests")
    
    # CTA finale
    st.markdown("### Vous souhaitez en savoir plus ?")
    st.markdown("""
    L'Institut d'Économie Durable propose des formations adaptées pour développer votre carrière ESG.
    Notre équipe vous contactera prochainement pour vous présenter nos programmes.
    """)

# ----- FONCTION PRINCIPALE -----
def main():
    """Fonction principale de l'application."""
    # Configurer l'application
    configure_app()
    
    # Initialiser l'état de la session
    initialize_session_state()
    
    # Afficher la page correspondante à l'état actuel
    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "interests":
        page_interests()
    elif st.session_state.page == "resultats":
        page_resultats()
    elif st.session_state.page == "contact":
        page_contact()
    elif st.session_state.page == "metier_detail":
        page_metier_detail()
    else:
        # Page par défaut
        page_accueil()

# ----- POINT D'ENTRÉE -----
if __name__ == "__main__":
    main()