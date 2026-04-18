import json
from typing import List

from langchain_core.prompts import ChatPromptTemplate

from app.llm_factory import build_llm
from app.prompts import PLAN_PROMPT, EVALUATE_PROMPT, SYNTHESIS_PROMPT
from app.schemas import ResearchQuestionSet, SearchResultNote, FinalReport
from app.search import build_search_tool, run_search


class ResearchAgent:
    def __init__(
        self,
        provider: str = "ollama",
        model: str | None = None,
        max_results: int = 2,
    ):
        self.provider = provider
        self.model_name = model
        self.llm = build_llm(provider=provider, model=model, temperature=0)
        self.search_tool = build_search_tool(max_results=max_results)

    def plan(self, topic: str) -> ResearchQuestionSet:
        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", PLAN_PROMPT),
                ("human", "Topic: {topic}"),
            ]
        )

        structured_llm = self.llm.with_structured_output(ResearchQuestionSet)
        chain = prompt | structured_llm
        return chain.invoke({"topic": topic})

    def evaluate_result(self, subquestion: str, raw_result: dict) -> SearchResultNote:
        title = raw_result.get("title", "")
        url = raw_result.get("url", "")
        content = raw_result.get("content", "") or raw_result.get("snippet", "")

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", EVALUATE_PROMPT),
                (
                    "human",
                    "subquestion: {subquestion}\n"
                    "title: {title}\n"
                    "url: {url}\n"
                    "content: {content}",
                ),
            ]
        )

        structured_llm = self.llm.with_structured_output(SearchResultNote)
        chain = prompt | structured_llm

        return chain.invoke(
            {
                "subquestion": subquestion,
                "title": title,
                "url": url,
                "content": content[:6000],
            }
        )

    def synthesize(self, topic: str, notes: List[SearchResultNote]) -> FinalReport:
        relevant_notes = [n for n in notes if n.relevant]

        serializable_notes = [
            {
                "subquestion": n.subquestion,
                "title": n.title,
                "url": n.url,
                "relevance_score": n.relevance_score,
                "extracted_points": n.extracted_points,
                "rationale": n.rationale,
            }
            for n in relevant_notes
        ]

        prompt = ChatPromptTemplate.from_messages(
            [
                ("system", SYNTHESIS_PROMPT),
                ("human", "topic: {topic}\nnotes:\n{notes}"),
            ]
        )

        structured_llm = self.llm.with_structured_output(FinalReport)
        chain = prompt | structured_llm

        return chain.invoke(
            {
                "topic": topic,
                "notes": json.dumps(serializable_notes, indent=2),
            }
        )

    def run(self, topic: str) -> dict:
        question_set = self.plan(topic)

        all_notes: List[SearchResultNote] = []
        seen_urls = set() #??

        for subq in question_set.subquestions:
            results = run_search(self.search_tool, subq)[:2] ## 하드 코딩 ? max_result 안쓰고

            for result in results:
                url = result.get("url")
                if not url or url in seen_urls:
                    continue

                seen_urls.add(url)

                try:
                    note = self.evaluate_result(subq, result)
                    if note.relevant:
                        all_notes.append(note)
                except Exception as e:
                    print(f"Skipping result due to evaluation error: {e}")

            if len(all_notes) >= 4: # Threshhold 하드 코딩?  thresh hold 같은거 config로 정해야
                break

        report = self.synthesize(topic, all_notes)

        return {
            "question_set": question_set,
            "notes": all_notes,
            "report": report,
            "provider": self.provider,
            "model": self.model_name,
        }