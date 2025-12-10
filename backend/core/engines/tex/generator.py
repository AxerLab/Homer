from pathlib import Path
from pylatex import Document, NoEscape
from ...generator.generator import generate_presentation
from ...models.layouts.slide_layout import SlideLayout
from ...models.content.textcontent.textcontent import TextContent
from typing import Union
import subprocess
import requests
from io import BytesIO
from urllib.parse import urlparse
import tempfile
import os

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

def handle_image_for_latex(image_path: str, output_dir: Path) -> str:
    """
    Handle image path for LaTeX inclusion. Downloads URLs to temporary files.
    
    Args:
        image_path: Path to the image file or URL
        output_dir: Directory where temporary files should be saved
        
    Returns:
        Local file path suitable for LaTeX inclusion
    """
    if not image_path:
        return ""
    
    parsed = urlparse(image_path)
    if parsed.scheme in ('http', 'https'):
        try:
            # Download the image from URL
            response = requests.get(image_path, timeout=10)
            response.raise_for_status()
            
            # Determine file extension from URL or content-type
            ext = Path(parsed.path).suffix
            if not ext:
                content_type = response.headers.get('content-type', '')
                if 'jpeg' in content_type or 'jpg' in content_type:
                    ext = '.jpg'
                elif 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                else:
                    ext = '.jpg'  # default
            
            # Save to a temporary file in the output directory
            temp_file = tempfile.NamedTemporaryFile(
                delete=False, 
                suffix=ext, 
                dir=output_dir
            )
            temp_file.write(response.content)
            temp_file.close()
            
            return temp_file.name
        except (requests.RequestException, OSError) as e:
            print(f"Error downloading image from {image_path}: {e}")
            return ""
    else:
        # Local file path - verify it exists
        if Path(image_path).exists():
            return image_path
        else:
            print(f"Warning: Image file not found: {image_path}")
            return ""

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
        
        elif slide.layout == SlideLayout.PICTURE_WITH_CAPTION:
            if slide.image:
                local_image_path = handle_image_for_latex(slide.image, output_dir)
                if local_image_path:
                    # Escape backslashes for Windows paths
                    escaped_path = local_image_path.replace('\\', '/')
                    doc.append(NoEscape(r'\begin{center}'))
                    doc.append(NoEscape(f'\\includegraphics[width=0.8\\textwidth]{{{escaped_path}}}'))
                    doc.append(NoEscape(r'\end{center}'))
            if slide.content and slide.content.text and slide.content.text.para:
                doc.append(NoEscape(r'{\tiny\par}'))
                doc.append(NoEscape(escape_latex(slide.content.text.para)))
        
        doc.append(NoEscape(r'\end{frame}'))

    # generate_tex expects a path without the .tex extension
    # Generate tex file in the output directory
    tex_output_path = output_dir / pdf_basename
    doc.generate_tex(str(tex_output_path))

    # Reconstruct the full path to the .tex file
    tex_file_path = Path(f"{tex_output_path}.tex")
    
    # Call the TeX service
    import requests
    import os
    
    tex_service_url = os.getenv("TEX_SERVICE_URL", "http://localhost:8001")
    url = f"{tex_service_url}/generate-pdf"
    
    try:
        with open(tex_file_path, 'rb') as f:
            files = {'file': (tex_file_path.name, f, 'application/x-tex')}
            response = requests.post(url, files=files, timeout=120)
        
        if response.status_code == 200:
            pdf_path = output_dir / f"{pdf_basename}.pdf"
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            return pdf_path.resolve()
        else:
            print(f"TeX Service Error: {response.status_code} - {response.text}")
            raise Exception(f"TeX Service failed: {response.text}")
            
    except Exception as e:
        print(f"Error calling TeX service: {e}")
        raise

