"""
app.py — Interface Streamlit · Thème Al-Noor (Zellige Noir)
Faculté de Charia d'Aït Melloul · EST Guelmim
Encadrant : Pr. El Qasimi
"""

import sys
import os

# Ajout du dossier racine au sys.path pour les imports
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

import streamlit as st
from langchain_core.messages import HumanMessage

from graph.workflow import build_workflow


# ── Chargement unique du workflow ─────────────────────────────────────────────
@st.cache_resource
def charger_workflow():
    return build_workflow()


# ── Configuration de la page ──────────────────────────────────────────────────
st.set_page_config(
    page_title="Al-Noor · Faculté de Charia",
    page_icon="🌙",
    layout="wide",
    initial_sidebar_state="expanded",
)


# ── Injection CSS — Thème Zellige Noir ────────────────────────────────────────
st.markdown("""
<link rel="preconnect" href="https://fonts.googleapis.com">
<link href="https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@300;400;500;700&display=swap" rel="stylesheet">

<style>
/* ── Variables ───────────────────────────────────── */
:root {
    --bg:         #07090f;
    --surface:    #0d1120;
    --surface2:   #121828;
    --teal:       #00c3a0;
    --teal-dim:   rgba(0,195,160,0.08);
    --gold:       #c8a050;
    --gold-dim:   rgba(200,160,80,0.10);
    --text:       #e4dfd6;
    --text-dim:   #7a8ba8;
    --border:     rgba(0,195,160,0.12);
    --border2:    rgba(0,195,160,0.22);
}

/* ── App background + motif étoile islamique ─────── */
.stApp {
    background-color: var(--bg) !important;
    background-image: url("data:image/svg+xml,%3Csvg xmlns='http://www.w3.org/2000/svg' width='80' height='80'%3E%3Cpolygon points='40,5 44,18 56,11 49,23 62,27 49,31 56,43 44,36 40,49 36,36 24,43 31,31 18,27 31,23 24,11 36,18' fill='none' stroke='%2300c3a0' stroke-width='0.4' opacity='0.13'/%3E%3Ccircle cx='40' cy='27' r='1.5' fill='%2300c3a0' opacity='0.07'/%3E%3C/svg%3E");
    background-size: 80px 80px;
    font-family: 'Tajawal', sans-serif !important;
}

/* ── Masquer éléments Streamlit par défaut ───────── */
#MainMenu, footer, header { visibility: hidden !important; }
.stDeployButton { display: none !important; }

/* ── Sidebar ─────────────────────────────────────── */
[data-testid="stSidebar"] {
    background-color: var(--surface) !important;
    border-right: 1px solid var(--border) !important;
}

[data-testid="stSidebar"]::before {
    content: '';
    display: block;
    height: 3px;
    background: linear-gradient(90deg, transparent, var(--teal), var(--gold), transparent);
    margin-bottom: 8px;
}

[data-testid="stSidebar"] * {
    color: var(--text-dim) !important;
    font-family: 'Tajawal', sans-serif !important;
}

[data-testid="stSidebarContent"] {
    padding: 0 !important;
}

/* ── Contenu principal ───────────────────────────── */
.main .block-container {
    padding: 0 !important;
    max-width: 100% !important;
}

/* ── Messages chat ───────────────────────────────── */

/* Conteneur général d'un message */
[data-testid="stChatMessage"] {
    background: transparent !important;
    padding: 6px 0 !important;
    gap: 14px !important;
}

/* Avatar utilisateur */
[data-testid="stChatMessage"][data-testid*="user"] [data-testid="chatAvatarIcon-user"],
.stChatMessage [data-testid="chatAvatarIcon-user"] {
    background-color: rgba(0,195,160,0.12) !important;
    border: 1px solid rgba(0,195,160,0.3) !important;
    color: var(--teal) !important;
}

/* Avatar assistant */
.stChatMessage [data-testid="chatAvatarIcon-assistant"] {
    background-color: var(--surface2) !important;
    border: 1px solid var(--border2) !important;
}

/* Bulle utilisateur */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-user"]) .stMarkdown {
    background: rgba(0,195,160,0.07) !important;
    border: 1px solid rgba(0,195,160,0.2) !important;
    border-radius: 14px 4px 14px 14px !important;
    padding: 12px 16px !important;
    color: var(--text) !important;
}

/* Bulle assistant */
[data-testid="stChatMessage"]:has([data-testid="chatAvatarIcon-assistant"]) .stMarkdown {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-left: 2px solid var(--teal) !important;
    border-radius: 4px 14px 14px 14px !important;
    padding: 12px 16px !important;
    color: var(--text) !important;
}

/* Texte dans les bulles */
[data-testid="stChatMessage"] p,
[data-testid="stChatMessage"] li,
[data-testid="stChatMessage"] span {
    color: var(--text) !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 15px !important;
    line-height: 1.7 !important;
}

/* ── Champ de saisie ─────────────────────────────── */
[data-testid="stChatInputContainer"] {
    background: var(--surface) !important;
    border: 1px solid var(--border) !important;
    border-radius: 14px !important;
    padding: 4px 8px !important;
    transition: border-color 0.2s !important;
}

[data-testid="stChatInputContainer"]:focus-within {
    border-color: var(--teal) !important;
    box-shadow: 0 0 0 3px rgba(0,195,160,0.08) !important;
}

[data-testid="stChatInputContainer"] textarea {
    background: transparent !important;
    color: var(--text) !important;
    font-family: 'Tajawal', sans-serif !important;
    font-size: 15px !important;
    caret-color: var(--teal) !important;
}

[data-testid="stChatInputContainer"] textarea::placeholder {
    color: var(--text-dim) !important;
    opacity: 0.6 !important;
}

/* Bouton envoi */
[data-testid="stChatInputContainer"] button {
    background-color: var(--teal) !important;
    border-radius: 10px !important;
    color: #07090f !important;
    transition: background 0.2s !important;
}

[data-testid="stChatInputContainer"] button:hover {
    background-color: #00dfb8 !important;
}

/* ── Spinner ─────────────────────────────────────── */
[data-testid="stSpinner"] {
    color: var(--teal) !important;
}

[data-testid="stSpinner"] * {
    color: var(--teal) !important;
    border-top-color: var(--teal) !important;
}

/* ── Scrollbar ───────────────────────────────────── */
::-webkit-scrollbar { width: 4px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: var(--border2); border-radius: 4px; }

/* ── Markdown général ────────────────────────────── */
.stMarkdown p, .stMarkdown li {
    color: var(--text) !important;
}

strong { color: var(--text) !important; }

/* ── Alerte / info ───────────────────────────────── */
[data-testid="stAlert"] {
    background: rgba(200,160,80,0.08) !important;
    border-left: 2px solid var(--gold) !important;
    color: var(--text) !important;
    border-radius: 8px !important;
}
</style>
""", unsafe_allow_html=True)


# ── Barre latérale ────────────────────────────────────────────────────────────
with st.sidebar:

    # Logo + titre
    st.markdown("""
    <div style="padding:24px 20px 16px; border-bottom:1px solid rgba(0,195,160,0.12);">

      <svg width="44" height="44" viewBox="0 0 42 42" fill="none" style="display:block; margin-bottom:12px;">
        <polygon points="21,2 25.2,13.8 36,8 29.8,18.2 42,21 29.8,23.8 36,34 25.2,28.2 21,40 16.8,28.2 6,34 12.2,23.8 0,21 12.2,18.2 6,8 16.8,13.8"
          fill="none" stroke="#00c3a0" stroke-width="1.2"/>
        <polygon points="21,7 24,16 33,13 27.5,20 35,21 27.5,22 33,29 24,26 21,35 18,26 9,29 14.5,22 7,21 14.5,20 9,13 18,16"
          fill="rgba(0,195,160,0.09)" stroke="#c8a050" stroke-width="0.6"/>
        <circle cx="21" cy="21" r="3" fill="#00c3a0" opacity="0.7"/>
      </svg>

      <div style="font-family:'Amiri',serif; font-size:24px; font-weight:700; color:#e4dfd6; letter-spacing:0.02em;">
        Al‑Noor
      </div>
      <div style="font-size:11px; font-weight:500; color:#00c3a0; letter-spacing:0.12em; text-transform:uppercase; margin-top:2px;">
        Faculté de Charia · Aït Melloul
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Description
    st.markdown("""
    <div style="padding:20px 20px 0; font-size:13px; line-height:1.65; color:#7a8ba8;">
      <p style="margin-bottom:12px;">
        Assistant virtuel spécialisé en sciences islamiques, fondé sur un système
        <strong style="color:#e4dfd6;">Agentic RAG</strong> avec LangGraph.
      </p>

      <div style="margin-bottom:8px;">
        <span style="color:#00c3a0; font-weight:500;">📗 Coran</span>
        <span style="color:#7a8ba8;"> — 6 236 versets indexés</span>
      </div>
      <div style="margin-bottom:16px;">
        <span style="color:#c8a050; font-weight:500;">📘 Hadiths</span>
        <span style="color:#7a8ba8;"> — bientôt disponible</span>
      </div>

      <div style="border-top:1px solid rgba(0,195,160,0.10); padding-top:14px; font-size:11px; color:#3a4a60;">
        <div style="margin-bottom:4px;">🔧 qwen3:8b · nomic-embed-text</div>
        <div style="margin-bottom:4px;">🗄️ PostgreSQL + pgvector</div>
        <div>⚙️ LangGraph · Ollama · Streamlit</div>
      </div>
    </div>
    """, unsafe_allow_html=True)

    # Séparateur
    st.markdown("<hr style='border:none; border-top:1px solid rgba(0,195,160,0.10); margin:20px;'>",
                unsafe_allow_html=True)

    # Bouton reset
    if st.button("✦  Nouvelle conversation", use_container_width=True, key="reset"):
        st.session_state.historique = []
        st.rerun()

    # Footer
    st.markdown("""
    <div style="padding:16px 20px; margin-top:auto;">
      <div style="display:inline-flex; align-items:center; gap:7px; padding:6px 12px;
           border-radius:20px; background:rgba(200,160,80,0.09);
           border:1px solid rgba(200,160,80,0.2); font-size:11px; color:#c8a050; font-weight:500;">
        <span style="width:6px;height:6px;border-radius:50%;background:#c8a050;display:inline-block;"></span>
        Modèle actif
      </div>
      <div style="margin-top:10px; font-size:11px; color:#3a4a60; line-height:1.5;">
        Encadrant : Pr. El Qasimi<br>
        Stage PFE · EST Guelmim
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── En-tête principal ─────────────────────────────────────────────────────────
st.markdown("""
<div style="
  display:flex; align-items:center; justify-content:space-between;
  padding:16px 36px;
  border-bottom:1px solid rgba(0,195,160,0.12);
  background:rgba(13,17,32,0.7);
  backdrop-filter:blur(12px);
  position:sticky; top:0; z-index:99;
">
  <span style="font-family:'Amiri',serif; font-size:17px; color:#e4dfd6; font-style:italic;">
    Assistant Agentic RAG — Coran &amp; Hadiths
  </span>
  <span style="display:inline-flex; align-items:center; gap:8px; padding:5px 14px;
    border-radius:20px; border:1px solid rgba(0,195,160,0.14);
    background:#0d1120; font-size:12px; color:#7a8ba8;">
    <span style="width:6px;height:6px;border-radius:50%;background:#00c3a0;display:inline-block;"></span>
    qwen3:8b · Ollama
  </span>
</div>
""", unsafe_allow_html=True)


# ── Écran de bienvenue (première visite) ──────────────────────────────────────
if "historique" not in st.session_state:
    st.session_state.historique = []

if not st.session_state.historique:
    st.markdown("""
    <div style="text-align:center; padding:60px 20px 40px; max-width:600px; margin:0 auto;">

      <svg width="64" height="64" viewBox="0 0 64 64" fill="none" style="margin:0 auto 20px; display:block;">
        <polygon points="32,3 38,20 54,12 45,28 63,32 45,36 54,52 38,44 32,61 26,44 10,52 19,36 1,32 19,28 10,12 26,20"
          fill="none" stroke="#00c3a0" stroke-width="1.4"/>
        <polygon points="32,10 36,22 48,17 42,28 55,32 42,36 48,47 36,42 32,54 28,42 16,47 22,36 9,32 22,28 16,17 28,22"
          fill="rgba(0,195,160,0.07)" stroke="#c8a050" stroke-width="0.8"/>
        <circle cx="32" cy="32" r="5" fill="#00c3a0" opacity="0.6"/>
      </svg>

      <div style="font-family:'Amiri',serif; font-size:32px; font-weight:700; color:#e4dfd6; margin-bottom:6px;">
        بسم الله الرحمن الرحيم
      </div>
      <div style="font-family:'Amiri',serif; font-size:18px; color:#00c3a0; font-style:italic; margin-bottom:14px;">
        Al‑Noor — La Lumière
      </div>
      <div style="font-size:15px; color:#7a8ba8; line-height:1.6; font-weight:300; margin-bottom:0;">
        Posez vos questions sur le Coran et la Sunna.<br>
        Toutes les réponses sont fondées sur des sources authentiques.
      </div>
    </div>
    """, unsafe_allow_html=True)


# ── Affichage de l'historique ─────────────────────────────────────────────────
for msg in st.session_state.historique:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])


# ── Saisie et traitement ──────────────────────────────────────────────────────
question = st.chat_input("Posez votre question sur le Coran ou les Hadiths…")

if question:
    # Afficher et mémoriser la question
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.historique.append({"role": "user", "content": question})

    # Appel au workflow LangGraph
    with st.chat_message("assistant"):
        with st.spinner(""):
            try:
                workflow = charger_workflow()

                etat_initial = {
                    "question": question,
                    "messages": [HumanMessage(content=question)],
                }

                resultat = workflow.invoke(etat_initial)
                reponse = resultat["messages"][-1].content

            except Exception as e:
                reponse = f"⚠️ Erreur : {e}"

        st.markdown(reponse)

    st.session_state.historique.append({"role": "assistant", "content": reponse})