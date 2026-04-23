import argparse
import re
from datetime import datetime
from pathlib import Path

from app.agent import ResearchAgent

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