from pathlib import Path
from pylatex import Document, NoEscape
from src.aislides.core.generator.generator import generate_presentation
from src.aislides.core.models.presentation.presentation import SlidePresentation
from src.aislides.core.models.layouts.slide_layout import SlideLayout
from src.aislides.core.models.content.textcontent.textcontent import TextContent
from typing import Union

def escape_latex(text: str) -> str:
    if text is None:
        return ""
    return text.replace('&', r'\&').replace('%', r'\%').replace('$', r'\$').replace('#', r'\#').replace('_', r'\_').replace('{', r'\{').replace('}', r'\}')

def content_to_latex(content: Union[TextContent, list]) -> str:
    latex = ""
    if isinstance(content, list):
        latex += "\\begin{itemize}\n"
        for item in content:
            latex += f"\\item {escape_latex(item)}\n"
        latex += "\\end{itemize}\n"
    else:
        if content.para:
            latex += escape_latex(content.para) + "\n"
        if content.bullet:
            latex += "\\begin{itemize}\n"
            for item in content.bullet:
                latex += f"\\item {escape_latex(item)}\n"
            latex += "\\end{itemize}\n"
    return latex

def generate_tex_and_pdf(original_prompt: str, user_prompt: str, tex_path: str = "test.tex", pdf_basename: str = "test"):
    presentation = generate_presentation(original_prompt=original_prompt, user_prompt=user_prompt)

    doc = Document(documentclass='beamer')
    doc.preamble.append(NoEscape(r'\usepackage[utf8]{inputenc}'))
    doc.preamble.append(NoEscape(r'\usepackage{graphicx}'))
    doc.preamble.append(NoEscape(r'\DeclareUnicodeCharacter{202F}{\,}'))
    
    title = presentation.slides[0].title if presentation.slides else "Presentation"
    doc.preamble.append(NoEscape(f'\\title{{{escape_latex(title)}}}'))
    
    doc.append(NoEscape(r'\frame{\maketitle}'))

    for slide in presentation.slides:
        doc.append(NoEscape(f'\\begin{{frame}}{{{escape_latex(slide.title)}}}'))
        
        if slide.layout == SlideLayout.TITLE_AND_CONTENT:
            if slide.content.text:
                doc.append(NoEscape(content_to_latex(slide.content.text)))
        
        elif slide.layout == SlideLayout.TWO_CONTENT:
            doc.append(NoEscape(r'\begin{columns}[T]'))
            doc.append(NoEscape(r'\begin{column}{.5\textwidth}'))
            if slide.content.text:
                doc.append(NoEscape(content_to_latex(slide.content.text)))
            doc.append(NoEscape(r'\end{column}'))
            doc.append(NoEscape(r'\begin{column}{.5\textwidth}'))
            if slide.content.text2:
                doc.append(NoEscape(content_to_latex(slide.content.text2)))
            doc.append(NoEscape(r'\end{column}'))
            doc.append(NoEscape(r'\end{columns}'))

        elif slide.layout == SlideLayout.COMPARISON:
            doc.append(NoEscape(r'\begin{columns}[T]'))
            doc.append(NoEscape(r'\begin{column}{.5\textwidth}'))
            if slide.content.comparison:
                doc.append(NoEscape(f'\\textbf{{{escape_latex(slide.content.comparison.left_title)}}}')) # type: ignore
                doc.append(NoEscape(content_to_latex(slide.content.comparison.left_content))) # type: ignore
            doc.append(NoEscape(r'\end{column}'))
            doc.append(NoEscape(r'\begin{column}{.5\textwidth}'))
            if slide.content.comparison:
                doc.append(NoEscape(f'\\textbf{{{escape_latex(slide.content.comparison.right_title)}}}')) # type: ignore
                doc.append(NoEscape(content_to_latex(slide.content.comparison.right_content))) # type: ignore
            doc.append(NoEscape(r'\end{column}'))
            doc.append(NoEscape(r'\end{columns}'))
        
        elif slide.layout == SlideLayout.SECTION_HEADER:
            if slide.content.text:
                doc.append(NoEscape(content_to_latex(slide.content.text)))
        
        elif slide.layout == SlideLayout.CONTENT_WITH_CAPTION:
            if slide.content.text:
                doc.append(NoEscape(content_to_latex(slide.content.text)))
            if slide.content.text2:
                doc.append(NoEscape(r'{\tiny\par}'))
                doc.append(NoEscape(content_to_latex(slide.content.text2)))
        
        doc.append(NoEscape(r'\end{frame}'))

    doc.generate_pdf(pdf_basename, compiler="pdflatex", clean_tex=False)
    doc.generate_tex(tex_path)

    return Path(f"{pdf_basename}.pdf").resolve()

if __name__ == "__main__":
    import sys
    prompt = " ".join(sys.argv[1:]) or "Generate a short 3-slide presentation about AI safety"
    out_pdf = generate_tex_and_pdf(prompt, prompt)
    print("Generated PDF:", out_pdf)
