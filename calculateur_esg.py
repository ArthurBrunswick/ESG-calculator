"""
Calculateur de Carrière ESG Simplifié - Institut d'Économie Durable
Application Streamlit minimaliste pour l'exploration des carrières ESG
"""

import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt

# ----- CONFIGURATION DE L'APPLICATION -----
def configure_app():
    """Configure l'application Streamlit avec les paramètres de base."""
    st.set_page_config(
        page_title="Calculateur ESG - Institut d'Économie Durable",
        page_icon="🌱",
        layout="wide"
    )
    
    # Définition des couleurs
    st.session_state.setdefault('colors', {
        'primary': "#0356A5",     # Bleu foncé
        'secondary': "#FFE548",   # Jaune
        'green': "#00916E",       # Vert
        'background': "#FFFFFF"   # Fond blanc
    })
    
    # CSS minimal
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
            'niveau_etudes': "",
            'experience': "",
            'opt_in': False,
            'metier': ""          # Stocke aussi le métier dans user_data pour cohérence
        },
        'secteur': "",            # Secteur sélectionné
        'metier': "",             # Métier sélectionné
        'data_loaded': False,     # Indicateur de chargement des données
        'data': {},               # Données chargées
        'email_submitted': False  # Indicateur de soumission d'email
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
    st.session_state.page = page_name
    st.rerun()

# ----- GESTION DES DONNÉES -----
def load_data():
    """Charge les données depuis le fichier Excel."""
    if st.session_state.data_loaded:
        return st.session_state.data
    
    try:
        file_path = 'data/IED _ esg_calculator data.xlsx'
        
        # Charger toutes les feuilles nécessaires
        df_salaire = pd.read_excel(file_path, sheet_name='salaire')
        df_competences = pd.read_excel(file_path, sheet_name='competences_cles')
        
        # Charger les feuilles supplémentaires pour enrichir les résultats
        try:
            df_formations = pd.read_excel(file_path, sheet_name='formations_IED')
            df_tendances = pd.read_excel(file_path, sheet_name='tendances_marche')
        except Exception:
            # Si les feuilles supplémentaires ne sont pas disponibles, utiliser des DataFrames vides
            df_formations = pd.DataFrame()
            df_tendances = pd.DataFrame()
        
        # Stocker les données dans l'état de la session
        st.session_state.data = {
            'salaire': df_salaire,
            'competences': df_competences,
            'formations': df_formations,
            'tendances': df_tendances
        }
        st.session_state.data_loaded = True
        return st.session_state.data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return {
            'salaire': pd.DataFrame(),
            'competences': pd.DataFrame(),
            'formations': pd.DataFrame(),
            'tendances': pd.DataFrame()
        }

def get_metiers_par_secteur(df_salaire):
    """Retourne un dictionnaire des métiers par secteur."""
    metiers_par_secteur = {}
    
    # Trier les secteurs par ordre alphabétique pour une présentation cohérente
    secteurs = sorted(df_salaire['Secteur'].unique())
    
    for secteur in secteurs:
        # Trier les métiers par ordre alphabétique dans chaque secteur
        metiers_dans_secteur = sorted(df_salaire[df_salaire['Secteur'] == secteur]['Métier'].unique().tolist())
        metiers_par_secteur[secteur] = metiers_dans_secteur
    
    return metiers_par_secteur

def get_competences_par_metier(df_competences, metier):
    """Retourne les compétences pour un métier donné - version simplifiée."""
    if df_competences.empty or 'Métier' not in df_competences.columns:
        return pd.DataFrame()
    
    # Filtrer pour le métier spécifique
    df_filtered = df_competences[df_competences['Métier'] == metier]
    
    if df_filtered.empty:
        return pd.DataFrame()
    
    # Vérifier si nous avons le format avec Compétence_1, Compétence_2, etc.
    competence_cols = [col for col in df_filtered.columns if col.startswith('Compétence_')]
    
    if competence_cols:
        # Créer un nouveau DataFrame pour stocker les compétences
        competences_list = []
        
        for _, row in df_filtered.iterrows():
            # Pour chaque colonne de compétence, créer une ligne
            for i, col in enumerate(competence_cols, 1):
                if pd.notna(row[col]) and row[col]:
                    competence_entry = {
                        'Compétence': row[col],
                        'Importance': 6-i  # Importance décroissante basée sur l'ordre
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
    
    return df_filtered

# ----- VISUALISATIONS SIMPLIFIÉES -----
def create_salary_chart(df_filtered):
    """Crée un graphique d'évolution salariale simplifié."""
    colors = st.session_state.colors
    
    # Réduire la taille du graphique de 30%
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
    ax.legend(fontsize=8)
    
    # Ajouter les valeurs
    for i, avg_val in enumerate(avg_salary):
        ax.annotate(f"{avg_val}€", (i, avg_val), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontweight='bold', fontsize=8)
    
    plt.tight_layout()
    return fig

# ----- COMPOSANTS D'INTERFACE -----
def display_header(step=None):
    """Affiche l'en-tête avec le logo et la barre de progression simplifiée."""
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.markdown("<h3>🌱 IED</h3>", unsafe_allow_html=True)
    
    with col2:
        st.markdown("<h1>Calculateur de Carrière ESG</h1>", unsafe_allow_html=True)
    
    if step:
        # Barre de progression simplifiée
        progress_percent = {
            "accueil": 20,
            "profil": 40,
            "metier": 60,
            "apercu": 80,
            "email": 90,
            "resultats": 100
        }
        
        # Afficher la barre de progression
        st.markdown(
            f"""
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: {progress_percent.get(step, 0)}%;"></div>
            </div>
            """,
            unsafe_allow_html=True
        )

def display_email_form():
    """Affiche un formulaire de collecte d'email et téléphone simplifié."""
    if not st.session_state.email_submitted:
        st.markdown("### Pour accéder aux résultats complets")
        st.markdown("Recevez gratuitement des informations sur les carrières ESG et nos formations.")
        
        # Pré-remplir les champs si disponibles
        email_value = st.session_state.user_data.get('email', '')
        telephone_value = st.session_state.user_data.get('telephone', '')
        
        email = st.text_input("Votre email professionnel*", 
                              value=email_value, 
                              placeholder="nom@entreprise.com")
        telephone = st.text_input("Votre numéro de téléphone*", 
                                  value=telephone_value, 
                                  placeholder="06XXXXXXXX")
        opt_in = st.checkbox("J'accepte de recevoir des informations de l'Institut d'Économie Durable", value=True)
        
        st.markdown("*Champs obligatoires")
        
        submit = st.button("Accéder aux résultats complets", type="primary")
        
        if submit:
            errors = []
            
            # Validation de l'email
            if not email or "@" not in email or "." not in email:
                errors.append("Veuillez entrer une adresse email valide.")
            
            # Validation basique du téléphone (au moins 10 chiffres)
            if not telephone or len(''.join(c for c in telephone if c.isdigit())) < 10:
                errors.append("Veuillez entrer un numéro de téléphone valide (minimum 10 chiffres).")
            
            if errors:
                for error in errors:
                    st.error(error)
                return False
            
            # Enregistrer les coordonnées
            st.session_state.user_data['email'] = email
            st.session_state.user_data['telephone'] = telephone
            st.session_state.user_data['opt_in'] = opt_in
            st.session_state.email_submitted = True
            
            # Succès et redirection
            st.success("Merci ! Vous allez accéder aux résultats complets.")
            change_page("resultats")
            return True
        return False
    return True

# ----- PAGES DE L'APPLICATION -----
def page_accueil():
    """Affiche la page d'accueil simplifiée."""
    display_header("accueil")
    
    st.markdown("""
    ## Découvrez votre potentiel de carrière dans l'économie durable
    
    Bienvenue sur le calculateur de carrière de l'**Institut d'Économie Durable**. 
    Cet outil vous permet de visualiser les perspectives salariales et d'évolution des métiers ESG.
    
    ### Les métiers ESG sont parmi les plus prometteurs
    Avec une croissance estimée à 20% par an, ce secteur offre des opportunités diversifiées
    pour contribuer positivement à la transition écologique.
    """)
    
    st.info("""
    **Comment utiliser cet outil ?**
    
    En quelques étapes simples, vous allez :
    1. Renseigner votre profil
    2. Découvrir les métiers ESG qui correspondent à vos aspirations
    3. Visualiser les perspectives salariales et compétences requises
    4. Recevoir des recommandations personnalisées pour votre carrière
    """)
    
    if st.button("Commencer", use_container_width=True):
        change_page("profil")

def page_profil():
    """Affiche la page du profil utilisateur simplifiée."""
    display_header("profil")
    
    st.markdown("## Quelques informations sur vous")
    st.markdown("Ces informations nous permettront de vous proposer des perspectives adaptées.")
    
    # Formulaire simplifié
    with st.form(key="profil_form"):
        prenom = st.text_input("Votre prénom", value=st.session_state.user_data.get('prenom', ''))
        nom = st.text_input("Votre nom", value=st.session_state.user_data.get('nom', ''))
        
        niveau_etudes = st.selectbox(
            "Quel est votre niveau d'études ?",
            options=["", "Bac", "Bac+2 / Bac+3", "Bac+4 / Bac+5", "Bac+6 et plus"],
            index=0 if not st.session_state.user_data.get('niveau_etudes') else 
                  ["", "Bac", "Bac+2 / Bac+3", "Bac+4 / Bac+5", "Bac+6 et plus"].index(st.session_state.user_data.get('niveau_etudes'))
        )
        
        experience = st.radio(
            "Quelle expérience professionnelle avez-vous ?",
            options=["Aucune (étudiant)", "Stage/Alternance", "0-2 ans", "2-5 ans", "5-10 ans", "10+ ans"],
            index=0
        )
        
        # Navigation
        submit = st.form_submit_button("Continuer", use_container_width=True)
        
        if submit:
            # Vérification minimale
            if not prenom:
                st.error("Veuillez saisir votre prénom.")
            elif not nom:
                st.error("Veuillez saisir votre nom.")
            elif not niveau_etudes:
                st.error("Veuillez sélectionner votre niveau d'études.")
            else:
                # Mettre à jour les données utilisateur
                st.session_state.user_data.update({
                    'prenom': prenom,
                    'nom': nom,
                    'niveau_etudes': niveau_etudes,
                    'experience': experience
                })
                
                # Passer à la page suivante
                change_page("metier")

def page_metier():
    """Affiche la page de sélection du métier simplifiée."""
    display_header("metier")
    
    st.markdown("## Choisissez un métier ESG")
    st.markdown("Sélectionnez un secteur puis un métier qui vous intéresse.")
    
    # Charger les données
    data_dict = load_data()
    df_salaire = data_dict['salaire']
    
    # Obtenir les métiers par secteur
    metiers_par_secteur = get_metiers_par_secteur(df_salaire)
    
    # Si aucun métier n'est disponible, afficher un message d'erreur
    if not metiers_par_secteur:
        st.error("Impossible de charger les secteurs et métiers. Veuillez réessayer plus tard.")
        return
    
    # Afficher le nombre total de métiers disponibles
    total_metiers = sum(len(metiers) for metiers in metiers_par_secteur.values())
    st.info(f"🌱 {total_metiers} métiers ESG disponibles dans {len(metiers_par_secteur)} secteurs")
    
    # Sélection du secteur EN DEHORS du formulaire pour mise à jour immédiate
    secteur_options = list(metiers_par_secteur.keys())
    
    # Définir une fonction de callback pour le changement de secteur
    def on_secteur_change():
        # Cette fonction est appelée automatiquement quand le secteur change
        pass
    
    # Vérifier si le secteur est dans les options et définir l'index 
    if 'secteur' not in st.session_state or st.session_state.secteur not in secteur_options:
        secteur_index = 0  # Premier secteur par défaut
    else:
        secteur_index = secteur_options.index(st.session_state.secteur)
    
    # Utiliser on_change pour forcer le rechargement quand le secteur change
    secteur = st.selectbox(
        "Secteur d'activité",
        options=secteur_options,
        index=secteur_index,
        key="secteur_selectbox",
        on_change=on_secteur_change
    )
    
    # Récupérer le secteur sélectionné depuis la session state
    secteur = st.session_state.secteur_selectbox
    
    # Ajouter une indication du nombre de métiers dans ce secteur
    st.caption(f"{len(metiers_par_secteur[secteur])} métiers disponibles dans le secteur '{secteur}'")
    
    # Formulaire simplifié (uniquement pour le métier)
    with st.form(key="metier_form"):
        # Sélection du métier en fonction du secteur choisi
        metier_options = metiers_par_secteur[secteur]
        metier_index = 0
        
        # Vérifier si le métier actuel est dans les options du secteur sélectionné
        if st.session_state.metier in metier_options:
            metier_index = metier_options.index(st.session_state.metier)
        
        metier = st.selectbox(
            "Métier",
            options=metier_options,
            index=metier_index
        )
        
        # Navigation
        submit = st.form_submit_button("Voir les perspectives", use_container_width=True)
        
        if submit:
            # Mettre à jour les données de session pour le métier et le secteur
            st.session_state.metier = metier
            st.session_state.secteur = secteur  # S'assurer que le secteur est bien enregistré
            st.session_state.user_data['metier'] = metier
            
            # Passer à la page suivante
            change_page("apercu")

def page_apercu():
    """Affiche un aperçu des salaires avant la collecte d'email."""
    display_header("apercu")
    
    # Vérifier que nous avons les données nécessaires
    if not st.session_state.metier:
        st.warning("Veuillez d'abord sélectionner un métier.")
        change_page("metier")
        return
    
    # En-tête et résumé du profil
    st.markdown("## Aperçu des perspectives salariales")
    
    # Charger les données
    data_dict = load_data()
    df_salaire = data_dict['salaire']
    df_competences = data_dict['competences']
    metier = st.session_state.metier
    secteur = st.session_state.secteur
    
    # Afficher des informations de contexte
    st.markdown(f"### {metier}")
    st.caption(f"Secteur: {secteur}")
    
    # Récupérer les données spécifiques au métier
    df_salaire_filtered = df_salaire[df_salaire['Métier'] == metier]
    if not df_salaire_filtered.empty:
        # Afficher une brève description si disponible
        if 'Description' in df_salaire_filtered.columns:
            description = df_salaire_filtered['Description'].iloc[0]
            if pd.notna(description):
                st.markdown(f"**Description:** {description[:200]}..." if len(description) > 200 else f"**Description:** {description}")
        
        # Afficher un graphique simplifié
        fig = create_salary_chart(df_salaire_filtered)
        st.pyplot(fig)
        
        # Afficher toutes les compétences clés disponibles
        competences = get_competences_par_metier(df_competences, metier)
        if not competences.empty:
            st.markdown("### Principales compétences requises")
            # Afficher toutes les compétences
            for _, row in competences.iterrows():
                st.markdown(f"• {row['Compétence']}")
    
    st.markdown("---")
    
    # Si l'utilisateur a déjà soumis ses coordonnées, on peut aller directement aux résultats complets
    if st.session_state.email_submitted:
        st.markdown("### Accéder aux résultats complets")
        if st.button("Voir les résultats complets", type="primary", use_container_width=True):
            change_page("resultats")
    else:
        st.markdown("### Vous souhaitez accéder aux résultats complets ?")
        st.markdown("Pour obtenir toutes les perspectives de ce métier et nos recommandations:")
        
        if st.button("Continuer", type="primary", use_container_width=True):
            change_page("email")

def page_email():
    """Page dédiée à la collecte d'email."""
    display_header("email")
    
    st.markdown("## Accédez aux résultats complets")
    
    # Afficher le formulaire d'email
    display_email_form()
    
    # Option de retour
    if st.button("Retour"):
        change_page("apercu")

def page_resultats():
    """Affiche la page des résultats enrichie avec plus d'informations."""
    display_header("resultats")
    
    # Vérifier que les coordonnées ont été soumises
    if not st.session_state.email_submitted:
        st.warning("Veuillez d'abord fournir vos coordonnées.")
        change_page("email")
        return
        
    # Personnalisation avec le prénom s'il existe
    if st.session_state.user_data.get('prenom'):
        st.markdown(f"## Bonjour {st.session_state.user_data['prenom']}, voici vos résultats !")
    else:
        # Afficher les résultats complets
        st.markdown("## Résultats complets")
    
    # Charger les données
    data_dict = load_data()
    df_salaire = data_dict['salaire']
    df_competences = data_dict['competences']
    df_formations = data_dict.get('formations', pd.DataFrame())
    df_tendances = data_dict.get('tendances', pd.DataFrame())
    metier = st.session_state.metier
    secteur = st.session_state.secteur
    
    # Filtrer les données pour le métier sélectionné
    df_salaire_filtered = df_salaire[df_salaire['Métier'] == metier]
    df_competences_filtered = get_competences_par_metier(df_competences, metier)
    df_formations_filtered = get_formations_par_metier(df_formations, metier) if not df_formations.empty else pd.DataFrame()
    
    # Titre de la page avec le métier et le secteur
    st.markdown(f"# {metier}")
    st.caption(f"Secteur: **{secteur}**")
    st.divider()
    
    # Description du métier (section améliorée)
    st.markdown("## 📋 Description du métier")
    if 'Description' in df_salaire_filtered.columns and not df_salaire_filtered.empty:
        description = df_salaire_filtered['Description'].iloc[0]
        if pd.notna(description):
            st.markdown(description)
        else:
            st.info(f"Aucune description disponible pour le métier de {metier}.")
    else:
        st.info(f"Aucune description disponible pour le métier de {metier}.")
    
    st.divider()
    
    # Salaires (section améliorée avec colonnes pour une meilleure organisation)
    st.markdown("## 💰 Perspectives salariales")
    if not df_salaire_filtered.empty:
        # Utilisation de colonnes pour organiser les informations
        col1, col2 = st.columns([3, 2])
        
        with col1:
            # Graphique des salaires
            fig_salary = create_salary_chart(df_salaire_filtered)
            st.pyplot(fig_salary)
        
        with col2:
            # Afficher un tableau de salaires avec mise en forme
            st.markdown("### Détail des salaires")
            st.dataframe(
                df_salaire_filtered[['Expérience', 'Salaire_Min', 'Salaire_Max', 'Salaire_Moyen']].rename(
                    columns={
                        'Salaire_Min': 'Minimum (€)',
                        'Salaire_Max': 'Maximum (€)',
                        'Salaire_Moyen': 'Moyen (€)'
                    }
                ),
                hide_index=True,
                use_container_width=True
            )
            
            # Ajouter des informations supplémentaires
            if 'Croissance_Salaire' in df_salaire_filtered.columns:
                croissance = df_salaire_filtered['Croissance_Salaire'].iloc[0]
                if pd.notna(croissance):
                    st.metric("Croissance annuelle moyenne", f"{croissance}%")
    
    st.divider()
    
    # Compétences clés (section améliorée)
    st.markdown("## 🔑 Compétences clés")
    if not df_competences_filtered.empty:
        # Utiliser des colonnes pour organiser les compétences
        competences_cols = st.columns(2)
        
        # Préparer la liste complète des compétences
        competences_list = df_competences_filtered.sort_values(by='Importance', ascending=False)
        
        # Utiliser une boucle pour ajouter les compétences aux colonnes
        for i, row in competences_list.iterrows():
            col_index = i % 2  # Alterner entre les deux colonnes
            with competences_cols[col_index]:
                importance = row['Importance']
                emoji = "🔴" if importance >= 4 else "🟠" if importance >= 2 else "🟡"
                st.markdown(f"{emoji} **{row['Compétence']}**")
    else:
        st.info("Aucune information sur les compétences n'est disponible pour ce métier.")
    
    st.divider()
    
    # Formations recommandées (nouvelle section)
    st.markdown("## 🎓 Formations recommandées")
    if not df_formations_filtered.empty and 'Formation' in df_formations_filtered.columns:
        # Créer un conteneur pour les formations
        formations_container = st.container()
        
        with formations_container:
            # Afficher chaque formation dans un expander avec détails
            for i, row in df_formations_filtered.iterrows():
                formation_name = row.get('Formation', f"Formation {i+1}")
                with st.expander(formation_name):
                    # Afficher les détails de la formation si disponibles
                    if 'Description' in row:
                        st.markdown(row['Description'])
                    if 'Durée' in row:
                        st.markdown(f"**Durée**: {row['Durée']}")
                    if 'Niveau' in row:
                        st.markdown(f"**Niveau**: {row['Niveau']}")
                    if 'Prix' in row:
                        st.markdown(f"**Prix**: {row['Prix']}€")
                    if 'Lien' in row:
                        st.markdown(f"[En savoir plus]({row['Lien']})")
    else:
        st.info("Aucune formation spécifique n'est disponible pour ce métier.")
        st.markdown("""
        L'Institut d'Économie Durable propose néanmoins plusieurs formations généralistes 
        qui peuvent vous aider à développer vos compétences dans le domaine ESG.
        """)
    
    # Tendances du marché (si disponibles)
    if not df_tendances.empty and 'Métier' in df_tendances.columns:
        df_tendances_filtered = df_tendances[df_tendances['Métier'] == metier]
        
        if not df_tendances_filtered.empty:
            st.divider()
            st.markdown("## 📈 Tendances du marché")
            
            # Afficher les tendances selon les colonnes disponibles
            if 'Tendance_Globale' in df_tendances_filtered.columns:
                tendance = df_tendances_filtered['Tendance_Globale'].iloc[0]
                if pd.notna(tendance):
                    st.markdown(f"**Tendance globale**: {tendance}")
            
            if 'Perspectives' in df_tendances_filtered.columns:
                perspectives = df_tendances_filtered['Perspectives'].iloc[0]
                if pd.notna(perspectives):
                    st.markdown(f"**Perspectives d'évolution**: {perspectives}")
    
    # Métiers similaires (nouvelle section)
    st.divider()
    st.markdown("## 🔄 Métiers similaires")
    
    # Filtrer les métiers du même secteur (sauf le métier actuel)
    metiers_meme_secteur = df_salaire[(df_salaire['Secteur'] == secteur) & (df_salaire['Métier'] != metier)]['Métier'].unique()
    
    if len(metiers_meme_secteur) > 0:
        # Afficher jusqu'à 3 métiers similaires dans le même secteur
        st.markdown(f"### Dans le secteur {secteur}")
        cols_secteur = st.columns(min(3, len(metiers_meme_secteur)))
        
        for i, metier_similaire in enumerate(metiers_meme_secteur[:3]):
            with cols_secteur[i]:
                st.markdown(f"**{metier_similaire}**")
                # Ajouter un bouton pour explorer ce métier
                if st.button(f"Explorer", key=f"btn_sect_{i}"):
                    # Mettre à jour le métier sélectionné
                    st.session_state.metier = metier_similaire
                    st.session_state.user_data['metier'] = metier_similaire
                    # Recharger la page
                    st.rerun()
    
    # Suggérer d'autres secteurs avec des métiers intéressants
    autres_secteurs = [s for s in df_salaire['Secteur'].unique() if s != secteur]
    if autres_secteurs:
        st.markdown("### Explorer d'autres secteurs")
        # Sélectionner jusqu'à 4 autres secteurs
        autres_secteurs_sample = autres_secteurs[:min(4, len(autres_secteurs))]
        for autre_secteur in autres_secteurs_sample:
            # Créer un expander pour chaque secteur
            with st.expander(autre_secteur):
                # Trouver des métiers dans ce secteur
                metiers_autre_secteur = df_salaire[df_salaire['Secteur'] == autre_secteur]['Métier'].unique()
                # Afficher jusqu'à 3 métiers pour ce secteur
                for metier_autre in metiers_autre_secteur[:3]:
                    col1, col2 = st.columns([4,1])
                    with col1:
                        st.markdown(f"• **{metier_autre}**")
                    with col2:
                        if st.button("Voir", key=f"btn_{autre_secteur}_{metier_autre}".replace(" ", "_")):
                            # Mettre à jour le secteur et le métier sélectionnés
                            st.session_state.secteur = autre_secteur
                            st.session_state.metier = metier_autre
                            st.session_state.user_data['metier'] = metier_autre
                            # Recharger la page
                            st.rerun()
    
    # CTA finale
    st.divider()
    st.markdown("### Vous souhaitez en savoir plus ?")
    
    st.markdown("""
    L'Institut d'Économie Durable propose des formations adaptées pour développer votre carrière ESG.
    Notre équipe vous contactera prochainement pour vous présenter nos programmes.
    """)
    
    # Ajout d'un CTA final sans option de retour
    st.markdown("""
    Contactez-nous pour plus d'informations sur nos programmes de formation
    et comment développer votre carrière dans le secteur ESG.
    """)

# ----- FONCTION PRINCIPALE -----
def main():
    """Fonction principale de l'application simplifiée."""
    # Configurer l'application
    configure_app()
    
    # Initialiser l'état de la session
    initialize_session_state()
    
    # Afficher la page correspondante à l'état actuel
    if st.session_state.page == "accueil":
        page_accueil()
    elif st.session_state.page == "profil":
        page_profil()
    elif st.session_state.page == "metier":
        page_metier()
    elif st.session_state.page == "apercu":
        page_apercu()
    elif st.session_state.page == "email":
        page_email()
    elif st.session_state.page == "resultats":
        page_resultats()
    else:
        # Page par défaut
        page_accueil()

# ----- POINT D'ENTRÉE -----
if __name__ == "__main__":
    main()