"""
Interview Analysis System for AI Candidate Evaluation Framework

This module processes candidate responses using natural language understanding,
sentiment analysis, and technical accuracy assessment to evaluate the quality
and relevance of answers.
"""

import logging
import os
import json
import time
from typing import Dict, List, Any, Optional
import spacy
from nltk.sentiment import SentimentIntensityAnalyzer
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class ResponseAnalyzer:
    """Analyzes candidate responses to interview questions."""
    
    def __init__(self, models_config: Optional[Dict[str, str]] = None):
        """
        Initialize the response analyzer.
        
        Args:
            models_config: Configuration for analysis models
        """
        self.models_config = models_config or {}
        
        try:
            # Load spaCy model for text processing
            self.nlp = spacy.load("en_core_web_sm")
            logger.info("Loaded spaCy model successfully")
        except Exception as e:
            logger.warning(f"Could not load spaCy model: {str(e)}. Using basic NLP functionality.")
            self.nlp = None
        
        try:
            # Load sentiment analyzer
            self.sentiment_analyzer = SentimentIntensityAnalyzer()
            logger.info("Loaded sentiment analyzer successfully")
        except Exception as e:
            logger.warning(f"Could not load sentiment analyzer: {str(e)}. Sentiment analysis will be limited.")
            self.sentiment_analyzer = None
        
        # Load technical knowledge model
        self.technical_model = self._load_model(
            self.models_config.get("technical_model_path", "models/technical_v1")
        )
        
        # Load coherence model
        self.coherence_model = self._load_model(
            self.models_config.get("coherence_model_path", "models/coherence_v1")
        )
        
        logger.info("Response analyzer initialized")
    
    def analyze_response(self, question: str, response: str, expected_concepts: Optional[List[str]] = None) -> Dict[str, Any]:
        """
        Analyze a candidate's response to an interview question.
        
        Args:
            question: The interview question
            response: The candidate's response
            expected_concepts: List of concepts expected in the answer
            
        Returns:
            Analysis results dictionary
        """
        logger.info(f"Analyzing response to question: {question[:50]}...")
        
        # Process text with spaCy if available
        if self.nlp:
            question_doc = self.nlp(question)
            response_doc = self.nlp(response)
            
            # Basic metrics
            word_count = len(response_doc)
            sentence_count = len(list(response_doc.sents))
            avg_sentence_length = word_count / max(1, sentence_count)
            
            # Relevance score (similarity between question and answer)
            relevance_score = question_doc.similarity(response_doc)
        else:
            # Fallback metrics if spaCy not available
            words = response.split()
            sentences = [s.strip() for s in response.split('.') if s.strip()]
            
            word_count = len(words)
            sentence_count = len(sentences)
            avg_sentence_length = word_count / max(1, sentence_count)
            
            # Simple relevance based on word overlap
            question_words = set(question.lower().split())
            response_words = set(response.lower().split())
            overlap = len(question_words.intersection(response_words))
            relevance_score = overlap / max(1, len(question_words))
        
        # Sentiment analysis
        if self.sentiment_analyzer:
            sentiment = self.sentiment_analyzer.polarity_scores(response)
        else:
            # Fallback sentiment if analyzer not available
            sentiment = {"pos": 0.33, "neg": 0.33, "neu": 0.34, "compound": 0}
        
        # Technical content analysis
        technical_score = self._analyze_technical_content(
            response, expected_concepts
        )
        
        # Coherence and structure
        coherence_score = self._analyze_coherence(response_doc if self.nlp else response)
        
        # Combine all metrics
        analysis = {
            "metrics": {
                "word_count": word_count,
                "sentence_count": sentence_count,
                "avg_sentence_length": avg_sentence_length
            },
            "relevance": {
                "score": float(relevance_score),
                "is_relevant": relevance_score > 0.5
            },
            "sentiment": {
                "positive": sentiment["pos"],
                "negative": sentiment["neg"],
                "neutral": sentiment["neu"],
                "compound": sentiment["compound"]
            },
            "technical": {
                "score": technical_score["score"],
                "concepts_mentioned": technical_score["concepts_mentioned"],
                "concepts_missing": technical_score["concepts_missing"]
            },
            "coherence": {
                "score": coherence_score,
                "is_coherent": coherence_score > 0.7
            },
            "overall_score": self._calculate_overall_score(
                relevance_score, 
                technical_score["score"], 
                coherence_score,
                sentiment["compound"]
            )
        }
        
        logger.info(f"Response analysis complete. Overall score: {analysis['overall_score']:.2f}")
        return analysis
    
    def analyze_interview(self, interview_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Analyze a complete interview with multiple questions and responses.
        
        Args:
            interview_data: Dictionary containing interview questions and responses
            
        Returns:
            Complete interview analysis
        """
        logger.info(f"Analyzing complete interview with {len(interview_data.get('responses', {}))} responses")
        
        # Extract questions and responses
        responses = interview_data.get("responses", {})
        
        # Analyze each response
        response_analyses = {}
        for question_id, data in responses.items():
            question = data.get("question", "")
            response = data.get("response", "")
            expected_concepts = data.get("expected_concepts", [])
            
            if question and response:
                response_analyses[question_id] = self.analyze_response(
                    question, response, expected_concepts
                )
        
        # Calculate overall interview scores
        overall_scores = self._calculate_interview_scores(response_analyses)
        
        # Generate interview insights
        insights = self._generate_interview_insights(response_analyses)
        
        # Combine everything into interview analysis
        interview_analysis = {
            "interview_id": interview_data.get("interview_id", "unknown"),
            "candidate_id": interview_data.get("candidate_id", "unknown"),
            "job_id": interview_data.get("job_id", "unknown"),
            "response_analyses": response_analyses,
            "overall_scores": overall_scores,
            "insights": insights,
            "analysis_timestamp": time.time()
        }
        
        logger.info(f"Interview analysis complete. Overall technical score: {overall_scores['technical']:.2f}")
        return interview_analysis
    
    def _analyze_technical_content(self, response: str, expected_concepts: Optional[List[str]]) -> Dict[str, Any]:
        """
        Analyze technical content of the response.
        
        Args:
            response: Candidate's response
            expected_concepts: List of concepts expected in the answer
            
        Returns:
            Technical content analysis
        """
        if not expected_concepts:
            # Use model to extract technical concepts if none provided
            return self.technical_model.analyze(response)
        
        # Check for expected concepts
        response_lower = response.lower()
        concepts_mentioned = []
        concepts_missing = []
        
        for concept in expected_concepts:
            if concept.lower() in response_lower:
                concepts_mentioned.append(concept)
            else:
                # Check for synonyms or related terms if spaCy is available
                if self.nlp:
                    concept_doc = self.nlp(concept)
                    found = False
                    
                    for token in self.nlp(response):
                        if token.vector_norm and concept_doc[0].vector_norm:
                            similarity = token.similarity(concept_doc[0])
                            if similarity > 0.8:
                                concepts_mentioned.append(concept)
                                found = True
                                break
                    
                    if not found:
                        concepts_missing.append(concept)
                else:
                    # Simple word matching if spaCy not available
                    concept_words = concept.lower().split()
                    if any(word in response_lower for word in concept_words):
                        concepts_mentioned.append(concept)
                    else:
                        concepts_missing.append(concept)
        
        # Calculate score based on concept coverage
        score = len(concepts_mentioned) / max(1, len(expected_concepts))
        
        return {
            "score": score,
            "concepts_mentioned": concepts_mentioned,
            "concepts_missing": concepts_missing
        }
    
    def _analyze_coherence(self, doc) -> float:
        """
        Analyze the coherence and structure of the response.
        
        Args:
            doc: spaCy document or text string
            
        Returns:
            Coherence score (0-1)
        """
        # If spaCy is available, use it for coherence analysis
        if self.nlp and isinstance(doc, spacy.tokens.doc.Doc):
            # Get sentences
            sentences = list(doc.sents)
            
            if len(sentences) <= 1:
                return 0.5  # Neutral score for very short responses
            
            # Check for coherence between adjacent sentences
            coherence_scores = []
            for i in range(len(sentences) - 1):
                similarity = sentences[i].similarity(sentences[i + 1])
                coherence_scores.append(similarity)
            
            avg_coherence = sum(coherence_scores) / len(coherence_scores)
            
            # Adjust score based on discourse markers
            discourse_markers = ["however", "therefore", "furthermore", "consequently", 
                                "in addition", "moreover", "thus", "hence", "in conclusion"]
            
            marker_count = sum(1 for marker in discourse_markers if marker in doc.text.lower())
            marker_bonus = min(0.2, marker_count * 0.05)  # Cap bonus at 0.2
            
            return min(1.0, avg_coherence + marker_bonus)
        
        else:
            # Fallback coherence analysis if spaCy not available
            text = doc if isinstance(doc, str) else doc.text
            
            # Split into sentences
            sentences = [s.strip() for s in text.split('.') if s.strip()]
            
            if len(sentences) <= 1:
                return 0.5  # Neutral score for very short responses
            
            # Check for discourse markers
            discourse_markers = ["however", "therefore", "furthermore", "consequently", 
                                "in addition", "moreover", "thus", "hence", "in conclusion"]
            
            marker_count = sum(1 for marker in discourse_markers if marker in text.lower())
            
            # Simple coherence based on sentence length consistency
            sentence_lengths = [len(s.split()) for s in sentences]
            length_variance = np.var(sentence_lengths) if len(sentence_lengths) > 1 else 0
            length_consistency = 1 / (1 + length_variance / 100)  # Normalize variance
            
            # Combine factors
            coherence_score = 0.5 + (marker_count * 0.05) + (length_consistency * 0.3)
            
            return min(1.0, coherence_score)
    
    def _calculate_overall_score(self, relevance: float, technical: float, coherence: float, sentiment: float) -> float:
        """
        Calculate overall response quality score.
        
        Args:
            relevance: Relevance score
            technical: Technical content score
            coherence: Coherence score
            sentiment: Sentiment score
            
        Returns:
            Overall score (0-1)
        """
        # Weighted average of different factors
        weights = {
            "relevance": 0.3,
            "technical": 0.4,
            "coherence": 0.2,
            "sentiment": 0.1
        }
        
        # Normalize sentiment from [-1, 1] to [0, 1]
        sentiment_score = (sentiment + 1) / 2
        
        overall = (
            relevance * weights["relevance"] +
            technical * weights["technical"] +
            coherence * weights["coherence"] +
            sentiment_score * weights["sentiment"]
        )
        
        return overall
    
    def _calculate_interview_scores(self, response_analyses: Dict[str, Dict[str, Any]]) -> Dict[str, float]:
        """
        Calculate overall interview scores based on individual response analyses.
        
        Args:
            response_analyses: Dictionary of response analyses
            
        Returns:
            Overall interview scores
        """
        if not response_analyses:
            return {
                "overall": 0,
                "technical": 0,
                "communication": 0,
                "relevance": 0
            }
        
        # Extract scores from each response
        overall_scores = [analysis["overall_score"] for analysis in response_analyses.values()]
        technical_scores = [analysis["technical"]["score"] for analysis in response_analyses.values()]
        coherence_scores = [analysis["coherence"]["score"] for analysis in response_analyses.values()]
        relevance_scores = [analysis["relevance"]["score"] for analysis in response_analyses.values()]
        
        # Calculate averages
        avg_overall = sum(overall_scores) / len(overall_scores)
        avg_technical = sum(technical_scores) / len(technical_scores)
        avg_coherence = sum(coherence_scores) / len(coherence_scores)
        avg_relevance = sum(relevance_scores) / len(relevance_scores)
        
        # Combine coherence with other communication factors
        communication_score = avg_coherence
        
        return {
            "overall": avg_overall,
            "technical": avg_technical,
            "communication": communication_score,
            "relevance": avg_relevance
        }
    
    def _generate_interview_insights(self, response_analyses: Dict[str, Dict[str, Any]]) -> List[str]:
        """
        Generate insights based on interview response analyses.
        
        Args:
            response_analyses: Dictionary of response analyses
            
        Returns:
            List of insights
        """
        insights = []
        
        if not response_analyses:
            return ["No responses to analyze"]
        
        # Find strongest and weakest responses
        response_scores = [(q_id, analysis["overall_score"]) 
                          for q_id, analysis in response_analyses.items()]
        
        if response_scores:
            # Sort by score
            response_scores.sort(key=lambda x: x[1], reverse=True)
            
            # Get strongest and weakest
            strongest_id, strongest_score = response_scores[0]
            weakest_id, weakest_score = response_scores[-1]
            
            # Add insights if scores are notable
            if strongest_score > 0.8:
                strongest_analysis = response_analyses[strongest_id]
                concepts = strongest_analysis["technical"]["concepts_mentioned"]
                concept_str = ", ".join(concepts[:3]) if concepts else "key concepts"
                insights.append(f"Strongest response demonstrated excellent understanding of {concept_str}")
            
            if weakest_score < 0.5:
                weakest_analysis = response_analyses[weakest_id]
                missing_concepts = weakest_analysis["technical"]["concepts_missing"]
                if missing_concepts:
                    insights.append(f"Knowledge gap identified in: {', '.join(missing_concepts[:3])}")
        
        # Check for overall technical strength
        technical_scores = [analysis["technical"]["score"] for analysis in response_analyses.values()]
        avg_technical = sum(technical_scores) / len(technical_scores) if technical_scores else 0
        
        if avg_technical > 0.8:
            insights.append("Demonstrates strong technical knowledge across questions")
        elif avg_technical < 0.5:
            insights.append("Technical knowledge appears limited in several areas")
        
        # Check for communication patterns
        coherence_scores = [analysis["coherence"]["score"] for analysis in response_analyses.values()]
        avg_coherence = sum(coherence_scores) / len(coherence_scores) if coherence_scores else 0
        
        if avg_coherence > 0.8:
            insights.append("Communicates with exceptional clarity and structure")
        elif avg_coherence < 0.5:
            insights.append("Communication could be more structured and coherent")
        
        # Check for relevance patterns
        relevance_scores = [analysis["relevance"]["score"] for analysis in response_analyses.values()]
        avg_relevance = sum(relevance_scores) / len(relevance_scores) if relevance_scores else 0
        
        if avg_relevance < 0.6:
            insights.append("Tendency to provide responses that don't directly address questions")
        
        # Check for sentiment patterns
        sentiment_scores = [analysis["sentiment"]["compound"] for analysis in response_analyses.values()]
        avg_sentiment = sum(sentiment_scores) / len(sentiment_scores) if sentiment_scores else 0
        
        if avg_sentiment > 0.5:
            insights.append("Consistently positive and enthusiastic communication style")
        elif avg_sentiment < -0.3:
            insights.append("Communication style tends toward negativity")
        
        return insights
    
    def _load_model(self, model_path: str):
        """
        Load a model from the specified path.
        
        Args:
            model_path: Path to the model
            
        Returns:
            Loaded model
        """
        logger.info(f"Loading model from {model_path}")
        
        # In a real implementation, this would load actual ML models
        # For this example, we'll use a mock model
        return MockModel(model_path)


class MockModel:
    """Mock model for demonstration purposes."""
    
    def __init__(self, model_path: str):
        """
        Initialize the mock model.
        
        Args:
            model_path: Path to the model
        """
        self.model_path = model_path
        logger.info(f"Initialized mock model from {model_path}")
    
    def analyze(self, text: str) -> Dict[str, Any]:
        """
        Mock analysis that returns simulated scores.
        
        Args:
            text: Text to analyze
            
        Returns:
            Analysis results
        """
        import random
        
        # Generate random concepts
        all_concepts = ["algorithms", "data structures", "complexity", "optimization", 
                       "databases", "APIs", "frameworks", "testing", "deployment",
                       "scalability", "security", "performance", "design patterns",
                       "architecture", "cloud services", "containerization"]
        
        # Make analysis somewhat deterministic based on text content
        text_hash = sum(ord(c) for c in text[:100])
        random.seed(text_hash)
        
        # Select concepts based on text length and content
        num_concepts = max(2, min(8, len(text) // 100))
        concepts = random.sample(all_concepts, num_concepts)
        
        # Determine how many concepts are "mentioned" based on text quality
        quality_factor = min(1.0, len(text) / 500)  # Longer answers tend to cover more
        num_mentioned = max(1, int(num_concepts * quality_factor))
        
        concepts_mentioned = concepts[:num_mentioned]
        concepts_missing = concepts[num_mentioned:]
        
        # Generate a score
        score = num_mentioned / num_concepts
        
        # Adjust score based on text features
        if len(text) < 50:  # Very short answer
            score *= 0.5
        elif len(text) > 1000:  # Very long answer
            score *= 0.9  # Slight penalty for excessive length
        
        # Check for technical keywords
        tech_keywords = ["implement", "algorithm", "solution", "code", "design", 
                        "architecture", "system", "database", "optimize", "performance"]
        
        keyword_count = sum(1 for keyword in tech_keywords if keyword in text.lower())
        keyword_bonus = min(0.2, keyword_count * 0.02)
        
        # Final score with bonus
        final_score = min(1.0, score + keyword_bonus)
        
        return {
            "score": final_score,
            "concepts_mentioned": concepts_mentioned,
            "concepts_missing": concepts_missing
        }


# Example usage
if __name__ == "__main__":
    # Example question and response
    question = "Explain the difference between REST and GraphQL APIs and when you would choose one over the other."
    response = """
    REST and GraphQL are both API paradigms for building web services. REST is resource-based where you access different endpoints for different resources, while GraphQL uses a single endpoint where you specify exactly what data you need.

    I would choose REST when working with well-defined resources that map cleanly to HTTP methods, when caching is important, or when working with teams familiar with REST principles. REST is also more widely adopted and has better tooling support.

    I would choose GraphQL when working with complex, nested data structures, when bandwidth efficiency is critical (mobile apps), or when the frontend needs flexibility in the data it retrieves. GraphQL excels at preventing over-fetching and under-fetching of data.

    In my last project, we switched from REST to GraphQL because our mobile app needed to minimize network requests and our data had many relationships that were inefficient to query with multiple REST endpoints.
    """

    # Expected concepts for this technical question
    expected_concepts = [
        "resource-based", "endpoints", "HTTP methods", 
        "single endpoint", "over-fetching", "under-fetching",
        "caching", "bandwidth", "query flexibility"
    ]

    # Initialize analyzer
    analyzer = ResponseAnalyzer()

    # Analyze the response
    analysis = analyzer.analyze_response(question, response, expected_concepts)

    # Print analysis results
    print("\nResponse Analysis:")
    print(f"Word count: {analysis['metrics']['word_count']}")
    print(f"Sentence count: {analysis['metrics']['sentence_count']}")
    
    print("\nRelevance:")
    print(f"Score: {analysis['relevance']['score']:.2f}")
    print(f"Is relevant: {analysis['relevance']['is_relevant']}")
    
    print("\nTechnical content:")
    print(f"Score: {analysis['technical']['score']:.2f}")
    print("Concepts mentioned:")
    for concept in analysis['technical']['concepts_mentioned']:
        print(f"- {concept}")
    print("Concepts missing:")
    for concept in analysis['technical']['concepts_missing']:
        print(f"- {concept}")
    
    print("\nCoherence:")
    print(f"Score: {analysis['coherence']['score']:.2f}")
    print(f"Is coherent: {analysis['coherence']['is_coherent']}")
    
    print("\nSentiment:")
    print(f"Positive: {analysis['sentiment']['positive']:.2f}")
    print(f"Negative: {analysis['sentiment']['negative']:.2f}")
    print(f"Neutral: {analysis['sentiment']['neutral']:.2f}")
    print(f"Compound: {analysis['sentiment']['compound']:.2f}")
    
    print("\nOverall score: {analysis['overall_score']:.2f}")
    
    # Example interview analysis
    interview_data = {
        "interview_id": "interview_12345",
        "candidate_id": "candidate_67890",
        "job_id": "job_54321",
        "responses": {
            "q1": {
                "question": "Explain the difference between REST and GraphQL APIs and when you would choose one over the other.",
                "response": response,
                "expected_concepts": expected_concepts
            },
            "q2": {
                "question": "Describe your experience with containerization technologies like Docker.",
                "response": "I've used Docker extensively in my current role. We containerize all our microservices to ensure consistent environments across development, testing, and production. I've written Dockerfiles, managed multi-container applications with Docker Compose, and implemented CI/CD pipelines that build and deploy Docker images. I'm also familiar with container orchestration using Kubernetes, though I have more experience with Docker Swarm.",
                "expected_concepts": ["Dockerfile", "containers", "images", "Docker Compose", "orchestration", "CI/CD"]
            }
        }
    }
    
    # Analyze the interview
    interview_analysis = analyzer.analyze_interview(interview_data)
    
    print("\n\nInterview Analysis:")
    print(f"Overall score: {interview_analysis['overall_scores']['overall']:.2f}")
    print(f"Technical score: {interview_analysis['overall_scores']['technical']:.2f}")
    print(f"Communication score: {interview_analysis['overall_scores']['communication']:.2f}")
    print(f"Relevance score: {interview_analysis['overall_scores']['relevance']:.2f}")
    
    print("\nInsights:")
    for insight in interview_analysis['insights']:
        print(f"- {insight}")
