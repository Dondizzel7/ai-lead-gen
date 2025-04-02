"""
Skills Extractor for Resume Screening AI Module

This module handles the extraction and normalization of skills from resume text.
It includes skill identification, categorization, and confidence scoring.
"""

import logging
import re
import json
import os
from typing import Dict, List, Any, Optional, Set, Tuple
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SkillsExtractor:
    """
    Skills Extractor class for identifying and normalizing skills from resume text.
    """
    
    def __init__(self, skill_taxonomy_path: Optional[str] = None):
        """
        Initialize the Skills Extractor.
        
        Args:
            skill_taxonomy_path: Path to skill taxonomy JSON file (optional)
        """
        # Load skill taxonomy
        self.skill_taxonomy = self._load_skill_taxonomy(skill_taxonomy_path)
        
        # Create skill name to category mapping
        self.skill_to_category = {}
        for category, skills in self.skill_taxonomy.items():
            for skill in skills:
                self.skill_to_category[skill.lower()] = category
        
        # Create skill aliases mapping
        self.skill_aliases = self._create_skill_aliases()
        
        # Compile regex patterns for skill detection
        self.skill_patterns = self._compile_skill_patterns()
        
        logger.info("Skills Extractor initialized with %d skills in %d categories", 
                   len(self.skill_to_category), len(self.skill_taxonomy))
    
    def _load_skill_taxonomy(self, taxonomy_path: Optional[str] = None) -> Dict[str, List[str]]:
        """
        Load skill taxonomy from file or use default taxonomy.
        
        Args:
            taxonomy_path: Path to skill taxonomy JSON file
            
        Returns:
            Dictionary mapping skill categories to lists of skills
        """
        if taxonomy_path and os.path.exists(taxonomy_path):
            try:
                with open(taxonomy_path, 'r') as f:
                    taxonomy = json.load(f)
                logger.info(f"Loaded skill taxonomy from {taxonomy_path}")
                return taxonomy
            except Exception as e:
                logger.error(f"Error loading skill taxonomy: {str(e)}")
        
        # Default taxonomy if file not provided or loading fails
        return {
            "programming_languages": [
                "Python", "Java", "JavaScript", "TypeScript", "C++", "C#", "Ruby", "Go", "Rust",
                "PHP", "Swift", "Kotlin", "Scala", "R", "MATLAB", "Perl", "Haskell", "Clojure",
                "Groovy", "Objective-C", "Assembly", "Shell", "PowerShell", "Bash", "SQL", "PL/SQL"
            ],
            "web_development": [
                "HTML", "CSS", "React", "Angular", "Vue.js", "Node.js", "Express", "Django",
                "Flask", "Ruby on Rails", "ASP.NET", "Spring Boot", "Laravel", "jQuery",
                "Bootstrap", "Tailwind CSS", "Redux", "GraphQL", "REST API", "SOAP",
                "WebSockets", "PWA", "SPA", "SSR", "JAMstack", "MERN", "MEAN", "LAMP"
            ],
            "databases": [
                "MySQL", "PostgreSQL", "MongoDB", "SQLite", "Oracle", "SQL Server", "Redis",
                "Cassandra", "DynamoDB", "Elasticsearch", "Firebase", "Neo4j", "MariaDB",
                "CouchDB", "Firestore", "InfluxDB", "Snowflake", "BigQuery", "Redshift"
            ],
            "devops": [
                "Docker", "Kubernetes", "AWS", "Azure", "GCP", "Jenkins", "GitLab CI",
                "GitHub Actions", "CircleCI", "Travis CI", "Terraform", "Ansible", "Puppet",
                "Chef", "Prometheus", "Grafana", "ELK Stack", "Nginx", "Apache", "Serverless",
                "Microservices", "CI/CD", "Infrastructure as Code", "Containerization"
            ],
            "data_science": [
                "Machine Learning", "Deep Learning", "NLP", "Computer Vision", "Data Mining",
                "Data Analysis", "Data Visualization", "Statistical Analysis", "Big Data",
                "Pandas", "NumPy", "SciPy", "scikit-learn", "TensorFlow", "PyTorch", "Keras",
                "NLTK", "spaCy", "Hadoop", "Spark", "Tableau", "Power BI", "Matplotlib",
                "Seaborn", "Jupyter", "A/B Testing", "Regression", "Classification", "Clustering"
            ],
            "cloud_platforms": [
                "AWS", "Azure", "Google Cloud", "IBM Cloud", "Oracle Cloud", "DigitalOcean",
                "Heroku", "Netlify", "Vercel", "AWS Lambda", "Azure Functions", "Cloud Run",
                "EC2", "S3", "RDS", "DynamoDB", "CloudFront", "Route 53", "IAM", "VPC",
                "ECS", "EKS", "App Engine", "Cloud Functions", "Cloud Storage", "Cloud SQL"
            ],
            "mobile_development": [
                "Android", "iOS", "React Native", "Flutter", "Xamarin", "Ionic", "Swift",
                "Kotlin", "Objective-C", "Java", "Mobile UI/UX", "ARKit", "CoreML",
                "Firebase", "Push Notifications", "App Store", "Google Play", "Mobile Testing",
                "Responsive Design", "Progressive Web Apps", "Mobile Analytics"
            ],
            "project_management": [
                "Agile", "Scrum", "Kanban", "Waterfall", "JIRA", "Confluence", "Trello",
                "Asana", "Monday.com", "MS Project", "Product Management", "Sprint Planning",
                "Backlog Grooming", "Retrospectives", "User Stories", "Requirements Gathering",
                "Stakeholder Management", "Risk Management", "Resource Planning", "Roadmapping"
            ],
            "soft_skills": [
                "Communication", "Teamwork", "Problem Solving", "Critical Thinking",
                "Time Management", "Leadership", "Adaptability", "Creativity", "Collaboration",
                "Emotional Intelligence", "Conflict Resolution", "Decision Making",
                "Presentation Skills", "Negotiation", "Customer Service", "Mentoring"
            ],
            "design": [
                "UI Design", "UX Design", "Graphic Design", "Web Design", "Responsive Design",
                "Adobe Photoshop", "Adobe Illustrator", "Adobe XD", "Sketch", "Figma",
                "InVision", "Wireframing", "Prototyping", "User Research", "Usability Testing",
                "Information Architecture", "Visual Design", "Interaction Design", "Typography"
            ]
        }
    
    def _create_skill_aliases(self) -> Dict[str, str]:
        """
        Create mapping of skill aliases to canonical skill names.
        
        Returns:
            Dictionary mapping aliases to canonical names
        """
        aliases = {
            # Programming Languages
            "js": "javascript",
            "ts": "typescript",
            "py": "python",
            "golang": "go",
            "c sharp": "c#",
            "c plus plus": "c++",
            "objective c": "objective-c",
            
            # Web Development
            "reactjs": "react",
            "react.js": "react",
            "vuejs": "vue.js",
            "nodejs": "node.js",
            "node": "node.js",
            "expressjs": "express",
            "angularjs": "angular",
            "angular.js": "angular",
            "rails": "ruby on rails",
            "asp.net core": "asp.net",
            "asp.net mvc": "asp.net",
            "tailwind": "tailwind css",
            "restful api": "rest api",
            "restful": "rest api",
            "graphql api": "graphql",
            
            # Databases
            "postgres": "postgresql",
            "mongo": "mongodb",
            "mssql": "sql server",
            "ms sql": "sql server",
            "elastic search": "elasticsearch",
            "maria db": "mariadb",
            "couch db": "couchdb",
            "influx db": "influxdb",
            "dynamo db": "dynamodb",
            "big query": "bigquery",
            
            # DevOps
            "k8s": "kubernetes",
            "amazon web services": "aws",
            "microsoft azure": "azure",
            "google cloud platform": "gcp",
            "gitlab cicd": "gitlab ci",
            "github workflow": "github actions",
            "circle ci": "circleci",
            "travis": "travis ci",
            "elk": "elk stack",
            "ci cd": "ci/cd",
            "continuous integration": "ci/cd",
            "continuous deployment": "ci/cd",
            "iac": "infrastructure as code",
            
            # Data Science
            "ml": "machine learning",
            "dl": "deep learning",
            "natural language processing": "nlp",
            "cv": "computer vision",
            "sci-kit learn": "scikit-learn",
            "sklearn": "scikit-learn",
            "tensorflow": "tensorflow",
            "tf": "tensorflow",
            "pytorch": "pytorch",
            "powerbi": "power bi",
            "ab testing": "a/b testing",
            
            # Cloud Platforms
            "amazon aws": "aws",
            "microsoft azure": "azure",
            "gcp": "google cloud",
            "digital ocean": "digitalocean",
            "lambda": "aws lambda",
            "s3 bucket": "s3",
            "ec2 instance": "ec2",
            "route53": "route 53",
            
            # Mobile Development
            "reactnative": "react native",
            "android development": "android",
            "ios development": "ios",
            "mobile ui": "mobile ui/ux",
            "mobile ux": "mobile ui/ux",
            "push notification": "push notifications",
            "pwa": "progressive web apps",
            
            # Project Management
            "agile methodology": "agile",
            "scrum methodology": "scrum",
            "kanban methodology": "kanban",
            "waterfall methodology": "waterfall",
            "atlassian jira": "jira",
            "atlassian confluence": "confluence",
            "microsoft project": "ms project",
            "sprint planning meetings": "sprint planning",
            "backlog refinement": "backlog grooming",
            "sprint retrospective": "retrospectives",
            
            # Soft Skills
            "verbal communication": "communication",
            "written communication": "communication",
            "team work": "teamwork",
            "problem-solving": "problem solving",
            "time-management": "time management",
            "team leadership": "leadership",
            "emotional-intelligence": "emotional intelligence",
            "conflict-resolution": "conflict resolution",
            "decision-making": "decision making",
            
            # Design
            "user interface design": "ui design",
            "user experience design": "ux design",
            "photoshop": "adobe photoshop",
            "illustrator": "adobe illustrator",
            "xd": "adobe xd",
            "wire framing": "wireframing",
            "user testing": "usability testing"
        }
        
        return aliases
    
    def _compile_skill_patterns(self) -> Dict[str, re.Pattern]:
        """
        Compile regex patterns for skill detection.
        
        Returns:
            Dictionary mapping skill names to compiled regex patterns
        """
        patterns = {}
        
        # Create patterns for all skills in taxonomy
        for category, skills in self.skill_taxonomy.items():
            for skill in skills:
                # Create pattern that matches the skill as a whole word
                # Case insensitive and handles word boundaries
                pattern_str = r'\b' + re.escape(skill) + r'\b'
                patterns[skill.lower()] = re.compile(pattern_str, re.IGNORECASE)
        
        return patterns
    
    def extract_skills(self, text: str, min_confidence: float = 0.5) -> List[Dict[str, Any]]:
        """
        Extract skills from resume text.
        
        Args:
            text: Resume text
            min_confidence: Minimum confidence threshold (0.0 to 1.0)
            
        Returns:
            List of extracted skills with metadata
        """
        logger.info("Extracting skills from text")
        
        # Extract skills section if present
        sections = self._extract_sections(text)
        skills_section = sections.get("skills", "")
        
        # Find skills using regex patterns
        found_skills = []
        
        # First check the skills section with higher confidence
        if skills_section:
            section_skills = self._find_skills_in_text(skills_section, base_confidence=0.8)
            found_skills.extend(section_skills)
        
        # Then check the entire text
        all_skills = self._find_skills_in_text(text, base_confidence=0.6)
        
        # Merge skills, keeping the highest confidence version
        skill_dict = {}
        for skill in found_skills + all_skills:
            skill_name = skill["name"].lower()
            if skill_name not in skill_dict or skill["confidence"] > skill_dict[skill_name]["confidence"]:
                skill_dict[skill_name] = skill
        
        # Filter by minimum confidence
        filtered_skills = [skill for skill in skill_dict.values() if skill["confidence"] >= min_confidence]
        
        # Sort by confidence (descending)
        sorted_skills = sorted(filtered_skills, key=lambda x: x["confidence"], reverse=True)
        
        logger.info(f"Extracted {len(sorted_skills)} skills with confidence >= {min_confidence}")
        return sorted_skills
    
    def _find_skills_in_text(self, text: str, base_confidence: float = 0.6) -> List[Dict[str, Any]]:
        """
        Find skills in text using regex patterns.
        
        Args:
            text: Text to search for skills
            base_confidence: Base confidence level for matches
            
        Returns:
            List of found skills with metadata
        """
        found_skills = []
        
        # Check for each skill pattern
        for skill_name, pattern in self.skill_patterns.items():
            matches = pattern.findall(text)
            
            if matches:
                # Calculate confidence based on number of matches and context
                confidence = base_confidence
                
                # Increase confidence for multiple mentions
                if len(matches) > 1:
                    confidence = min(confidence + 0.1 * len(matches), 0.95)
                
                # Get canonical skill name and category
                canonical_name = self._get_canonical_skill_name(skill_name)
                category = self.skill_to_category.get(canonical_name.lower(), "other")
                
                # Add to found skills
                found_skills.append({
                    "name": canonical_name,
                    "category": category,
                    "confidence": confidence,
                    "mentions": len(matches),
                    "raw_matches": matches
                })
        
        return found_skills
    
    def _get_canonical_skill_name(self, skill_name: str) -> str:
        """
        Get canonical name for a skill, handling aliases.
        
        Args:
            skill_name: Skill name or alias
            
        Returns:
            Canonical skill name
        """
        skill_lower = skill_name.lower()
        
        # Check if it's an alias
        if skill_lower in self.skill_aliases:
            canonical_lower = self.skill_aliases[skill_lower]
        else:
            canonical_lower = skill_lower
        
        # Find the original case from the taxonomy
        for category, skills in self.skill_taxonomy.items():
            for skill in skills:
                if skill.lower() == canonical_lower:
                    return skill
        
        # If not found in taxonomy, use the original with first letter capitalized
        return skill_name.capitalize()
    
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
    
    def categorize_skills(self, skills: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """
        Categorize skills by their categories.
        
        Args:
            skills: List of extracted skills
            
        Returns:
            Dictionary mapping categories to lists of skills
        """
        categorized = defaultdict(list)
        
        for skill in skills:
            category = skill["category"]
            categorized[category].append(skill)
        
        return dict(categorized)
    
    def match_skills_to_job(self, 
                           extracted_skills: List[Dict[str, Any]], 
                           required_skills: List[str],
                           preferred_skills: List[str]) -> Dict[str, Any]:
        """
        Match extracted skills against job requirements.
        
        Args:
            extracted_skills: List of extracted skills
            required_skills: List of required skills for the job
            preferred_skills: List of preferred skills for the job
            
        Returns:
            Dictionary with match results
        """
        # Normalize all skills
        extracted_skill_names = [skill["name"].lower() for skill in extracted_skills]
        required_skills_norm = [skill.lower() for skill in required_skills]
        preferred_skills_norm = [skill.lower() for skill in preferred_skills]
        
        # Find matches
        matched_required = []
        missing_required = []
        matched_preferred = []
        
        # Check required skills
        for skill in required_skills_norm:
            canonical = self._get_canonical_skill_name(skill).lower()
            if canonical in extracted_skill_names:
                matched_required.append(canonical)
            else:
                # Check aliases
                found = False
                for alias, canonical_name in self.skill_aliases.items():
                    if alias == skill and canonical_name in extracted_skill_names:
                        matched_required.append(canonical_name)
                        found = True
                        break
                
                if not found:
                    missing_required.append(skill)
        
        # Check preferred skills
        for skill in preferred_skills_norm:
            canonical = self._get_canonical_skill_name(skill).lower()
            if canonical in extracted_skill_names and canonical not in matched_required:
                matched_preferred.append(canonical)
            else:
                # Check aliases
                for alias, canonical_name in self.skill_aliases.items():
                    if alias == skill and canonical_name in extracted_skill_names and canonical_name not in matched_required:
                        matched_preferred.append(canonical_name)
                        break
        
        # Calculate match scores
        required_match_score = (len(matched_required) / len(required_skills_norm)) * 100 if required_skills_norm else 100
        preferred_match_score = (len(matched_preferred) / len(preferred_skills_norm)) * 100 if preferred_skills_norm else 100
        
        # Calculate overall skill match score (70% required, 30% preferred)
        overall_skill_score = (required_match_score * 0.7) + (preferred_match_score * 0.3)
        
        return {
            "overall_skill_score": overall_skill_score,
            "required_match_score": required_match_score,
            "preferred_match_score": preferred_match_score,
            "matched_required": matched_required,
            "missing_required": missing_required,
            "matched_preferred": matched_preferred,
            "has_all_required": len(missing_required) == 0
        }

# Example usage
if __name__ == "__main__":
    extractor = SkillsExtractor()
    
    # Example resume text
    resume_text = """
    SKILLS
    
    Programming Languages: Python, JavaScript, Java, SQL
    Web Development: React, Node.js, HTML, CSS
    Databases: PostgreSQL, MongoDB
    DevOps: Docker, AWS, CI/CD
    Tools: Git, JIRA, VS Code
    
    EXPERIENCE
    
    Senior Software Engineer
    Tech Company Inc., San Francisco, CA
    January 2020 - Present
    
    - Developed and maintained web applications using React and Node.js
    - Implemented RESTful APIs and integrated with PostgreSQL database
    - Deployed applications using Docker and AWS
    - Collaborated with cross-functional teams using Agile methodologies
    
    Software Engineer
    Startup Corp., San Jose, CA
    June 2017 - December 2019
    
    - Built frontend components with JavaScript and React
    - Created backend services with Java and Spring Boot
    - Worked with MongoDB for data storage
    - Participated in code reviews and mentored junior developers
    """
    
    # Extract skills
    skills = extractor.extract_skills(resume_text)
    
    # Print extracted skills
    print("Extracted Skills:")
    for skill in skills:
        print(f"- {skill['name']} ({skill['category']}): {skill['confidence']:.2f}")
    
    # Categorize skills
    categorized = extractor.categorize_skills(skills)
    
    print("\nSkills by Category:")
    for category, category_skills in categorized.items():
        print(f"\n{category.upper()}:")
        for skill in category_skills:
            print(f"- {skill['name']}: {skill['confidence']:.2f}")
    
    # Match against job requirements
    job_required = ["Python", "React", "SQL", "AWS"]
    job_preferred = ["Docker", "MongoDB", "Node.js", "CI/CD"]
    
    match_results = extractor.match_skills_to_job(skills, job_required, job_preferred)
    
    print("\nJob Match Results:")
    print(f"Overall Skill Score: {match_results['overall_skill_score']:.2f}%")
    print(f"Required Skills Match: {match_results['required_match_score']:.2f}%")
    print(f"Preferred Skills Match: {match_results['preferred_match_score']:.2f}%")
    print(f"Has All Required Skills: {match_results['has_all_required']}")
    
    print("\nMatched Required Skills:")
    for skill in match_results['matched_required']:
        print(f"- {skill}")
    
    print("\nMissing Required Skills:")
    for skill in match_results['missing_required']:
        print(f"- {skill}")
    
    print("\nMatched Preferred Skills:")
    for skill in match_results['matched_preferred']:
        print(f"- {skill}")
