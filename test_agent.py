import logfire
from src.aislides.core.generator.generator import generate_presentation
from src.aislides.core.engines.pptx.json_handler import structure_to_ppt
from src.aislides.core.iterator.iterator import regenerate_slide

logfire.configure()
logfire.instrument_pydantic_ai()

# Get topic from user
original_prompt = input("Enter a topic for the presentation: ")

print(f"Generating presentation for topic: {original_prompt}")

tries = 0

while True:
    current_prompt = original_prompt
    if tries > 0:
        current_prompt = input(
            "Enter your slide gen prompt if you want to refine it (or type 'q' to quit): "
        )
        if current_prompt.lower() == "q":
            print("Goodbye!")
            break
    res = generate_presentation(current_prompt, original_prompt)

    print(res)

    structure_to_ppt(res, save_path="test.pptx")

    # Ask if user wants to continue
    while True:
        slide_choice = (
            input(
                "\nEnter the slide number (not zero based) you wish to change (or 'q' to exit): "
            )
            .lower()
            .strip()
        )
        if slide_choice in ["n", "q"]:
            print("Goodbye!")
            break
        elif slide_choice.isdigit() and 1 <= int(slide_choice) <= len(
            res.slides
        ):
            slide_num = int(slide_choice) - 1  # Convert to zero-based index
            new_content = input(f"Enter new content prompt for slide {slide_choice}: ")
            edited_ppt = regenerate_slide(
                presentation=res,
                slide_index=slide_num,
                edit_prompt=new_content,
                original_prompt=original_prompt,
            )
            structure_to_ppt(edited_ppt, save_path="test.pptx")
            print(f"Slide {slide_choice} updated and presentation saved as test.pptx")
        else:
            print("Please enter valid slide number or 'q' for quit.")

    tries += 1
