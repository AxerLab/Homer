import os
import json
import requests
from pylatex import Document
from dotenv import load_dotenv

load_dotenv()

OPENROUTER_API_KEY = os.getenv('OPENROUTER_API_KEY')
if not OPENROUTER_API_KEY:
    raise ValueError("Please set OPENROUTER_API_KEY environment variable")

def call_openrouter(prompt, model="openai/gpt-oss-120b:free"):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "Content-Type": "application/json"
    }
    data = {
        "model": model,
        "messages": [{"role": "user", "content": prompt}]
    }
    response = requests.post(url, headers=headers, json=data)
    response.raise_for_status()
    return response.json()['choices'][0]['message']['content']

def get_json_from_prompt(prompt, user_scope=""):
    scope_context = f" for {user_scope}" if user_scope else ""
    system_prompt = f"""Convert the following prompt into a JSON structure for slides{scope_context}.
The JSON should be in this format:
{{
  "title": "Presentation Title",
  "slides": [
    {{
      "title": "Slide Title 1",
      "content": "Slide content here"
    }},
    {{
      "title": "Slide Title 2",
      "content": "More content"
    }}
  ]
}}
Output only the JSON, no extra text."""
    full_prompt = f"{system_prompt}\n\nPrompt: {prompt}"
    response = call_openrouter(full_prompt).strip()
    
    # Clean the response to extract only the JSON
    if response.startswith('```
        response = response[7:]
    if response.endswith('```'):
        response = response[:-3]
        
    return json.loads(response.strip())

def generate_beamer_from_json(json_data, user_scope=""):
    scope_context = f" for {user_scope}" if user_scope else ""
    system_prompt = f"""Convert the following JSON slide structure into LaTeX Beamer code{scope_context}.
The JSON structure:
{json.dumps(json_data, indent=2)}

Generate complete LaTeX Beamer code that can be compiled directly.
Include proper document class, preamble with necessary packages, and the slide content.
Output only the LaTeX code, no extra text or explanations."""
    
    response = call_openrouter(system_prompt).strip()
    
    # Clean the response to extract only the LaTeX code
    if response.startswith('```
        response = response[8:]
    elif response.startswith('```tex'):
        response = response[6:]
    
    if response.endswith('```
        response = response[:-3]
        
    return response.strip()

def save_latex_to_file(latex_code, filename='slides'):
    filepath = f'{filename}.tex'
    with open(filepath, 'w') as f:
        f.write(latex_code)
    return filepath

def main():
    user_scope = input("Enter user scope/context (e.g., 'high school students', 'business professionals'): ")
    prompt = input("Enter prompt for slides: ")

    # First API call: Generate JSON structure
    print("Generating JSON structure...")
    json_data = get_json_from_prompt(prompt, user_scope)

    # Second API call: Generate LaTeX Beamer code
    print("Generating LaTeX Beamer code...")
    latex_code = generate_beamer_from_json(json_data, user_scope)
    
    # Save the LaTeX code
    tex_file = save_latex_to_file(latex_code)
    print(f"Generated {tex_file}")
    
    print("\nNote: To compile the .tex file into a PDF, you need a LaTeX distribution (like MiKTeX, TeX Live, or MacTeX) installed on your system.")

if __name__ == "__main__":
    main()
