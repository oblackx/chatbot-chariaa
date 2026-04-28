"""
app.py — Interface Streamlit du Chatbot Faculté de Charia.
Améliorations UI : RTL pour l'arabe, bulles de chat, séparation visuelle des versets.
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from langchain_core.messages import HumanMessage
from graph.workflow import build_workflow

# ── Configuration ──────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chatbot Charia — كلية الشريعة",
    page_icon="🕌",
    layout="centered",
)

# ── CSS : RTL arabe + style des versets ────────────────────────────────────
st.markdown("""
<style>
/* Police arabe */
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&display=swap');

/* Texte arabe dans les blockquotes (versets) */
blockquote p, blockquote {
    font-family: 'Amiri', 'Traditional Arabic', serif !important;
    font-size: 1.25rem !important;
    line-height: 2.2 !important;
    direction: rtl !important;
    text-align: right !important;
    color: #1a1a2e !important;
    background: #f8f4e8 !important;
    border-right: 4px solid #c8a96e !important;
    border-left: none !important;
    padding: 12px 16px !important;
    border-radius: 6px !important;
    margin: 6px 0 !important;
}

/* Texte arabe général dans les messages */
.stChatMessage p, .stChatMessage li {
    line-height: 1.9;
}

/* Titre de la page */
h1 { text-align: center; }

/* Zone de saisie */
.stChatInputContainer textarea {
    font-family: 'Amiri', Arial, sans-serif;
}

/* Badge score bleu (exact) */
strong { font-weight: 600; }
</style>
""", unsafe_allow_html=True)

# ── Workflow (cache) ────────────────────────────────────────────────────────
@st.cache_resource
def load_workflow():
    return build_workflow()

workflow = load_workflow()

# ── En-tête ─────────────────────────────────────────────────────────────────
st.markdown(
    "<h1>🕌 Chatbot — كلية الشريعة</h1>"
    "<p style='text-align:center;color:#666;'>أيت مليول — Aït Melloul</p>",
    unsafe_allow_html=True,
)
st.divider()

# ── Historique ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Saisie ──────────────────────────────────────────────────────────────────
if question := st.chat_input("اكتب سؤالك... / Posez votre question..."):
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        with st.spinner("🔍 بحث في قاعدة البيانات..."):
            state = {
                "question": question,
                "messages": [HumanMessage(content=question)],
            }
            result   = workflow.invoke(state)
            answer   = result["messages"][-1].content
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})