"""
app.py — Interface Streamlit raffinée du Chatbot Faculté de Charia.
Design : islamique-minimaliste, logo mosquée à gauche, animation "thinking".
"""

import sys, time
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import streamlit as st
from langchain_core.messages import HumanMessage
from graph.workflow import build_workflow

# ── Config page ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Chatbot Charia — كلية الشريعة",
    page_icon="🕌",
    layout="centered",
    initial_sidebar_state="collapsed",
)

# ── Design System ──────────────────────────────────────────────────────────────
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Amiri:ital,wght@0,400;0,700;1,400&family=Tajawal:wght@300;400;500;700&display=swap');

:root {
  --gold:      #B8973A;
  --gold-lt:   #D4AF5A;
  --green:     #1A3A2A;
  --green-lt:  #2D5A40;
  --cream:     #FAF7F0;
  --sand:      #F0EAD8;
  --text:      #1C1C1E;
  --text-muted:#6B6B6B;
  --radius:    14px;
}

/* ── Reset & base ── */
html, body, .stApp { background: var(--cream) !important; }
* { box-sizing: border-box; }

/* ── Hide default Streamlit chrome ── */
#MainMenu, footer, header { visibility: hidden; }
.stDeployButton { display: none; }

/* ── Global font ── */
.stApp, .stChatMessage, .stMarkdown, input, textarea {
  font-family: 'Tajawal', 'Amiri', sans-serif !important;
}

/* ── Header band ── */
.charia-header {
  display: flex;
  align-items: center;
  gap: 16px;
  padding: 22px 28px;
  background: linear-gradient(135deg, var(--green) 0%, var(--green-lt) 100%);
  border-radius: var(--radius);
  margin-bottom: 24px;
  box-shadow: 0 4px 20px rgba(26,58,42,0.18);
}
.charia-header .mosque-icon {
  font-size: 3rem;
  line-height: 1;
  filter: drop-shadow(0 2px 6px rgba(0,0,0,0.3));
}
.charia-header .header-text { flex: 1; }
.charia-header h1 {
  margin: 0;
  font-family: 'Amiri', serif !important;
  font-size: 1.6rem;
  font-weight: 700;
  color: var(--gold-lt) !important;
  letter-spacing: 0.02em;
  text-align: right !important;
  direction: rtl;
}
.charia-header p {
  margin: 2px 0 0;
  font-size: 0.82rem;
  color: rgba(255,255,255,0.65);
  font-family: 'Tajawal', sans-serif;
  letter-spacing: 0.05em;
  text-align: right;
  direction: rtl;
}
.gold-line {
  height: 2px;
  background: linear-gradient(90deg, transparent, var(--gold), transparent);
  margin: 0 0 24px;
  border: none;
  opacity: 0.6;
}

/* ── Chat messages ── */
.stChatMessage {
  background: transparent !important;
  border: none !important;
  box-shadow: none !important;
}
/* User bubble */
.stChatMessage[data-testid="stChatMessageContent"]:has(> div.user-msg) {
  background: var(--green) !important;
}

/* Assistant bubble wrapper */
[data-testid="stChatMessage"] {
  padding: 4px 0 !important;
}

/* ── Versets (blockquotes) ── */
blockquote, blockquote p {
  font-family: 'Amiri', serif !important;
  font-size: 1.18rem !important;
  line-height: 2.1 !important;
  direction: rtl !important;
  text-align: right !important;
  color: var(--green) !important;
  background: var(--sand) !important;
  border-right: 4px solid var(--gold) !important;
  border-left: none !important;
  border-top: none !important;
  border-bottom: none !important;
  padding: 14px 18px !important;
  border-radius: 8px !important;
  margin: 8px 0 !important;
  box-shadow: inset 0 0 0 1px rgba(184,151,58,0.15) !important;
}

/* ── Chat input ── */
.stChatInputContainer {
  background: white !important;
  border-radius: var(--radius) !important;
  border: 1.5px solid rgba(184,151,58,0.3) !important;
  box-shadow: 0 2px 12px rgba(0,0,0,0.06) !important;
  padding: 2px 6px !important;
  transition: border-color 0.2s;
}
.stChatInputContainer:focus-within {
  border-color: var(--gold) !important;
  box-shadow: 0 2px 16px rgba(184,151,58,0.15) !important;
}
.stChatInputContainer textarea {
  font-family: 'Tajawal', 'Amiri', sans-serif !important;
  font-size: 1rem !important;
  direction: auto !important;
}

/* ── Thinking animation ── */
.thinking-dots {
  display: inline-flex;
  align-items: center;
  flex-direction: row;
  flex-wrap: nowrap;
  gap: 5px;
  padding: 12px 18px;
  background: white;
  border-radius: 18px;
  border: 1px solid rgba(184,151,58,0.2);
  box-shadow: 0 2px 8px rgba(0,0,0,0.06);
  white-space: nowrap;
}
.thinking-dot {
  width: 7px !important; height: 7px !important;
  min-width: 7px !important;
  background: var(--gold) !important;
  border-radius: 50% !important;
  display: inline-block !important;
  animation: bounce 1.2s infinite !important;
  flex-shrink: 0;
}
.thinking-dot:nth-child(2) { animation-delay: 0.2s !important; }
.thinking-dot:nth-child(3) { animation-delay: 0.4s !important; }
@keyframes bounce {
  0%, 60%, 100% { transform: translateY(0); opacity: 0.4; }
  30%           { transform: translateY(-6px); opacity: 1; }
}
.thinking-label {
  font-size: 0.78rem !important;
  color: var(--text-muted) !important;
  margin-right: 6px !important; margin-left: 4px !important;
  font-family: 'Tajawal', sans-serif !important;
  display: inline !important;
  white-space: nowrap !important;
  direction: rtl;
}

/* ── Suggested questions ── */
.suggest-grid {
  display: grid;
  grid-template-columns: 1fr 1fr;
  gap: 10px;
  margin-bottom: 20px;
}
.suggest-btn {
  background: white;
  border: 1.5px solid rgba(184,151,58,0.25);
  border-radius: 10px;
  padding: 10px 14px;
  font-family: 'Tajawal', 'Amiri', sans-serif;
  font-size: 0.83rem;
  color: var(--green);
  cursor: pointer;
  text-align: right;
  direction: rtl;
  line-height: 1.5;
  transition: all 0.18s;
  box-shadow: 0 1px 4px rgba(0,0,0,0.04);
}
.suggest-btn:hover {
  border-color: var(--gold);
  background: var(--sand);
  box-shadow: 0 2px 10px rgba(184,151,58,0.15);
}

/* ── Scrollbar ── */
::-webkit-scrollbar { width: 5px; }
::-webkit-scrollbar-track { background: transparent; }
::-webkit-scrollbar-thumb { background: rgba(184,151,58,0.3); border-radius: 10px; }
</style>
""", unsafe_allow_html=True)

# ── Header ─────────────────────────────────────────────────────────────────────
st.markdown("""
<div class="charia-header">
  <div class="header-text">
    <h1>كلية الشريعة</h1>
    <p>Faculté de Charia &nbsp;·&nbsp; أيت مليول &nbsp;·&nbsp; Aït Melloul</p>
  </div>
  <div class="mosque-icon">🕌</div>
</div>
<hr class="gold-line">
""", unsafe_allow_html=True)

# ── Workflow ───────────────────────────────────────────────────────────────────
@st.cache_resource
def load_workflow():
    return build_workflow()

workflow = load_workflow()

# ── Session state ──────────────────────────────────────────────────────────────
if "messages" not in st.session_state:
    st.session_state.messages = []
if "pending_question" not in st.session_state:
    st.session_state.pending_question = None

# ── Suggestions (affiché si aucun historique) ──────────────────────────────────
SUGGESTIONS = [
    "ما هي الآية التي تأمر بالوفاء بالعقود؟",
    "اذكر السورة التي تتحدث عن صلاة الجمعة",
    "ما هي الآية التي وصفت النبي بفضائل الأخلاق؟",
    "ما الذي يقوله القرآن عن الصبر؟",
]

if not st.session_state.messages:
    st.markdown(
        "<p style='text-align:center;color:#888;font-size:0.85rem;"
        "font-family:Tajawal,sans-serif;margin-bottom:10px;'>"
        "💡 أسئلة مقترحة — Questions suggérées</p>",
        unsafe_allow_html=True,
    )
    cols = st.columns(2)
    for i, s in enumerate(SUGGESTIONS):
        if cols[i % 2].button(s, key=f"sug_{i}", use_container_width=True):
            st.session_state.pending_question = s
            st.rerun()

# ── Historique ─────────────────────────────────────────────────────────────────
for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.markdown(msg["content"])

# ── Traitement (question clavier ou suggestion) ────────────────────────────────
def process_question(question: str):
    with st.chat_message("user"):
        st.markdown(question)
    st.session_state.messages.append({"role": "user", "content": question})

    with st.chat_message("assistant"):
        # Animation "thinking"
        thinking_ph = st.empty()
        thinking_ph.markdown("""
        <div class="thinking-dots">
          <span class="thinking-dot"></span>
          <span class="thinking-dot"></span>
          <span class="thinking-dot"></span>
          <span class="thinking-label">جاري البحث في قاعدة البيانات…</span>
        </div>
        """, unsafe_allow_html=True)

        state  = {"question": question, "messages": [HumanMessage(content=question)]}
        result = workflow.invoke(state)
        answer = result["messages"][-1].content

        thinking_ph.empty()
        st.markdown(answer)

    st.session_state.messages.append({"role": "assistant", "content": answer})

# Question depuis suggestion
if st.session_state.pending_question:
    q = st.session_state.pending_question
    st.session_state.pending_question = None
    process_question(q)

# Question depuis le chat input
if question := st.chat_input("اكتب سؤالك… / Posez votre question…"):
    process_question(question)                  