"""
Resume Scorer for Resume Screening AI Module

This module handles the overall evaluation of resumes against job requirements.
It integrates data from all extractors to provide a comprehensive candidate assessment.
"""

import logging
from typing import Dict, List, Any, Optional
import json
import os
import datetime

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResumeScorer:
    """
    Resume Scorer class for evaluating resumes against job requirements.
    """
    
    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the Resume Scorer.
        
        Args:
            config_path: Path to scoring configuration JSON file (optional)
        """
        # Load scoring configuration
        self.config = self._load_config(config_path)
        
        logger.info("Resume Scorer initialized")
    
    def _load_config(self, config_path: Optional[str] = None) -> Dict[str, Any]:
        """
        Load scoring configuration from file or use default configuration.
        
        Args:
            config_path: Path to configuration JSON file
            
        Returns:
            Dictionary with scoring configuration
        """
        if config_path and os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    config = json.load(f)
                logger.info(f"Loaded scoring configuration from {config_path}")
                return config
            except Exception as e:
                logger.error(f"Error loading configuration: {str(e)}")
        
        # Default configuration if file not provided or loading fails
        return {
            "weights": {
                "skills": 0.35,
                "experience": 0.35,
                "education": 0.20,
                "resume_quality": 0.10
            },
            "thresholds": {
                "excellent": 85,
                "good": 70,
                "average": 50,
                "below_average": 30
            },
            "required_skills_importance": 0.7,  # Weight of required vs preferred skills
            "experience_factors": {
                "years": 0.6,
                "relevance": 0.4
            },
            "education_factors": {
                "degree_level": 0.5,
                "field_relevance": 0.3,
                "institution_quality": 0.2
            },
            "resume_quality_factors": {
                "completeness": 0.4,
                "clarity": 0.3,
                "formatting": 0.3
            }
        }
    
    def evaluate(self, 
                parsed_resume: Dict[str, Any], 
                job_requirements: Dict[str, Any]) -> Dict[str, Any]:
        """
        Evaluate a parsed resume against job requirements.
        
        Args:
            parsed_resume: Dictionary with parsed resume data
            job_requirements: Dictionary with job requirements
            
        Returns:
            Dictionary with evaluation results
        """
        logger.info("Evaluating resume against job requirements")
        
        # Calculate component scores
        skills_score = self._evaluate_skills(parsed_resume.get("skills", []), job_requirements)
        experience_score = self._evaluate_experience(parsed_resume.get("experience", {}), job_requirements)
        education_score = self._evaluate_education(parsed_resume.get("education", []), job_requirements)
        resume_quality_score = self._evaluate_resume_quality(parsed_resume)
        
        # Calculate weighted overall score
        weights = self.config["weights"]
        overall_score = (
            skills_score * weights["skills"] +
            experience_score * weights["experience"] +
            education_score * weights["education"] +
            resume_quality_score * weights["resume_quality"]
        )
        
        # Determine rating based on thresholds
        rating = self._determine_rating(overall_score)
        
        # Generate strengths and weaknesses
        strengths, weaknesses = self._identify_strengths_weaknesses(
            skills_score, experience_score, education_score, resume_quality_score,
            parsed_resume, job_requirements
        )
        
        # Create evaluation result
        evaluation = {
            "overall_score": round(overall_score, 1),
            "rating": rating,
            "component_scores": {
                "skills_score": round(skills_score, 1),
                "experience_score": round(experience_score, 1),
                "education_score": round(education_score, 1),
                "resume_quality_score": round(resume_quality_score, 1)
            },
            "strengths": strengths,
            "weaknesses": weaknesses,
            "details": {
                "skills_evaluation": parsed_resume.get("skills_evaluation", {}),
                "experience_evaluation": parsed_resume.get("experience_evaluation", {}),
                "education_evaluation": parsed_resume.get("education_evaluation", {})
            },
            "job_match": self._calculate_job_match(overall_score, skills_score, experience_score),
            "evaluation_date": datetime.datetime.now().isoformat()
        }
        
        logger.info(f"Resume evaluation complete. Overall score: {evaluation['overall_score']}, Rating: {evaluation['rating']}")
        return evaluation
    
    def _evaluate_skills(self, skills: List[Dict[str, Any]], job_requirements: Dict[str, Any]) -> float:
        """
        Evaluate candidate skills against job requirements.
        
        Args:
            skills: List of candidate skills
            job_requirements: Dictionary with job requirements
            
        Returns:
            Skills score (0-100)
        """
        # If skills evaluation already exists, use it
        if "skills_evaluation" in job_requirements:
            eval_data = job_requirements["skills_evaluation"]
            return eval_data.get("overall_skill_score", 0)
        
        # Extract required and preferred skills from job requirements
        required_skills = job_requirements.get("required_skills", [])
        preferred_skills = job_requirements.get("preferred_skills", [])
        
        if not required_skills and not preferred_skills:
            return 50  # Neutral score if no skill requirements specified
        
        # Extract candidate skill names
        candidate_skill_names = [skill.get("name", "").lower() for skill in skills]
        
        # Count matches
        required_matches = sum(1 for skill in required_skills if skill.lower() in candidate_skill_names)
        preferred_matches = sum(1 for skill in preferred_skills if skill.lower() in candidate_skill_names)
        
        # Calculate match percentages
        required_match_pct = (required_matches / len(required_skills)) * 100 if required_skills else 100
        preferred_match_pct = (preferred_matches / len(preferred_skills)) * 100 if preferred_skills else 100
        
        # Calculate weighted score
        importance = self.config["required_skills_importance"]
        skills_score = (required_match_pct * importance) + (preferred_match_pct * (1 - importance))
        
        return skills_score
    
    def _evaluate_experience(self, experience: Dict[str, Any], job_requirements: Dict[str, Any]) -> float:
        """
        Evaluate candidate experience against job requirements.
        
        Args:
            experience: Dictionary with candidate experience data
            job_requirements: Dictionary with job requirements
            
        Returns:
            Experience score (0-100)
        """
        # If experience evaluation already exists, use it
        if "experience_evaluation" in job_requirements:
            eval_data = job_requirements["experience_evaluation"]
            return eval_data.get("overall_experience_score", 0)
        
        # Extract experience requirements
        required_years = job_requirements.get("min_experience_years", 0)
        preferred_years = job_requirements.get("preferred_experience_years", required_years + 2)
        
        # Extract candidate experience
        total_years = experience.get("total_experience_years", 0)
        
        # Calculate years score
        if total_years >= preferred_years:
            years_score = 100
        elif total_years >= required_years:
            # Scale between 70-99 based on how close to preferred years
            years_score = 70 + (total_years - required_years) / (preferred_years - required_years) * 29
        elif total_years > 0:
            # Scale between 0-69 based on how close to required years
            years_score = (total_years / required_years) * 69 if required_years > 0 else 50
        else:
            years_score = 0
        
        # Calculate relevance score
        relevance_score = 50  # Default if no relevance data
        
        if "experience_evaluation" in experience:
            relevance_score = experience["experience_evaluation"].get("title_match_score", 50)
        
        # Calculate weighted score
        factors = self.config["experience_factors"]
        experience_score = (years_score * factors["years"]) + (relevance_score * factors["relevance"])
        
        return experience_score
    
    def _evaluate_education(self, education: List[Dict[str, Any]], job_requirements: Dict[str, Any]) -> float:
        """
        Evaluate candidate education against job requirements.
        
        Args:
            education: List of candidate education entries
            job_requirements: Dictionary with job requirements
            
        Returns:
            Education score (0-100)
        """
        # If education evaluation already exists, use it
        if "education_evaluation" in job_requirements:
            eval_data = job_requirements["education_evaluation"]
            return eval_data.get("overall_education_score", 0)
        
        # Extract education requirements
        required_level = job_requirements.get("education_level", "").lower()
        required_fields = [field.lower() for field in job_requirements.get("education_fields", [])]
        
        if not required_level and not required_fields:
            return 70  # Default score if no education requirements specified
        
        # Define degree levels and their values
        degree_levels = {
            "high school": 10,
            "associate": 20,
            "associate's": 20,
            "bachelor": 30,
            "bachelor's": 30,
            "undergraduate": 30,
            "master": 40,
            "master's": 40,
            "graduate": 40,
            "mba": 45,
            "phd": 50,
            "doctorate": 50,
            "doctoral": 50
        }
        
        # Find highest degree
        highest_degree = {"level": "none", "field": "", "institution": ""}
        highest_value = 0
        
        for edu in education:
            degree = edu.get("degree", "").lower()
            
            # Determine degree level value
            degree_value = 0
            for level, value in degree_levels.items():
                if level in degree:
                    degree_value = value
                    break
            
            if degree_value > highest_value:
                highest_value = degree_value
                highest_degree = {
                    "level": degree,
                    "field": edu.get("field", ""),
                    "institution": edu.get("institution", "")
                }
        
        # Calculate degree level score
        level_score = 0
        required_value = 0
        
        for level, value in degree_levels.items():
            if level in required_level:
                required_value = value
                break
        
        if highest_value >= required_value:
            level_score = 100
        else:
            level_score = (highest_value / required_value) * 100 if required_value > 0 else 50
        
        # Calculate field relevance score
        field_score = 0
        
        if required_fields:
            candidate_field = highest_degree["field"].lower()
            
            for field in required_fields:
                if field in candidate_field:
                    field_score = 100
                    break
            
            if field_score == 0:
                # Check for related fields
                related_fields = {
                    "computer science": ["software", "information technology", "it", "computing", "computer engineering"],
                    "engineering": ["mechanical", "electrical", "civil", "chemical", "industrial"],
                    "business": ["management", "finance", "accounting", "economics", "marketing"],
                    "data science": ["statistics", "mathematics", "analytics", "machine learning", "ai"]
                }
                
                for req_field in required_fields:
                    if req_field in related_fields:
                        for related in related_fields[req_field]:
                            if related in candidate_field:
                                field_score = 70  # Partial match for related field
                                break
        else:
            field_score = 70  # Default if no specific fields required
        
        # Calculate institution quality score (simplified)
        institution_score = 70  # Default score
        
        # Calculate weighted score
        factors = self.config["education_factors"]
        education_score = (
            level_score * factors["degree_level"] +
            field_score * factors["field_relevance"] +
            institution_score * factors["institution_quality"]
        )
        
        return education_score
    
    def _evaluate_resume_quality(self, parsed_resume: Dict[str, Any]) -> float:
        """
        Evaluate the overall quality of the resume.
        
        Args:
            parsed_resume: Dictionary with parsed resume data
            
        Returns:
            Resume quality score (0-100)
        """
        # Calculate completeness score
        required_sections = ["contact_info", "experience", "education", "skills"]
        present_sections = sum(1 for section in required_sections if section in parsed_resume and parsed_resume[section])
        completeness_score = (present_sections / len(required_sections)) * 100
        
        # Calculate clarity score (based on structure analysis)
        clarity_score = 70  # Default score
        
        if "structure_analysis" in parsed_resume:
            analysis = parsed_resume["structure_analysis"]
            
            # Check for issues
            issues = analysis.get("issues", [])
            if issues:
                clarity_score -= len(issues) * 10
            
            # Check section count
            section_count = analysis.get("metrics", {}).get("section_count", 0)
            if section_count >= 5:
                clarity_score += 10
            
            # Ensure score is within bounds
            clarity_score = max(0, min(100, clarity_score))
        
        # Calculate formatting score
        formatting_score = 70  # Default score
        
        if "document_metadata" in parsed_resume:
            metadata = parsed_resume["document_metadata"]
            
            # Check for formatting indicators
            if metadata.get("has_consistent_formatting", False):
                formatting_score += 10
            
            if metadata.get("has_proper_spacing", False):
                formatting_score += 10
            
            if metadata.get("has_appropriate_margins", False):
                formatting_score += 10
            
            # Ensure score is within bounds
            formatting_score = max(0, min(100, formatting_score))
        
        # Calculate weighted score
        factors = self.config["resume_quality_factors"]
        quality_score = (
            completeness_score * factors["completeness"] +
            clarity_score * factors["clarity"] +
            formatting_score * factors["formatting"]
        )
        
        return quality_score
    
    def _determine_rating(self, score: float) -> str:
        """
        Determine rating based on score and thresholds.
        
        Args:
            score: Overall score
            
        Returns:
            Rating string
        """
        thresholds = self.config["thresholds"]
        
        if score >= thresholds["excellent"]:
            return "Excellent"
        elif score >= thresholds["good"]:
            return "Good"
        elif score >= thresholds["average"]:
            return "Average"
        elif score >= thresholds["below_average"]:
            return "Below Average"
        else:
            return "Poor"
    
    def _identify_strengths_weaknesses(self,
                                     skills_score: float,
                                     experience_score: float,
                                     education_score: float,
                                     resume_quality_score: float,
                                     parsed_resume: Dict[str, Any],
                                     job_requirements: Dict[str, Any]) -> Tuple[List[str], List[str]]:
        """
        Identify candidate strengths and weaknesses.
        
        Args:
            skills_score: Skills evaluation score
            experience_score: Experience evaluation score
            education_score: Education evaluation score
            resume_quality_score: Resume quality score
            parsed_resume: Dictionary with parsed resume data
            job_requirements: Dictionary with job requirements
            
        Returns:
            Tuple of (strengths list, weaknesses list)
        """
        strengths = []
        weaknesses = []
        
        # Analyze skills
        if skills_score >= 85:
            strengths.append("Strong match on required technical skills")
        elif skills_score >= 70:
            strengths.append("Good match on technical skills")
        elif skills_score < 50:
            weaknesses.append("Missing several required technical skills")
        
        # Check for specific skill matches/gaps
        if "skills_evaluation" in parsed_resume:
            skill_eval = parsed_resume["skills_evaluation"]
            
            if skill_eval.get("has_all_required", False):
                strengths.append("Has all required skills for the position")
            
            missing = skill_eval.get("missing_required", [])
            if missing and len(missing) <= 2:
                weaknesses.append(f"Missing key skills: {', '.join(missing)}")
            
            preferred = skill_eval.get("matched_preferred", [])
            if preferred and len(preferred) >= 3:
                strengths.append("Possesses multiple preferred skills")
        
        # Analyze experience
        required_years = job_requirements.get("min_experience_years", 0)
        preferred_years = job_requirements.get("preferred_experience_years", required_years + 2)
        
        total_years = parsed_resume.get("experience", {}).get("total_experience_years", 0)
        
        if total_years >= preferred_years:
            strengths.append(f"Exceeds desired experience level with {total_years} years")
        elif total_years >= required_years:
            strengths.append(f"Meets required experience level with {total_years} years")
        elif total_years < required_years:
            gap = required_years - total_years
            weaknesses.append(f"Experience gap of {gap} years below requirement")
        
        # Analyze education
        if education_score >= 85:
            strengths.append("Education credentials exceed requirements")
        elif education_score >= 70:
            strengths.append("Education credentials meet requirements")
        elif education_score < 50:
            weaknesses.append("Education credentials below position requirements")
        
        # Analyze resume quality
        if resume_quality_score < 60:
            weaknesses.append("Resume could benefit from improved formatting and structure")
        
        return strengths, weaknesses
    
    def _calculate_job_match(self, overall_score: float, skills_score: float, experience_score: float) -> Dict[str, Any]:
        """
        Calculate overall job match metrics.
        
        Args:
            overall_score: Overall evaluation score
            skills_score: Skills evaluation score
            experience_score: Experience evaluation score
            
        Returns:
            Dictionary with job match metrics
        """
        # Calculate match percentage
        match_percentage = overall_score
        
        # Determine fit category
        if match_percentage >= 85:
            fit_category = "Excellent Fit"
            recommendation = "Strongly Recommend for Interview"
        elif match_percentage >= 70:
            fit_category = "Good Fit"
            recommendation = "Recommend for Interview"
        elif match_percentage >= 60:
            fit_category = "Potential Fit"
            recommendation = "Consider for Interview"
        elif match_percentage >= 50:
            fit_category = "Partial Fit"
            recommendation = "Consider if Applicant Pool is Limited"
        else:
            fit_category = "Poor Fit"
            recommendation = "Do Not Recommend"
        
        # Calculate technical match (based on skills)
        technical_match = skills_score
        
        # Calculate experience match
        experience_match = experience_score
        
        return {
            "match_percentage": round(match_percentage, 1),
            "fit_category": fit_category,
            "recommendation": recommendation,
            "technical_match": round(technical_match, 1),
            "experience_match": round(experience_match, 1)
        }

# Example usage
if __name__ == "__main__":
    scorer = ResumeScorer()
    
    # Example parsed resume
    parsed_resume = {
        "contact_info": {
            "name": "John Doe",
            "email": "john.doe@example.com",
            "phone": "555-123-4567",
            "location": "San Francisco, CA"
        },
        "skills": [
            {"name": "Python", "category": "programming_languages", "confidence": 0.95},
            {"name": "JavaScript", "category": "programming_languages", "confidence": 0.9},
            {"name": "React", "category": "web_development", "confidence": 0.85},
            {"name": "Node.js", "category": "web_development", "confidence": 0.8},
            {"name": "PostgreSQL", "category": "databases", "confidence": 0.85},
            {"name": "MongoDB", "category": "databases", "confidence": 0.75},
            {"name": "Docker", "category": "devops", "confidence": 0.7},
            {"name": "AWS", "category": "cloud_platforms", "confidence": 0.65}
        ],
        "skills_evaluation": {
            "overall_skill_score": 85.5,
            "required_match_score": 90.0,
            "preferred_match_score": 75.0,
            "matched_required": ["Python", "JavaScript", "React", "PostgreSQL"],
            "missing_required": ["TypeScript"],
            "matched_preferred": ["Node.js", "Docker", "AWS"],
            "has_all_required": False
        },
        "experience": {
            "total_experience_years": 4.5,
            "total_experience_months": 54,
            "job_count": 2,
            "average_tenure_months": 27,
            "companies": ["Tech Company Inc.", "Startup Corp."],
            "job_titles": ["Senior Software Engineer", "Software Engineer"]
        },
        "experience_evaluation": {
            "overall_experience_score": 78.5,
            "experience_years_score": 85.0,
            "title_match_score": 70.0,
            "has_required_years": True,
            "has_preferred_years": False,
            "matched_titles": ["Software Engineer"],
            "experience_gap_years": 0
        },
        "education": [
            {
                "degree": "Bachelor of Science",
                "field": "Computer Science",
                "institution": "University of California, Berkeley",
                "graduation_date": "2016-05-15",
                "gpa": "3.7"
            }
        ],
        "education_evaluation": {
            "overall_education_score": 90.0,
            "level_match_score": 100.0,
            "field_match_score": 100.0,
            "institution_score": 80.0
        },
        "structure_analysis": {
            "metrics": {
                "word_count": 850,
                "line_count": 75,
                "section_count": 6
            },
            "issues": []
        },
        "document_metadata": {
            "has_consistent_formatting": True,
            "has_proper_spacing": True,
            "has_appropriate_margins": True
        }
    }
    
    # Example job requirements
    job_requirements = {
        "title": "Senior Software Engineer",
        "required_skills": ["Python", "JavaScript", "React", "PostgreSQL", "TypeScript"],
        "preferred_skills": ["Node.js", "Docker", "AWS", "Kubernetes", "GraphQL"],
        "min_experience_years": 3,
        "preferred_experience_years": 5,
        "education_level": "Bachelor's",
        "education_fields": ["Computer Science", "Software Engineering"]
    }
    
    # Evaluate resume
    evaluation = scorer.evaluate(parsed_resume, job_requirements)
    
    # Print evaluation results
    print(f"Overall Score: {evaluation['overall_score']}%")
    print(f"Rating: {evaluation['rating']}")
    print("\nComponent Scores:")
    for component, score in evaluation['component_scores'].items():
        print(f"- {component}: {score}%")
    
    print("\nStrengths:")
    for strength in evaluation['strengths']:
        print(f"- {strength}")
    
    print("\nWeaknesses:")
    for weakness in evaluation['weaknesses']:
        print(f"- {weakness}")
    
    print("\nJob Match:")
    print(f"Match Percentage: {evaluation['job_match']['match_percentage']}%")
    print(f"Fit Category: {evaluation['job_match']['fit_category']}")
    print(f"Recommendation: {evaluation['job_match']['recommendation']}")
    print(f"Technical Match: {evaluation['job_match']['technical_match']}%")
    print(f"Experience Match: {evaluation['job_match']['experience_match']}%")
