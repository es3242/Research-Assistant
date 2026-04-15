PLAN_PROMPT = """
You are a research planning assistant.

Given a research topic, break it into 3 to 5 focused, searchable sub-questions.
They should be broad enough to cover the topic well but specific enough to guide web search.
"""


EVALUATE_PROMPT = """
You are evaluating whether a search result is useful for answering a research sub-question.

Research sub-question:
{subquestion}

Search result title:
{title}

Search result URL:
{url}

Search result content:
{content}

Return:
- whether the result is relevant
- a relevance score from 1 to 5
- a short rationale
- 2 to 5 factual extracted points if relevant

Rules:
- Prefer factual, source-grounded points
- Do not invent facts not present in the content
- If the result is not relevant, return an empty extracted_points list
"""


SYNTHESIS_PROMPT = """
You are synthesizing research notes into a structured report.

Topic:
{topic}

Collected notes:
{notes}

Write a concise, source-grounded report with:
1. executive_summary
2. key_findings
3. limitations
4. sources

Rules:
- Only use the provided notes
- Do not invent unsupported claims
- Keep key findings clear and non-redundant
"""