"""
Prompt Templates
Strict Qur’an-only prompts for contextual meaning summarization.
"""

from typing import Tuple

SYSTEM_PROMPT = """
You are an AI assistant that explains the meaning of Qur’an translations
in clear, human-friendly English.

GUIDELINES:
- Base the explanation primarily on the provided Qur’an translation.
- You MAY include general background or contextual information.
- Do NOT quote Arabic text.
- Do NOT quote verse numbers.
- Do NOT present explanations as absolute or final meanings.
- Do NOT issue religious rulings or legal advice.
- Avoid sectarian or doctrinal bias.
- Keep a neutral, educational tone.

If the provided verses do not clearly relate to the question,
respond exactly with:
"Not describing about it."
""".strip()


def format_ayahs_for_prompt(ayahs: list) -> str:
    """
    Format ayahs for LLM input (English translation only).
    """
    return "\n".join(a["english"] for a in ayahs if a.get("english"))


# ============================
# Q&A PROMPT
# ============================

def build_qa_prompt(question: str, relevant_ayahs: list) -> Tuple[str, str]:
    ayah_text = format_ayahs_for_prompt(relevant_ayahs)

    user_prompt = f"""
Qur’an Verses (English translation):
{ayah_text}

User Question:
{question}

Task:
Write a clear, meaningful explanation in natural English that helps
a general reader understand the message of these verses in relation
to the question.

Do NOT quote the verses.
Do NOT mention verse numbers.
""".strip()

    return SYSTEM_PROMPT, user_prompt


# ============================
# SUMMARY PROMPT (REQUIRED)
# ============================

def build_summary_prompt(text_type: str, text_content: list) -> Tuple[str, str]:
    ayah_text = format_ayahs_for_prompt(text_content)

    user_prompt = f"""
Text Type: {text_type}

Qur’an Verses (English translation):
{ayah_text}

Task:
Provide a clear, human-friendly explanation of the meaning and theme
conveyed by this text.

Do NOT quote the verses.
Do NOT claim a single definitive interpretation.
""".strip()

    return SYSTEM_PROMPT, user_prompt
