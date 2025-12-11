"""
PPTX to PDF converter using wteja/pdf-converter Docker container

This module provides functionality to convert PPTX files to PDF
using the wteja/pdf-converter Docker container which exposes an HTTP API.
"""

import requests
import logging
from pathlib import Path
import os

logger = logging.getLogger(__name__)
PDF_CONVERTER_URL = os.getenv("PDF_CONVERTER_URL","http://localhost:5001")


def convert_pptx_to_pdf(pptx_path: str, pdf_path: str) -> bool:
    """
    Convert a PPTX file to PDF using the wteja/pdf-converter Docker container.
    
    Args:
        pptx_path: Absolute path to the PPTX file on the host
        pdf_path: Absolute path where the PDF should be saved on the host
        
    Returns:
        bool: True if conversion was successful, False otherwise
    """
    try:
        pptx_file = Path(pptx_path)
        pdf_file = Path(pdf_path)
        
        if not pptx_file.exists():
            logger.error(f"PPTX file not found: {pptx_path}")
            return False
        
        if not PDF_CONVERTER_URL:
            logger.error("PDF_CONVERTER_URL is not set")
            return False
        
        logger.info(f"Converting {pptx_path} to PDF using wteja/pdf-converter")
        
        # Construct the conversion URL
        convert_url = f"{PDF_CONVERTER_URL.rstrip('/')}/convert"

        # Send the file to the conversion service
        with open(pptx_path, 'rb') as f:
            files = {'file': (pptx_file.name, f, 'application/vnd.openxmlformats-officedocument.presentationml.presentation')}
            response = requests.post(convert_url, files=files, timeout=120)
        
        if response.status_code == 200:
            content_length = len(response.content)
            logger.info(f"Received PDF response from service. Size: {content_length} bytes")
            
            if content_length == 0:
                logger.error("Received empty PDF content from service")
                return False

            # Save the PDF response
            with open(pdf_path, 'wb') as f:
                f.write(response.content)
            
            if pdf_file.exists():
                logger.info(f"Successfully converted {pptx_path} to {pdf_path}")
                return True
            else:
                logger.error(f"PDF file not created at {pdf_path}")
                return False
        else:
            logger.error(f"Conversion failed with status {response.status_code}: {response.text}")
            return False
            
    except requests.Timeout:
        logger.error("PDF conversion timed out")
        return False
    except requests.RequestException as e:
        logger.error(f"Request error during conversion: {e}")
        return False
    except Exception as e:
        logger.error(f"Error during PPTX to PDF conversion: {e}")
        return False


def is_converter_available() -> bool:
    """
    Check if the pdf-converter service is running and available.
    
    Returns:
        bool: True if service is available, False otherwise
    """
    try:
        if not PDF_CONVERTER_URL:
            logger.warning("PDF_CONVERTER_URL is not set")
            return False
        # Try a simple health check at the root
        requests.get(PDF_CONVERTER_URL, timeout=5)
        # Any response means the service is up
        return True
    except Exception as e:
        logger.warning(f"pdf-converter service not available: {e}")
        return False
