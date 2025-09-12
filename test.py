from src.aislides.core.agent.agent import agent

res = agent.run_sync("Taj mahal") # RAG prompt here

print(res.output)