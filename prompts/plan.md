I want to design a frontend UI for my project. The project is about a AI generated PPT maker that supports pptx and pdf/tex output. One
can iterate through slides and suggest improvements/enhancements to slides to the AI which will then work to get it done.  It is basically
like cursor, but for ppts.

# UI requirements
- the UI should be futuristic, sleek, modern
- The UI should follow the stack requirements set in @README.md
- The UI will not have a welcome/login page for now, only one single page that contains the main prompt and the editor.
- The UI will have a left bar similar to openAI chatgpt interface and it will contain the past chats (presentation generations)
- A new chat button will also be there in the left bar
- The middle section will have the main prompt textbox, a pptx/pdf viewer (once generated).
- The right side will have a pane which will show when slide gets generated. It will have a textbox for iterative prompting. It will work
on a per slide basis and automatically select the slide number the user is currently viewing
- The UI should work with the backend apis which are described in @api_spec.md

# Important
- The code you generate should only be visual or functional
- No telemetry, smoke testing or other junk codes that do not contribute for functionality and/or visuals is needed
- You will make sure the code is extremely minimal, but satisfies all the constraints.

# Output
- You will not write code, you will create a plan for how to implement it
- You will forsake grammartical correctness for brevity in what you generate in the plan
- The plan should be concise but sufficient
- The plan should have high readability and quick reading friendly without the need of tldrs.

# Process
- You will begin by understanding the code base. read and understand large files of the entire code using gemini cli tool given to you.
- You will then load and read the attached files which contain task specific instructions.
- With your understanding you will create the plan document that handles the UI code generation task.
- Think like a senior developer and follow good practises.
- This is not a production build, this is a mvp so speed of development is more important than quality here.
- Create a plan.md file with phase by phase plan once you are done and I will review it and give a green signal.
- You will also create a checklist at the end of the plan document which will have all the phase wise tasks and later it will get filled by the developers who will build the code.
- You will add the required message for the developer who will code any of the phases that they should fill up the checklist as they get done with the work.
- Deployment and dockerization are not part of the task.
