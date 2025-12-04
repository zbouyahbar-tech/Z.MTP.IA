import streamlit as st
import openai
import requests
from bs4 import BeautifulSoup
import PyPDF2

# --- 1. CONFIGURATION INITIALE ---
st.set_page_config(
    page_title="MTP.IA Enterprise",
    page_icon="🧬",
    layout="wide",
    initial_sidebar_state="expanded"
)

# --- 2. INTERFACE ENGINE (LE DESIGN PRO) ---
def load_professional_ui():
    st.markdown("""
    <style>
        /* Import d'une police professionnelle (Inter) */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;600&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', sans-serif;
        }

        /* Nettoyage de l'interface Streamlit */
        #MainMenu {visibility: hidden;}
        footer {visibility: hidden;}
        header {visibility: hidden;}

        /* Style des bulles de chat */
        .stChatMessage {
            background-color: #262730;
            border: 1px solid #444;
            border-radius: 12px;
            padding: 15px;
            margin-bottom: 10px;
            box-shadow: 0 2px 5px rgba(0,0,0,0.1);
        }

        /* Style spécifique pour l'utilisateur */
        div[data-testid="stChatMessage"]:nth-child(odd) {
            background-color: #1E1E1E; /* Plus sombre pour user */
        }

        /* Badges de statut en haut */
        .status-badge {
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: 600;
            font-size: 0.85rem;
            text-transform: uppercase;
            letter-spacing: 1px;
            display: inline-block;
            margin-bottom: 20px;
        }
        
        .badge-general { background-color: #3b82f6; color: white; } /* Bleu */
        .badge-gathering { background-color: #eab308; color: black; } /* Jaune */
        .badge-simulation { background-color: #22c55e; color: white; box-shadow: 0 0 15px rgba(34, 197, 94, 0.4); } /* Vert Néon */

        /* Boutons */
        .stButton>button {
            border-radius: 8px;
            font-weight: 600;
            transition: all 0.3s ease;
        }
        .stButton>button:hover {
            transform: translateY(-2px);
            box-shadow: 0 4px 12px rgba(0,0,0,0.2);
        }

        /* Sidebar plus propre */
        section[data-testid="stSidebar"] {
            background-color: #111;
            border-right: 1px solid #333;
        }
    </style>
    """, unsafe_allow_html=True)

def render_header(mode, persona_role=None):
    """Affiche l'en-tête dynamique"""
    col1, col2 = st.columns([3, 1])
    with col1:
        st.title("🧬 MTP.IA")
        st.caption("Méta-Transformateur de Processus | v4.2 Enterprise")
    with col2:
        if mode == "GENERAL":
            st.markdown('<div class="status-badge badge-general">● Mode Standard</div>', unsafe_allow_html=True)
        elif mode == "GATHERING":
            st.markdown('<div class="status-badge badge-gathering">● Architecture en cours</div>', unsafe_allow_html=True)
        elif mode == "SIMULATION":
            st.markdown(f'<div class="status-badge badge-simulation">● {persona_role or "IA ACTIVE"}</div>', unsafe_allow_html=True)

# Chargement du design
load_professional_ui()

# --- 3. VARIABLES DE SESSION (MÉMOIRE) ---
if "messages" not in st.session_state:
    st.session_state["messages"] = [{"role": "assistant", "content": "Bonjour. Je suis MTP. \n\nMon interface est prête. Je peux concevoir des outils, analyser des documents ou générer des médias. Par quoi commençons-nous ?"}]
if "mode" not in st.session_state:
    st.session_state["mode"] = "GENERAL"
if "gathering_history" not in st.session_state:
    st.session_state["gathering_history"] = []
if "context_data" not in st.session_state:
    st.session_state["context_data"] = ""
if "api_key" not in st.session_state:
    st.session_state["api_key"] = ""
if "current_role_name" not in st.session_state:
    st.session_state["current_role_name"] = ""

# --- 4. SIDEBAR (PANNEAU DE CONTRÔLE) ---
with st.sidebar:
    st.markdown("### ⚙️ Paramètres Système")
    
    # API Key Discrète
    with st.expander("🔐 Clé API OpenAI", expanded=not st.session_state["api_key"]):
        key_input = st.text_input("Insérer la clé (sk-...)", type="password", key="api_key_input")
        if key_input:
            st.session_state["api_key"] = key_input
            openai.api_key = key_input

    st.markdown("---")
    st.markdown("### 📂 Ingestion de Données")
    st.caption("Ces fichiers nourriront l'intelligence de MTP.")
    
    tab1, tab2 = st.tabs(["📄 Fichiers", "🌐 Web"])
    
    with tab1:
        uploaded_file = st.file_uploader("Drop PDF/TXT", type=['pdf', 'txt'], label_visibility="collapsed")
        if uploaded_file and st.button("Ingérer le document", use_container_width=True):
            text = ""
            if uploaded_file.type == "application/pdf":
                reader = PyPDF2.PdfReader(uploaded_file)
                for page in reader.pages: text += page.extract_text()
            else:
                text = str(uploaded_file.read(), "utf-8")
            st.session_state["context_data"] += f"\n[DOC: {uploaded_file.name}] {text[:8000]}"
            st.toast("Document mémorisé avec succès !", icon="✅")

    with tab2:
        url = st.text_input("URL à scraper", placeholder="https://...")
        if url and st.button("Lire le site", use_container_width=True):
            try:
                res = requests.get(url, timeout=5)
                soup = BeautifulSoup(res.content, 'html.parser')
                text = " ".join([p.text for p in soup.find_all('p')])
                st.session_state["context_data"] += f"\n[WEB: {url}] {text[:5000]}"
                st.toast("Page web analysée !", icon="✅")
            except: st.error("Erreur lecture URL")
    
    st.markdown("---")
    
    # Zone de danger / Reset
    if st.session_state["mode"] == "SIMULATION":
        st.warning("⚠️ IA Spécialisée en cours d'exécution")
        if st.button("🔴 DÉTRUIRE L'IA (Reset)", use_container_width=True):
            st.session_state["mode"] = "GENERAL"
            st.session_state["gathering_history"] = []
            st.session_state["current_role_name"] = ""
            st.session_state["messages"].append({"role": "assistant", "content": "IA détruite. Retour au noyau MTP standard."})
            st.rerun()

# --- 5. LOGIQUE INTELLIGENTE (BACKEND) ---

def generate_image(prompt):
    try:
        res = openai.Image.create(model="dall-e-3", prompt=prompt, size="1024x1024", n=1)
        return res.data[0].url
    except: return None

def detect_intent(text):
    t = text.lower()
    if any(x in t for x in ["crée", "conçois", "nouvelle ia", "nouveau bot", "fabrique"]): return "CREATE"
    if any(x in t for x in ["image", "photo", "dessine"]): return "IMAGE"
    return "CHAT"

def mtp_architect_brain(user_input, history_text, context_docs):
    """Le cerveau qui décide s'il faut poser des questions ou transformer"""
    system_prompt = f"""
    Tu es MTP, architecte d'IA.
    Données : {context_docs}
    Historique Conception : {history_text}
    Dernière entrée : {user_input}
    
    1. Si tu as TOUT (Rôle, Ton, Format, Cible), réponds par le JSON : {{"action": "TRANSFORM", "role_name": "NOM_DU_ROLE"}}
    2. Sinon, pose UNE question pertinente pour avancer.
    """
    # Note: On simplifie le retour texte pour ce code, mais un JSON serait idéal.
    # Ici on garde le mode texte libre pour la fluidité.
    prompt_simple = f"Si tu as toutes les infos pour créer l'IA (rôle, ton, format), réponds exactement: '[TRANSFORMATION: NOM_DU_ROLE]'. Sinon, pose la question suivante la plus pertinente. Historique: {history_text}. User: {user_input}"
    
    response = openai.ChatCompletion.create(
        model="gpt-4-turbo",
        messages=[{"role": "system", "content": prompt_simple}]
    )
    return response.choices[0].message.content

# --- 6. AFFICHAGE PRINCIPAL ---

# Affichage du Header personnalisé
render_header(st.session_state["mode"], st.session_state["current_role_name"])

# Zone de chat
chat_container = st.container()

with chat_container:
    for msg in st.session_state.messages:
        # Choix de l'avatar
        avatar = "🧬" if msg["role"] == "assistant" else "👤"
        if st.session_state["mode"] == "SIMULATION" and msg["role"] == "assistant":
            avatar = "🤖" # Avatar différent pour l'IA créée

        with st.chat_message(msg["role"], avatar=avatar):
            if "image_url" in msg and msg["image_url"]:
                st.image(msg["image_url"], width=500, caption="Généré par MTP")
            st.markdown(msg["content"])

# Input Utilisateur
if prompt := st.chat_input("Envoyer un message à MTP..."):
    
    if not st.session_state["api_key"]:
        st.error("⚠️ Clé API manquante dans la barre latérale.")
        st.stop()

    # User Msg
    st.session_state.messages.append({"role": "user", "content": prompt})
    with st.chat_message("user", avatar="👤"):
        st.markdown(prompt)

    response = ""
    img_url = None

    # === MODE GÉNÉRAL ===
    if st.session_state["mode"] == "GENERAL":
        intent = detect_intent(prompt)
        
        if intent == "CREATE":
            st.session_state["mode"] = "GATHERING"
            st.session_state["gathering_history"].append(f"Demande initiale: {prompt}")
            response = "🏗️ **Protocole d'Architecture Activé.**\n\nJe vais concevoir cette IA avec vous. J'analyse votre demande... Dites-moi en plus sur ce que vous attendez exactement (ou laissez-moi vous guider)."
            st.rerun() # Refresh pour changer le badge header
            
        elif intent == "IMAGE":
            with st.spinner("🎨 Création visuelle en cours..."):
                img_url = generate_image(prompt)
                response = f"Voici l'image pour : *{prompt}*"
        
        else: # Chat standard
            res = openai.ChatCompletion.create(
                model="gpt-4-turbo",
                messages=[{"role": "system", "content": f"Tu es MTP. Docs: {st.session_state['context_data']}"}, {"role": "user", "content": prompt}]
            )
            response = res.choices[0].message.content

    # === MODE CONCEPTION ===
    elif st.session_state["mode"] == "GATHERING":
        history_txt = "\n".join(st.session_state["gathering_history"])
        decision = mtp_architect_brain(prompt, history_txt, st.session_state["context_data"])
        
        if "[TRANSFORMATION:" in decision:
            # Extraction du nom du rôle
            role_name = decision.split(":")[1].replace("]", "").strip()
            st.session_state["current_role_name"] = role_name
            
            response = f"✅ **Spécifications validées.**\n\nCompilation du modèle neuronal pour : **{role_name}**...\n\n🚀 **TRANSFORMATION**"
            st.session_state["mode"] = "SIMULATION"
            st.rerun()
        else:
            response = decision
            st.session_state["gathering_history"].append(f"User: {prompt}")
            st.session_state["gathering_history"].append(f"MTP: {decision}")

    # === MODE SIMULATION ===
    elif st.session_state["mode"] == "SIMULATION":
        specs_history = "\n".join(st.session_state["gathering_history"])
        system_prompt = f"""
        TU ES L'IA DÉFINIE PAR : {specs_history}
        CONTEXTE : {st.session_state['context_data']}
        Si image demandée, réponds [IMG].
        """
        
        res = openai.ChatCompletion.create(
            model="gpt-4-turbo",
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": prompt}]
        )
        response = res.choices[0].message.content
        
        if "[IMG]" in response:
            response = response.replace("[IMG]", "")
            with st.spinner("L'IA spécialisée génère une image..."):
                img_url = generate_image(prompt)

    # Affichage Réponse
    st.session_state.messages.append({"role": "assistant", "content": response, "image_url": img_url})
    with st.chat_message("assistant", avatar="🤖" if st.session_state["mode"] == "SIMULATION" else "🧬"):
        if img_url: st.image(img_url, width=500)
        st.markdown(response)
