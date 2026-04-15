from pydantic import BaseModel, Field
from typing import List


class ResearchQuestionSet(BaseModel):
    topic: str
    subquestions: List[str] = Field(
        description="3 to 5 focused research sub-questions"
    )


class SearchResultNote(BaseModel):
    subquestion: str
    title: str
    url: str
    relevance_score: int = Field(ge=1, le=5)
    relevant: bool
    extracted_points: List[str]
    rationale: str


class FinalReport(BaseModel):
    topic: str
    executive_summary: str
    key_findings: List[str]
    limitations: List[str]
    sources: List[str]