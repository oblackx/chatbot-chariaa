"""
agents/domain_agent.py

- run_quran_agent        : recherche Coran (pgvector + exact), zéro hallucination
- run_hadith_agent       : recherche Bukhari (pgvector + exact), zéro hallucination
- run_conversation_agent : LLM libre (salutations, Darija, faits généraux)
"""

import re
import json
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage
from rag.database import get_connection
from rag.embeddings import get_embed_model

def _is_arabic(text: str) -> bool:
    """Détecte si le texte contient principalement des caractères arabes."""
    arabic_re = re.compile(r'[\u0600-\u06FF]')
    arabic_chars = len(arabic_re.findall(text))
    return arabic_chars > len(text) * 0.3

MIN_RELEVANCE_SCORE = 0.40

_NO_RESULT_QURAN = (
    "لم أجد في قاعدة البيانات آيات مرتبطة بهذا السؤال.\n"
    "Les versets disponibles dans ma base ne permettent pas de répondre à cette question."
)
_NO_RESULT_HADITH = (
    "لم أجد في قاعدة البيانات أحاديث مرتبطة بهذا السؤال.\n"
    "Les hadiths disponibles dans ma base ne permettent pas de répondre à cette question."
)


# ---------------------------------------------------------------------------
# Utilitaires communs
# ---------------------------------------------------------------------------

def _strip_think(text: str) -> str:
    return re.sub(r"<think>.*?</think>", "", text, flags=re.DOTALL).strip()


def _best_score(results: list[dict]) -> float:
    return max((r["similarity"] for r in results), default=0.0)


# ---------------------------------------------------------------------------
# Extraction de mots-clés arabes (Coran ou Hadith)
# ---------------------------------------------------------------------------

_KEYWORDS_PROMPT_QURAN = """\
أنت خبير في اللغة العربية ومتخصص في الألفاظ القرآنية.

السؤال : {question}

مهمتك :
1. حدد الجذر العربي للمفهوم الرئيسي في السؤال.
2. اذكر الألفاظ القرآنية الأكثر شيوعاً المشتقة من هذا الجذر أو المرادفة له
   (بدون تشكيل، كما تظهر في المصحف).
3. اذكر كذلك الفعل الأمري إن وُجد في القرآن (مثل : أوفوا، اتقوا...).

أعطني من 3 إلى 5 مصطلحات فقط، كل واحد في سطر منفصل.
بدون ترقيم، بدون شرح، بدون أي كلام آخر."""

_KEYWORDS_PROMPT_HADITH = """\
أنت خبير في علوم الحديث النبوي.

السؤال : {question}

مهمتك :
1. حدد الجذر العربي للمفهوم الرئيسي في السؤال.
2. اذكر الألفاظ التي تظهر في متون الأحاديث النبوية للتعبير عن هذا المفهوم
   (بدون تشكيل، كما تظهر في كتب الحديث).
3. اذكر الفعل أو الاسم الأكثر ورودًا في كتب الحديث.

أعطني من 3 إلى 5 مصطلحات فقط، كل واحد في سطر منفصل.
بدون ترقيم، بدون شرح، بدون أي كلام آخر."""


def _extract_keywords(question: str, domain: str = "quran") -> list[str]:
    """Extrait les mots-clés arabes selon le domaine (quran/hadith)."""
    llm = ChatOllama(model="qwen3:8b", temperature=0)
    prompt_tpl = _KEYWORDS_PROMPT_QURAN if domain == "quran" else _KEYWORDS_PROMPT_HADITH
    try:
        response = llm.invoke(prompt_tpl.format(question=question))
        content = _strip_think(response.content)
        terms = [
            line.strip().strip("\"'''\"«»،.-–—0123456789.")
            for line in content.splitlines() if line.strip()
        ]
        arabic_re = re.compile(r'[\u0600-\u06FF]')
        return [t for t in terms if arabic_re.search(t) and len(t) <= 40][:5]
    except Exception:
        return []


# ---------------------------------------------------------------------------
# Recherche dans PostgreSQL (source filtrée)
# ---------------------------------------------------------------------------

def _retrieve(
    query: str,
    source: str,           # 'quran' ou 'bukhari'
    k: int = 15,
    keywords: list[str] | None = None,
) -> list[dict]:
    """
    Recherche hybride filtrée par source :
    - Sémantique  : pgvector cosinus sur la question complète
    - Exacte      : normalize_arabic LIKE sur chaque mot-clé
    Fusion : meilleur score par contenu.
    """
    embed_model = get_embed_model()
    query_vector = embed_model.embed_query(query)
    search_terms = keywords if keywords else [query]

    conn = get_connection()
    try:
        with conn.cursor() as cur:
            # 1. Sémantique filtré par source
            cur.execute(
                """
                SELECT content, metadata,
                       1 - (embedding <=> %s::vector) AS similarity
                FROM document_chunks
                WHERE metadata->>'source' = %s
                ORDER BY embedding <=> %s::vector
                LIMIT %s
                """,
                (query_vector, source, query_vector, k),
            )
            semantic_rows = cur.fetchall()

            # 2. Exact normalisé filtré par source
            exact_rows: list[tuple] = []
            for term in search_terms:
                if not term or not term.strip():
                    continue
                cur.execute(
                    """
                    SELECT content, metadata, 1.0 AS similarity
                    FROM document_chunks
                    WHERE metadata->>'source' = %s
                      AND normalize_arabic(content)
                          LIKE '%%' || normalize_arabic(%s) || '%%'
                    LIMIT %s
                    """,
                    (source, term, k),
                )
                exact_rows.extend(cur.fetchall())
    finally:
        conn.close()

    # Fusion
    combined: dict[str, dict] = {}
    for content, metadata, similarity in semantic_rows + exact_rows:
        if isinstance(metadata, str):
            metadata = json.loads(metadata)
        sim = round(float(similarity), 4)
        if content not in combined or sim > combined[content]["similarity"]:
            combined[content] = {
                "content": content,
                "metadata": metadata or {},
                "similarity": sim,
            }

    return sorted(combined.values(), key=lambda x: x["similarity"], reverse=True)[:k]


# ---------------------------------------------------------------------------
# Agent Coran
# ---------------------------------------------------------------------------

def run_quran_agent(question: str) -> str:
    keywords = _extract_keywords(question, domain="quran")
    results  = _retrieve(question, source="quran", k=20, keywords=keywords or None)

    if _best_score(results) < MIN_RELEVANCE_SCORE:
        return _NO_RESULT_QURAN

    lines = ["📖 **Versets trouvés dans la base :**\n"]
    for i, r in enumerate(results, 1):
        m     = r["metadata"]
        ref   = f"{m.get('sourate_nom','?')} [{m.get('sourate','?')}:{m.get('verset','?')}]"
        if m.get("lieu"):
            ref += f" — {m['lieu']}"
        score = r["similarity"]
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
# Agent Hadith (Bukhari)
# ---------------------------------------------------------------------------

def run_hadith_agent(question: str) -> str:
    keywords = _extract_keywords(question, domain="hadith")
    results  = _retrieve(question, source="bukhari", k=5, keywords=keywords or None)

    if _best_score(results) < MIN_RELEVANCE_SCORE:
        return _NO_RESULT_HADITH

    lines = ["📚 **Hadiths trouvés dans la base (Sahih Bukhari) :**\n"]
    for i, r in enumerate(results, 1):
        m     = r["metadata"]
        num   = m.get("hadith_number", "?")
        chap  = m.get("chapter_arabic", "")
        sec   = m.get("section_arabic", "")
        grade = m.get("grade_arabic", "")
        score = r["similarity"]
        badge = "🔵" if score >= 1.0 else "🟡"

        ref = f"حديث رقم {num}"
        if chap:
            ref += f" — {chap}"
        if grade:
            ref += f" ({grade})"

        lines.append(f"{badge} **{i}. {ref}** (score : {score:.2f})")
        if sec:
            lines.append(f"*{sec}*")

        # Isnad (chaîne de transmission) — affiché en petit
        isnad = m.get("isnad_arabic", "")
        if isnad:
            lines.append(f"<small>*السند :* {isnad[:120]}…</small>")

        # Matn (texte du hadith)
        content_display = r['content'][:500] + ("…" if len(r['content']) > 500 else "")
        lines.append(f"> {content_display}")
        lines.append("")

    if keywords:
        lines.append(f"---\n*Mots-clés utilisés : {', '.join(keywords)}*")
    lines.append("\n⚠️ *Ces hadiths sont fournis sans interprétation. "
                 "Consultez un enseignant pour les vérifications.*")
    return "\n".join(lines)


# ---------------------------------------------------------------------------
# Agent Conversation
# ---------------------------------------------------------------------------


_CONVERSATION_SYSTEM = """\
أنت مساعد ودود لطلاب كلية الشريعة بأيت ملول.
 
مفردات الدارجة المغربية :
- نتا / نتي = أنت / أنتِ  →  "شكون نتا؟" = "من أنت؟"
- أشنو = ما هو / ماذا
- كيداير / لاباس = كيف حالك / بخير
- واش = هل
- بغيت = أريد
- مزيان = جيد / حسناً
 
قواعد صارمة :
1. تجيب بالدارجة المغربية أو العربية أو الفرنسية حسب لغة المستخدم.
2. تجيب مباشرة على الأسئلة الإسلامية الثابتة :
   - عدد سور القرآن : 114 سورة
   - عدد الآيات : 6236 آية
   - أركان الإسلام الخمسة : الشهادة، الصلاة، الزكاة، الصوم، الحج
3. ⛔ إذا سألك عن تقنية حديثة (هاتف، إنترنت، كمبيوتر...) في السياق الإسلامي :
   قل فقط : "القرآن الكريم نزل قبل هذه التقنيات. للسؤال عن مبادئ إسلامية مرتبطة، اسأل سؤالاً محدداً عن آية أو حديث."
   لا تذكر أي رقم سورة أو رقم آية. لا تخترع أي نص قرآني أو حديثي.
4. ⛔ لا تنسب أي نص لآية أو حديث من ذاكرتك. أبداً.
5. تجيب بإيجاز ولطف.
"""

def run_conversation_agent(question: str) -> str:
    llm = ChatOllama(model="qwen3:8b", temperature=0.3, max_tokens=300)
    response = llm.invoke([
        SystemMessage(content=_CONVERSATION_SYSTEM),
        HumanMessage(content=question),
    ])
    return _strip_think(response.content)