from src.aislides.core.agent.agent import agent

res = agent.run_sync("Hello, world!")

print(res.output)