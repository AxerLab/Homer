from pathlib import Path
import json

from src.aislides.core.generator.generator import generate_presentation
from src.aislides.core.agent.agent import tex_agent
from pylatex import Document, NoEscape

def generate_tex_and_pdf(original_prompt: str, user_prompt: str, tex_path: str = "test.tex", pdf_basename: str = "test"):
    # 1) generate SlidePresentation using existing generator
    presentation = generate_presentation(original_prompt=original_prompt, user_prompt=user_prompt)

    # 2) serialize to JSON for tex_agent
    if hasattr(presentation, "model_dump_json"):
        presentation_json = presentation.model_dump_json()
    else:
        presentation_json = json.dumps(presentation)

    # 3) get LaTeX source from tex_agent
    tex_source = tex_agent.run_sync(presentation_json)
    tex_source = str(tex_source)

    # 4) write raw tex output for inspection
    Path(tex_path).write_text(tex_source, encoding="utf-8")

    # 5) compile with pylatex (uses pdflatex internally)
    # If the agent produced a full document, try to extract preamble and body.
    if "\\begin{document}" in tex_source:
        preamble, rest = tex_source.split("\\begin{document}", 1)
        body = rest
        if "\\end{document}" in body:
            body, _ = body.split("\\end{document}", 1)

        # remove any \documentclass lines to avoid duplicate documentclass entries
        preamble_lines = [
            line for line in preamble.splitlines() if not line.strip().startswith("\\documentclass")
        ]
        preamble_clean = "\n".join(preamble_lines).strip()

        doc = Document(pdf_basename)
        if preamble_clean:
            # insert remaining preamble raw (packages / defs)
            doc.preamble.append(NoEscape(preamble_clean))
        doc.append(NoEscape(body))
    else:
        # assume tex_source is a document body; wrap in a basic Document
        doc = Document(pdf_basename)
        doc.append(NoEscape(tex_source))

    # generate pdf using pylatex (which invokes pdflatex internally)
    doc.generate_pdf(pdf_basename, compiler="pdflatex", clean_tex=False)

    return Path(f"{pdf_basename}.pdf").resolve()


if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) or "Generate a short 3-slide presentation about AI safety"
    out_pdf = generate_tex_and_pdf(prompt, prompt)
    print("Generated PDF:", out_pdf)