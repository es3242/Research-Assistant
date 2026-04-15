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
```
## How It Works

1. Generate 3 focused sub-questions from a research topic
2. Search the web for each sub-question
3. Evaluate each result for relevance
4. Extract structured notes from relevant results
5. Synthesize a final report and save it as markdown

## Example Commands

### Run with Ollama

```bash
python -m app.main --topic "AI in healthcare" --provider ollama
```

### Run with Gemini

```bash
python -m app.main --topic "AI in healthcare" --provider gemini
```

## Environment Variables

Create a `.env` file in the project root.

### Required for Tavily

```env
TAVILY_API_KEY=your_tavily_api_key
```

### Required for Gemini

```env
GOOGLE_API_KEY=your_google_api_key
```

## Key Design Choices

- Kept the project as a CLI-based MVP for fast iteration
- Used LangChain for orchestration and structured output
- Used Tavily for web search instead of building a custom scraper
- Separated the workflow into planning, search, evaluation, extraction, and synthesis
- Added provider switching so the workflow stays the same while the model backend changes

## Development Issues Encountered

- PowerShell execution policy blocked virtual environment activation
- Accidentally ran the system Python instead of the virtual environment Python
- OpenAI API quota was unavailable
- Gemini free-tier quota was exhausted quickly during repeated testing
- Tavily integration had a deprecation warning and was migrated to `langchain-tavily`
- Tavily response format required normalization after migration

## Current Status

- End-to-end MVP execution confirmed
- Ollama-based local development workflow working
- Markdown report generation working
- Provider-swappable architecture implemented

## Limitations

- Source trust ranking is still basic
- Relevance filtering is model-dependent
- Report quality may vary depending on the selected provider
- Search depth is intentionally limited to reduce cost and quota usage

## Next Steps

- Improve source quality filtering
- Add better logging and error handling
- Compare report quality across model providers
- Add a sample output file for demonstration
