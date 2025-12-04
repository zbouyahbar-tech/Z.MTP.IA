import streamlit as st
import google.generativeai as genai
import requests
from bs4 import BeautifulSoup
import PyPDF2
import io

# --- Configuration de la page ---
st.set_page_config(
    page_title="MTP-IA Assistant",
    page_icon="🤖",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- Fonctions Utilitaires ---

def extract_text_from_pdf(file):
    """Extrait le texte d'un fichier PDF téléchargé."""
    try:
        pdf_reader = PyPDF2.PdfReader(file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text() or ""
        return text
    except Exception as e:
        return f"Erreur de lecture du PDF: {e}"

def scrape_website(url):
    """Récupère le texte visible d'une page web."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'}
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # On supprime les scripts et styles pour ne garder que le texte
        for script in soup(["script", "style", "nav", "footer"]):
            script.decompose()
            
        text = soup.get_text(separator=' ', strip=True)
        # Limiter la taille pour éviter de saturer le context window si la page est énorme
        return text[:10000] 
    except Exception as e:
        return f"Erreur lors de l'accès au site web: {e}"

def initialize_ai(api_key):
    """Configure l'IA Google Gemini."""
    if not api_key:
        return None
    genai.configure(api_key=api_key)
    # Utilisation du modèle flash pour la rapidité
    return genai.GenerativeModel('gemini-1.5-flash')

# --- Gestion de l'état (Session State) ---
if "messages" not in st.session_state:
    st.session_state.messages = []
if "context_data" not in st.session_state:
    st.session_state.context_data = ""

# --- Navigation ---
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à", ["Accueil", "Assistant MTP-IA"])

# --- PAGE 1 : ACCUEIL / INTRODUCTION ---
if page == "Accueil":
    # CSS personnalisé pour l'intro
    st.markdown("""
    <style>
        .main-title { font-size: 3.5rem; color: #4F46E5; text-align: center; font-weight: bold; margin-bottom: 0;}
        .subtitle { font-size: 1.5rem; color: #6B7280; text-align: center; margin-bottom: 2rem;}
        .feature-card { background-color: #f3f4f6; padding: 20px; border-radius: 10px; margin: 10px 0; border-left: 5px solid #4F46E5;}
    </style>
    """, unsafe_allow_html=True)

    st.markdown('<div class="main-title">Bienvenue sur MTP-IA</div>', unsafe_allow_html=True)
    st.markdown('<div class="subtitle">Votre assistant intelligent augmenté par vos données</div>', unsafe_allow_html=True)

    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.markdown("""
        <div class="feature-card">
            <h3>🧠 Intelligence Artificielle</h3>
            <p>Propulsé par les derniers modèles de langage pour répondre à toutes vos questions complexes.</p>
        </div>
        """, unsafe_allow_html=True)
        
    with col2:
        st.markdown("""
        <div class="feature-card">
            <h3>📄 Analyse de Documents</h3>
            <p>Importez vos fichiers PDF. L'IA les lit, les analyse et répond en fonction de leur contenu.</p>
        </div>
        """, unsafe_allow_html=True)

    with col3:
        st.markdown("""
        <div class="feature-card">
            <h3>🌐 Accès Web</h3>
            <p>Donnez une URL à l'assistant. Il lira le contenu de la page pour enrichir sa réponse.</p>
        </div>
        """, unsafe_allow_html=True)

    st.divider()
    
    col_center = st.columns([1, 2, 1])
    with col_center[1]:
        st.info("👈 Utilisez le menu latéral pour accéder à l'interface de discussion.")
        if st.button("Lancer l'Assistant maintenant", type="primary", use_container_width=True):
            # Hack simple pour changer de page via le bouton (nécessite un rerun parfois)
            st.toast("Veuillez cliquer sur 'Assistant MTP-IA' dans le menu latéral.", icon="ℹ️")


# --- PAGE 2 : ASSISTANT IA ---
elif page == "Assistant MTP-IA":
    st.title("💬 Discussion avec MTP-IA")
    
    # --- Sidebar Configuration IA ---
    with st.sidebar:
        st.markdown("---")
        st.header("⚙️ Configuration")
        
        # Clé API (Nécessaire pour que ça marche réellement)
        api_key = st.text_input("Clé API Google Gemini", type="password", help="Obtenez une clé sur aistudio.google.com")
        
        st.markdown("---")
        st.header("📂 Sources de données")
        
        # 1. Upload de Fichier
        uploaded_file = st.file_uploader("Ajouter un fichier (PDF)", type=['pdf'])
        if uploaded_file:
            with st.spinner("Lecture du fichier..."):
                file_text = extract_text_from_pdf(uploaded_file)
                st.session_state.context_data += f"\n\n--- CONTENU FICHIER ({uploaded_file.name}) ---\n{file_text}"
                st.success(f"Fichier '{uploaded_file.name}' analysé !")

        # 2. Ajout de Lien
        url_input = st.text_input("Ajouter une URL à analyser")
        if st.button("Lire l'URL"):
            if url_input:
                with st.spinner("Analyse de la page web..."):
                    web_text = scrape_website(url_input)
                    st.session_state.context_data += f"\n\n--- CONTENU WEB ({url_input}) ---\n{web_text}"
                    st.success("Contenu web ajouté au contexte !")

        # Bouton pour vider le contexte
        if st.button("🗑️ Vider le contexte mémoire"):
            st.session_state.context_data = ""
            st.session_state.messages = []
            st.rerun()

    # --- Zone de Chat ---
    
    # Afficher l'historique
    for message in st.session_state.messages:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    # Entrée utilisateur
    if prompt := st.chat_input("Posez votre question ici..."):
        # 1. Afficher le message utilisateur
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.markdown(prompt)

        # 2. Générer la réponse
        if not api_key:
            with st.chat_message("assistant"):
                st.error("Veuillez entrer une clé API Google Gemini dans la barre latérale pour activer l'IA.")
        else:
            with st.chat_message("assistant"):
                message_placeholder = st.empty()
                try:
                    model = initialize_ai(api_key)
                    
                    # Construction du prompt avec le contexte (RAG simplifié)
                    full_prompt = prompt
                    if st.session_state.context_data:
                        full_prompt = f"""Tu es un assistant IA utile. Utilise les informations de contexte ci-dessous si elles sont pertinentes pour répondre à la question de l'utilisateur.
                        
                        CONTEXTE DONNÉES:
                        {st.session_state.context_data}
                        
                        QUESTION UTILISATEUR:
                        {prompt}
                        """
                    
                    # Appel à l'IA (Streamé pour l'effet machine à écrire)
                    response = model.generate_content(full_prompt, stream=True)
                    full_response = ""
                    
                    for chunk in response:
                        if chunk.text:
                            full_response += chunk.text
                            message_placeholder.markdown(full_response + "▌")
                    
                    message_placeholder.markdown(full_response)
                    
                    # Sauvegarder la réponse
                    st.session_state.messages.append({"role": "assistant", "content": full_response})
                    
                except Exception as e:
                    st.error(f"Une erreur s'est produite : {e}")
