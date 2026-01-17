"""
Resume Parser Module
Extracts text from PDF resumes using pdfplumber
"""

import os
import tempfile
import pdfplumber
from fastapi import UploadFile


async def parse_resume(pdf_file: UploadFile) -> str:
    """
    Parse a PDF resume and extract text content.
    
    Args:
        pdf_file: FastAPI UploadFile object containing the PDF
        
    Returns:
        Extracted text from the PDF as a string
    """
    # Create a temporary file to store the uploaded PDF
    temp_path = None
    try:
        # Save uploaded file to temp location
        with tempfile.NamedTemporaryFile(delete=False, suffix=".pdf") as temp_file:
            temp_path = temp_file.name
            content = await pdf_file.read()
            temp_file.write(content)
        
        # Extract text using pdfplumber
        extracted_text = []
        with pdfplumber.open(temp_path) as pdf:
            for page in pdf.pages:
                page_text = page.extract_text()
                if page_text:
                    extracted_text.append(page_text)
        
        return "\n\n".join(extracted_text)
    
    finally:
        # Clean up: delete temporary file
        if temp_path and os.path.exists(temp_path):
            os.unlink(temp_path)
