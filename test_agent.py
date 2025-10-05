import logfire
from src.aislides.core.agent.agent import agent
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.core.iterator.iterator import regenerate_slide

logfire.configure()
logfire.instrument_pydantic_ai() 

# Get topic from user
topic = input("Enter a topic for the presentation: ")

print(f"Generating presentation for topic: {topic}")

while True:
    try:
        res = agent.run_sync(topic) # RAG prompt here
        break
    except Exception as e:
        print(f"Error generating presentation: {e}")
        continue

print(res.output)

structure_to_ppt(res.output, save_path="test.pptx")

# Ask if user wants to continue
while True:
    slide_choice = input("\nEnter the slide number (not zero based) you wish to change (or 'q' to exit): ").lower().strip()
    if slide_choice in ['n', 'q']:
        print("Goodbye!")
        break
    elif slide_choice.isdigit() and 1 <= int(slide_choice) <= len(res.output.slides):
        slide_num = int(slide_choice) - 1  # Convert to zero-based index
        new_content = input(f"Enter new content prompt for slide {slide_choice}: ")
        edited_ppt = regenerate_slide(
            presentation=res.output,
            slide_index=slide_num,
            edit_prompt=new_content,
            original_prompt=topic,
        )
        structure_to_ppt(edited_ppt, save_path="test.pptx")
        print(f"Slide {slide_choice} updated and presentation saved as test.pptx")
    else:
        print("Please enter valid slide number or 'q' for quit.")