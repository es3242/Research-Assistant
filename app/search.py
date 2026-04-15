from langchain_tavily import TavilySearch


def build_search_tool(max_results: int = 2):
    return TavilySearch(max_results=max_results)


def run_search(search_tool, query: str):
    results = search_tool.invoke({"query": query})

    if not results:
        return []

    # Case 1: already a list of result dicts
    if isinstance(results, list):
        return results

    # Case 2: dict wrapper like {"results": [...]}
    if isinstance(results, dict):
        if "results" in results and isinstance(results["results"], list):
            return results["results"]
        return [results]

    # Fallback
    return []