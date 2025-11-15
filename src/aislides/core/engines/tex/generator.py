from pathlib import Path
from pylatex import Document, NoEscape
from src.aislides.core.generator.generator import generate_presentation
from src.aislides.core.models.presentation.presentation import SlidePresentation
from src.aislides.core.models.layouts.slide_layout import SlideLayout
from src.aislides.core.models.content.textcontent.textcontent import TextContent
from typing import Union
import subprocess

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

def generate_tex_and_pdf(original_prompt: str, user_prompt: str, tex_path: str = "test.tex", output_filename: str = None):
    presentation = generate_presentation(original_prompt=original_prompt, user_prompt=user_prompt)

    # Determine the base name for files from tex_path or use output_filename if provided
    if output_filename:
        # If output_filename is a full path, use it as is
        pdf_basename = Path(output_filename).stem
        output_dir = Path(output_filename).parent
    else:
        p = Path(tex_path)
        pdf_basename = p.stem
        output_dir = p.parent if p.parent != Path('.') else Path.cwd()
    
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

    # generate_tex expects a path without the .tex extension
    # Generate tex file in the output directory
    tex_output_path = output_dir / pdf_basename
    doc.generate_tex(str(tex_output_path))

    # Reconstruct the full path to the .tex file for docker command
    tex_file = Path(f"{tex_output_path}.tex")
    tex_dir = tex_file.parent.resolve()
    tex_filename = tex_file.name
    
    docker_image = "blang/latex:ubuntu"
    
    command = [
        "docker", "run", "--rm",
        "-v", f"{tex_dir}:/workdir",
        docker_image,
        "pdflatex",
        "-output-directory=/workdir",
        f"/workdir/{tex_filename}"
    ]
    
    try:
        subprocess.run(command, check=True, capture_output=True, text=True)
    except subprocess.CalledProcessError as e:
        print("Error during LaTeX compilation:")
        print(e.stdout)
        print(e.stderr)
        raise
    except FileNotFoundError:
        print("Error: Docker is not installed or not in the system's PATH.")
        raise

    return Path(output_dir / f"{pdf_basename}.pdf").resolve()

