"""
agents/domain_agent.py

- run_quran_agent   : recherche DB uniquement, zéro hallucination
- run_hadith_agent  : idem
- run_conversation_agent : LLM libre (salutations, faits généraux, Darija)
"""

import re
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from rag.retriever import retrieve_context

MIN_RELEVANCE_SCORE = 0.40

_NO_RESULT = (
    "لم أجد في قاعدة البيانات آيات مرتبطة بهذا السؤال.\n"
    "Les versets disponibles dans ma base ne permettent pas de répondre à cette question."
)


# ---------------------------------------------------------------------------
# Extraction de mots-clés arabes (recherche exacte normalisée)
# ---------------------------------------------------------------------------

_KEYWORDS_PROMPT = """\
أنت خبير في اللغة العربية ومتخصص في الألفاظ القرآنية.

السؤال : {question}

مهمتك :
1. حدد الجذر العربي للمفهوم الرئيسي في السؤال.
2. اذكر الألفاظ القرآنية الأكثر شيوعاً المشتقة من هذا الجذر أو المرادفة له
   (بدون تشكيل، كما تظهر في المصحف).
3. اذكر كذلك الفعل الأمري إن وُجد في القرآن (مثل : أوفوا، اتقوا...).

أعطني من 3 إلى 5 مصطلحات فقط، كل واحد في سطر منفصل.
بدون ترقيم، بدون شرح، بدون أي كلام آخر."""


def _extract_arabic_keywords(question: str) -> list[str]:
    llm = ChatOllama(model="qwen3:8b", temperature=0)
    try:
        response = llm.invoke(_KEYWORDS_PROMPT.format(question=question))
        content = re.sub(r"<think>.*?</think>", "", response.content, flags=re.DOTALL).strip()
        terms = [
            line.strip().strip("\"'''\"«»،.-–—0123456789.")
            for line in content.splitlines() if line.strip()
        ]
        arabic_re = re.compile(r'[\u0600-\u06FF]')
        return [t for t in terms if arabic_re.search(t) and len(t) <= 40][:5]
    except Exception:
        return []


def _best_score(results: list[dict]) -> float:
    return max((r["similarity"] for r in results), default=0.0)


def _strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


# ---------------------------------------------------------------------------
# Agent Coran — DB uniquement, zéro LLM de génération
# ---------------------------------------------------------------------------

def run_quran_agent(question: str) -> str:
    keywords = _extract_arabic_keywords(question)
    results = retrieve_context(question, k=20, keywords=keywords if keywords else None)

    if _best_score(results) < MIN_RELEVANCE_SCORE:
        return _NO_RESULT

    lines = ["📖 **Versets trouvés dans la base :**\n"]
    for i, r in enumerate(results, 1):
        m = r["metadata"]
        ref = (f"{m.get('sourate_nom','?')} "
               f"[{m.get('sourate','?')}:{m.get('verset','?')}]")
        if m.get("lieu"):
            ref += f" — {m['lieu']}"
        score = r["similarity"]
        # Distinguer visuellement les matches exacts des matches sémantiques
        badge = "🔵" if score >= 1.0 else "🟡"
        lines.append(f"{badge} **{i}. {ref}** (score : {score:.2f})")
        lines.append(f"> {r['content']}")
        lines.append("")

    if keywords:
        lines.append(f"---\n*Mots-clés utilisés : {', '.join(keywords)}*")
    lines.append("\n⚠️ *Ces versets sont fournis sans interprétation. "
                 "Consultez un enseignant pour le tafsir.*")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Agent Hadith
# ---------------------------------------------------------------------------

def run_hadith_agent(question: str) -> str:
    return "⚙️ Les hadiths ne sont pas encore disponibles dans la base."


# ---------------------------------------------------------------------------
# Agent Conversation — LLM libre (salutations, Darija, faits généraux)
# ---------------------------------------------------------------------------

_CONVERSATION_SYSTEM = """\
أنت مساعد ودود لطلاب كلية الشريعة بأيت ملول.

قواعد المحادثة :
1. تفهم وتجيب بالدارجة المغربية، العربية الفصحى، والفرنسية والإنجليزية.
2. تجيب على الأسئلة المعلوماتية الإسلامية العامة مثل :
   - عدد سور القرآن (114 سورة)
   - عدد آيات القرآن (6236 آية في المصحف العثماني)
   - أسماء الأنبياء، أركان الإسلام، تعريفات بسيطة...
3. للأسئلة التي تحتاج بحثاً في الآيات، تقول :
   "اكتب سؤالك بشكل كامل وسأبحث لك في قاعدة البيانات."
4. تجيب بنفس لغة المستخدم، بإيجاز ولطف.
5. لا تخترع آيات أو أحاديث.
"""

def run_conversation_agent(question: str) -> str:
    llm = ChatOllama(model="qwen3:8b", temperature=0.3, max_tokens=300)
    response = llm.invoke([
        SystemMessage(content=_CONVERSATION_SYSTEM),
        HumanMessage(content=question),
    ])
    return _strip_think(response.content)