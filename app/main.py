import argparse
import re
from datetime import datetime
from pathlib import Path

from app.agent import ResearchAgent


def slugify(text: str, max_length: int = 50) -> str:
    text = text.lower().strip()
    text = re.sub(r"[^a-z0-9\s-]", "", text)
    text = re.sub(r"[\s-]+", "_", text)
    return text[:max_length].strip("_") or "report"


def generate_output_path(topic: str, provider: str) -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    topic_slug = slugify(topic)
    provider_slug = slugify(provider)
    return f"outputs/{topic_slug}_{provider_slug}_{timestamp}.md"


def save_markdown(output_path: str, result: dict):
    report = result["report"]
    question_set = result["question_set"]
    notes = result["notes"]
    provider = result.get("provider", "unknown")
    model = result.get("model", "default")

    lines = []
    lines.append(f"# Research Report: {report.topic}\n")
    lines.append(f"**Provider:** {provider}")
    lines.append(f"**Model:** {model}")
    lines.append("")

    lines.append("## Generated Sub-Questions\n")
    for idx, q in enumerate(question_set.subquestions, start=1):
        lines.append(f"{idx}. {q}")
    lines.append("")

    lines.append("## Executive Summary\n")
    lines.append(report.executive_summary)
    lines.append("")

    lines.append("## Key Findings\n")
    for item in report.key_findings:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Limitations\n")
    for item in report.limitations:
        lines.append(f"- {item}")
    lines.append("")

    lines.append("## Extracted Notes\n")
    for note in notes:
        lines.append(f"### {note.title}")
        lines.append(f"- Sub-question: {note.subquestion}")
        lines.append(f"- URL: {note.url}")
        lines.append(f"- Relevance Score: {note.relevance_score}")
        lines.append(f"- Rationale: {note.rationale}")
        if note.extracted_points:
            lines.append("- Extracted Points:")
            for point in note.extracted_points:
                lines.append(f"  - {point}")
        lines.append("")

    lines.append("## Sources\n")
    for src in report.sources:
        lines.append(f"- {src}")

    output_file = Path(output_path)
    output_file.parent.mkdir(parents=True, exist_ok=True)
    output_file.write_text("\n".join(lines), encoding="utf-8")


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--topic", required=True, help="Research topic")
    parser.add_argument(
        "--provider",
        default="ollama",
        choices=["ollama", "gemini"],
        help="LLM provider to use",
    )
    parser.add_argument(
        "--model",
        default=None,
        help="Optional model override",
    )
    parser.add_argument(
        "--output",
        default=None,
        help="Optional custom output path",
    )
    args = parser.parse_args()

    output_path = args.output if args.output else generate_output_path(args.topic, args.provider)

    agent = ResearchAgent(
        provider=args.provider,
        model=args.model,
        max_results=2, # limited search results to two per sub-question for test to keep latency and cost manageable.
    )
    result = agent.run(args.topic)

    print(f"\nProvider: {args.provider}")
    if args.model:
        print(f"Model override: {args.model}")

    print("\nGenerated sub-questions:")
    for idx, q in enumerate(result["question_set"].subquestions, start=1):
        print(f"{idx}. {q}")

    print(f"\nRelevant notes collected: {len(result['notes'])}")

    save_markdown(output_path, result)
    print(f"Saved report to {output_path}")


if __name__ == "__main__":
    main()