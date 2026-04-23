import re
from datetime import datetime
from pathlib import Path

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

