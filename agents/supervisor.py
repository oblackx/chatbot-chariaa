"""
agents/supervisor.py — Route vers : 'quran', 'hadith', ou 'conversation'.
"""

import re
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

_SUPERVISOR_PROMPT = """\
أنت موجّه ذكي لروبوت محادثة خاص بكلية الشريعة. مهمتك تصنيف الرسائل فقط.

يُرسل المستخدمون رسائل بالعربية الفصحى أو الفرنسية أو الدارجة المغربية أو اللغة الإنجليزية.

أجب بواحد فقط من هذه الرموز الثلاثة، بدون أي نص إضافي :

  [conversation] ← اختَر هذا في الحالات التالية :
    • تحيات وإنهاء المحادثة : bonjour, merci, bonsoir, سلام, مرحبا, شكرا,
      لاباس, كيداير, أشنو عندك, صباح الخير, واش راك ...
    • أسئلة معلوماتية عامة لا تحتاج بحثاً في الآيات مثل :
        - عدد السور (الجواب : 114)
        - عدد الآيات
        - أسماء الأنبياء
        - تعريف مصطلح إسلامي بسيط
    • أي رسالة غير دينية أو غير واضحة

  [quran]        ← سؤال عن آية أو سورة أو تفسير أو موضوع قرآني يحتاج بحثاً
  [hadith]       ← سؤال عن حديث أو سنة أو فقه نبوي يحتاج بحثاً

قاعدة : عند الشك بين [quran] و[hadith] → اختر [quran].
لا تضف أي شرح أو علامة ترقيم إضافية."""


def route_question(question: str) -> str:
    """Retourne 'conversation', 'quran' ou 'hadith'."""
    llm = ChatOllama(model="qwen3:8b", temperature=0)
    response = llm.invoke([
        SystemMessage(content=_SUPERVISOR_PROMPT),
        HumanMessage(content=question),
    ])
    content = response.content.strip()
    content = re.sub(r"<think>.*?</think>", "", content, flags=re.DOTALL).strip()
    content = content.lower()

    if "[conversation]" in content:
        return "conversation"
    if "[hadith]" in content:
        return "hadith"
    return "quran"