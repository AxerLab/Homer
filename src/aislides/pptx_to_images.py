"""
Convert PPTX slides to images using Aspose.Slides
"""
import os
import base64
from pathlib import Path
from typing import List, Dict, Any
import aspose.slides as slides
import aspose.pydrawing as drawing

def convert_pptx_to_images(pptx_path: str, output_dir: str = None) -> Dict[str, Any]:
    """
    Convert PPTX slides to images and return as base64 encoded strings.
    """
    try:
        # Create output directory if specified
        if output_dir:
            Path(output_dir).mkdir(parents=True, exist_ok=True)

        # Load the presentation
        pres = slides.Presentation(pptx_path)

        slide_images = []

        # Process each slide
        for i, slide in enumerate(pres.slides):
            # Create a bitmap image of the slide
            # Default size is usually good enough
            bmp = slide.get_image()

            # Save to temporary file first, then read it back
            import tempfile
            with tempfile.NamedTemporaryFile(suffix='.png', delete=False) as tmp_file:
                tmp_path = tmp_file.name
                bmp.save(tmp_path, drawing.imaging.ImageFormat.png)

            # Read the saved image
            with open(tmp_path, 'rb') as f:
                image_bytes = f.read()

            # Clean up temp file
            import os
            os.unlink(tmp_path)

            # Convert to base64
            image_base64 = base64.b64encode(image_bytes).decode('utf-8')

            # Save to file if output_dir specified
            if output_dir:
                image_path = Path(output_dir) / f"slide_{i + 1}.png"
                with open(image_path, 'wb') as f:
                    f.write(image_bytes)

            slide_data = {
                "slide_number": i + 1,
                "image_base64": f"data:image/png;base64,{image_base64}",
                "width": int(pres.slide_size.size.width),
                "height": int(pres.slide_size.size.height)
            }

            # Try to extract title and notes
            try:
                title = ""
                notes = ""

                for shape in slide.shapes:
                    if hasattr(shape, 'text_frame') and shape.text_frame:
                        text = shape.text_frame.text
                        if text and not title and hasattr(shape, 'placeholder') and shape.placeholder:
                            if shape.placeholder.type == slides.PlaceholderType.TITLE:
                                title = text

                # Get notes if available
                if slide.notes_slide and slide.notes_slide.notes_text_frame:
                    notes = slide.notes_slide.notes_text_frame.text

                slide_data["title"] = title or f"Slide {i + 1}"
                slide_data["notes"] = notes
            except:
                slide_data["title"] = f"Slide {i + 1}"
                slide_data["notes"] = ""

            slide_images.append(slide_data)

        return {
            "success": True,
            "total_slides": len(pres.slides),
            "slides": slide_images,
            "presentation_width": int(pres.slide_size.size.width),
            "presentation_height": int(pres.slide_size.size.height)
        }

    except Exception as e:
        print(f"Error converting PPTX to images: {e}")
        return {
            "success": False,
            "error": str(e),
            "total_slides": 0,
            "slides": []
        }

def get_pptx_slide_images(file_path: str) -> Dict[str, Any]:
    """
    Main function to get PPTX slides as images.
    Returns base64 encoded images that can be displayed directly in the browser.
    """
    if not os.path.exists(file_path):
        return {"error": "File not found", "success": False}

    return convert_pptx_to_images(file_path)