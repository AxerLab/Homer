import logfire
from src.aislides.core.agent.agent import agent, interator_agent
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.core.models.SliderIterator import SlideIterator

logfire.configure()
logfire.instrument_pydantic_ai() 

while True:
    # Get topic from user
    topic = input("Enter a topic for the presentation (or 'quit' to exit): ")
    
    if topic.lower() in ['quit', 'q']:
        break
    
    print(f"Generating presentation for topic: {topic}")
    res = agent.run_sync(topic) # RAG prompt here

    print(res.output)

    structure_to_ppt(res.output, save_path="test.pptx")
    
    # Ask if user wants to continue
    while True:
        slide_choice = input("\nEnter the slide number (not zero based) you wish to change (or 'q' to exit):").lower().strip()
        if slide_choice in ['n', 'no']:
            print("Goodbye!")
            exit()
        elif slide_choice.isdigit() and 1 <= int(slide_choice) <= len(res.output.slides):
            slide_num = int(slide_choice) - 1  # Convert to zero-based index
            new_content = input(f"Enter new content prompt for slide {slide_choice}:")
            slider_iterator = SlideIterator(
                slide=res.output.slides[slide_num],
                slides_before=res.output.slides[:slide_num] if slide_num > 0 else None,
                slides_after=res.output.slides[slide_num+1:] if slide_num < len(res.output.slides) - 1 else None,
                instructions=new_content,
                prompt=topic
            )
            edited_slide = interator_agent.run_sync(slider_iterator.model_dump_json())
            print(edited_slide.output)
            # modify the slide in res.output.slides
            res.output.slides[slide_num] = edited_slide.output
            structure_to_ppt(res.output, save_path="test.pptx")
            print(f"Slide {slide_choice} updated and presentation saved as test.pptx")
        else:
            print("Please enter valid slide number or 'q' for quit.")