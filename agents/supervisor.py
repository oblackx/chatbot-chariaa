"""
agents/supervisor.py
Modèle : qwen3:8b — précision de routage multilingue (fr/ar/darija).
"""

import re
from langchain_ollama import ChatOllama
from langchain_core.messages import HumanMessage, SystemMessage

_SUPERVISOR_PROMPT = """\
أنت موجّه لروبوت محادثة خاص بكلية الشريعة. مهمتك الوحيدة : تصنيف الرسالة.

أجب بواحد فقط من هذه الرموز، بدون أي نص إضافي :

[conversation] ← اختر هذا لكل ما يلي :
  • تحيات : bonjour, bonsoir, merci, salut, salam, مرحبا, شكرا, لاباس, كيداير, واش راك,
    صباح الخير, comment ça va, ça va, qui es-tu, شكون نتا, أشنو عندك
    (تنبيه: "نتا/نتي" بالدارجة المغربية = "أنت" ← دائماً [conversation])
  • أسئلة عن هوية البوت أو قدراته
  • أسئلة عامة لا علاقة لها بالقرآن أو الحديث
    (téléphone, internet, ordinateur, clonage, météo, sport...)
  • أسئلة مستحيلة (سورة 115, آية 9999, هل استخدم النبي الكمبيوتر؟)
  • أسئلة معلوماتية إسلامية ذات إجابة ثابتة :
    - كم عدد السور؟ / Combien de sourates? → [conversation]
    - ما هي أركان الإسلام؟ / Quels sont les piliers de l'Islam? → [conversation]
    - ما معنى كلمة X الإسلامية؟ → [conversation]
    - ما عدد آيات القرآن؟ → [conversation]

[hadith] ← سؤال يطلب حديثاً نبوياً أو كلام النبي ﷺ، مثل :
  • hadith sur X / حديث عن X / ما قاله النبي عن X
  • Que dit le Prophète sur... / Parle-moi d'un hadith...
  • ما روي عن النبي في موضوع...

[quran] ← سؤال عن آية أو سورة أو موضوع قرآني يحتاج بحثاً في المصحف
  • ما هي الآية التي... / اذكر السورة التي...
  • Que dit le Coran sur... / Quel verset parle de...
  • أي آية تأمر بـ... / ما معنى قوله تعالى...

قاعدة : عند الشك بين [quran] و[hadith] → اختر [quran].
قاعدة : أي رسالة لا تحتاج بحثاً في الآيات أو الأحاديث → [conversation].
لا تضف أي شرح. أجب بالرمز فقط."""


def route_question(question: str) -> str:
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