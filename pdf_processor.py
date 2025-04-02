"""
PDF Resume Processor for Resume Screening AI Module

This module handles the extraction and preprocessing of text from PDF resumes.
It includes document structure analysis and text normalization.
"""

import logging
import os
import io
import re
from typing import Dict, List, Any, Optional, BinaryIO
import PyPDF2
from pdfminer.high_level import extract_text
from pdfminer.layout import LAParams

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class PDFResumeProcessor:
    """
    PDF Resume Processor class for extracting and preprocessing text from PDF resumes.
    """
    
    def __init__(self, use_pdfminer: bool = True):
        """
        Initialize the PDF Resume Processor.
        
        Args:
            use_pdfminer: Whether to use PDFMiner for text extraction (better quality but slower)
        """
        self.use_pdfminer = use_pdfminer
        logger.info("PDF Resume Processor initialized")
    
    def extract_text_from_file(self, file_path: str) -> Dict[str, Any]:
        """
        Extract text from a PDF file.
        
        Args:
            file_path: Path to the PDF file
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        logger.info(f"Extracting text from PDF file: {file_path}")
        
        if not os.path.exists(file_path):
            logger.error(f"File not found: {file_path}")
            return {"success": False, "message": "File not found", "text": "", "metadata": {}}
        
        try:
            with open(file_path, 'rb') as file:
                return self.extract_text_from_binary(file)
        except Exception as e:
            logger.exception(f"Error extracting text from PDF file: {str(e)}")
            return {"success": False, "message": str(e), "text": "", "metadata": {}}
    
    def extract_text_from_binary(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """
        Extract text from a binary PDF file object.
        
        Args:
            file_obj: Binary file object
            
        Returns:
            Dictionary containing extracted text and metadata
        """
        logger.info("Extracting text from binary PDF file")
        
        try:
            # Extract text using preferred method
            if self.use_pdfminer:
                text = self._extract_with_pdfminer(file_obj)
                extraction_method = "pdfminer"
            else:
                text = self._extract_with_pypdf2(file_obj)
                extraction_method = "pypdf2"
            
            # If text extraction failed with primary method, try fallback
            if not text.strip() and self.use_pdfminer:
                logger.warning("PDFMiner extraction failed, falling back to PyPDF2")
                file_obj.seek(0)  # Reset file pointer
                text = self._extract_with_pypdf2(file_obj)
                extraction_method = "pypdf2_fallback"
            elif not text.strip() and not self.use_pdfminer:
                logger.warning("PyPDF2 extraction failed, falling back to PDFMiner")
                file_obj.seek(0)  # Reset file pointer
                text = self._extract_with_pdfminer(file_obj)
                extraction_method = "pdfminer_fallback"
            
            # Extract metadata
            file_obj.seek(0)  # Reset file pointer
            metadata = self._extract_metadata(file_obj)
            
            # Preprocess text
            processed_text = self._preprocess_text(text)
            
            return {
                "success": True,
                "text": processed_text,
                "raw_text": text,
                "metadata": metadata,
                "extraction_method": extraction_method
            }
        except Exception as e:
            logger.exception(f"Error extracting text from binary PDF file: {str(e)}")
            return {"success": False, "message": str(e), "text": "", "metadata": {}}
    
    def _extract_with_pdfminer(self, file_obj: BinaryIO) -> str:
        """
        Extract text from PDF using PDFMiner.
        
        Args:
            file_obj: Binary file object
            
        Returns:
            Extracted text
        """
        try:
            # Create a copy of the file in memory to avoid modifying the original
            file_copy = io.BytesIO(file_obj.read())
            file_obj.seek(0)  # Reset original file pointer
            
            # Configure PDFMiner parameters
            laparams = LAParams(
                line_margin=0.5,
                word_margin=0.1,
                char_margin=2.0,
                all_texts=True
            )
            
            # Extract text
            text = extract_text(file_copy, laparams=laparams)
            return text
        except Exception as e:
            logger.warning(f"PDFMiner extraction error: {str(e)}")
            return ""
    
    def _extract_with_pypdf2(self, file_obj: BinaryIO) -> str:
        """
        Extract text from PDF using PyPDF2.
        
        Args:
            file_obj: Binary file object
            
        Returns:
            Extracted text
        """
        try:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file_obj)
            
            # Extract text from each page
            text = ""
            for page_num in range(len(pdf_reader.pages)):
                page = pdf_reader.pages[page_num]
                text += page.extract_text() + "\n\n"
            
            return text
        except Exception as e:
            logger.warning(f"PyPDF2 extraction error: {str(e)}")
            return ""
    
    def _extract_metadata(self, file_obj: BinaryIO) -> Dict[str, Any]:
        """
        Extract metadata from PDF file.
        
        Args:
            file_obj: Binary file object
            
        Returns:
            Dictionary of metadata
        """
        try:
            # Create a PDF reader object
            pdf_reader = PyPDF2.PdfReader(file_obj)
            
            # Extract metadata
            metadata = pdf_reader.metadata
            if metadata:
                return {
                    "title": metadata.get("/Title", ""),
                    "author": metadata.get("/Author", ""),
                    "subject": metadata.get("/Subject", ""),
                    "creator": metadata.get("/Creator", ""),
                    "producer": metadata.get("/Producer", ""),
                    "creation_date": metadata.get("/CreationDate", ""),
                    "modification_date": metadata.get("/ModDate", ""),
                    "page_count": len(pdf_reader.pages)
                }
            else:
                return {"page_count": len(pdf_reader.pages)}
        except Exception as e:
            logger.warning(f"Metadata extraction error: {str(e)}")
            return {}
    
    def _preprocess_text(self, text: str) -> str:
        """
        Preprocess extracted text to improve quality.
        
        Args:
            text: Raw extracted text
            
        Returns:
            Preprocessed text
        """
        if not text:
            return ""
        
        # Replace multiple newlines with a single newline
        processed = re.sub(r'\n{3,}', '\n\n', text)
        
        # Replace multiple spaces with a single space
        processed = re.sub(r' {2,}', ' ', processed)
        
        # Remove non-printable characters
        processed = re.sub(r'[^\x20-\x7E\n]', '', processed)
        
        # Fix common PDF extraction issues
        processed = processed.replace('•', '* ')  # Fix bullet points
        processed = re.sub(r'(\w)- (\w)', r'\1\2', processed)  # Fix hyphenated words
        
        return processed.strip()
    
    def identify_sections(self, text: str) -> Dict[str, str]:
        """
        Identify common resume sections in the text.
        
        Args:
            text: Preprocessed resume text
            
        Returns:
            Dictionary mapping section names to section content
        """
        # Common section headers in resumes
        section_patterns = {
            "contact_info": r"(?i)^(.*?)(CONTACT|PERSONAL|INFO|PROFILE)",
            "summary": r"(?i)^(.*?)(SUMMARY|OBJECTIVE|PROFESSIONAL SUMMARY|CAREER OBJECTIVE)",
            "experience": r"(?i)^(.*?)(EXPERIENCE|WORK|EMPLOYMENT|CAREER|PROFESSIONAL EXPERIENCE)",
            "education": r"(?i)^(.*?)(EDUCATION|ACADEMIC|QUALIFICATION|DEGREE)",
            "skills": r"(?i)^(.*?)(SKILLS|TECHNICAL|TECHNOLOGIES|COMPETENCIES|EXPERTISE)",
            "projects": r"(?i)^(.*?)(PROJECTS|PROJECT EXPERIENCE|PORTFOLIO)",
            "certifications": r"(?i)^(.*?)(CERTIFICATIONS|CERTIFICATES|ACCREDITATIONS)",
            "languages": r"(?i)^(.*?)(LANGUAGES|LANGUAGE PROFICIENCY)",
            "interests": r"(?i)^(.*?)(INTERESTS|HOBBIES|ACTIVITIES)",
            "references": r"(?i)^(.*?)(REFERENCES|REFEREES)"
        }
        
        # Split text into lines
        lines = text.split('\n')
        
        # Identify potential section headers
        section_headers = []
        for i, line in enumerate(lines):
            line = line.strip()
            if line and len(line) < 50 and line.upper() == line:
                section_headers.append((i, line))
        
        # If no section headers found, try alternative approach
        if not section_headers:
            for i, line in enumerate(lines):
                line = line.strip()
                if line and len(line) < 50 and any(re.search(pattern, line, re.IGNORECASE) for pattern in section_patterns.values()):
                    section_headers.append((i, line))
        
        # Extract sections
        sections = {}
        for i in range(len(section_headers)):
            header_idx, header = section_headers[i]
            
            # Determine section name
            section_name = "unknown"
            for name, pattern in section_patterns.items():
                if re.search(pattern, header, re.IGNORECASE):
                    section_name = name
                    break
            
            # Determine section end
            if i < len(section_headers) - 1:
                end_idx = section_headers[i + 1][0]
            else:
                end_idx = len(lines)
            
            # Extract section content
            section_content = '\n'.join(lines[header_idx + 1:end_idx]).strip()
            sections[section_name] = section_content
        
        return sections
    
    def analyze_resume_structure(self, text: str) -> Dict[str, Any]:
        """
        Analyze the structure of a resume.
        
        Args:
            text: Preprocessed resume text
            
        Returns:
            Dictionary with resume structure analysis
        """
        # Identify sections
        sections = self.identify_sections(text)
        
        # Calculate basic metrics
        word_count = len(text.split())
        line_count = len(text.split('\n'))
        char_count = len(text)
        
        # Analyze section distribution
        section_distribution = {
            section: len(content.split()) / word_count if word_count > 0 else 0
            for section, content in sections.items()
        }
        
        # Detect potential issues
        issues = []
        if word_count < 200:
            issues.append("Resume is very short")
        if "experience" not in sections or not sections.get("experience"):
            issues.append("No experience section detected")
        if "education" not in sections or not sections.get("education"):
            issues.append("No education section detected")
        if "skills" not in sections or not sections.get("skills"):
            issues.append("No skills section detected")
        
        return {
            "sections": sections,
            "metrics": {
                "word_count": word_count,
                "line_count": line_count,
                "char_count": char_count,
                "section_count": len(sections)
            },
            "section_distribution": section_distribution,
            "issues": issues
        }

# Example usage
if __name__ == "__main__":
    processor = PDFResumeProcessor()
    
    # Example: Process a PDF resume
    result = processor.extract_text_from_file("example_resume.pdf")
    
    if result["success"]:
        print(f"Extraction method: {result['extraction_method']}")
        print(f"Page count: {result['metadata'].get('page_count', 'Unknown')}")
        print(f"Word count: {len(result['text'].split())}")
        
        # Analyze resume structure
        structure = processor.analyze_resume_structure(result["text"])
        
        print("\nDetected Sections:")
        for section, content in structure["sections"].items():
            print(f"- {section.upper()}: {len(content.split())} words")
        
        print("\nPotential Issues:")
        for issue in structure["issues"]:
            print(f"- {issue}")
    else:
        print(f"Error: {result['message']}")
