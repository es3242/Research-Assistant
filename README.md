# Automated Research Assistant

A lightweight research assistant built with LangChain that:

- breaks a topic into focused sub-questions
- searches the web for relevant sources
- evaluates source relevance
- extracts useful notes
- synthesizes a structured markdown report with citations

## Features

- Topic decomposition into 3 searchable sub-questions
- Web search using Tavily
- Relevance filtering and note extraction with an LLM
- Final structured markdown report output
- Provider-swappable architecture:
  - `ollama` for local iterative development
  - `gemini` for occasional quality validation

## Project Structure

```text
research-assistant/
├─ app/
│  ├─ main.py
│  ├─ agent.py
│  ├─ llm_factory.py
│  ├─ prompts.py
│  ├─ schemas.py
│  └─ search.py
├─ outputs/
├─ requirements.txt
├─ .env.example
└─ README.md
