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
        search_results_per_question: int = 2,
    ):
        self.provider = provider
        self.model_name = model
        self.llm = build_llm(provider=provider, model=model, temperature=0) #set temperature to 0 to  generate consistent structured outputs rather than creative generation
        self.search_tool = build_search_tool(search_results_per_question=search_results_per_question)
        self.search_results_per_question = search_results_per_question

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
        print(f"[1/4] Planning research questions for topic: {topic}")
        question_set = self.plan(topic)

        all_notes: List[SearchResultNote] = []
        seen_urls = set()

        for idx, subq in enumerate(question_set.subquestions, start=1):
            print(f"[2/4] Searching for sub-question {idx}/{len(question_set.subquestions)}: {subq}")

            results = run_search(self.search_tool, subq)[: self.search_results_per_question]

            for result_idx, result in enumerate(results, start=1):
                url = result.get("url")

                if not url or url in seen_urls:
                    print("      Skipping duplicate or missing URL.")
                    continue

                seen_urls.add(url)

                title = result.get("title", "Untitled")
                print(f"      Evaluating result {result_idx}/{len(results)}: {title}")

                try:
                    note = self.evaluate_result(subq, result)

                    if note.relevant:
                        print(f"      Relevant result found. Score: {note.relevance_score}")
                        all_notes.append(note)
                    else:
                        print(f"      Skipped. Score: {note.relevance_score}")

                except Exception as e:
                    print(f"      Skipping result due to evaluation error: {e}")

            if len(all_notes) >= 4:
                print("[3/4] Enough relevant notes collected. Stopping search early.")
                break

        print(f"[4/4] Synthesizing final report from {len(all_notes)} notes.")
        report = self.synthesize(topic, all_notes)

        print("Done. Final report generated.")

        return {
            "question_set": question_set,
            "notes": all_notes,
            "report": report,
            "provider": self.provider,
            "model": self.model_name,
        }