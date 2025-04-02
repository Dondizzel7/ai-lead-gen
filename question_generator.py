"""
Question Generation Engine for AI Candidate Evaluation Framework

This module creates tailored interview questions based on job requirements,
candidate profile, and assessment goals. It ensures a balanced mix of
technical, behavioral, and situational questions.
"""

import random
import logging
import os
import json
from typing import Dict, List, Any, Optional
import spacy
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class QuestionBank:
    """Repository of interview questions organized by categories, skills, and traits."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the question bank.
        
        Args:
            data_path: Path to question bank data files
        """
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), 'data')
        self.questions = {
            'technical': [],
            'behavioral': [],
            'situational': []
        }
        
        # Load questions from data files
        self._load_questions()
        
        # Create indexes for efficient retrieval
        self._create_indexes()
        
        logger.info(f"Question bank initialized with {len(self.questions['technical'])} technical, "
                   f"{len(self.questions['behavioral'])} behavioral, and "
                   f"{len(self.questions['situational'])} situational questions")
    
    def _load_questions(self):
        """Load questions from data files."""
        try:
            # In a real implementation, this would load from actual data files
            # For this example, we'll use mock data
            
            # Technical questions
            self.questions['technical'] = [
                {
                    'id': f'tech_{i}',
                    'text': f'Technical question {i}',
                    'difficulty': random.choice(['easy', 'medium', 'hard']),
                    'skills': random.sample(['Python', 'JavaScript', 'SQL', 'React', 'AWS', 'Docker', 
                                           'Machine Learning', 'Data Analysis', 'DevOps', 'Networking'], 
                                          random.randint(1, 3)),
                    'expected_concepts': [f'concept_{j}' for j in range(random.randint(3, 6))],
                    'follow_ups': [f'Follow-up {j}' for j in range(random.randint(1, 3))]
                }
                for i in range(1, 101)  # 100 technical questions
            ]
            
            # Behavioral questions
            self.questions['behavioral'] = [
                {
                    'id': f'behav_{i}',
                    'text': f'Behavioral question {i}',
                    'traits': random.sample(['leadership', 'teamwork', 'communication', 'problem-solving',
                                           'adaptability', 'initiative', 'integrity', 'customer-focus'], 
                                          random.randint(1, 3)),
                    'evaluation_criteria': [f'criteria_{j}' for j in range(random.randint(2, 4))]
                }
                for i in range(1, 51)  # 50 behavioral questions
            ]
            
            # Situational questions
            self.questions['situational'] = [
                {
                    'id': f'sit_{i}',
                    'text': f'Situational question {i}',
                    'roles': random.sample(['Software Engineer', 'Data Scientist', 'Product Manager',
                                          'DevOps Engineer', 'UX Designer', 'Project Manager'], 
                                         random.randint(1, 2)),
                    'industries': random.sample(['Technology', 'Finance', 'Healthcare', 'E-commerce',
                                               'Manufacturing', 'Education'], 
                                              random.randint(1, 2)),
                    'scenarios': [f'scenario_{j}' for j in range(random.randint(1, 3))],
                    'evaluation_criteria': [f'criteria_{j}' for j in range(random.randint(2, 4))]
                }
                for i in range(1, 31)  # 30 situational questions
            ]
            
        except Exception as e:
            logger.error(f"Error loading questions: {str(e)}")
            # Initialize with empty lists if loading fails
            for category in self.questions:
                if not self.questions[category]:
                    self.questions[category] = []
    
    def _create_indexes(self):
        """Create indexes for efficient question retrieval."""
        # Technical question indexes
        self.tech_by_skill = defaultdict(list)
        self.tech_by_difficulty = defaultdict(list)
        
        for q in self.questions['technical']:
            for skill in q.get('skills', []):
                self.tech_by_skill[skill.lower()].append(q)
            
            difficulty = q.get('difficulty', 'medium')
            self.tech_by_difficulty[difficulty].append(q)
        
        # Behavioral question indexes
        self.behav_by_trait = defaultdict(list)
        
        for q in self.questions['behavioral']:
            for trait in q.get('traits', []):
                self.behav_by_trait[trait.lower()].append(q)
        
        # Situational question indexes
        self.sit_by_role = defaultdict(list)
        self.sit_by_industry = defaultdict(list)
        
        for q in self.questions['situational']:
            for role in q.get('roles', []):
                self.sit_by_role[role.lower()].append(q)
            
            for industry in q.get('industries', []):
                self.sit_by_industry[industry.lower()].append(q)
    
    def get_questions(self, category: str, count: int = 5, **filters) -> List[Dict[str, Any]]:
        """
        Get questions from the bank based on category and filters.
        
        Args:
            category: Question category ('technical', 'behavioral', or 'situational')
            count: Number of questions to return
            **filters: Additional filters (skill, trait, role, industry, difficulty)
            
        Returns:
            List of matching questions
        """
        if category not in self.questions:
            logger.warning(f"Invalid category: {category}")
            return []
        
        # Apply filters
        filtered_questions = self._apply_filters(category, filters)
        
        # If no questions match filters, return random questions from the category
        if not filtered_questions and self.questions[category]:
            logger.info(f"No questions match filters, returning random {category} questions")
            filtered_questions = self.questions[category]
        
        # Randomly select questions up to the requested count
        if len(filtered_questions) <= count:
            return filtered_questions
        else:
            return random.sample(filtered_questions, count)
    
    def _apply_filters(self, category: str, filters: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Apply filters to questions in a category."""
        filtered_questions = []
        
        if category == 'technical':
            # Filter by skill
            if 'skill' in filters:
                skill = filters['skill'].lower()
                filtered_questions = self.tech_by_skill.get(skill, [])
            
            # Filter by difficulty
            elif 'difficulty' in filters:
                difficulty = filters['difficulty'].lower()
                filtered_questions = self.tech_by_difficulty.get(difficulty, [])
            
            # No specific filters
            else:
                filtered_questions = self.questions['technical']
        
        elif category == 'behavioral':
            # Filter by trait
            if 'trait' in filters:
                trait = filters['trait'].lower()
                filtered_questions = self.behav_by_trait.get(trait, [])
            
            # No specific filters
            else:
                filtered_questions = self.questions['behavioral']
        
        elif category == 'situational':
            # Filter by role
            if 'role' in filters:
                role = filters['role'].lower()
                filtered_questions = self.sit_by_role.get(role, [])
            
            # Filter by industry
            elif 'industry' in filters:
                industry = filters['industry'].lower()
                filtered_questions = self.sit_by_industry.get(industry, [])
            
            # No specific filters
            else:
                filtered_questions = self.questions['situational']
        
        return filtered_questions


class QuestionGenerator:
    """Generates tailored interview questions based on job requirements and candidate profile."""
    
    def __init__(self, job_requirements: Dict[str, Any], candidate_profile: Dict[str, Any], question_bank: Optional[QuestionBank] = None):
        """
        Initialize the question generator.
        
        Args:
            job_requirements: Job requirements data
            candidate_profile: Candidate profile data
            question_bank: Question bank instance
        """
        self.job_requirements = job_requirements
        self.candidate_profile = candidate_profile
        self.question_bank = question_bank or QuestionBank()
        
        try:
            # Load spaCy model for text processing
            self.nlp = spacy.load("en_core_web_sm")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {str(e)}. Some functionality may be limited.")
            self.nlp = None
        
        logger.info("Question generator initialized")
    
    def generate_interview_plan(self, duration_minutes: int = 60) -> Dict[str, Any]:
        """
        Generate a complete interview plan based on job requirements and candidate profile.
        
        Args:
            duration_minutes: Total interview duration in minutes
            
        Returns:
            Interview plan with questions and timing
        """
        # Determine question counts based on interview duration
        total_questions = max(5, duration_minutes // 10)  # Roughly 10 minutes per question including discussion
        
        # Allocate questions by type
        technical_count = total_questions // 2  # 50% technical
        behavioral_count = total_questions // 4  # 25% behavioral
        situational_count = total_questions - technical_count - behavioral_count  # Remaining 25%
        
        # Generate questions by type
        technical_questions = self.generate_technical_questions(count=technical_count)
        behavioral_questions = self.generate_behavioral_questions(count=behavioral_count)
        situational_questions = self.generate_situational_questions(count=situational_count)
        
        # Calculate timing
        question_time = duration_minutes // total_questions
        
        # Create interview plan
        interview_plan = {
            'job_id': self.job_requirements.get('id', 'unknown'),
            'candidate_id': self.candidate_profile.get('id', 'unknown'),
            'duration_minutes': duration_minutes,
            'sections': [
                {
                    'name': 'Introduction',
                    'duration_minutes': 5,
                    'description': 'Welcome the candidate and explain the interview process'
                },
                {
                    'name': 'Technical Assessment',
                    'duration_minutes': technical_count * question_time,
                    'questions': technical_questions
                },
                {
                    'name': 'Behavioral Assessment',
                    'duration_minutes': behavioral_count * question_time,
                    'questions': behavioral_questions
                },
                {
                    'name': 'Situational Assessment',
                    'duration_minutes': situational_count * question_time,
                    'questions': situational_questions
                },
                {
                    'name': 'Candidate Questions',
                    'duration_minutes': 10,
                    'description': 'Allow the candidate to ask questions about the role and company'
                },
                {
                    'name': 'Conclusion',
                    'duration_minutes': 5,
                    'description': 'Thank the candidate and explain next steps'
                }
            ],
            'total_questions': len(technical_questions) + len(behavioral_questions) + len(situational_questions)
        }
        
        return interview_plan
    
    def generate_technical_questions(self, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate technical questions based on job requirements and candidate skills.
        
        Args:
            count: Number of questions to generate
            
        Returns:
            List of technical questions
        """
        required_skills = self.job_requirements.get("required_skills", [])
        candidate_skills = self.candidate_profile.get("skills", [])
        
        # Find skills to focus on (required but not strong in candidate)
        focus_skills = []
        for skill in required_skills:
            # Find candidate's proficiency in this skill
            candidate_skill = next((s for s in candidate_skills if isinstance(s, dict) and 
                                  s.get("name", "").lower() == skill.lower()), None)
            
            # If candidate doesn't have the skill or has low proficiency, focus on it
            if not candidate_skill or candidate_skill.get("level", 0) < 4:
                focus_skills.append(skill)
        
        # If no focus skills found, use all required skills
        if not focus_skills:
            focus_skills = required_skills
        
        # Select questions from bank based on focus skills
        questions = []
        for skill in focus_skills:
            skill_questions = self.question_bank.get_questions(
                category="technical",
                skill=skill,
                difficulty=self._determine_difficulty(skill),
                count=2  # Get up to 2 questions per skill
            )
            
            if skill_questions:
                questions.extend(skill_questions)
        
        # If we need more questions, add general technical questions
        if len(questions) < count:
            general_questions = self.question_bank.get_questions(
                category="technical",
                count=count - len(questions)
            )
            questions.extend(general_questions)
        
        # Ensure no duplicate questions
        unique_questions = []
        question_ids = set()
        
        for q in questions:
            if q['id'] not in question_ids:
                unique_questions.append(q)
                question_ids.add(q['id'])
                
                # Stop when we have enough questions
                if len(unique_questions) >= count:
                    break
        
        return unique_questions[:count]  # Return requested number of questions
    
    def generate_behavioral_questions(self, count: int = 3) -> List[Dict[str, Any]]:
        """
        Generate behavioral questions based on job requirements.
        
        Args:
            count: Number of questions to generate
            
        Returns:
            List of behavioral questions
        """
        job_traits = self.job_requirements.get("desired_traits", [])
        
        # If no traits specified, use default important traits
        if not job_traits:
            job_traits = ["teamwork", "communication", "problem-solving", "adaptability"]
        
        # Select questions based on desired traits
        questions = []
        for trait in job_traits:
            trait_questions = self.question_bank.get_questions(
                category="behavioral",
                trait=trait,
                count=1  # Get 1 question per trait
            )
            
            if trait_questions:
                questions.extend(trait_questions)
        
        # If we need more questions, add general behavioral questions
        if len(questions) < count:
            general_questions = self.question_bank.get_questions(
                category="behavioral",
                count=count - len(questions)
            )
            questions.extend(general_questions)
        
        # Ensure no duplicate questions
        unique_questions = []
        question_ids = set()
        
        for q in questions:
            if q['id'] not in question_ids:
                unique_questions.append(q)
                question_ids.add(q['id'])
                
                # Stop when we have enough questions
                if len(unique_questions) >= count:
                    break
        
        return unique_questions[:count]
    
    def generate_situational_questions(self, count: int = 2) -> List[Dict[str, Any]]:
        """
        Generate situational questions relevant to the role.
        
        Args:
            count: Number of questions to generate
            
        Returns:
            List of situational questions
        """
        role = self.job_requirements.get("title", "")
        industry = self.job_requirements.get("industry", "")
        
        # Get role-specific questions
        role_questions = []
        if role:
            role_questions = self.question_bank.get_questions(
                category="situational",
                role=role,
                count=count
            )
        
        # Get industry-specific questions
        industry_questions = []
        if industry and len(role_questions) < count:
            industry_questions = self.question_bank.get_questions(
                category="situational",
                industry=industry,
                count=count - len(role_questions)
            )
        
        # Combine questions
        questions = role_questions + industry_questions
        
        # If we still need more questions, add general situational questions
        if len(questions) < count:
            general_questions = self.question_bank.get_questions(
                category="situational",
                count=count - len(questions)
            )
            questions.extend(general_questions)
        
        # Ensure no duplicate questions
        unique_questions = []
        question_ids = set()
        
        for q in questions:
            if q['id'] not in question_ids:
                unique_questions.append(q)
                question_ids.add(q['id'])
                
                # Stop when we have enough questions
                if len(unique_questions) >= count:
                    break
        
        return unique_questions[:count]
    
    def _determine_difficulty(self, skill: str) -> str:
        """
        Determine appropriate difficulty level for questions about a skill.
        
        Args:
            skill: Skill name
            
        Returns:
            Difficulty level ('easy', 'medium', or 'hard')
        """
        # Find candidate's proficiency in this skill
        candidate_skill = next((s for s in self.candidate_profile.get("skills", []) 
                               if isinstance(s, dict) and s.get("name", "").lower() == skill.lower()), None)
        
        if not candidate_skill:
            return "medium"  # Default to medium if skill not found
        
        skill_level = candidate_skill.get("level", 0)
        
        if skill_level >= 4:  # Expert level
            return "hard"
        elif skill_level >= 2:  # Intermediate level
            return "medium"
        else:  # Beginner level
            return "easy"
    
    def customize_question(self, question: Dict[str, Any]) -> Dict[str, Any]:
        """
        Customize a question for the specific candidate and job.
        
        Args:
            question: Base question
            
        Returns:
            Customized question
        """
        # Create a copy to avoid modifying the original
        customized = question.copy()
        
        # Add candidate-specific context if available
        if self.nlp and 'text' in customized:
            # Get candidate's company and role
            current_company = self.candidate_profile.get("current_company", "")
            current_role = self.candidate_profile.get("current_role", "")
            
            # Get job title and company
            job_title = self.job_requirements.get("title", "")
            company = self.job_requirements.get("company", "")
            
            # Customize question text
            text = customized['text']
            
            # Replace placeholders if they exist
            if "{role}" in text and job_title:
                text = text.replace("{role}", job_title)
            
            if "{company}" in text and company:
                text = text.replace("{company}", company)
            
            if "{candidate_role}" in text and current_role:
                text = text.replace("{candidate_role}", current_role)
            
            if "{candidate_company}" in text and current_company:
                text = text.replace("{candidate_company}", current_company)
            
            customized['text'] = text
        
        return customized


# Example usage
if __name__ == "__main__":
    # Example job requirements
    job_requirements = {
        "id": "job_12345",
        "title": "Senior Software Engineer",
        "company": "TechCorp",
        "industry": "Technology",
        "required_skills": ["Python", "JavaScript", "SQL", "AWS", "Docker"],
        "preferred_skills": ["React", "TypeScript", "Kubernetes"],
        "desired_traits": ["teamwork", "communication", "problem-solving", "leadership"]
    }
    
    # Example candidate profile
    candidate_profile = {
        "id": "cand_67890",
        "name": "Jane Smith",
        "current_role": "Software Engineer",
        "current_company": "CodeCo",
        "skills": [
            {"name": "Python", "level": 4},
            {"name": "JavaScript", "level": 3},
            {"name": "SQL", "level": 3},
            {"name": "React", "level": 2},
            {"name": "Docker", "level": 1}
        ]
    }
    
    # Initialize question bank
    question_bank = QuestionBank()
    
    # Initialize question generator
    generator = QuestionGenerator(job_requirements, candidate_profile, question_bank)
    
    # Generate interview plan
    interview_plan = generator.generate_interview_plan(duration_minutes=60)
    
    # Print interview plan
    print("Interview Plan:")
    print(f"Job: {interview_plan['job_id']}")
    print(f"Candidate: {interview_plan['candidate_id']}")
    print(f"Duration: {interview_plan['duration_minutes']} minutes")
    print(f"Total Questions: {interview_plan['total_questions']}")
    
    print("\nSections:")
    for section in interview_plan['sections']:
        print(f"\n{section['name']} ({section['duration_minutes']} minutes)")
        
        if 'description' in section:
            print(f"Description: {section['description']}")
        
        if 'questions' in section:
            print(f"Questions ({len(section['questions'])}):")
            for i, q in enumerate(section['questions']):
                print(f"{i+1}. {q['text']}")
                if 'difficulty' in q:
                    print(f"   Difficulty: {q['difficulty']}")
                if 'skills' in q:
                    print(f"   Skills: {', '.join(q['skills'])}")
                if 'traits' in q:
                    print(f"   Traits: {', '.join(q['traits'])}")
