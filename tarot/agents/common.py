from dataclasses import dataclass


@dataclass
class ReadingDependencies:
    question: str
    locale: str = "en"
    mentor_style: str = ""
