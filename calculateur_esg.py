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
            'nom': "",
            'email': "",
            'niveau_etudes': "",
            'experience': ""
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
        
        # Charger seulement les feuilles nécessaires
        df_salaire = pd.read_excel(file_path, sheet_name='salaire')
        df_competences = pd.read_excel(file_path, sheet_name='competences_cles')
        
        # Stocker les données dans l'état de la session
        st.session_state.data = {
            'salaire': df_salaire,
            'competences': df_competences
        }
        st.session_state.data_loaded = True
        return st.session_state.data
    except Exception as e:
        st.error(f"Erreur lors du chargement des données: {str(e)}")
        return {
            'salaire': pd.DataFrame(),
            'competences': pd.DataFrame()
        }

def get_metiers_par_secteur(df_salaire):
    """Retourne un dictionnaire des métiers par secteur."""
    metiers_par_secteur = {}
    
    for secteur in df_salaire['Secteur'].unique():
        metiers_dans_secteur = df_salaire[df_salaire['Secteur'] == secteur]['Métier'].unique().tolist()
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

# ----- VISUALISATIONS SIMPLIFIÉES -----
def create_salary_chart(df_filtered):
    """Crée un graphique d'évolution salariale simplifié."""
    colors = st.session_state.colors
    
    fig, ax = plt.subplots(figsize=(10, 6))
    
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
    ax.set_ylabel('Salaire annuel brut (€)', fontsize=12)
    ax.set_xlabel('Expérience', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(experience)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Ajouter les valeurs
    for i, avg_val in enumerate(avg_salary):
        ax.annotate(f"{avg_val}€", (i, avg_val), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontweight='bold')
    
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
    """Affiche un formulaire de collecte d'email simplifié."""
    if not st.session_state.email_submitted:
        st.markdown("### Pour accéder aux résultats complets")
        st.markdown("Recevez gratuitement des informations sur les carrières ESG et nos formations.")
        
        email = st.text_input("Votre email professionnel", placeholder="nom@entreprise.com")
        opt_in = st.checkbox("J'accepte de recevoir des informations de l'Institut d'Économie Durable", value=True)
        
        submit = st.button("Accéder aux résultats complets", type="primary")
        
        if submit:
            if not email or "@" not in email or "." not in email:
                st.error("Veuillez entrer une adresse email valide.")
                return False
            
            # Enregistrer l'email
            st.session_state.user_data['email'] = email
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
    
    if st.button("Commencer", use_container_width=True):
        change_page("profil")

def page_profil():
    """Affiche la page du profil utilisateur simplifiée."""
    display_header("profil")
    
    st.markdown("## Quelques informations sur vous")
    st.markdown("Ces informations nous permettront de vous proposer des perspectives adaptées.")
    
    # Formulaire simplifié
    with st.form(key="profil_form"):
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
            if not nom:
                st.error("Veuillez saisir votre nom.")
            elif not niveau_etudes:
                st.error("Veuillez sélectionner votre niveau d'études.")
            else:
                # Mettre à jour les données utilisateur
                st.session_state.user_data.update({
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
    
    # Formulaire simplifié
    with st.form(key="metier_form"):
        # Sélection du secteur
        secteur_options = list(metiers_par_secteur.keys())
        secteur_index = 0
        
        if st.session_state.secteur in secteur_options:
            secteur_index = secteur_options.index(st.session_state.secteur)
        
        secteur = st.selectbox(
            "Secteur d'activité",
            options=secteur_options,
            index=secteur_index
        )
    
        # Sélection du métier en fonction du secteur choisi
        metier_options = metiers_par_secteur[secteur]
        metier_index = 0
        
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
            # Mettre à jour les données de session
            st.session_state.secteur = secteur
            st.session_state.metier = metier
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
    metier = st.session_state.metier
    
    # Afficher un aperçu des résultats
    st.markdown(f"### {metier}")
    
    df_salaire_filtered = df_salaire[df_salaire['Métier'] == metier]
    if not df_salaire_filtered.empty:
        # Afficher un graphique simplifié
        fig = create_salary_chart(df_salaire_filtered)
        st.pyplot(fig)
    
    st.markdown("---")
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
    """Affiche la page des résultats simplifiée."""
    display_header("resultats")
    
    # Vérifier que l'email a été soumis
    if not st.session_state.email_submitted:
        st.warning("Veuillez d'abord fournir votre email.")
        change_page("email")
        return
    
    # Afficher les résultats complets
    st.markdown("## Résultats complets")
    
    # Charger les données
    data_dict = load_data()
    df_salaire = data_dict['salaire']
    df_competences = data_dict['competences']
    metier = st.session_state.metier
    
    # Filtrer les données pour le métier sélectionné
    df_salaire_filtered = df_salaire[df_salaire['Métier'] == metier]
    df_competences_filtered = get_competences_par_metier(df_competences, metier)
    
    # Afficher les informations du métier
    st.markdown(f"### {metier}")
    
    # Description du métier
    if 'Description' in df_salaire_filtered.columns and not df_salaire_filtered.empty:
        description = df_salaire_filtered['Description'].iloc[0]
        if pd.notna(description):
            st.info(description)
    
    # Salaires
    st.markdown("### Perspectives salariales")
    if not df_salaire_filtered.empty:
        # Graphique des salaires
        fig_salary = create_salary_chart(df_salaire_filtered)
        st.pyplot(fig_salary)
        
        # Tableau des salaires
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
    
    # Compétences
    st.markdown("### Compétences clés")
    if not df_competences_filtered.empty:
        # Afficher simplement la liste des compétences
        for i, row in df_competences_filtered.head(5).iterrows():
            st.markdown(f"- **{row['Compétence']}**")
    else:
        st.info("Aucune information sur les compétences n'est disponible pour ce métier.")
    
    # CTA finale
    st.markdown("---")
    st.markdown("### Vous souhaitez en savoir plus ?")
    
    st.markdown("""
    L'Institut d'Économie Durable propose des formations adaptées pour développer votre carrière ESG.
    Notre équipe vous contactera prochainement pour vous présenter nos programmes.
    """)
    
    # Option de retour à l'accueil
    if st.button("Découvrir d'autres métiers", use_container_width=True):
        # Conserver l'email mais réinitialiser le métier
        email = st.session_state.user_data.get('email', '')
        opt_in = st.session_state.user_data.get('opt_in', False)
        nom = st.session_state.user_data.get('nom', '')
        niveau_etudes = st.session_state.user_data.get('niveau_etudes', '')
        experience = st.session_state.user_data.get('experience', '')
        
        # Réinitialiser la sélection de métier
        st.session_state.secteur = ""
        st.session_state.metier = ""
        
        # Restaurer les données utilisateur
        st.session_state.user_data = {
            'email': email,
            'opt_in': opt_in,
            'nom': nom,
            'niveau_etudes': niveau_etudes,
            'experience': experience
        }
        
        # Retour à la page de sélection de métier
        change_page("metier")

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