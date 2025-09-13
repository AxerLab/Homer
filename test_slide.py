from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.core.models.presentation.presentation import SlidePresentation
import json

# load test_ppt.json file as structure
with open("test_ppt.json", "r") as f:
    data = json.load(f)

data = SlidePresentation.model_validate(data)

structure_to_ppt(data, save_path="test.pptx")