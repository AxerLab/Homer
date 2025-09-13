import logfire
from src.aislides.core.agent.agent import agent
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt

logfire.configure()
logfire.instrument_pydantic_ai() 

res = agent.run_sync("Artificial Intelligence") # RAG prompt here

print(res.output)

structure_to_ppt(res.output, save_path="test.pptx")