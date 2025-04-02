"""
Experience Extractor for Resume Screening AI Module

This module handles the extraction and analysis of work experience from resume text.
It includes job title recognition, company identification, duration calculation, and relevance scoring.
"""

import logging
import re
import datetime
from typing import Dict, List, Any, Optional, Tuple
from dateutil import parser as date_parser
import spacy
from spacy.matcher import Matcher

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ExperienceExtractor:
    """
    Experience Extractor class for identifying and analyzing work experience from resume text.
    """
    
    def __init__(self, use_spacy: bool = True):
        """
        Initialize the Experience Extractor.
        
        Args:
            use_spacy: Whether to use spaCy for entity recognition
        """
        self.use_spacy = use_spacy
        
        # Initialize spaCy if enabled
        if self.use_spacy:
            try:
                self.nlp = spacy.load("en_core_web_sm")
                logger.info("Loaded spaCy model: en_core_web_sm")
            except Exception as e:
                logger.warning(f"Failed to load spaCy model: {str(e)}")
                logger.warning("Falling back to regex-based extraction")
                self.use_spacy = False
        
        # Compile regex patterns
        self.patterns = self._compile_patterns()
        
        # Initialize job title database
        self.job_titles = self._load_job_titles()
        
        logger.info("Experience Extractor initialized")
    
    def _compile_patterns(self) -> Dict[str, re.Pattern]:
        """
        Compile regex patterns for experience extraction.
        
        Returns:
            Dictionary of compiled regex patterns
        """
        patterns = {
            # Date patterns
            "date_range": re.compile(r'((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4})\s*(?:-|–|to)\s*((?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current|Now)', re.IGNORECASE),
            "date_range_year": re.compile(r'(\d{4})\s*(?:-|–|to)\s*(\d{4}|Present|Current|Now)', re.IGNORECASE),
            
            # Job title patterns
            "job_title_line": re.compile(r'^([A-Z][a-zA-Z\s]+)(?:,|\sat|\s-|\s@)\s+([A-Za-z0-9\s\.,&]+)'),
            "job_title_with_dates": re.compile(r'([A-Z][a-zA-Z\s]+)(?:,|\sat|\s-|\s@)\s+([A-Za-z0-9\s\.,&]+)(?:.*?)(\d{4}\s*(?:-|–|to)\s*(?:\d{4}|Present|Current|Now)|(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}\s*(?:-|–|to)\s*(?:(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Oct|Nov|Dec)[a-z]*\.?\s+\d{4}|Present|Current|Now))', re.IGNORECASE),
            
            # Company patterns
            "company_name": re.compile(r'(?:at|with|for)\s+([A-Z][A-Za-z0-9\s\.,&]+)'),
            
            # Location patterns
            "location": re.compile(r'(?:in|at)\s+([A-Z][A-Za-z\s]+,\s*[A-Z]{2}|[A-Z][A-Za-z\s]+,\s*[A-Za-z\s]+)'),
            
            # Duration patterns
            "duration_years": re.compile(r'(\d+)\+?\s*(?:years|yrs|yr)', re.IGNORECASE),
            "duration_months": re.compile(r'(\d+)\+?\s*(?:months|mos|mo)', re.IGNORECASE)
        }
        
        return patterns
    
    def _load_job_titles(self) -> List[str]:
        """
        Load common job titles database.
        
        Returns:
            List of common job titles
        """
        # Common tech job titles
        return [
            "Software Engineer", "Senior Software Engineer", "Software Developer", "Full Stack Developer",
            "Frontend Developer", "Backend Developer", "Web Developer", "Mobile Developer",
            "iOS Developer", "Android Developer", "DevOps Engineer", "Site Reliability Engineer",
            "Data Scientist", "Data Engineer", "Machine Learning Engineer", "AI Engineer",
            "Product Manager", "Project Manager", "Program Manager", "Scrum Master",
            "QA Engineer", "Quality Assurance Engineer", "Test Engineer", "Automation Engineer",
            "UX Designer", "UI Designer", "UX/UI Designer", "Graphic Designer",
            "System Administrator", "Network Engineer", "Security Engineer", "Cloud Engineer",
            "Database Administrator", "Data Analyst", "Business Analyst", "Systems Analyst",
            "Technical Writer", "Content Developer", "IT Support", "Help Desk Technician",
            "CTO", "CIO", "VP of Engineering", "Director of Engineering",
            "Engineering Manager", "Technical Lead", "Team Lead", "Tech Lead",
            "Architect", "Solutions Architect", "Enterprise Architect", "Technical Architect",
            "Software Architect", "Cloud Architect", "Security Architect", "Network Architect",
            "Consultant", "Technical Consultant", "IT Consultant", "Software Consultant",
            "Intern", "Software Engineering Intern", "Developer Intern", "Research Intern"
        ]
    
    def extract_experience(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract work experience from resume text.
        
        Args:
            text: Resume text
            
        Returns:
            List of extracted experience entries
        """
        logger.info("Extracting work experience from text")
        
        # Extract experience section if present
        sections = self._extract_sections(text)
        experience_section = sections.get("experience", "")
        
        # If no specific experience section found, use the entire text
        if not experience_section:
            experience_section = text
        
        # Extract experience entries
        if self.use_spacy:
            experiences = self._extract_with_spacy(experience_section)
        else:
            experiences = self._extract_with_regex(experience_section)
        
        # Calculate duration and additional metrics
        for exp in experiences:
            self._calculate_duration(exp)
            self._extract_responsibilities(exp, experience_section)
        
        # Sort by start date (most recent first)
        experiences = sorted(experiences, key=lambda x: x.get("start_date", ""), reverse=True)
        
        logger.info(f"Extracted {len(experiences)} experience entries")
        return experiences
    
    def _extract_with_regex(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract experience entries using regex patterns.
        
        Args:
            text: Experience section text
            
        Returns:
            List of extracted experience entries
        """
        experiences = []
        
        # Split text into lines
        lines = text.split('\n')
        
        # Process each line
        current_exp = None
        description_lines = []
        
        for i, line in enumerate(lines):
            line = line.strip()
            
            # Skip empty lines
            if not line:
                continue
            
            # Check if line contains job title and company
            job_title_match = self.patterns["job_title_line"].search(line)
            date_match = self.patterns["date_range"].search(line) or self.patterns["date_range_year"].search(line)
            
            # If line has job title or date, it might be the start of a new experience entry
            if job_title_match or date_match:
                # Save previous experience if exists
                if current_exp:
                    current_exp["description"] = "\n".join(description_lines).strip()
                    experiences.append(current_exp)
                    description_lines = []
                
                # Create new experience entry
                current_exp = {
                    "title": "",
                    "company": "",
                    "location": "",
                    "start_date": "",
                    "end_date": "",
                    "is_current": False,
                    "duration_months": 0,
                    "description": ""
                }
                
                # Extract job title and company
                if job_title_match:
                    current_exp["title"] = job_title_match.group(1).strip()
                    current_exp["company"] = job_title_match.group(2).strip()
                
                # Extract date range
                if date_match:
                    if self.patterns["date_range"].search(line):
                        date_match = self.patterns["date_range"].search(line)
                    else:
                        date_match = self.patterns["date_range_year"].search(line)
                    
                    start_date = date_match.group(1).strip()
                    end_date = date_match.group(2).strip()
                    
                    current_exp["start_date"] = start_date
                    current_exp["end_date"] = end_date
                    current_exp["is_current"] = end_date.lower() in ["present", "current", "now"]
                
                # Extract location if present
                location_match = self.patterns["location"].search(line)
                if location_match:
                    current_exp["location"] = location_match.group(1).strip()
            
            # If not a new entry, add to description of current entry
            elif current_exp:
                description_lines.append(line)
        
        # Add the last experience entry
        if current_exp:
            current_exp["description"] = "\n".join(description_lines).strip()
            experiences.append(current_exp)
        
        return experiences
    
    def _extract_with_spacy(self, text: str) -> List[Dict[str, Any]]:
        """
        Extract experience entries using spaCy NER.
        
        Args:
            text: Experience section text
            
        Returns:
            List of extracted experience entries
        """
        experiences = []
        
        # Process text with spaCy
        doc = self.nlp(text)
        
        # Set up custom matcher for job titles
        matcher = Matcher(self.nlp.vocab)
        
        # Add patterns for job titles
        for title in self.job_titles:
            words = title.lower().split()
            pattern = [{"LOWER": word} for word in words]
            matcher.add("JOB_TITLE", [pattern])
        
        # Find matches
        matches = matcher(doc)
        
        # Extract job title spans
        job_title_spans = []
        for match_id, start, end in matches:
            span = doc[start:end]
            job_title_spans.append((span.start_char, span.end_char, span.text))
        
        # Sort by position in text
        job_title_spans.sort()
        
        # Extract experience entries
        for i, (start, end, title) in enumerate(job_title_spans):
            # Determine the text range for this entry
            if i < len(job_title_spans) - 1:
                next_start = job_title_spans[i + 1][0]
                entry_text = text[start:next_start]
            else:
                entry_text = text[start:]
            
            # Create experience entry
            exp = {
                "title": title,
                "company": "",
                "location": "",
                "start_date": "",
                "end_date": "",
                "is_current": False,
                "duration_months": 0,
                "description": entry_text.strip()
            }
            
            # Extract company
            company_match = self.patterns["company_name"].search(entry_text)
            if company_match:
                exp["company"] = company_match.group(1).strip()
            
            # Extract date range
            date_match = self.patterns["date_range"].search(entry_text) or self.patterns["date_range_year"].search(entry_text)
            if date_match:
                if self.patterns["date_range"].search(entry_text):
                    date_match = self.patterns["date_range"].search(entry_text)
                else:
                    date_match = self.patterns["date_range_year"].search(entry_text)
                
                start_date = date_match.group(1).strip()
                end_date = date_match.group(2).strip()
                
                exp["start_date"] = start_date
                exp["end_date"] = end_date
                exp["is_current"] = end_date.lower() in ["present", "current", "now"]
            
            # Extract location
            location_match = self.patterns["location"].search(entry_text)
            if location_match:
                exp["location"] = location_match.group(1).strip()
            
            # Add to experiences
            experiences.append(exp)
        
        return experiences
    
    def _calculate_duration(self, experience: Dict[str, Any]) -> None:
        """
        Calculate duration in months for an experience entry.
        
        Args:
            experience: Experience entry dictionary (modified in place)
        """
        start_date_str = experience.get("start_date", "")
        end_date_str = experience.get("end_date", "")
        
        if not start_date_str:
            return
        
        try:
            # Parse start date
            start_date = self._parse_date(start_date_str)
            
            # Parse end date
            if experience.get("is_current", False) or end_date_str.lower() in ["present", "current", "now"]:
                end_date = datetime.datetime.now()
                experience["is_current"] = True
            else:
                end_date = self._parse_date(end_date_str)
            
            # Calculate duration in months
            if start_date and end_date:
                years_diff = end_date.year - start_date.year
                months_diff = end_date.month - start_date.month
                total_months = years_diff * 12 + months_diff
                
                # Adjust for partial months
                if end_date.day < start_date.day:
                    total_months -= 1
                
                experience["duration_months"] = max(0, total_months)
                experience["duration_years"] = round(total_months / 12, 1)
        except Exception as e:
            logger.warning(f"Error calculating duration: {str(e)}")
    
    def _parse_date(self, date_str: str) -> Optional[datetime.datetime]:
        """
        Parse date string into datetime object.
        
        Args:
            date_str: Date string
            
        Returns:
            Datetime object or None if parsing fails
        """
        try:
            # Handle year-only dates
            if re.match(r'^\d{4}$', date_str):
                return datetime.datetime(int(date_str), 1, 1)
            
            # Parse with dateutil
            return date_parser.parse(date_str, fuzzy=True)
        except Exception as e:
            logger.warning(f"Error parsing date '{date_str}': {str(e)}")
            return None
    
    def _extract_responsibilities(self, experience: Dict[str, Any], full_text: str) -> None:
        """
        Extract responsibilities and achievements from experience description.
        
        Args:
            experience: Experience entry dictionary (modified in place)
            full_text: Full text to search for responsibilities
        """
        description = experience.get("description", "")
        
        # Find the section of text that corresponds to this experience
        title = experience.get("title", "")
        company = experience.get("company", "")
        
        if title and company:
            # Create a pattern to find this experience in the full text
            pattern = re.compile(f"{re.escape(title)}.*?{re.escape(company)}", re.IGNORECASE | re.DOTALL)
            match = pattern.search(full_text)
            
            if match:
                # Find the start of this experience
                start_pos = match.start()
                
                # Find the next experience or the end of the section
                next_exp_pattern = re.compile(r'(?:\n\n|\n)([A-Z][a-zA-Z\s]+)(?:,|\sat|\s-|\s@)\s+([A-Za-z0-9\s\.,&]+)')
                next_match = next_exp_pattern.search(full_text, start_pos + len(match.group(0)))
                
                if next_match:
                    end_pos = next_match.start()
                else:
                    # Find the next section header
                    section_pattern = re.compile(r'\n\n([A-Z][A-Z\s]+)(?:\n|\:)')
                    section_match = section_pattern.search(full_text, start_pos + len(match.group(0)))
                    
                    if section_match:
                        end_pos = section_match.start()
                    else:
                        end_pos = len(full_text)
                
                # Extract the text for this experience
                exp_text = full_text[start_pos:end_pos].strip()
                
                # Extract bullet points
                bullet_points = []
                for line in exp_text.split('\n'):
                    line = line.strip()
                    if line.startswith('-') or line.startswith('•') or line.startswith('*') or re.match(r'^\d+\.', line):
                        bullet_points.append(line.lstrip('- •*').strip())
                
                if bullet_points:
                    experience["responsibilities"] = bullet_points
                    
                    # Update description if it was empty
                    if not description:
                        experience["description"] = exp_text
    
    def _extract_sections(self, text: str) -> Dict[str, str]:
        """
        Extract common resume sections from text.
        
        Args:
            text: Resume text
            
        Returns:
            Dictionary mapping section names to content
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
    
    def analyze_experience(self, experiences: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Analyze experience entries to extract insights.
        
        Args:
            experiences: List of experience entries
            
        Returns:
            Dictionary with experience analysis
        """
        if not experiences:
            return {
                "total_experience_months": 0,
                "total_experience_years": 0,
                "current_job": None,
                "longest_position": None,
                "average_tenure_months": 0,
                "job_count": 0,
                "companies": [],
                "job_titles": [],
                "most_recent_experience": None
            }
        
        # Calculate total experience (avoiding overlaps)
        experiences_sorted = sorted(experiences, key=lambda x: self._parse_date(x.get("start_date", "")) or datetime.datetime.now(), reverse=False)
        
        total_months = 0
        current_end_date = None
        
        for exp in experiences_sorted:
            start_date = self._parse_date(exp.get("start_date", ""))
            
            if exp.get("is_current", False):
                end_date = datetime.datetime.now()
            else:
                end_date = self._parse_date(exp.get("end_date", ""))
            
            if not start_date or not end_date:
                continue
            
            # Check for overlap with previous position
            if current_end_date and start_date <= current_end_date:
                # Positions overlap, use the later end date
                if end_date > current_end_date:
                    months_to_add = (end_date.year - current_end_date.year) * 12 + (end_date.month - current_end_date.month)
                    total_months += max(0, months_to_add)
                    current_end_date = end_date
            else:
                # No overlap, add full duration
                months = exp.get("duration_months", 0)
                total_months += months
                current_end_date = end_date
        
        # Find current job
        current_job = next((exp for exp in experiences if exp.get("is_current", False)), None)
        
        # Find longest position
        longest_position = max(experiences, key=lambda x: x.get("duration_months", 0), default=None)
        
        # Calculate average tenure
        average_tenure = total_months / len(experiences) if experiences else 0
        
        # Extract companies and job titles
        companies = [exp.get("company", "") for exp in experiences if exp.get("company")]
        job_titles = [exp.get("title", "") for exp in experiences if exp.get("title")]
        
        # Get most recent experience
        most_recent = experiences[0] if experiences else None
        
        return {
            "total_experience_months": total_months,
            "total_experience_years": round(total_months / 12, 1),
            "current_job": current_job,
            "longest_position": longest_position,
            "average_tenure_months": round(average_tenure, 1),
            "job_count": len(experiences),
            "companies": companies,
            "job_titles": job_titles,
            "most_recent_experience": most_recent
        }
    
    def match_experience_to_job(self, 
                              experience_analysis: Dict[str, Any], 
                              job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Match candidate experience against job requirements.
        
        Args:
            experience_analysis: Experience analysis dictionary
            job_requirements: Job requirements dictionary
            
        Returns:
            Dictionary with match results
        """
        # Extract job requirements
        required_years = job_requirements.get("min_experience_years", 0)
        preferred_years = job_requirements.get("preferred_experience_years", required_years + 2)
        required_titles = job_requirements.get("relevant_titles", [])
        required_industries = job_requirements.get("relevant_industries", [])
        
        # Calculate experience match
        total_years = experience_analysis.get("total_experience_years", 0)
        
        if total_years >= preferred_years:
            experience_score = 100
        elif total_years >= required_years:
            # Scale between 70-99 based on how close to preferred years
            experience_score = 70 + (total_years - required_years) / (preferred_years - required_years) * 29
        elif total_years > 0:
            # Scale between 0-69 based on how close to required years
            experience_score = (total_years / required_years) * 69 if required_years > 0 else 50
        else:
            experience_score = 0
        
        # Check for relevant job titles
        job_titles = experience_analysis.get("job_titles", [])
        title_matches = []
        
        for title in job_titles:
            for required_title in required_titles:
                if required_title.lower() in title.lower():
                    title_matches.append(title)
                    break
        
        title_match_score = (len(title_matches) / len(required_titles)) * 100 if required_titles else 100
        
        # Calculate overall match score (70% experience years, 30% title relevance)
        overall_score = (experience_score * 0.7) + (title_match_score * 0.3)
        
        return {
            "overall_experience_score": overall_score,
            "experience_years_score": experience_score,
            "title_match_score": title_match_score,
            "has_required_years": total_years >= required_years,
            "has_preferred_years": total_years >= preferred_years,
            "matched_titles": title_matches,
            "experience_gap_years": max(0, required_years - total_years)
        }

# Example usage
if __name__ == "__main__":
    extractor = ExperienceExtractor()
    
    # Example resume text
    resume_text = """
    EXPERIENCE
    
    Senior Software Engineer, Tech Company Inc., San Francisco, CA
    January 2020 - Present
    
    - Developed and maintained web applications using React and Node.js
    - Implemented RESTful APIs and integrated with PostgreSQL database
    - Deployed applications using Docker and AWS
    - Collaborated with cross-functional teams using Agile methodologies
    
    Software Engineer, Startup Corp., San Jose, CA
    June 2017 - December 2019
    
    - Built frontend components with JavaScript and React
    - Created backend services with Java and Spring Boot
    - Worked with MongoDB for data storage
    - Participated in code reviews and mentored junior developers
    
    Junior Developer, Small Business LLC, Oakland, CA
    January 2016 - May 2017
    
    - Assisted in developing and maintaining company website
    - Fixed bugs and implemented new features
    - Learned and applied best practices in web development
    """
    
    # Extract experience
    experiences = extractor.extract_experience(resume_text)
    
    # Print extracted experiences
    print("Extracted Experiences:")
    for exp in experiences:
        print(f"\n{exp['title']} at {exp['company']}")
        print(f"Duration: {exp['start_date']} to {exp['end_date']} ({exp['duration_months']} months)")
        print(f"Current: {exp['is_current']}")
        if "responsibilities" in exp:
            print("Responsibilities:")
            for resp in exp["responsibilities"]:
                print(f"- {resp}")
    
    # Analyze experience
    analysis = extractor.analyze_experience(experiences)
    
    print("\nExperience Analysis:")
    print(f"Total Experience: {analysis['total_experience_years']} years ({analysis['total_experience_months']} months)")
    print(f"Job Count: {analysis['job_count']}")
    print(f"Average Tenure: {analysis['average_tenure_months']} months")
    print(f"Companies: {', '.join(analysis['companies'])}")
    print(f"Job Titles: {', '.join(analysis['job_titles'])}")
    
    # Match against job requirements
    job_requirements = {
        "min_experience_years": 3,
        "preferred_experience_years": 5,
        "relevant_titles": ["Software Engineer", "Developer", "Programmer"]
    }
    
    match_results = extractor.match_experience_to_job(analysis, job_requirements)
    
    print("\nJob Match Results:")
    print(f"Overall Experience Score: {match_results['overall_experience_score']:.2f}%")
    print(f"Experience Years Score: {match_results['experience_years_score']:.2f}%")
    print(f"Title Match Score: {match_results['title_match_score']:.2f}%")
    print(f"Has Required Years: {match_results['has_required_years']}")
    print(f"Has Preferred Years: {match_results['has_preferred_years']}")
    print(f"Matched Titles: {', '.join(match_results['matched_titles'])}")
    if match_results['experience_gap_years'] > 0:
        print(f"Experience Gap: {match_results['experience_gap_years']} years")
