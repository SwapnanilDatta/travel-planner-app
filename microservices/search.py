from duckduckgo_search import DDGS
results = DDGS().text("cache_breakpoint litellm groq", max_results=5)
for r in results:
    print(r)
