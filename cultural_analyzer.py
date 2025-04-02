"""
Cultural Fit Analyzer for AI Candidate Evaluation Framework

This module assesses candidate alignment with company culture and values
through analysis of interview responses, communication style, and behavioral patterns.
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional
import numpy as np
from collections import defaultdict

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class CultureValueRepository:
    """Repository of company culture values and associated traits."""
    
    def __init__(self, data_path: Optional[str] = None):
        """
        Initialize the culture value repository.
        
        Args:
            data_path: Path to culture values data files
        """
        self.data_path = data_path or os.path.join(os.path.dirname(__file__), 'data')
        self.culture_values = {}
        
        # Load culture values from data files
        self._load_culture_values()
        
        logger.info(f"Culture value repository initialized with {len(self.culture_values)} values")
    
    def _load_culture_values(self):
        """Load culture values from data files."""
        try:
            # In a real implementation, this would load from actual data files
            # For this example, we'll use mock data
            
            self.culture_values = {
                "innovation": {
                    "description": "We value creative thinking and novel approaches to solving problems.",
                    "traits": ["creativity", "curiosity", "risk-taking", "adaptability", "forward-thinking"],
                    "indicators": {
                        "positive": [
                            "experimentation", "new ideas", "creative solutions", "challenging status quo",
                            "continuous improvement", "learning from failure", "thinking outside the box"
                        ],
                        "negative": [
                            "rigid thinking", "resistance to change", "fear of failure", "excessive caution",
                            "following rules blindly", "lack of imagination"
                        ]
                    },
                    "questions": [
                        "Describe a time when you came up with a novel solution to a problem.",
                        "How do you approach situations where established methods aren't working?",
                        "Tell me about a time you took a calculated risk that didn't work out. What did you learn?"
                    ]
                },
                "collaboration": {
                    "description": "We believe in working together across teams to achieve common goals.",
                    "traits": ["teamwork", "communication", "empathy", "conflict resolution", "inclusivity"],
                    "indicators": {
                        "positive": [
                            "team success", "helping others", "sharing credit", "active listening",
                            "constructive feedback", "cross-functional work", "inclusive language"
                        ],
                        "negative": [
                            "individual focus", "taking sole credit", "poor listening", "exclusionary behavior",
                            "unwillingness to compromise", "siloed thinking"
                        ]
                    },
                    "questions": [
                        "Describe a successful team project and your role in it.",
                        "How do you handle disagreements with team members?",
                        "Tell me about a time you helped a colleague who was struggling."
                    ]
                },
                "customer_focus": {
                    "description": "We prioritize understanding and meeting customer needs above all else.",
                    "traits": ["empathy", "service orientation", "problem-solving", "adaptability", "communication"],
                    "indicators": {
                        "positive": [
                            "customer perspective", "user experience", "customer feedback", "service excellence",
                            "going above and beyond", "understanding user needs"
                        ],
                        "negative": [
                            "internal focus", "ignoring feedback", "technical solutions without user context",
                            "impatience with customers", "prioritizing features over usability"
                        ]
                    },
                    "questions": [
                        "Describe a time when you went above and beyond for a customer or user.",
                        "How do you incorporate user feedback into your work?",
                        "Tell me about a challenging customer situation and how you resolved it."
                    ]
                },
                "integrity": {
                    "description": "We act with honesty, transparency, and ethical behavior in all situations.",
                    "traits": ["honesty", "accountability", "consistency", "transparency", "ethical decision-making"],
                    "indicators": {
                        "positive": [
                            "admitting mistakes", "taking responsibility", "ethical considerations", "transparency",
                            "keeping commitments", "consistent behavior", "standing up for what's right"
                        ],
                        "negative": [
                            "blame shifting", "hiding information", "inconsistent standards", "cutting corners",
                            "ethical compromises", "lack of accountability"
                        ]
                    },
                    "questions": [
                        "Tell me about a time when you had to make a difficult ethical decision.",
                        "Describe a situation where you made a mistake. How did you handle it?",
                        "How have you handled situations where you were asked to compromise your values?"
                    ]
                },
                "excellence": {
                    "description": "We strive for the highest standards of quality and continuous improvement.",
                    "traits": ["attention to detail", "high standards", "continuous learning", "perseverance", "self-motivation"],
                    "indicators": {
                        "positive": [
                            "quality focus", "continuous improvement", "learning from mistakes", "thoroughness",
                            "professional development", "exceeding expectations", "attention to detail"
                        ],
                        "negative": [
                            "cutting corners", "minimum effort", "resistance to feedback", "complacency",
                            "lack of attention to detail", "settling for mediocrity"
                        ]
                    },
                    "questions": [
                        "How do you ensure the quality of your work?",
                        "Describe a time when you weren't satisfied with your performance. What did you do?",
                        "How do you approach professional development and continuous learning?"
                    ]
                }
            }
            
        except Exception as e:
            logger.error(f"Error loading culture values: {str(e)}")
            self.culture_values = {}
    
    def get_all_values(self) -> Dict[str, Dict[str, Any]]:
        """
        Get all culture values.
        
        Returns:
            Dictionary of all culture values
        """
        return self.culture_values
    
    def get_value(self, value_id: str) -> Optional[Dict[str, Any]]:
        """
        Get a specific culture value.
        
        Args:
            value_id: Culture value identifier
            
        Returns:
            Culture value data or None if not found
        """
        return self.culture_values.get(value_id)
    
    def get_all_traits(self) -> List[str]:
        """
        Get all traits across all culture values.
        
        Returns:
            List of all traits
        """
        all_traits = set()
        for value in self.culture_values.values():
            all_traits.update(value.get("traits", []))
        
        return list(all_traits)
    
    def get_all_indicators(self) -> Dict[str, List[str]]:
        """
        Get all indicators across all culture values.
        
        Returns:
            Dictionary of positive and negative indicators
        """
        all_indicators = {
            "positive": [],
            "negative": []
        }
        
        for value in self.culture_values.values():
            indicators = value.get("indicators", {})
            all_indicators["positive"].extend(indicators.get("positive", []))
            all_indicators["negative"].extend(indicators.get("negative", []))
        
        return all_indicators
    
    def get_questions_for_value(self, value_id: str) -> List[str]:
        """
        Get interview questions for a specific culture value.
        
        Args:
            value_id: Culture value identifier
            
        Returns:
            List of questions
        """
        value = self.culture_values.get(value_id, {})
        return value.get("questions", [])


class CulturalFitAnalyzer:
    """Analyzes candidate cultural fit based on interview responses and behavior."""
    
    def __init__(self, culture_repo: Optional[CultureValueRepository] = None):
        """
        Initialize the cultural fit analyzer.
        
        Args:
            culture_repo: Repository of company culture values
        """
        self.culture_repo = culture_repo or CultureValueRepository()
        
        # Load all culture values
        self.culture_values = self.culture_repo.get_all_values()
        
        # Load all traits and indicators
        self.all_traits = self.culture_repo.get_all_traits()
        self.all_indicators = self.culture_repo.get_all_indicators()
        
        logger.info(f"Cultural fit analyzer initialized with {len(self.culture_values)} culture values")
    
    def analyze_cultural_fit(self, candidate_data: Dict[str, Any], company_values: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze candidate's cultural fit based on interview data.
        
        Args:
            candidate_data: Candidate interview data
            company_values: List of company culture value IDs to focus on
            
        Returns:
            Cultural fit analysis
        """
        logger.info(f"Analyzing cultural fit for candidate {candidate_data.get('candidate_id', 'unknown')}")
        
        # If no specific company values provided, use all values
        if not company_values:
            company_values = list(self.culture_values.keys())
        
        # Filter to only include valid values
        company_values = [v for v in company_values if v in self.culture_values]
        
        if not company_values:
            logger.warning("No valid company values provided for analysis")
            return {
                "candidate_id": candidate_data.get("candidate_id", "unknown"),
                "overall_fit": 0.5,  # Neutral score
                "value_alignment": {},
                "strengths": [],
                "gaps": [],
                "recommendations": ["Unable to analyze cultural fit without valid company values"]
            }
        
        # Extract interview responses
        responses = candidate_data.get("responses", {})
        
        # Analyze fit for each company value
        value_alignment = {}
        for value_id in company_values:
            value_data = self.culture_values.get(value_id, {})
            value_alignment[value_id] = self._analyze_value_alignment(
                value_id, value_data, responses
            )
        
        # Calculate overall fit score
        overall_fit = sum(v["score"] for v in value_alignment.values()) / len(value_alignment)
        
        # Identify strengths and gaps
        strengths, gaps = self._identify_strengths_gaps(value_alignment)
        
        # Generate recommendations
        recommendations = self._generate_recommendations(value_alignment, gaps)
        
        return {
            "candidate_id": candidate_data.get("candidate_id", "unknown"),
            "overall_fit": overall_fit,
            "value_alignment": value_alignment,
            "strengths": strengths,
            "gaps": gaps,
            "recommendations": recommendations
        }
    
    def generate_cultural_questions(self, company_values: Optional[List[str]] = None, count: int = 5) -> List[Dict[str, Any]]:
        """
        Generate culture-focused interview questions.
        
        Args:
            company_values: List of company culture value IDs to focus on
            count: Number of questions to generate
            
        Returns:
            List of culture-focused questions
        """
        # If no specific company values provided, use all values
        if not company_values:
            company_values = list(self.culture_values.keys())
        
        # Filter to only include valid values
        company_values = [v for v in company_values if v in self.culture_values]
        
        if not company_values:
            logger.warning("No valid company values provided for question generation")
            return []
        
        # Collect questions for each value
        all_questions = []
        for value_id in company_values:
            value_data = self.culture_values.get(value_id, {})
            questions = value_data.get("questions", [])
            
            for question in questions:
                all_questions.append({
                    "text": question,
                    "value_id": value_id,
                    "value_name": value_id.replace("_", " ").title(),
                    "traits": value_data.get("traits", [])
                })
        
        # If we need more questions than available, duplicate some
        if len(all_questions) < count:
            import random
            while len(all_questions) < count:
                all_questions.append(random.choice(all_questions).copy())
        
        # Shuffle and select requested number
        import random
        random.shuffle(all_questions)
        
        return all_questions[:count]
    
    def _analyze_value_alignment(self, value_id: str, value_data: Dict[str, Any], responses: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze alignment with a specific culture value.
        
        Args:
            value_id: Culture value identifier
            value_data: Culture value data
            responses: Candidate responses
            
        Returns:
            Value alignment analysis
        """
        # Extract traits and indicators for this value
        traits = value_data.get("traits", [])
        indicators = value_data.get("indicators", {})
        positive_indicators = indicators.get("positive", [])
        negative_indicators = indicators.get("negative", [])
        
        # Analyze all responses for evidence of traits and indicators
        trait_evidence = defaultdict(list)
        positive_evidence = []
        negative_evidence = []
        
        for question_id, response_data in responses.items():
            question = response_data.get("question", "")
            response = response_data.get("response", "")
            
            # Skip if no response
            if not response:
                continue
            
            # Check for traits
            for trait in traits:
                if self._check_for_trait(trait, response):
                    trait_evidence[trait].append({
                        "question_id": question_id,
                        "question": question,
                        "excerpt": self._extract_relevant_excerpt(response, trait)
                    })
            
            # Check for positive indicators
            for indicator in positive_indicators:
                if self._check_for_indicator(indicator, response):
                    positive_evidence.append({
                        "indicator": indicator,
                        "question_id": question_id,
                        "question": question,
                        "excerpt": self._extract_relevant_excerpt(response, indicator)
                    })
            
            # Check for negative indicators
            for indicator in negative_indicators:
                if self._check_for_indicator(indicator, response):
                    negative_evidence.append({
                        "indicator": indicator,
                        "question_id": question_id,
                        "question": question,
                        "excerpt": self._extract_relevant_excerpt(response, indicator)
                    })
        
        # Calculate trait coverage
        trait_coverage = len([t for t in traits if t in trait_evidence]) / len(traits) if traits else 0
        
        # Calculate evidence ratio
        total_evidence = len(positive_evidence) + len(negative_evidence)
        evidence_ratio = len(positive_evidence) / max(1, total_evidence)
        
        # Calculate overall score for this value
        if total_evidence == 0:
            # No clear evidence either way
            score = 0.5
        else:
            # Weight evidence ratio more heavily when there's more evidence
            evidence_weight = min(1.0, total_evidence / 5)  # Cap at 5 pieces of evidence
            trait_weight = 1.0 - evidence_weight
            
            score = (evidence_ratio * evidence_weight) + (trait_coverage * trait_weight)
        
        return {
            "value_id": value_id,
            "value_name": value_id.replace("_", " ").title(),
            "description": value_data.get("description", ""),
            "score": score,
            "trait_coverage": trait_coverage,
            "trait_evidence": dict(trait_evidence),
            "positive_evidence": positive_evidence,
            "negative_evidence": negative_evidence
        }
    
    def _check_for_trait(self, trait: str, text: str) -> bool:
        """
        Check if text contains evidence of a trait.
        
        Args:
            trait: Trait to check for
            text: Text to analyze
            
        Returns:
            True if trait evidence found
        """
        # In a real implementation, this would use NLP techniques
        # For this example, we'll use simple keyword matching
        
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        trait_lower = trait.lower()
        
        # Direct mention of the trait
        if trait_lower in text_lower:
            return True
        
        # Check for trait synonyms
        trait_synonyms = self._get_trait_synonyms(trait)
        for synonym in trait_synonyms:
            if synonym.lower() in text_lower:
                return True
        
        return False
    
    def _check_for_indicator(self, indicator: str, text: str) -> bool:
        """
        Check if text contains an indicator phrase.
        
        Args:
            indicator: Indicator phrase to check for
            text: Text to analyze
            
        Returns:
            True if indicator found
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        indicator_lower = indicator.lower()
        
        # Check for exact phrase
        if indicator_lower in text_lower:
            return True
        
        # Check for variations (would use more sophisticated NLP in real implementation)
        words = indicator_lower.split()
        if len(words) > 1:
            # Check if most words appear close together
            word_positions = []
            for word in words:
                if word in text_lower:
                    word_positions.append(text_lower.find(word))
            
            if len(word_positions) >= len(words) * 0.7:  # At least 70% of words found
                # Check if words appear within reasonable proximity
                word_positions.sort()
                if word_positions[-1] - word_positions[0] < 100:  # Within 100 characters
                    return True
        
        return False
    
    def _extract_relevant_excerpt(self, text: str, keyword: str) -> str:
        """
        Extract a relevant excerpt from text containing the keyword.
        
        Args:
            text: Source text
            keyword: Keyword to find
            
        Returns:
            Relevant excerpt
        """
        # Convert to lowercase for case-insensitive matching
        text_lower = text.lower()
        keyword_lower = keyword.lower()
        
        # Find position of keyword
        pos = text_lower.find(keyword_lower)
        if pos == -1:
            # Try finding individual words
            words = keyword_lower.split()
            for word in words:
                pos = text_lower.find(word)
                if pos != -1:
                    break
        
        if pos == -1:
            # Keyword not found, return first 100 characters
            return text[:100] + "..."
        
        # Extract context around keyword (50 chars before, 100 after)
        start = max(0, pos - 50)
        end = min(len(text), pos + len(keyword) + 100)
        
        excerpt = text[start:end]
        
        # Add ellipsis if excerpt doesn't start/end at text boundaries
        if start > 0:
            excerpt = "..." + excerpt
        if end < len(text):
            excerpt = excerpt + "..."
        
        return excerpt
    
    def _get_trait_synonyms(self, trait: str) -> List[str]:
        """
        Get synonyms for a trait.
        
        Args:
            trait: Trait name
            
        Returns:
            List of synonyms
        """
        # In a real implementation, this would use a thesaurus API or WordNet
        # For this example, we'll use a simple mapping
        
        synonyms = {
            "creativity": ["innovative", "inventive", "original", "imaginative", "creative thinking"],
            "curiosity": ["inquisitive", "questioning", "exploring", "investigative", "eager to learn"],
            "risk-taking": ["bold", "daring", "adventurous", "courageous", "willing to try"],
            "adaptability": ["flexible", "versatile", "adjustable", "resilient", "open to change"],
            "teamwork": ["collaboration", "cooperative", "team player", "working together", "collective effort"],
            "communication": ["articulate", "expressive", "clear", "effective communicator", "good listener"],
            "empathy": ["understanding", "compassionate", "considerate", "sensitive", "perspective-taking"],
            "honesty": ["truthful", "sincere", "authentic", "straightforward", "integrity"],
            "accountability": ["responsible", "answerable", "ownership", "reliable", "dependable"],
            "attention to detail": ["meticulous", "thorough", "precise", "careful", "detail-oriented"]
        }
        
        return synonyms.get(trait.lower(), [])
    
    def _identify_strengths_gaps(self, value_alignment: Dict[str, Dict[str, Any]]) -> tuple:
        """
        Identify cultural strengths and gaps.
        
        Args:
            value_alignment: Value alignment analysis
            
        Returns:
            Tuple of (strengths, gaps)
        """
        strengths = []
        gaps = []
        
        for value_id, alignment in value_alignment.items():
            value_name = alignment["value_name"]
            score = alignment["score"]
            
            if score >= 0.8:
                # Strong alignment
                strengths.append({
                    "value_id": value_id,
                    "value_name": value_name,
                    "score": score,
                    "evidence": self._summarize_evidence(alignment["positive_evidence"])
                })
            elif score <= 0.4:
                # Weak alignment
                gaps.append({
                    "value_id": value_id,
                    "value_name": value_name,
                    "score": score,
                    "evidence": self._summarize_evidence(alignment["negative_evidence"])
                })
        
        return strengths, gaps
    
    def _summarize_evidence(self, evidence_list: List[Dict[str, Any]]) -> str:
        """
        Summarize evidence into a concise statement.
        
        Args:
            evidence_list: List of evidence items
            
        Returns:
            Summarized evidence
        """
        if not evidence_list:
            return "No specific evidence found."
        
        # Group by indicator
        indicators = defaultdict(int)
        for item in evidence_list:
            indicators[item["indicator"]] += 1
        
        # Get top 3 indicators
        top_indicators = sorted(indicators.items(), key=lambda x: x[1], reverse=True)[:3]
        
        if top_indicators:
            summary = "Evidence includes "
            indicator_phrases = []
            
            for indicator, count in top_indicators:
                if count > 1:
                    indicator_phrases.append(f"multiple instances of {indicator}")
                else:
                    indicator_phrases.append(indicator)
            
            summary += ", ".join(indicator_phrases)
            return summary
        
        return "Limited specific evidence found."
    
    def _generate_recommendations(self, value_alignment: Dict[str, Dict[str, Any]], gaps: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on cultural fit analysis.
        
        Args:
            value_alignment: Value alignment analysis
            gaps: Identified cultural gaps
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Overall recommendation based on fit
        overall_score = sum(v["score"] for v in value_alignment.values()) / len(value_alignment)
        
        if overall_score >= 0.8:
            recommendations.append("Strong cultural fit. Candidate aligns well with company values.")
        elif overall_score >= 0.6:
            recommendations.append("Good cultural fit with some areas for discussion.")
        elif overall_score >= 0.4:
            recommendations.append("Moderate cultural fit. Further assessment recommended.")
        else:
            recommendations.append("Potential cultural fit concerns. In-depth discussion of values recommended.")
        
        # Specific recommendations for gaps
        for gap in gaps:
            value_id = gap["value_id"]
            value_name = gap["value_name"]
            
            # Get questions for this value
            questions = self.culture_repo.get_questions_for_value(value_id)
            
            if questions:
                # Suggest a follow-up question
                import random
                question = random.choice(questions)
                recommendations.append(f"Explore {value_name} alignment with follow-up question: '{question}'")
        
        # Add general recommendations if few specific ones
        if len(recommendations) < 3:
            if overall_score < 0.7:
                recommendations.append("Consider team dynamics when evaluating cultural fit.")
            
            if any(v["score"] < 0.5 for v in value_alignment.values()):
                recommendations.append("Discuss company values explicitly in follow-up interview.")
        
        return recommendations


class BehavioralPatternAnalyzer:
    """Analyzes behavioral patterns from interview interactions."""
    
    def __init__(self):
        """Initialize the behavioral pattern analyzer."""
        logger.info("Behavioral pattern analyzer initialized")
    
    def analyze_behavior(self, interaction_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze behavioral patterns from interview interactions.
        
        Args:
            interaction_data: Interview interaction data
            
        Returns:
            Behavioral analysis
        """
        logger.info(f"Analyzing behavioral patterns for candidate {interaction_data.get('candidate_id', 'unknown')}")
        
        # Extract interaction metrics
        communication_metrics = self._analyze_communication(interaction_data)
        engagement_metrics = self._analyze_engagement(interaction_data)
        interpersonal_metrics = self._analyze_interpersonal(interaction_data)
        
        # Calculate overall behavioral score
        overall_score = (
            communication_metrics["overall"] * 0.4 +
            engagement_metrics["overall"] * 0.3 +
            interpersonal_metrics["overall"] * 0.3
        )
        
        # Identify behavioral traits
        behavioral_traits = self._identify_behavioral_traits(
            communication_metrics, engagement_metrics, interpersonal_metrics
        )
        
        # Generate insights
        insights = self._generate_behavioral_insights(
            communication_metrics, engagement_metrics, interpersonal_metrics, behavioral_traits
        )
        
        return {
            "candidate_id": interaction_data.get("candidate_id", "unknown"),
            "overall_score": overall_score,
            "communication_metrics": communication_metrics,
            "engagement_metrics": engagement_metrics,
            "interpersonal_metrics": interpersonal_metrics,
            "behavioral_traits": behavioral_traits,
            "insights": insights
        }
    
    def _analyze_communication(self, interaction_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze communication patterns.
        
        Args:
            interaction_data: Interview interaction data
            
        Returns:
            Communication metrics
        """
        # Extract communication data
        responses = interaction_data.get("responses", {})
        
        # In a real implementation, this would analyze actual communication patterns
        # For this example, we'll use mock metrics
        
        # Calculate average response length
        response_lengths = [len(r.get("response", "")) for r in responses.values()]
        avg_length = sum(response_lengths) / max(1, len(response_lengths))
        
        # Normalize to 0-1 scale (assuming ideal length is 200-500 characters)
        length_score = 0.5
        if avg_length < 50:
            length_score = 0.2  # Too brief
        elif avg_length < 200:
            length_score = 0.4 + (avg_length - 50) / 375  # Scaling up to 0.8
        elif avg_length <= 500:
            length_score = 0.8 + (avg_length - 200) / 1500  # Scaling up to 0.9
        elif avg_length <= 1000:
            length_score = 0.9  # Good length
        else:
            length_score = 0.9 - (avg_length - 1000) / 10000  # Scaling down for excessive length
        
        # Clarity score (would use NLP in real implementation)
        clarity_score = 0.7  # Default
        
        # Articulation score
        articulation_score = 0.75  # Default
        
        # Overall communication score
        overall = (length_score * 0.3) + (clarity_score * 0.4) + (articulation_score * 0.3)
        
        return {
            "length_score": length_score,
            "clarity_score": clarity_score,
            "articulation_score": articulation_score,
            "overall": overall
        }
    
    def _analyze_engagement(self, interaction_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze engagement patterns.
        
        Args:
            interaction_data: Interview interaction data
            
        Returns:
            Engagement metrics
        """
        # Extract engagement data
        responses = interaction_data.get("responses", {})
        
        # In a real implementation, this would analyze actual engagement patterns
        # For this example, we'll use mock metrics
        
        # Response time metrics
        response_times = interaction_data.get("response_times", [])
        if response_times:
            avg_response_time = sum(response_times) / len(response_times)
            
            # Normalize to 0-1 scale (assuming ideal time is 10-30 seconds)
            time_score = 0.5
            if avg_response_time < 5:
                time_score = 0.3  # Too quick, possibly rehearsed
            elif avg_response_time < 10:
                time_score = 0.5 + (avg_response_time - 5) / 10  # Scaling up
            elif avg_response_time <= 30:
                time_score = 0.8  # Good response time
            elif avg_response_time <= 60:
                time_score = 0.8 - (avg_response_time - 30) / 60  # Scaling down
            else:
                time_score = 0.4  # Too slow
        else:
            time_score = 0.5  # Default
        
        # Enthusiasm score
        enthusiasm_score = 0.7  # Default
        
        # Attentiveness score
        attentiveness_score = 0.8  # Default
        
        # Overall engagement score
        overall = (time_score * 0.3) + (enthusiasm_score * 0.4) + (attentiveness_score * 0.3)
        
        return {
            "response_time_score": time_score,
            "enthusiasm_score": enthusiasm_score,
            "attentiveness_score": attentiveness_score,
            "overall": overall
        }
    
    def _analyze_interpersonal(self, interaction_data: Dict[str, Any]) -> Dict[str, float]:
        """
        Analyze interpersonal interaction patterns.
        
        Args:
            interaction_data: Interview interaction data
            
        Returns:
            Interpersonal metrics
        """
        # In a real implementation, this would analyze actual interpersonal patterns
        # For this example, we'll use mock metrics
        
        # Rapport score
        rapport_score = 0.75  # Default
        
        # Empathy score
        empathy_score = 0.7  # Default
        
        # Adaptability score
        adaptability_score = 0.8  # Default
        
        # Overall interpersonal score
        overall = (rapport_score * 0.4) + (empathy_score * 0.3) + (adaptability_score * 0.3)
        
        return {
            "rapport_score": rapport_score,
            "empathy_score": empathy_score,
            "adaptability_score": adaptability_score,
            "overall": overall
        }
    
    def _identify_behavioral_traits(self, communication: Dict[str, float], engagement: Dict[str, float], interpersonal: Dict[str, float]) -> Dict[str, float]:
        """
        Identify behavioral traits from metrics.
        
        Args:
            communication: Communication metrics
            engagement: Engagement metrics
            interpersonal: Interpersonal metrics
            
        Returns:
            Behavioral traits with confidence scores
        """
        traits = {}
        
        # Communication-related traits
        if communication["clarity_score"] > 0.7 and communication["articulation_score"] > 0.7:
            traits["effective_communicator"] = (communication["clarity_score"] + communication["articulation_score"]) / 2
        
        if communication["length_score"] > 0.8:
            traits["thorough"] = communication["length_score"]
        elif communication["length_score"] < 0.4:
            traits["concise"] = 1 - communication["length_score"]
        
        # Engagement-related traits
        if engagement["enthusiasm_score"] > 0.7:
            traits["enthusiastic"] = engagement["enthusiasm_score"]
        
        if engagement["attentiveness_score"] > 0.7:
            traits["attentive"] = engagement["attentiveness_score"]
        
        if engagement["response_time_score"] > 0.7:
            traits["thoughtful"] = engagement["response_time_score"]
        elif engagement["response_time_score"] < 0.4:
            traits["quick_thinker"] = 1 - engagement["response_time_score"]
        
        # Interpersonal traits
        if interpersonal["rapport_score"] > 0.7:
            traits["personable"] = interpersonal["rapport_score"]
        
        if interpersonal["empathy_score"] > 0.7:
            traits["empathetic"] = interpersonal["empathy_score"]
        
        if interpersonal["adaptability_score"] > 0.7:
            traits["adaptable"] = interpersonal["adaptability_score"]
        
        # Combined traits
        if communication["overall"] > 0.7 and engagement["overall"] > 0.7:
            traits["confident"] = (communication["overall"] + engagement["overall"]) / 2
        
        if interpersonal["overall"] > 0.7 and engagement["enthusiasm_score"] > 0.7:
            traits["positive"] = (interpersonal["overall"] + engagement["enthusiasm_score"]) / 2
        
        return traits
    
    def _generate_behavioral_insights(self, communication: Dict[str, float], engagement: Dict[str, float], interpersonal: Dict[str, float], traits: Dict[str, float]) -> List[str]:
        """
        Generate insights based on behavioral analysis.
        
        Args:
            communication: Communication metrics
            engagement: Engagement metrics
            interpersonal: Interpersonal metrics
            traits: Behavioral traits
            
        Returns:
            List of insights
        """
        insights = []
        
        # Communication insights
        if communication["overall"] > 0.8:
            insights.append("Demonstrates excellent communication skills with clarity and articulation.")
        elif communication["overall"] > 0.6:
            insights.append("Shows good communication ability.")
        elif communication["overall"] < 0.5:
            insights.append("May benefit from improving communication clarity and structure.")
        
        # Engagement insights
        if engagement["overall"] > 0.8:
            insights.append("Highly engaged throughout the interview process.")
        elif engagement["enthusiasm_score"] < 0.5:
            insights.append("Could demonstrate more enthusiasm for the role and company.")
        
        # Interpersonal insights
        if interpersonal["overall"] > 0.8:
            insights.append("Excellent interpersonal skills suggest strong team fit.")
        elif interpersonal["rapport_score"] < 0.5:
            insights.append("May need to focus on building rapport in professional relationships.")
        
        # Trait-based insights
        top_traits = sorted(traits.items(), key=lambda x: x[1], reverse=True)[:3]
        if top_traits:
            trait_names = [t[0].replace("_", " ") for t in top_traits]
            insights.append(f"Key behavioral traits: {', '.join(trait_names)}.")
        
        # Team fit insight
        if interpersonal["overall"] > 0.7 and "adaptable" in traits and "empathetic" in traits:
            insights.append("Behavioral patterns suggest strong team collaboration potential.")
        
        return insights


# Example usage
if __name__ == "__main__":
    # Initialize culture repository
    culture_repo = CultureValueRepository()
    
    # Initialize cultural fit analyzer
    cultural_analyzer = CulturalFitAnalyzer(culture_repo)
    
    # Example candidate data
    candidate_data = {
        "candidate_id": "candidate_12345",
        "responses": {
            "q1": {
                "question": "Describe a time when you came up with a novel solution to a problem.",
                "response": "In my previous role, we were struggling with slow database queries that were affecting user experience. Instead of just optimizing the existing queries, I proposed a complete redesign of our data access layer using a caching strategy. I researched various caching solutions and implemented a Redis-based approach that reduced query times by 90%. This required thinking outside the box since the conventional approach would have been to just add indexes or optimize SQL."
            },
            "q2": {
                "question": "How do you handle disagreements with team members?",
                "response": "I believe healthy disagreement leads to better outcomes. When I disagree with a teammate, I first make sure I understand their perspective by asking clarifying questions. Then I explain my viewpoint with supporting evidence rather than just opinions. For example, on a recent project, a colleague wanted to use a new framework I thought was risky. Instead of dismissing the idea, we had a productive discussion about pros and cons, and ultimately found a compromise that incorporated the best aspects of both approaches."
            },
            "q3": {
                "question": "Tell me about a time you helped a colleague who was struggling.",
                "response": "One of our junior developers was having trouble with a complex authentication system. Rather than just giving them the solution, I set up a pair programming session where we worked through the problem together. I explained the concepts as we went and encouraged them to take the lead when they felt comfortable. After a few sessions, they were able to complete the feature independently. I believe in helping team members grow rather than just fixing problems for them."
            }
        }
    }
    
    # Company values to focus on
    company_values = ["innovation", "collaboration", "excellence"]
    
    # Analyze cultural fit
    fit_analysis = cultural_analyzer.analyze_cultural_fit(candidate_data, company_values)
    
    # Print results
    print("Cultural Fit Analysis:")
    print(f"Overall fit: {fit_analysis['overall_fit']:.2f}")
    
    print("\nValue alignment:")
    for value_id, alignment in fit_analysis["value_alignment"].items():
        print(f"- {alignment['value_name']}: {alignment['score']:.2f}")
    
    print("\nStrengths:")
    for strength in fit_analysis["strengths"]:
        print(f"- {strength['value_name']}: {strength['evidence']}")
    
    print("\nGaps:")
    for gap in fit_analysis["gaps"]:
        print(f"- {gap['value_name']}: {gap['evidence']}")
    
    print("\nRecommendations:")
    for recommendation in fit_analysis["recommendations"]:
        print(f"- {recommendation}")
    
    # Generate culture-focused questions
    culture_questions = cultural_analyzer.generate_cultural_questions(company_values, count=3)
    
    print("\nCulture-focused interview questions:")
    for i, question in enumerate(culture_questions):
        print(f"{i+1}. {question['text']} (assesses {question['value_name']})")
    
    # Initialize behavioral pattern analyzer
    behavioral_analyzer = BehavioralPatternAnalyzer()
    
    # Example interaction data
    interaction_data = {
        "candidate_id": "candidate_12345",
        "responses": candidate_data["responses"],
        "response_times": [15, 22, 18]  # seconds
    }
    
    # Analyze behavioral patterns
    behavior_analysis = behavioral_analyzer.analyze_behavior(interaction_data)
    
    print("\nBehavioral Pattern Analysis:")
    print(f"Overall score: {behavior_analysis['overall_score']:.2f}")
    
    print("\nBehavioral traits:")
    for trait, score in behavior_analysis["behavioral_traits"].items():
        print(f"- {trait.replace('_', ' ')}: {score:.2f}")
    
    print("\nInsights:")
    for insight in behavior_analysis["insights"]:
        print(f"- {insight}")
