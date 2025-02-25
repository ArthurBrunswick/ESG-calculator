# 1. Imports
import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import os

# 2. Configuration de la page
st.set_page_config(
    page_title="Calculateur de Carrière ESG - École de la Durabilité 2050",
    page_icon="🌱",
)

# 3. Fonctions de chargement de données
def load_data():
    """Charge les données des salaires ESG."""
    # Données directement intégrées (plus tard on pourra les mettre dans un CSV)
    data = {
        'Métier': ['Analyste ESG', 'Analyste ESG', 'Analyste ESG', 
                  'Responsable ESG', 'Responsable ESG', 'Responsable ESG'],
        'Expérience': ['0-2 ans', '2-5 ans', '5-10 ans', 
                      '0-2 ans', '2-5 ans', '5-10 ans'],
        'Salaire_Min': [35000, 40000, 50000, 35000, 47000, 61000],
        'Salaire_Max': [45000, 50000, 65000, 47000, 61000, 70000],
        'Salaire_Moyen': [40000, 45000, 57500, 41000, 54000, 65500]
    }
    return pd.DataFrame(data)

# 4. Fonctions de visualisation
def create_salary_chart(df_filtered):
    """Crée un graphique d'évolution salariale."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Tracer la ligne des salaires moyens
    ax.plot(df_filtered['Expérience'], df_filtered['Salaire_Moyen'], 
            marker='o', linestyle='-', color='green')
    
    ax.set_ylabel('Salaire annuel brut (€)')
    ax.set_xlabel('Expérience')
    ax.grid(True)
    
    return fig

# 5. Application principale
def main():
    """Fonction principale de l'application."""
    # Titre et introduction
    st.title("💰 Calculateur de Carrière ESG")
    st.markdown("### Découvrez les perspectives salariales des métiers durables")
    
    # Chargement des données
    df = load_data()
    
    # Interface utilisateur
    métier_sélectionné = st.selectbox(
        "Choisissez un métier à explorer",
        options=df['Métier'].unique()
    )
    
    # Filtrer les données
    df_filtered = df[df['Métier'] == métier_sélectionné]
    
    # Afficher les données dans un tableau
    st.write(f"Données salariales pour {métier_sélectionné}")
    st.dataframe(df_filtered[['Expérience', 'Salaire_Min', 'Salaire_Max', 'Salaire_Moyen']])
    
    # Afficher le graphique
    st.subheader(f"Évolution salariale : {métier_sélectionné}")
    st.pyplot(create_salary_chart(df_filtered))
    
    # Formulaire de contact
    st.markdown("---")
    st.markdown("### Intéressé(e) par une formation aux métiers de la durabilité?")
    
    with st.form("contact_form"):
        email = st.text_input("Votre email")
        submitted = st.form_submit_button("Me tenir informé(e)")
        
        if submitted and email:
            st.success("Merci! Vous recevrez bientôt plus d'informations.")

# 6. Point d'entrée
if __name__ == "__main__":
    main()