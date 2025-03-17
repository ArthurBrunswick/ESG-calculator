import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import os
import json
import io
import smtplib
import ssl
import csv
import tempfile
from datetime import datetime
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from reportlab.platypus import Table, TableStyle
from reportlab.lib.units import inch, cm

# Configuration de la page
st.set_page_config(
    page_title="Calculateur de Carrière ESG - Institut d'Économie Durable",
    page_icon="🌱",
    layout="wide"
)

# Définition des couleurs
PRIMARY_COLOR = "#003366"  # Bleu foncé
SECONDARY_COLOR = "#FFE548"  # Jaune pour les boutons

# CSS personnalisé
def load_custom_css():
    st.markdown("""
    <style>
    .main {
        background-color: #FFFFFF;
    }
    .stButton>button {
        background-color: #FFE548;
        color: #003366;
        font-weight: bold;
        border-radius: 5px;
        border: none;
        padding: 10px 20px;
        min-width: 200px;
    }
    .stButton>button:hover {
        background-color: #E5CE41;
        color: #003366;
    }
    .lead-capture-box {
        background-color: #f7f9fa;
        border-radius: 10px;
        padding: 20px;
        margin: 20px 0 30px 0;
        border-left: 4px solid #FFE548;
    }
    .form-submit-button {
        background-color: #FFE548 !important;
        color: #003366 !important;
        font-weight: bold !important;
        border-radius: 5px !important;
        border: none !important;
        padding: 12px 24px !important;
        min-width: 250px !important;
        text-align: center !important;
    }
    .progress-container {
        width: 100%;
        padding: 10px 0;
    }
    .progress-bar {
        height: 10px;
        background-color: #E0E0E0;
        border-radius: 5px;
        margin-bottom: 20px;
    }
    .progress-bar-fill {
        height: 100%;
        background-color: #FFE548;
        border-radius: 5px;
    }
    .header-container {
        display: flex;
        justify-content: space-between;
        align-items: center;
        margin-bottom: 20px;
    }
    .logo-container {
        margin-right: 20px;
    }
    .title-container {
        flex-grow: 1;
    }
    </style>
    """, unsafe_allow_html=True)

# Fonctions de gestion des données
def load_data():
    """Charge les données des salaires ESG depuis un fichier CSV."""
    try:
        # Essayer de charger depuis le fichier CSV
        df = pd.read_csv('data/metiers_esg.csv')
        return df
    except (FileNotFoundError, pd.errors.EmptyDataError):
        # Si le fichier n'existe pas ou est vide, utiliser les données par défaut
        print("Fichier CSV non trouvé, utilisation des données par défaut")
        data = {
            'Métier': [
                'Analyste ESG', 'Analyste ESG', 'Analyste ESG',
                'Responsable ESG', 'Responsable ESG', 'Responsable ESG'
            ],
            'Secteur': [
                'Finance', 'Finance', 'Finance',
                'Finance', 'Finance', 'Finance'
            ],
            'Expérience': [
                '0-2 ans', '2-5 ans', '5-10 ans',
                '0-2 ans', '2-5 ans', '5-10 ans'
            ],
            'Salaire_Min': [
                35000, 42000, 50000,
                38000, 47000, 61000
            ],
            'Salaire_Max': [
                45000, 52000, 65000,
                47000, 61000, 75000
            ],
            'Salaire_Moyen': [
                40000, 47000, 57500,
                42500, 54000, 68000
            ],
            'Description': [
                "Analyse et intégration des critères environnementaux, sociaux et de gouvernance dans l'évaluation des entreprises.",
                "Analyse et intégration des critères environnementaux, sociaux et de gouvernance dans l'évaluation des entreprises.",
                "Analyse et intégration des critères environnementaux, sociaux et de gouvernance dans l'évaluation des entreprises.",
                "Mise en œuvre et supervision des stratégies ESG au sein des organisations financières.",
                "Mise en œuvre et supervision des stratégies ESG au sein des organisations financières.",
                "Mise en œuvre et supervision des stratégies ESG au sein des organisations financières."
            ]
        }
        return pd.DataFrame(data)

def get_métiers_par_secteur():
    """Retourne un dictionnaire des métiers par secteur."""
    df = load_data()
    métiers_par_secteur = {}
    
    for secteur in df['Secteur'].unique():
        métiers_dans_secteur = df[df['Secteur'] == secteur]['Métier'].unique().tolist()
        métiers_par_secteur[secteur] = métiers_dans_secteur
    
    return métiers_par_secteur

# Fonctions de visualisation
def create_salary_chart(df_filtered):
    """Crée un graphique d'évolution salariale."""
    fig, ax = plt.subplots(figsize=(10, 6))
    
    # Créer des données pour le graphique
    experience = df_filtered['Expérience'].tolist()
    min_salary = df_filtered['Salaire_Min'].tolist()
    max_salary = df_filtered['Salaire_Max'].tolist()
    avg_salary = df_filtered['Salaire_Moyen'].tolist()
    
    # Tracer les lignes et l'aire entre min et max
    x = range(len(experience))
    ax.plot(x, avg_salary, marker='o', linestyle='-', color=PRIMARY_COLOR, linewidth=2, label='Salaire moyen')
    ax.fill_between(x, min_salary, max_salary, alpha=0.2, color=PRIMARY_COLOR, label='Fourchette salariale')
    
    # Personnaliser le graphique
    ax.set_ylabel('Salaire annuel brut (€)', fontsize=12)
    ax.set_xlabel('Expérience', fontsize=12)
    ax.set_xticks(x)
    ax.set_xticklabels(experience)
    ax.grid(True, linestyle='--', alpha=0.7)
    ax.legend()
    
    # Ajouter les valeurs
    for i, (min_val, avg_val, max_val) in enumerate(zip(min_salary, avg_salary, max_salary)):
        ax.annotate(f"{avg_val}€", (i, avg_val), textcoords="offset points", 
                    xytext=(0,10), ha='center', fontweight='bold')
    
    plt.tight_layout()
    return fig

def generate_salary_report_pdf(user_data, salary_data, filepath):
    """
    Génère un rapport PDF attrayant avec les données salariales et le profil utilisateur.
    
    Args:
        user_data (dict): Données du profil utilisateur
        salary_data (DataFrame): Données salariales filtrées pour le métier choisi
        filepath (str): Chemin où sauvegarder le PDF
    """
    # Préparer les données
    metier = user_data.get("metier", "Métier ESG")
    niveau_etudes = user_data.get("niveau_etudes", "")
    formation = user_data.get("formation", "")
    experience = user_data.get("experience", "")
    interets = user_data.get("interets", [])
    interets_str = ", ".join(interets) if interets else ""
    prenom = user_data.get("prenom", "")
    nom = user_data.get("nom", "")
    
    # Créer un fichier temporaire pour le graphique
    temp_img_path = os.path.join(tempfile.gettempdir(), f"temp_graph_{datetime.now().strftime('%Y%m%d%H%M%S')}.png")
    
    # Préparer les données du graphique
    df_filtered = salary_data
    
    # Générer le graphique et le sauvegarder dans un fichier temporaire
    fig = create_salary_chart(df_filtered)
    fig.savefig(temp_img_path, format='png', dpi=300, bbox_inches='tight')
    
    # Créer le PDF
    c = canvas.Canvas(filepath, pagesize=A4)
    width, height = A4
    
    # En-tête
    c.setFillColor(colors.HexColor(PRIMARY_COLOR))
    c.rect(0, height - 2*cm, width, 2*cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica-Bold", 16)
    c.drawString(1*cm, height - 1.3*cm, "Institut d'Économie Durable")
    
    # Sous-titre
    c.setFillColor(colors.HexColor(PRIMARY_COLOR))
    c.setFont("Helvetica-Bold", 14)
    c.drawString(1*cm, height - 3*cm, "Rapport de Perspectives Salariales ESG")
    
    # Date
    c.setFont("Helvetica", 10)
    today = datetime.now().strftime("%d/%m/%Y")
    c.drawString(width - 3*cm, height - 3*cm, f"Date: {today}")
    
    # Informations sur le profil
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*cm, height - 4*cm, f"Profil de {prenom} {nom}")
    
    c.setFont("Helvetica", 10)
    y_position = height - 4.5*cm
    c.drawString(1*cm, y_position, f"Niveau d'études: {niveau_etudes}")
    y_position -= 0.5*cm
    c.drawString(1*cm, y_position, f"Formation: {formation}")
    y_position -= 0.5*cm
    c.drawString(1*cm, y_position, f"Expérience: {experience}")
    y_position -= 0.5*cm
    c.drawString(1*cm, y_position, f"Centres d'intérêt: {interets_str}")
    
    # Métier analysé
    y_position -= 1*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*cm, y_position, f"Métier analysé: {metier}")
    
    # Description du métier
    description = ""
    if not df_filtered.empty and 'Description' in df_filtered.columns:
        description = df_filtered['Description'].iloc[0]
    
    if description:
        y_position -= 0.7*cm
        c.setFont("Helvetica-Oblique", 10)
        # Gérer le texte long en le divisant
        text = description
        max_width = width - 2*cm
        words = text.split()
        line = ""
        for word in words:
            test_line = line + word + " "
            if c.stringWidth(test_line, "Helvetica-Oblique", 10) < max_width:
                line = test_line
            else:
                c.drawString(1*cm, y_position, line)
                y_position -= 0.5*cm
                line = word + " "
        c.drawString(1*cm, y_position, line)
    
    # Graphique d'évolution salariale
    y_position -= 1.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*cm, y_position, f"Évolution salariale: {metier}")
    
    y_position -= 0.7*cm
    # Insérer le graphique enregistré dans un fichier temporaire
    c.drawImage(temp_img_path, 1*cm, y_position - 10*cm, width=width - 2*cm, height=10*cm)
    
    # Tableau des salaires
    y_position -= 11*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*cm, y_position, "Détail des salaires")
    
    if not df_filtered.empty:
        # Préparer les données du tableau
        data = [['Expérience', 'Minimum (€)', 'Maximum (€)', 'Moyen (€)']]
        for _, row in df_filtered.iterrows():
            data.append([
                row['Expérience'], 
                f"{row['Salaire_Min']}€", 
                f"{row['Salaire_Max']}€", 
                f"{row['Salaire_Moyen']}€"
            ])
        
        # Créer le tableau
        y_position -= 0.7*cm
        table = Table(data, colWidths=[3*cm, 3*cm, 3*cm, 3*cm])
        table.setStyle(TableStyle([
            ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor(PRIMARY_COLOR)),
            ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
            ('FONTSIZE', (0, 0), (-1, 0), 10),
            ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
            ('GRID', (0, 0), (-1, -1), 1, colors.black),
        ]))
        
        # Dessiner le tableau
        table.wrapOn(c, width, height)
        table.drawOn(c, 1*cm, y_position - 2*cm)
    
    # Informations sur les formations
    y_position -= 3.5*cm
    c.setFont("Helvetica-Bold", 12)
    c.drawString(1*cm, y_position, "Formations recommandées à l'Institut d'Économie Durable")
    
    y_position -= 0.7*cm
    c.setFont("Helvetica", 10)
    
    # Formations recommandées en fonction du métier
    formations_recommandees = {
        "Analyste ESG": ["Master Finance Durable", "Certification Analyse ESG"],
        "Responsable ESG": ["Executive MBA RSE & Impact", "Master Stratégie ESG"],
        "Consultant Développement Durable": ["Master Conseil en Développement Durable", "Programme Stratégies Durables"],
        "Chef de Projet RSE": ["Master Management RSE", "Certification Gestion de Projets Durables"],
        "Ingénieur Efficacité Énergétique": ["Master Transition Énergétique", "Programme Efficacité Énergétique"],
        "Chargé de Mission Biodiversité": ["Master Biodiversité & Écosystèmes", "Programme Gestion des Espaces Naturels"],
        "Responsable Achats Durables": ["Master Supply Chain Durable", "Certification Achats Responsables"],
        "Expert Économie Circulaire": ["Master Économie Circulaire", "Programme Zéro Déchet"],
        "Directeur RSE": ["Executive MBA RSE & Impact", "Programme Leadership Durable"],
        "Data Analyst ESG": ["Master Data Science pour l'ESG", "Certification Analyse de Données Durables"]
    }
    
    formations = formations_recommandees.get(metier, ["Master Économie Durable", "Certification RSE"])
    
    for formation in formations:
        c.drawString(1*cm, y_position, f"• {formation}")
        y_position -= 0.5*cm
    
    y_position -= 0.5*cm
    c.setFont("Helvetica-Italic", 9)
    c.drawString(1*cm, y_position, "Pour plus d'informations sur nos formations, visitez notre site web ou contactez-nous.")
    
    # Pied de page
    c.setFillColor(colors.HexColor(PRIMARY_COLOR))
    c.rect(0, 0, width, 1*cm, fill=1)
    c.setFillColor(colors.white)
    c.setFont("Helvetica", 8)
    c.drawString(1*cm, 0.4*cm, "© Institut d'Économie Durable - Tous droits réservés")
    c.drawString(width - 7*cm, 0.4*cm, "contact@ied-formation.fr | www.ied-formation.fr")
    
    # Finaliser le PDF
    c.save()
    
    # Supprimer le fichier temporaire de l'image
    try:
        os.remove(temp_img_path)
    except:
        pass
    
    return filepath

def send_results_email(recipient_email, pdf_path, user_data):
    """
    Envoie les résultats par email avec le PDF en pièce jointe.
    
    Args:
        recipient_email (str): Email du destinataire
        pdf_path (str): Chemin vers le fichier PDF à joindre
        user_data (dict): Données utilisateur pour personnaliser l'email
    
    Returns:
        bool: True si l'email a été envoyé avec succès, False sinon
    """
    # En mode simulation/développement
    if True:  # À remplacer par une vérification d'environnement en production
        # Simuler l'envoi d'email et journaliser
        log_email_send(recipient_email, user_data)
        return True
    
    # Code pour l'envoi réel d'emails (à activer en production)
    try:
        # Créer le message
        msg = MIMEMultipart()
        msg['From'] = "noreply@ied-formation.fr"
        msg['To'] = recipient_email
        msg['Subject'] = f"Votre rapport de perspectives salariales ESG - {user_data.get('metier', 'Métier durable')}"
        
        # Corps de l'email
        prenom = user_data.get("prenom", "")
        metier = user_data.get("metier", "")
        
        email_body = f"""
        <html>
        <body style="font-family: Arial, sans-serif; color: #333;">
            <div style="padding: 20px; max-width: 600px; margin: 0 auto;">
                <div style="background-color: #003366; padding: 20px; color: white; text-align: center;">
                    <h1>Institut d'Économie Durable</h1>
                </div>
                <div style="padding: 20px; border: 1px solid #ddd; border-top: none;">
                    <p>Bonjour {prenom},</p>
                    <p>Nous vous remercions d'avoir utilisé notre calculateur de carrière ESG.</p>
                    <p>Vous trouverez ci-joint votre rapport personnalisé concernant les perspectives salariales du métier <strong>{metier}</strong>.</p>
                    <p>Ce rapport contient :</p>
                    <ul>
                        <li>L'évolution salariale selon l'expérience</li>
                        <li>Les formations recommandées à l'Institut d'Économie Durable</li>
                        <li>Des informations pratiques pour votre orientation professionnelle</li>
                    </ul>
                    <p>Notre équipe pédagogique reste à votre disposition pour répondre à toutes vos questions concernant nos formations aux métiers de l'économie durable.</p>
                    <p>Cordialement,</p>
                    <p><strong>L'équipe de l'Institut d'Économie Durable</strong></p>
                </div>
                <div style="font-size: 12px; color: #666; margin-top: 20px; text-align: center;">
                    <p>© Institut d'Économie Durable - Tous droits réservés</p>
                    <p>Vous recevez cet email car vous avez utilisé notre calculateur de carrière ESG.</p>
                </div>
            </div>
        </body>
        </html>
        """
        
        # Attacher le corps HTML
        part = MIMEText(email_body, 'html')
        msg.attach(part)
        
        # Attacher le PDF
        with open(pdf_path, 'rb') as f:
            part = MIMEApplication(f.read(), Name=os.path.basename(pdf_path))
            part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
            msg.attach(part)
        
        # Configurer le serveur SMTP
        # En production, utiliser des variables d'environnement
        smtp_server = os.environ.get("SMTP_SERVER", "smtp.example.com")
        smtp_port = int(os.environ.get("SMTP_PORT", "587"))
        smtp_username = os.environ.get("SMTP_USERNAME", "")
        smtp_password = os.environ.get("SMTP_PASSWORD", "")
        
        # Établir une connexion sécurisée
        context = ssl.create_default_context()
        
        # Envoyer l'email
        with smtplib.SMTP(smtp_server, smtp_port) as server:
            server.starttls(context=context)
            server.login(smtp_username, smtp_password)
            server.send_message(msg)
        
        # Journaliser l'envoi
        log_email_send(recipient_email, user_data)
        
        return True
    
    except Exception as e:
        st.error(f"Erreur lors de l'envoi de l'email: {str(e)}")
        return False

def log_email_send(recipient_email, user_data):
    """
    Journalise l'envoi d'email pour un suivi des leads et future importation Hubspot.
    
    Args:
        recipient_email (str): Email du destinataire
        user_data (dict): Données de l'utilisateur
    """
    log_file = "logs/email_sends.csv"
    file_exists = os.path.isfile(log_file)
    
    # Préparer les données du lead
    lead_data = {
        "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
        "email": recipient_email,
        "prenom": user_data.get("prenom", ""),
        "nom": user_data.get("nom", ""),
        "telephone": user_data.get("telephone", ""),
        "niveau_etudes": user_data.get("niveau_etudes", ""),
        "formation": user_data.get("formation", ""),
        "experience": user_data.get("experience", ""),
        "interets": ",".join(user_data.get("interets", [])),
        "metier_interesse": user_data.get("metier", ""),
        "source": "Calculateur ESG",
        "consentement_rgpd": "Oui"
    }
    
    # Écrire dans le fichier CSV
    with open(log_file, mode='a', newline='', encoding='utf-8') as f:
        fieldnames = lead_data.keys()
        writer = csv.DictWriter(f, fieldnames=fieldnames)
        
        if not file_exists:
            writer.writeheader()
        
        writer.writerow(lead_data)

def send_to_hubspot(lead_data):
    """
    Envoie les données du lead à Hubspot (fonction squelette à implémenter quand Hubspot sera disponible).
    
    Args:
        lead_data (dict): Données du lead à envoyer à Hubspot
    
    Returns:
        bool: True si l'envoi a réussi, False sinon
    """
    # Ce code est un squelette à compléter quand Hubspot sera disponible
    try:
        # Exemple de structure pour une future intégration Hubspot
        hubspot_data = {
            "properties": {
                "email": lead_data.get("email", ""),
                "firstname": lead_data.get("prenom", ""),
                "lastname": lead_data.get("nom", ""),
                "phone": lead_data.get("telephone", ""),
                "niveau_etudes": lead_data.get("niveau_etudes", ""),
                "formation_actuelle": lead_data.get("formation", ""),
                "experience": lead_data.get("experience", ""),
                "interets_esg": lead_data.get("interets", ""),
                "metier_interesse": lead_data.get("metier", ""),
                "source": "Calculateur ESG",
                "hs_legal_basis": "Legitimate interest",
                "consentement_communications": True if lead_data.get("consentement_rgpd") == "Oui" else False
            }
        }
        
        # Ici viendra le code d'appel à l'API Hubspot
        # Ex: requests.post('https://api.hubapi.com/crm/v3/objects/contacts', json=hubspot_data, headers=headers)
        
        return True
    
    except Exception as e:
        print(f"Erreur lors de l'envoi à Hubspot: {str(e)}")
        return False

# Fonctions d'interface utilisateur
def display_progress_bar(percent):
    """Affiche une barre de progression."""
    st.markdown(
        f"""
        <div class="progress-container">
            <div class="progress-bar">
                <div class="progress-bar-fill" style="width: {percent}%;"></div>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

def display_header(step):
    """Affiche l'en-tête avec logo et titre."""
    col1, col2 = st.columns([1, 5])
    
    with col1:
        st.markdown("""
        <div class="logo-container">
            <h3>🌱 IED</h3>
        </div>
        """, unsafe_allow_html=True)
    
    with col2:
        st.markdown("""
        <div class="title-container">
            <h1>Calculateur de Carrière en Économie Durable</h1>
        </div>
        """, unsafe_allow_html=True)
    
    # Déterminer le pourcentage de progression en fonction de l'étape
    progress_percent = {
        "accueil": 5,
        "profil": 33,
        "metier": 66,
        "resultats": 100
    }
    
    display_progress_bar(progress_percent.get(step, 0))

def page_accueil():
    """Affiche la page d'accueil."""
    display_header("accueil")
    
    st.markdown("""
    ## Découvrez votre potentiel de carrière dans l'économie durable
    
    Bienvenue sur le calculateur de carrière de l'**Institut d'Économie Durable**. 
    Cet outil vous permet de visualiser les perspectives salariales et d'évolution des métiers 
    de la transition écologique et sociale.
    
    ### Comment ça marche ?
    
    1. **Parlez-nous de vous** - Votre niveau d'études, votre formation actuelle
    2. **Explorez les métiers** - Découvrez les secteurs et métiers qui vous correspondent
    3. **Analysez vos résultats** - Visualisez les perspectives d'évolution salariale
    
    ### Pourquoi l'économie durable ?
    
    Les métiers de la durabilité sont parmi les plus prometteurs pour les années à venir. 
    Avec une croissance estimée à 20% par an, ce secteur offre des opportunités diversifiées 
    pour contribuer positivement à la transition écologique tout en développant une carrière épanouissante.
    """)
    
    # Bouton pour démarrer
    if st.button("Commencer l'exploration ➡️"):
        # Initialiser la session
        st.session_state.step = "profil"
        st.rerun()

def page_profil():
    """Affiche la page du profil utilisateur."""
    display_header("profil")
    
    st.markdown("## Étape 1: Parlez-nous de vous")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Niveau d'études
        niveau_etudes = st.selectbox(
            "Quel est votre niveau d'études actuel ou visé ?",
            options=["Bac", "Bac+2 / Bac+3", "Bac+4 / Bac+5", "Bac+6 et plus"],
            key="niveau_etudes"
        )
        
        # Formation
        formation = st.selectbox(
            "Dans quel domaine êtes-vous formé(e) ?",
            options=["Commerce/Gestion", "Ingénierie/Technique", "Sciences Humaines", 
                    "Droit", "Finance", "Sciences", "Autre"],
            key="formation"
        )
    
    with col2:
        # Expérience
        experience = st.radio(
            "Quelle expérience professionnelle avez-vous ?",
            options=["Aucune (étudiant)", "Stage/Alternance", "0-2 ans", "2-5 ans", "5-10 ans", "10+ ans"],
            key="experience"
        )
        
        # Intérêt ESG
        interet_esg = st.multiselect(
            "Quels aspects de l'ESG vous intéressent le plus ?",
            options=["Environnement", "Social", "Gouvernance", "Finance durable", "Économie circulaire", 
                    "Biodiversité", "Transition énergétique"],
            key="interet_esg"
        )
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    
    with col2:
        if st.button("Étape suivante ➡️"):
            # Vérification que les champs sont remplis
            if "interet_esg" in st.session_state and len(st.session_state.interet_esg) > 0:
                st.session_state.step = "metier"
                st.rerun()
            else:
                st.error("Veuillez sélectionner au moins un centre d'intérêt.")

def page_metier():
    """Affiche la page de sélection du métier."""
    display_header("metier")
    
    st.markdown("## Étape 2: Explorez les métiers de l'économie durable")
    
    # Charger les données
    métiers_par_secteur = get_métiers_par_secteur()
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Sélection du secteur
        secteur_selectionne = st.selectbox(
            "Dans quel secteur souhaitez-vous travailler ?",
            options=list(métiers_par_secteur.keys()),
            key="secteur"
        )
    
    with col2:
        # Sélection du métier basée sur le secteur
        metier_selectionne = st.selectbox(
            "Quel métier vous intéresse ?",
            options=métiers_par_secteur[secteur_selectionne],
            key="metier"
        )
    
    # Afficher la description du métier
    df = load_data()
    description = df[df['Métier'] == metier_selectionne]['Description'].iloc[0]
    
    st.markdown("### Description du métier")
    st.info(description)
    
    # Navigation
    col1, col2 = st.columns([1, 1])
    
    with col1:
        if st.button("⬅️ Étape précédente"):
            st.session_state.step = "profil"
            st.rerun()
    
    with col2:
        if st.button("Voir les résultats ➡️"):
            st.session_state.step = "resultats"
            st.rerun()

def page_resultats():
    """Affiche la page des résultats."""
    display_header("resultats")
    
    st.markdown("## Étape 3: Vos perspectives de carrière")
    
    # Récupérer les données de session
    metier_selectionne = st.session_state.get("metier", "Analyste ESG")
    niveau_etudes = st.session_state.get("niveau_etudes", "Bac+4 / Bac+5")
    interets = st.session_state.get("interet_esg", ["Environnement"])
    formation = st.session_state.get("formation", "")
    experience = st.session_state.get("experience", "")
    
    # Charger et filtrer les données
    df = load_data()
    df_filtered = df[df['Métier'] == metier_selectionne]
    
    # Afficher le résumé du profil
    st.markdown("### Votre profil")
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"**Niveau d'études**: {niveau_etudes}")
        st.markdown(f"**Formation**: {formation}")
        st.markdown(f"**Métier ciblé**: {metier_selectionne}")
    
    with col2:
        st.markdown(f"**Expérience**: {experience}")
        st.markdown(f"**Centres d'intérêt**: {', '.join(interets)}")
    
    # Statut pour suivre l'envoi d'email
    if "email_sent" not in st.session_state:
        st.session_state.email_sent = False
    
    # Compteurs pour le suivi des conversions
    if "pdf_count" not in st.session_state:
        st.session_state.pdf_count = 0
    if "email_count" not in st.session_state:
        st.session_state.email_count = 0
    
    # Afficher le bloc de capture d'email AVANT les résultats détaillés
    if not st.session_state.email_sent:
        st.markdown("---")
        
        # Utiliser la classe CSS personnalisée pour le bloc de capture
        st.markdown('<div class="lead-capture-box">', unsafe_allow_html=True)
        
        # Titre attractif avec icône
        st.markdown(f"### 📊 Recevez votre rapport de carrière personnalisé")
        
        # Message ciblé et concis
        st.markdown(f"Obtenez une analyse détaillée des perspectives salariales, des compétences requises et des formations recommandées pour le métier de **{metier_selectionne}**.")
        
        # Formulaire simplifié
        with st.form("contact_form"):
            col1, col2 = st.columns([1, 1])
            
            with col1:
                prenom = st.text_input("Prénom", placeholder="Votre prénom")
                email = st.text_input("Email", placeholder="votre.email@exemple.com")
            
            with col2:
                # Champs additionnels cachés initialement ou affichés différemment
                nom = st.text_input("Nom (optionnel)", placeholder="Votre nom")
                # On pourrait aussi utiliser un expander pour les champs optionnels
                # with st.expander("Informations complémentaires (optionnel)"):
                #    telephone = st.text_input("Téléphone")
            
            # RGPD simplifié
            rgpd_consent = st.checkbox(
                "J'accepte de recevoir mon rapport et des informations sur les formations IED"
            )
            
            # Bouton d'action clair avec style personnalisé
            col_button = st.columns(1)[0]
            with col_button:
                submitted = st.form_submit_button("📩 Recevoir mon rapport complet", 
                                                 use_container_width=True)
            
            if submitted:
                if email and prenom and rgpd_consent:
                    with st.spinner("Génération de votre rapport en cours..."):
                        # Préparer les données utilisateur
                        user_data = {
                            "prenom": prenom,
                            "nom": nom,
                            "email": email,
                            "telephone": "",
                            "niveau_etudes": niveau_etudes,
                            "formation": formation,
                            "experience": experience,
                            "interets": interets,
                            "metier": metier_selectionne,
                            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                            "rgpd_consent": "Oui" if rgpd_consent else "Non"
                        }
                        
                        # Générer un nom de fichier unique
                        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
                        pdf_filename = f"rapport_carriere_{metier_selectionne.replace(' ', '_').lower()}_{timestamp}.pdf"
                        pdf_path = os.path.join(tempfile.gettempdir(), pdf_filename)
                        
                        # Générer le PDF
                        generate_salary_report_pdf(user_data, df_filtered, pdf_path)
                        st.session_state.pdf_count += 1
                        
                        # Envoyer l'email avec le PDF (simulé en mode développement)
                        if send_results_email(email, pdf_path, user_data):
                            st.session_state.email_count += 1
                            st.session_state.email_sent = True
                            st.session_state.lead_saved = user_data
                            
                            st.success("✅ Votre rapport a été généré et vous sera envoyé dans quelques instants ! Voici un aperçu des résultats ci-dessous.")
                            
                            # Préparer pour Hubspot (à implémenter plus tard)
                            # send_to_hubspot(user_data)
                        else:
                            st.error("Une erreur est survenue lors de l'envoi de l'email. Veuillez réessayer plus tard.")
                else:
                    st.error("Veuillez remplir votre prénom, email et accepter les conditions.")
        
        st.markdown('</div>', unsafe_allow_html=True)
    
    # Message de confirmation permanent après envoi
    if st.session_state.email_sent:
        st.success("✅ Votre rapport complet a été envoyé ! Consultez vos emails pour plus de détails sur les formations et l'évolution de carrière.")
    
    st.markdown("---")
    
    # Afficher les résultats
    st.markdown("### Perspectives salariales")
    
    col1, col2 = st.columns([3, 2])
    
    with col1:
        # Graphique d'évolution salariale
        fig = create_salary_chart(df_filtered)
        st.pyplot(fig)
        
        # Teaser si le rapport a été envoyé
        if st.session_state.email_sent:
            st.info("📝 **Votre rapport PDF contient des informations supplémentaires** sur les compétences requises et l'évolution de carrière.")
    
    with col2:
        # Tableau des données
        st.markdown("#### Détail des salaires")
        st.dataframe(
            df_filtered[['Expérience', 'Salaire_Min', 'Salaire_Max', 'Salaire_Moyen']].rename(
                columns={
                    'Salaire_Min': 'Minimum (€)',
                    'Salaire_Max': 'Maximum (€)',
                    'Salaire_Moyen': 'Moyen (€)'
                }
            ),
            hide_index=True,
            use_container_width=True
        )
    
    # Navigation (seulement si nécessaire)
    st.markdown("---")
    
    # Statistiques de conversion (visibles uniquement en mode développement)
    if st.session_state.email_sent and st.checkbox("Afficher les statistiques de conversion", value=False):
        st.info(f"PDFs générés: {st.session_state.pdf_count}, Emails envoyés: {st.session_state.email_count}")
    
    # Option pour recommencer 
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("⬅️ Revenir à la sélection du métier"):
            st.session_state.step = "metier"
            st.rerun()
    
    with col2:
        if st.session_state.email_sent and st.button("🔄 Recommencer l'exploration"):
            # Conserver les statistiques et les données lead mais réinitialiser le parcours
            for key in list(st.session_state.keys()):
                if key not in ['pdf_count', 'email_count', 'lead_saved']:
                    if key in st.session_state:
                        del st.session_state[key]
            st.session_state.step = "accueil"
            st.rerun()

# Application principale
def main():
    """Fonction principale de l'application."""
    # Charger le CSS personnalisé
    load_custom_css()
    
    # Initialiser la session si nécessaire
    if "step" not in st.session_state:
        st.session_state.step = "accueil"
    
    # Afficher la page correspondante à l'étape actuelle
    if st.session_state.step == "accueil":
        page_accueil()
    elif st.session_state.step == "profil":
        page_profil()
    elif st.session_state.step == "metier":
        page_metier()
    elif st.session_state.step == "resultats":
        page_resultats()

# Point d'entrée
if __name__ == "__main__":
    main()