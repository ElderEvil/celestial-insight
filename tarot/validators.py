import re


class QuestionValidator:
    """Validates if questions are appropriate for mystical readings"""

    @classmethod
    async def validate_question(cls, *, question: str) -> bool:
        personal_patterns = r"should i|will i|am i|my future|my path|my destiny|my life"
        return bool(re.search(personal_patterns, question.lower()))

    @classmethod
    async def get_question_theme(cls, *, question: str) -> str:
        themes = {
            r"love|relationship|partner": "love and relationships",
            r"job|career|work|business": "career and life purpose",
            r"health|wellness|energy": "health and wellness",
            r"money|finance|wealth": "abundance and prosperity",
        }

        for pattern, theme in themes.items():
            if re.search(pattern, question.lower()):
                return theme
        return "personal guidance"
