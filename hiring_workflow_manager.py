"""
Automated Hiring Workflow for Autonomous Recruitment System

This module integrates all previous components into a cohesive end-to-end hiring workflow,
managing the process from decision support through offer management and onboarding.
"""

import logging
import os
import json
import time
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DecisionSupportSystem:
    """Provides data-driven hiring recommendations based on all candidate assessments."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the decision support system.
        
        Args:
            config: Configuration settings
        """
        self.config = config or {}
        
        # Default weights for different assessment components
        self.default_weights = {
            "resume_score": 0.15,
            "technical_skills": 0.30,
            "interview_performance": 0.25,
            "cultural_fit": 0.20,
            "references": 0.10
        }
        
        # Use configured weights or defaults
        self.weights = self.config.get("assessment_weights", self.default_weights)
        
        # Normalize weights to ensure they sum to 1
        weight_sum = sum(self.weights.values())
        if weight_sum != 1.0:
            for key in self.weights:
                self.weights[key] = self.weights[key] / weight_sum
        
        logger.info("Decision support system initialized with weights: %s", self.weights)
    
    def generate_hiring_recommendation(self, candidate_id: str, job_id: str, assessments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a hiring recommendation based on all candidate assessments.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            assessments: All assessment data for the candidate
            
        Returns:
            Hiring recommendation
        """
        logger.info(f"Generating hiring recommendation for candidate {candidate_id} and job {job_id}")
        
        # Extract scores from assessments
        scores = self._extract_assessment_scores(assessments)
        
        # Calculate weighted overall score
        overall_score = self._calculate_overall_score(scores)
        
        # Determine recommendation
        recommendation, confidence = self._determine_recommendation(overall_score, scores)
        
        # Generate justification
        justification = self._generate_justification(recommendation, scores, assessments)
        
        # Identify strengths and areas of concern
        strengths, concerns = self._identify_strengths_concerns(scores, assessments)
        
        # Generate next steps
        next_steps = self._generate_next_steps(recommendation, concerns)
        
        return {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "overall_score": overall_score,
            "recommendation": recommendation,
            "confidence": confidence,
            "justification": justification,
            "component_scores": scores,
            "strengths": strengths,
            "concerns": concerns,
            "next_steps": next_steps
        }
    
    def compare_candidates(self, job_id: str, candidate_recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple candidates for the same job.
        
        Args:
            job_id: Job identifier
            candidate_recommendations: List of candidate recommendations
            
        Returns:
            Candidate comparison
        """
        logger.info(f"Comparing {len(candidate_recommendations)} candidates for job {job_id}")
        
        if not candidate_recommendations:
            return {
                "job_id": job_id,
                "timestamp": datetime.now().isoformat(),
                "error": "No candidates to compare"
            }
        
        # Sort candidates by overall score
        sorted_candidates = sorted(
            candidate_recommendations, 
            key=lambda x: x.get("overall_score", 0),
            reverse=True
        )
        
        # Extract top candidates
        top_candidates = sorted_candidates[:min(3, len(sorted_candidates))]
        
        # Generate comparison insights
        comparison_insights = self._generate_comparison_insights(top_candidates)
        
        # Generate recommendation for final selection
        final_recommendation = self._generate_final_recommendation(top_candidates)
        
        return {
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "candidate_count": len(candidate_recommendations),
            "top_candidates": [
                {
                    "candidate_id": c["candidate_id"],
                    "overall_score": c["overall_score"],
                    "recommendation": c["recommendation"],
                    "key_strengths": c["strengths"][:2] if len(c["strengths"]) > 1 else c["strengths"]
                }
                for c in top_candidates
            ],
            "comparison_insights": comparison_insights,
            "final_recommendation": final_recommendation
        }
    
    def _extract_assessment_scores(self, assessments: Dict[str, Any]) -> Dict[str, float]:
        """
        Extract normalized scores from assessment data.
        
        Args:
            assessments: Assessment data
            
        Returns:
            Normalized component scores
        """
        scores = {}
        
        # Resume score
        if "resume_assessment" in assessments:
            resume_data = assessments["resume_assessment"]
            scores["resume_score"] = resume_data.get("overall_score", 0) / 100
        
        # Technical skills
        if "technical_assessment" in assessments:
            tech_data = assessments["technical_assessment"]
            scores["technical_skills"] = tech_data.get("overall_score", 0) / 100
        
        # Interview performance
        if "interview_assessment" in assessments:
            interview_data = assessments["interview_assessment"]
            scores["interview_performance"] = interview_data.get("overall_scores", {}).get("overall", 0)
        
        # Cultural fit
        if "cultural_fit" in assessments:
            culture_data = assessments["cultural_fit"]
            scores["cultural_fit"] = culture_data.get("overall_fit", 0)
        
        # References
        if "references" in assessments:
            reference_data = assessments["references"]
            scores["references"] = reference_data.get("overall_score", 0) / 5  # Assuming 5-point scale
        
        # Fill in missing scores with neutral values
        for key in self.weights:
            if key not in scores:
                scores[key] = 0.5
                logger.warning(f"Missing assessment component: {key}, using neutral score")
        
        return scores
    
    def _calculate_overall_score(self, scores: Dict[str, float]) -> float:
        """
        Calculate weighted overall score.
        
        Args:
            scores: Component scores
            
        Returns:
            Overall weighted score
        """
        overall = 0.0
        
        for component, weight in self.weights.items():
            if component in scores:
                overall += scores[component] * weight
        
        return overall
    
    def _determine_recommendation(self, overall_score: float, scores: Dict[str, float]) -> tuple:
        """
        Determine hiring recommendation based on scores.
        
        Args:
            overall_score: Overall candidate score
            scores: Component scores
            
        Returns:
            Tuple of (recommendation, confidence)
        """
        # Check for any critical concerns
        has_critical_concern = False
        
        # Technical skills below threshold for technical roles
        if "technical_skills" in scores and scores["technical_skills"] < 0.6:
            has_critical_concern = True
        
        # Cultural fit below threshold
        if "cultural_fit" in scores and scores["cultural_fit"] < 0.4:
            has_critical_concern = True
        
        # Determine recommendation based on overall score
        if overall_score >= 0.85:
            recommendation = "Strong Hire"
            confidence = min(1.0, 0.7 + (overall_score - 0.85) * 2)
        elif overall_score >= 0.75:
            recommendation = "Hire"
            confidence = min(1.0, 0.6 + (overall_score - 0.75) * 2)
        elif overall_score >= 0.65:
            recommendation = "Lean Hire"
            confidence = min(1.0, 0.5 + (overall_score - 0.65) * 2)
        elif overall_score >= 0.55:
            recommendation = "Borderline"
            confidence = 0.5
        elif overall_score >= 0.45:
            recommendation = "Lean No Hire"
            confidence = min(1.0, 0.5 + (0.55 - overall_score) * 2)
        elif overall_score >= 0.35:
            recommendation = "No Hire"
            confidence = min(1.0, 0.6 + (0.45 - overall_score) * 2)
        else:
            recommendation = "Strong No Hire"
            confidence = min(1.0, 0.7 + (0.35 - overall_score) * 2)
        
        # Override for critical concerns
        if has_critical_concern and recommendation in ["Strong Hire", "Hire", "Lean Hire"]:
            recommendation = "Borderline"
            confidence = 0.6
        
        return recommendation, confidence
    
    def _generate_justification(self, recommendation: str, scores: Dict[str, float], assessments: Dict[str, Any]) -> str:
        """
        Generate justification for the recommendation.
        
        Args:
            recommendation: Hiring recommendation
            scores: Component scores
            assessments: Assessment data
            
        Returns:
            Justification text
        """
        # Start with the recommendation
        justification = f"The recommendation is {recommendation} based on an overall assessment of the candidate's qualifications, skills, and fit."
        
        # Add key factors that influenced the decision
        justification += " Key factors include:"
        
        # Sort components by weight and score
        weighted_scores = [(component, score * self.weights.get(component, 0)) 
                          for component, score in scores.items()]
        weighted_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Add top 3 factors
        for component, weighted_score in weighted_scores[:3]:
            score = scores[component]
            if score >= 0.8:
                strength = "excellent"
            elif score >= 0.7:
                strength = "strong"
            elif score >= 0.6:
                strength = "good"
            elif score >= 0.5:
                strength = "adequate"
            elif score >= 0.4:
                strength = "fair"
            else:
                strength = "concerning"
            
            component_name = component.replace("_", " ").title()
            justification += f" {component_name} ({strength}, {score:.2f});"
        
        # Add specific details from assessments
        if "interview_assessment" in assessments:
            interview_data = assessments["interview_assessment"]
            insights = interview_data.get("insights", [])
            if insights:
                justification += f" Interview insights: {insights[0]}"
        
        if "cultural_fit" in assessments:
            culture_data = assessments["cultural_fit"]
            strengths = culture_data.get("strengths", [])
            if strengths and len(strengths) > 0:
                justification += f" Cultural strength in {strengths[0].get('value_name', '')}."
        
        return justification
    
    def _identify_strengths_concerns(self, scores: Dict[str, float], assessments: Dict[str, Any]) -> tuple:
        """
        Identify candidate strengths and areas of concern.
        
        Args:
            scores: Component scores
            assessments: Assessment data
            
        Returns:
            Tuple of (strengths, concerns)
        """
        strengths = []
        concerns = []
        
        # Identify strengths and concerns from component scores
        for component, score in scores.items():
            component_name = component.replace("_", " ").title()
            
            if score >= 0.8:
                strengths.append(f"Excellent {component_name}")
            elif score >= 0.7:
                strengths.append(f"Strong {component_name}")
            elif score <= 0.4:
                concerns.append(f"Below expectations in {component_name}")
        
        # Add specific strengths from assessments
        if "technical_assessment" in assessments:
            tech_data = assessments["technical_assessment"]
            tech_strengths = tech_data.get("strengths", [])
            if tech_strengths:
                strengths.extend(tech_strengths[:2])
        
        if "cultural_fit" in assessments:
            culture_data = assessments["cultural_fit"]
            culture_strengths = [s.get("value_name", "") for s in culture_data.get("strengths", [])]
            if culture_strengths:
                strengths.append(f"Cultural alignment with {', '.join(culture_strengths)}")
        
        # Add specific concerns from assessments
        if "technical_assessment" in assessments:
            tech_data = assessments["technical_assessment"]
            tech_weaknesses = tech_data.get("weaknesses", [])
            if tech_weaknesses:
                concerns.extend(tech_weaknesses[:2])
        
        if "cultural_fit" in assessments:
            culture_data = assessments["cultural_fit"]
            culture_gaps = [g.get("value_name", "") for g in culture_data.get("gaps", [])]
            if culture_gaps:
                concerns.append(f"Cultural gap in {', '.join(culture_gaps)}")
        
        return strengths, concerns
    
    def _generate_next_steps(self, recommendation: str, concerns: List[str]) -> List[str]:
        """
        Generate recommended next steps.
        
        Args:
            recommendation: Hiring recommendation
            concerns: Areas of concern
            
        Returns:
            List of next steps
        """
        next_steps = []
        
        if recommendation in ["Strong Hire", "Hire"]:
            next_steps.append("Proceed with offer preparation")
            next_steps.append("Conduct final reference checks")
            next_steps.append("Prepare onboarding plan")
        
        elif recommendation in ["Lean Hire", "Borderline"]:
            next_steps.append("Consider additional interview to address specific concerns")
            
            # Add specific next steps based on concerns
            for concern in concerns:
                if "technical" in concern.lower():
                    next_steps.append("Conduct focused technical assessment in areas of concern")
                    break
            
            for concern in concerns:
                if "cultural" in concern.lower():
                    next_steps.append("Schedule team interview to evaluate cultural fit")
                    break
            
            next_steps.append("Review assessment details with hiring manager")
        
        elif recommendation in ["Lean No Hire", "No Hire", "Strong No Hire"]:
            next_steps.append("Prepare rejection communication")
            next_steps.append("Document decision rationale for compliance")
            next_steps.append("Consider for alternative roles if appropriate")
        
        return next_steps
    
    def _generate_comparison_insights(self, top_candidates: List[Dict[str, Any]]) -> List[str]:
        """
        Generate insights comparing top candidates.
        
        Args:
            top_candidates: List of top candidate recommendations
            
        Returns:
            List of comparison insights
        """
        if not top_candidates:
            return ["No candidates to compare"]
        
        if len(top_candidates) == 1:
            return ["Only one candidate available for consideration"]
        
        insights = []
        
        # Compare overall scores
        score_gap = top_candidates[0]["overall_score"] - top_candidates[1]["overall_score"]
        if score_gap > 0.15:
            insights.append(f"Top candidate significantly outperforms others (gap: {score_gap:.2f})")
        elif score_gap < 0.05:
            insights.append("Top candidates are very closely matched")
        
        # Compare strengths
        top_strengths = set([s.lower() for s in top_candidates[0]["strengths"][:3]])
        second_strengths = set([s.lower() for s in top_candidates[1]["strengths"][:3]])
        
        common_strengths = top_strengths.intersection(second_strengths)
        if common_strengths:
            insights.append(f"Top candidates share strengths in: {', '.join(common_strengths)}")
        
        unique_top_strengths = top_strengths - second_strengths
        if unique_top_strengths:
            insights.append(f"Top candidate uniquely strong in: {', '.join(unique_top_strengths)}")
        
        # Compare component scores if available
        if "component_scores" in top_candidates[0] and "component_scores" in top_candidates[1]:
            top_scores = top_candidates[0]["component_scores"]
            second_scores = top_candidates[1]["component_scores"]
            
            # Find areas where second candidate outperforms top candidate
            for component, score in second_scores.items():
                if component in top_scores and score > top_scores[component] + 0.1:
                    component_name = component.replace("_", " ").title()
                    insights.append(f"Second candidate stronger in {component_name}")
        
        return insights
    
    def _generate_final_recommendation(self, top_candidates: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Generate final recommendation for candidate selection.
        
        Args:
            top_candidates: List of top candidate recommendations
            
        Returns:
            Final recommendation
        """
        if not top_candidates:
            return {
                "decision": "No suitable candidates",
                "rationale": "No candidates available for consideration"
            }
        
        # If top candidate is a strong hire with good confidence, recommend them
        top_candidate = top_candidates[0]
        if (top_candidate["recommendation"] in ["Strong Hire", "Hire"] and 
            top_candidate["confidence"] >= 0.7):
            return {
                "decision": "Proceed with top candidate",
                "candidate_id": top_candidate["candidate_id"],
                "rationale": f"Clear top performer with {top_candidate['overall_score']:.2f} overall score"
            }
        
        # If top candidates are close, recommend additional evaluation
        if (len(top_candidates) > 1 and 
            abs(top_candidates[0]["overall_score"] - top_candidates[1]["overall_score"]) < 0.05):
            return {
                "decision": "Additional evaluation needed",
                "candidates": [c["candidate_id"] for c in top_candidates[:2]],
                "rationale": "Top candidates are closely matched, suggesting additional interviews or assessments"
            }
        
        # Default recommendation
        return {
            "decision": "Consider top candidate with caution",
            "candidate_id": top_candidate["candidate_id"],
            "rationale": f"Recommended as {top_candidate['recommendation']} with {top_candidate['confidence']:.2f} confidence"
        }


class OfferManagementSystem:
    """Manages the offer creation, approval, and tracking process."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the offer management system.
        
        Args:
            config: Configuration settings
        """
        self.config = config or {}
        
        # Default offer templates
        self.default_templates = {
            "standard": "templates/standard_offer.html",
            "executive": "templates/executive_offer.html",
            "contractor": "templates/contractor_offer.html"
        }
        
        # Use configured templates or defaults
        self.templates = self.config.get("offer_templates", self.default_templates)
        
        # Default approval workflows
        self.default_workflows = {
            "standard": ["hiring_manager", "hr_manager"],
            "executive": ["hiring_manager", "hr_manager", "ceo"],
            "contractor": ["hiring_manager", "procurement"]
        }
        
        # Use configured workflows or defaults
        self.workflows = self.config.get("approval_workflows", self.default_workflows)
        
        logger.info("Offer management system initialized")
    
    def create_offer(self, candidate_id: str, job_id: str, offer_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Create a new job offer.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            offer_details: Offer details including compensation, start date, etc.
            
        Returns:
            Created offer
        """
        logger.info(f"Creating offer for candidate {candidate_id} and job {job_id}")
        
        # Generate offer ID
        offer_id = f"offer_{uuid.uuid4().hex[:8]}"
        
        # Determine offer type
        offer_type = offer_details.get("offer_type", "standard")
        
        # Get approval workflow
        approval_workflow = self.workflows.get(offer_type, self.workflows["standard"])
        
        # Create offer object
        offer = {
            "offer_id": offer_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "created_at": datetime.now().isoformat(),
            "status": "draft",
            "offer_type": offer_type,
            "details": offer_details,
            "approval_workflow": approval_workflow,
            "approvals": {approver: {"status": "pending", "timestamp": None} for approver in approval_workflow},
            "expiration_date": (datetime.now() + timedelta(days=offer_details.get("validity_days", 7))).isoformat(),
            "candidate_response": None,
            "response_date": None
        }
        
        logger.info(f"Offer created with ID {offer_id}")
        return offer
    
    def update_offer(self, offer: Dict[str, Any], updates: Dict[str, Any]) -> Dict[str, Any]:
        """
        Update an existing offer.
        
        Args:
            offer: Existing offer
            updates: Updates to apply
            
        Returns:
            Updated offer
        """
        logger.info(f"Updating offer {offer['offer_id']}")
        
        # Create a copy of the offer
        updated_offer = offer.copy()
        
        # Apply updates to details
        if "details" in updates:
            updated_offer["details"].update(updates["details"])
        
        # Update other fields
        for key, value in updates.items():
            if key != "details" and key in updated_offer:
                updated_offer[key] = value
        
        # Update modification timestamp
        updated_offer["updated_at"] = datetime.now().isoformat()
        
        # Reset approvals if details changed
        if "details" in updates:
            updated_offer["approvals"] = {
                approver: {"status": "pending", "timestamp": None} 
                for approver in updated_offer["approval_workflow"]
            }
            updated_offer["status"] = "draft"
        
        logger.info(f"Offer {offer['offer_id']} updated")
        return updated_offer
    
    def process_approval(self, offer: Dict[str, Any], approver: str, approved: bool, comments: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an approval for an offer.
        
        Args:
            offer: Offer to approve
            approver: Approver identifier
            approved: Whether the offer is approved
            comments: Optional approval comments
            
        Returns:
            Updated offer
        """
        logger.info(f"Processing {approver} approval for offer {offer['offer_id']}")
        
        # Create a copy of the offer
        updated_offer = offer.copy()
        
        # Check if approver is in workflow
        if approver not in updated_offer["approval_workflow"]:
            logger.warning(f"Approver {approver} not in workflow for offer {offer['offer_id']}")
            return updated_offer
        
        # Update approval
        updated_offer["approvals"][approver] = {
            "status": "approved" if approved else "rejected",
            "timestamp": datetime.now().isoformat(),
            "comments": comments
        }
        
        # Check if all approvals are complete
        all_approved = all(a["status"] == "approved" for a in updated_offer["approvals"].values())
        any_rejected = any(a["status"] == "rejected" for a in updated_offer["approvals"].values())
        
        # Update offer status
        if any_rejected:
            updated_offer["status"] = "rejected"
        elif all_approved:
            updated_offer["status"] = "approved"
        else:
            updated_offer["status"] = "pending_approval"
        
        logger.info(f"Offer {offer['offer_id']} approval processed, new status: {updated_offer['status']}")
        return updated_offer
    
    def generate_offer_document(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate offer document from template.
        
        Args:
            offer: Offer data
            
        Returns:
            Document generation result
        """
        logger.info(f"Generating offer document for offer {offer['offer_id']}")
        
        # Check if offer is approved
        if offer["status"] != "approved":
            logger.warning(f"Attempting to generate document for unapproved offer {offer['offer_id']}")
            return {
                "success": False,
                "error": "Cannot generate document for unapproved offer",
                "offer_id": offer["offer_id"]
            }
        
        # Get template path
        offer_type = offer.get("offer_type", "standard")
        template_path = self.templates.get(offer_type, self.templates["standard"])
        
        # In a real implementation, this would use a template engine
        # For this example, we'll just return a mock result
        
        return {
            "success": True,
            "offer_id": offer["offer_id"],
            "document_id": f"doc_{uuid.uuid4().hex[:8]}",
            "template_used": template_path,
            "generated_at": datetime.now().isoformat(),
            "document_url": f"/offers/{offer['offer_id']}/document.pdf"
        }
    
    def record_candidate_response(self, offer: Dict[str, Any], accepted: bool, response_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Record candidate's response to the offer.
        
        Args:
            offer: Offer data
            accepted: Whether the offer was accepted
            response_details: Optional response details
            
        Returns:
            Updated offer
        """
        logger.info(f"Recording candidate response for offer {offer['offer_id']}: {'accepted' if accepted else 'declined'}")
        
        # Create a copy of the offer
        updated_offer = offer.copy()
        
        # Update response
        updated_offer["candidate_response"] = "accepted" if accepted else "declined"
        updated_offer["response_date"] = datetime.now().isoformat()
        
        # Add response details if provided
        if response_details:
            updated_offer["response_details"] = response_details
        
        # Update status
        updated_offer["status"] = "accepted" if accepted else "declined"
        
        logger.info(f"Candidate response recorded for offer {offer['offer_id']}")
        return updated_offer
    
    def get_offer_status(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Get detailed offer status.
        
        Args:
            offer: Offer data
            
        Returns:
            Offer status details
        """
        # Calculate days until expiration
        if "expiration_date" in offer:
            expiration_date = datetime.fromisoformat(offer["expiration_date"])
            now = datetime.now()
            days_until_expiration = (expiration_date - now).days
        else:
            days_until_expiration = None
        
        # Get pending approvers
        pending_approvers = [
            approver for approver, approval in offer.get("approvals", {}).items()
            if approval.get("status") == "pending"
        ]
        
        # Check if offer is expired
        is_expired = days_until_expiration is not None and days_until_expiration < 0
        
        return {
            "offer_id": offer["offer_id"],
            "status": offer["status"],
            "is_expired": is_expired,
            "days_until_expiration": days_until_expiration,
            "pending_approvers": pending_approvers,
            "can_generate_document": offer["status"] == "approved" and not is_expired,
            "needs_attention": (
                offer["status"] == "pending_approval" or 
                (offer["status"] == "approved" and not offer.get("candidate_response"))
            )
        }


class OnboardingSystem:
    """Manages the employee onboarding process after offer acceptance."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the onboarding system.
        
        Args:
            config: Configuration settings
        """
        self.config = config or {}
        
        # Default onboarding templates
        self.default_templates = {
            "standard": "templates/standard_onboarding.json",
            "remote": "templates/remote_onboarding.json",
            "executive": "templates/executive_onboarding.json"
        }
        
        # Use configured templates or defaults
        self.templates = self.config.get("onboarding_templates", self.default_templates)
        
        logger.info("Onboarding system initialized")
    
    def create_onboarding_plan(self, candidate_id: str, job_id: str, offer_id: str, plan_type: str = "standard") -> Dict[str, Any]:
        """
        Create an onboarding plan for a new hire.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            offer_id: Offer identifier
            plan_type: Type of onboarding plan
            
        Returns:
            Onboarding plan
        """
        logger.info(f"Creating {plan_type} onboarding plan for candidate {candidate_id}")
        
        # Generate plan ID
        plan_id = f"onboard_{uuid.uuid4().hex[:8]}"
        
        # Get template path
        template_path = self.templates.get(plan_type, self.templates["standard"])
        
        # In a real implementation, this would load a template from a file
        # For this example, we'll use mock data
        
        # Create tasks based on plan type
        tasks = self._generate_tasks(plan_type)
        
        # Create onboarding plan
        plan = {
            "plan_id": plan_id,
            "candidate_id": candidate_id,
            "job_id": job_id,
            "offer_id": offer_id,
            "created_at": datetime.now().isoformat(),
            "plan_type": plan_type,
            "template_used": template_path,
            "start_date": None,  # To be set later
            "status": "draft",
            "tasks": tasks,
            "progress": {
                "completed_tasks": 0,
                "total_tasks": len(tasks),
                "percentage": 0
            }
        }
        
        logger.info(f"Onboarding plan created with ID {plan_id}")
        return plan
    
    def _generate_tasks(self, plan_type: str) -> List[Dict[str, Any]]:
        """
        Generate onboarding tasks based on plan type.
        
        Args:
            plan_type: Type of onboarding plan
            
        Returns:
            List of onboarding tasks
        """
        # Common tasks for all plan types
        common_tasks = [
            {
                "task_id": f"task_{i}",
                "category": "paperwork",
                "title": "Complete employment paperwork",
                "description": "Fill out tax forms, direct deposit, and emergency contact information",
                "owner": "hr",
                "deadline_days": 1,
                "status": "pending",
                "completed_at": None
            },
            {
                "task_id": f"task_{i+1}",
                "category": "it_setup",
                "title": "Set up computer and accounts",
                "description": "Prepare workstation and create necessary system accounts",
                "owner": "it",
                "deadline_days": 1,
                "status": "pending",
                "completed_at": None
            },
            {
                "task_id": f"task_{i+2}",
                "category": "orientation",
                "title": "Attend company orientation",
                "description": "Introduction to company history, values, and policies",
                "owner": "hr",
                "deadline_days": 2,
                "status": "pending",
                "completed_at": None
            },
            {
                "task_id": f"task_{i+3}",
                "category": "team_introduction",
                "title": "Meet the team",
                "description": "Introduction to team members and roles",
                "owner": "manager",
                "deadline_days": 2,
                "status": "pending",
                "completed_at": None
            },
            {
                "task_id": f"task_{i+4}",
                "category": "training",
                "title": "Complete initial training",
                "description": "Overview of tools, processes, and expectations",
                "owner": "manager",
                "deadline_days": 5,
                "status": "pending",
                "completed_at": None
            }
        ]
        
        # Plan-specific tasks
        if plan_type == "remote":
            additional_tasks = [
                {
                    "task_id": f"task_{i+5}",
                    "category": "remote_setup",
                    "title": "Set up home office equipment",
                    "description": "Ensure proper ergonomic setup and equipment functionality",
                    "owner": "it",
                    "deadline_days": 3,
                    "status": "pending",
                    "completed_at": None
                },
                {
                    "task_id": f"task_{i+6}",
                    "category": "remote_tools",
                    "title": "Training on remote collaboration tools",
                    "description": "Learn to use video conferencing, chat, and project management tools",
                    "owner": "it",
                    "deadline_days": 3,
                    "status": "pending",
                    "completed_at": None
                }
            ]
        elif plan_type == "executive":
            additional_tasks = [
                {
                    "task_id": f"task_{i+5}",
                    "category": "executive_briefing",
                    "title": "Executive strategy briefing",
                    "description": "In-depth overview of company strategy and objectives",
                    "owner": "ceo",
                    "deadline_days": 3,
                    "status": "pending",
                    "completed_at": None
                },
                {
                    "task_id": f"task_{i+6}",
                    "category": "stakeholder_meetings",
                    "title": "Key stakeholder meetings",
                    "description": "Introduction to board members and key partners",
                    "owner": "ceo",
                    "deadline_days": 7,
                    "status": "pending",
                    "completed_at": None
                }
            ]
        else:  # standard
            additional_tasks = [
                {
                    "task_id": f"task_{i+5}",
                    "category": "project_assignment",
                    "title": "First project assignment",
                    "description": "Assignment of initial tasks and projects",
                    "owner": "manager",
                    "deadline_days": 5,
                    "status": "pending",
                    "completed_at": None
                }
            ]
        
        # Combine common and additional tasks
        return common_tasks + additional_tasks
    
    def set_start_date(self, plan: Dict[str, Any], start_date: str) -> Dict[str, Any]:
        """
        Set the start date for an onboarding plan.
        
        Args:
            plan: Onboarding plan
            start_date: Start date (ISO format)
            
        Returns:
            Updated onboarding plan
        """
        logger.info(f"Setting start date for onboarding plan {plan['plan_id']}: {start_date}")
        
        # Create a copy of the plan
        updated_plan = plan.copy()
        
        # Set start date
        updated_plan["start_date"] = start_date
        
        # Calculate task deadlines
        start_date_obj = datetime.fromisoformat(start_date)
        tasks = []
        
        for task in updated_plan["tasks"]:
            task_copy = task.copy()
            deadline_days = task_copy.get("deadline_days", 1)
            task_copy["deadline"] = (start_date_obj + timedelta(days=deadline_days)).isoformat()
            tasks.append(task_copy)
        
        updated_plan["tasks"] = tasks
        
        # Update status
        updated_plan["status"] = "scheduled"
        
        logger.info(f"Start date set for onboarding plan {plan['plan_id']}")
        return updated_plan
    
    def update_task_status(self, plan: Dict[str, Any], task_id: str, status: str, comments: Optional[str] = None) -> Dict[str, Any]:
        """
        Update the status of an onboarding task.
        
        Args:
            plan: Onboarding plan
            task_id: Task identifier
            status: New task status
            comments: Optional comments
            
        Returns:
            Updated onboarding plan
        """
        logger.info(f"Updating task {task_id} status to {status} in plan {plan['plan_id']}")
        
        # Create a copy of the plan
        updated_plan = plan.copy()
        
        # Find and update the task
        for i, task in enumerate(updated_plan["tasks"]):
            if task["task_id"] == task_id:
                updated_task = task.copy()
                updated_task["status"] = status
                
                if status == "completed":
                    updated_task["completed_at"] = datetime.now().isoformat()
                
                if comments:
                    updated_task["comments"] = comments
                
                updated_plan["tasks"][i] = updated_task
                break
        
        # Update progress
        completed_tasks = sum(1 for task in updated_plan["tasks"] if task["status"] == "completed")
        total_tasks = len(updated_plan["tasks"])
        percentage = (completed_tasks / total_tasks) * 100 if total_tasks > 0 else 0
        
        updated_plan["progress"] = {
            "completed_tasks": completed_tasks,
            "total_tasks": total_tasks,
            "percentage": percentage
        }
        
        # Update overall status
        if percentage == 100:
            updated_plan["status"] = "completed"
        elif percentage > 0:
            updated_plan["status"] = "in_progress"
        
        logger.info(f"Task status updated in plan {plan['plan_id']}, progress: {percentage:.1f}%")
        return updated_plan
    
    def generate_onboarding_report(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate a report on onboarding progress.
        
        Args:
            plan: Onboarding plan
            
        Returns:
            Onboarding report
        """
        logger.info(f"Generating onboarding report for plan {plan['plan_id']}")
        
        # Calculate days since start
        days_since_start = None
        if plan.get("start_date"):
            start_date = datetime.fromisoformat(plan["start_date"])
            now = datetime.now()
            days_since_start = (now - start_date).days
        
        # Group tasks by category
        tasks_by_category = {}
        for task in plan["tasks"]:
            category = task.get("category", "other")
            if category not in tasks_by_category:
                tasks_by_category[category] = []
            tasks_by_category[category].append(task)
        
        # Calculate category completion
        category_completion = {}
        for category, tasks in tasks_by_category.items():
            completed = sum(1 for task in tasks if task["status"] == "completed")
            total = len(tasks)
            percentage = (completed / total) * 100 if total > 0 else 0
            category_completion[category] = {
                "completed": completed,
                "total": total,
                "percentage": percentage
            }
        
        # Identify bottlenecks
        bottlenecks = []
        if plan["status"] != "completed":
            for category, stats in category_completion.items():
                if stats["percentage"] < 50 and days_since_start and days_since_start > 5:
                    bottlenecks.append({
                        "category": category,
                        "completion": stats["percentage"],
                        "pending_tasks": [
                            task["title"] for task in tasks_by_category[category]
                            if task["status"] != "completed"
                        ]
                    })
        
        # Generate report
        report = {
            "plan_id": plan["plan_id"],
            "candidate_id": plan["candidate_id"],
            "job_id": plan["job_id"],
            "generated_at": datetime.now().isoformat(),
            "days_since_start": days_since_start,
            "overall_progress": plan["progress"],
            "category_completion": category_completion,
            "bottlenecks": bottlenecks,
            "status": plan["status"],
            "recommendations": self._generate_recommendations(plan, bottlenecks)
        }
        
        logger.info(f"Onboarding report generated for plan {plan['plan_id']}")
        return report
    
    def _generate_recommendations(self, plan: Dict[str, Any], bottlenecks: List[Dict[str, Any]]) -> List[str]:
        """
        Generate recommendations based on onboarding progress.
        
        Args:
            plan: Onboarding plan
            bottlenecks: Identified bottlenecks
            
        Returns:
            List of recommendations
        """
        recommendations = []
        
        # Check overall progress
        progress = plan["progress"]["percentage"]
        days_since_start = None
        if plan.get("start_date"):
            start_date = datetime.fromisoformat(plan["start_date"])
            now = datetime.now()
            days_since_start = (now - start_date).days
        
        if plan["status"] == "completed":
            recommendations.append("Onboarding completed successfully. Schedule 30-day check-in.")
        elif progress == 0 and plan["status"] == "scheduled":
            recommendations.append("Onboarding hasn't started yet. Ensure all preparations are complete.")
        elif progress < 30 and days_since_start and days_since_start > 3:
            recommendations.append("Onboarding progress is slower than expected. Schedule a check-in meeting.")
        elif progress > 80:
            recommendations.append("Onboarding nearly complete. Prepare for transition to regular work.")
        
        # Add recommendations for bottlenecks
        for bottleneck in bottlenecks:
            category = bottleneck["category"].replace("_", " ").title()
            recommendations.append(f"Address delays in {category} tasks.")
        
        # Add general recommendations
        if days_since_start and days_since_start == 1:
            recommendations.append("Schedule a first-day check-in to address any immediate concerns.")
        elif days_since_start and days_since_start == 5:
            recommendations.append("Conduct a first-week review to gather feedback on the onboarding process.")
        
        return recommendations


class HiringWorkflowManager:
    """Manages the end-to-end hiring workflow, integrating all components."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """
        Initialize the hiring workflow manager.
        
        Args:
            config: Configuration settings
        """
        self.config = config or {}
        
        # Initialize component systems
        self.decision_system = DecisionSupportSystem(config.get("decision_support", {}))
        self.offer_system = OfferManagementSystem(config.get("offer_management", {}))
        self.onboarding_system = OnboardingSystem(config.get("onboarding", {}))
        
        logger.info("Hiring workflow manager initialized")
    
    def process_candidate_evaluation(self, candidate_id: str, job_id: str, assessments: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process candidate evaluation and generate hiring recommendation.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            assessments: All assessment data for the candidate
            
        Returns:
            Hiring recommendation
        """
        logger.info(f"Processing evaluation for candidate {candidate_id} and job {job_id}")
        
        # Generate hiring recommendation
        recommendation = self.decision_system.generate_hiring_recommendation(
            candidate_id, job_id, assessments
        )
        
        # Determine next steps based on recommendation
        workflow_status = self._determine_workflow_status(recommendation)
        
        # Combine recommendation with workflow status
        result = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "timestamp": datetime.now().isoformat(),
            "recommendation": recommendation,
            "workflow_status": workflow_status
        }
        
        logger.info(f"Evaluation processed for candidate {candidate_id}, recommendation: {recommendation['recommendation']}")
        return result
    
    def compare_candidates(self, job_id: str, candidate_recommendations: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Compare multiple candidates for the same job.
        
        Args:
            job_id: Job identifier
            candidate_recommendations: List of candidate recommendations
            
        Returns:
            Candidate comparison
        """
        logger.info(f"Comparing {len(candidate_recommendations)} candidates for job {job_id}")
        
        # Use decision support system to compare candidates
        comparison = self.decision_system.compare_candidates(job_id, candidate_recommendations)
        
        # Add workflow next steps
        comparison["workflow_next_steps"] = self._generate_workflow_next_steps(comparison)
        
        logger.info(f"Candidate comparison completed for job {job_id}")
        return comparison
    
    def initiate_offer_process(self, candidate_id: str, job_id: str, offer_details: Dict[str, Any]) -> Dict[str, Any]:
        """
        Initiate the offer process for a candidate.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            offer_details: Offer details
            
        Returns:
            Created offer
        """
        logger.info(f"Initiating offer process for candidate {candidate_id} and job {job_id}")
        
        # Create offer
        offer = self.offer_system.create_offer(candidate_id, job_id, offer_details)
        
        # Get offer status
        status = self.offer_system.get_offer_status(offer)
        
        # Combine offer with status
        result = {
            "offer": offer,
            "status": status,
            "next_steps": ["Submit for approval"]
        }
        
        logger.info(f"Offer process initiated for candidate {candidate_id}, offer ID: {offer['offer_id']}")
        return result
    
    def process_offer_approval(self, offer: Dict[str, Any], approver: str, approved: bool, comments: Optional[str] = None) -> Dict[str, Any]:
        """
        Process an approval for an offer.
        
        Args:
            offer: Offer to approve
            approver: Approver identifier
            approved: Whether the offer is approved
            comments: Optional approval comments
            
        Returns:
            Updated offer with status
        """
        logger.info(f"Processing {approver} approval for offer {offer['offer_id']}")
        
        # Process approval
        updated_offer = self.offer_system.process_approval(offer, approver, approved, comments)
        
        # Get offer status
        status = self.offer_system.get_offer_status(updated_offer)
        
        # Determine next steps
        next_steps = []
        if updated_offer["status"] == "approved":
            next_steps.append("Generate offer document")
            next_steps.append("Send offer to candidate")
        elif updated_offer["status"] == "rejected":
            next_steps.append("Review rejection reasons")
            next_steps.append("Revise offer or select alternative candidate")
        elif updated_offer["status"] == "pending_approval":
            next_steps.append(f"Awaiting approval from: {', '.join(status['pending_approvers'])}")
        
        # Combine offer with status and next steps
        result = {
            "offer": updated_offer,
            "status": status,
            "next_steps": next_steps
        }
        
        logger.info(f"Offer approval processed, new status: {updated_offer['status']}")
        return result
    
    def finalize_offer(self, offer: Dict[str, Any]) -> Dict[str, Any]:
        """
        Finalize an approved offer and generate document.
        
        Args:
            offer: Approved offer
            
        Returns:
            Finalized offer with document
        """
        logger.info(f"Finalizing offer {offer['offer_id']}")
        
        # Check if offer is approved
        if offer["status"] != "approved":
            logger.warning(f"Attempting to finalize unapproved offer {offer['offer_id']}")
            return {
                "success": False,
                "error": "Cannot finalize unapproved offer",
                "offer_id": offer["offer_id"]
            }
        
        # Generate offer document
        document = self.offer_system.generate_offer_document(offer)
        
        # Get offer status
        status = self.offer_system.get_offer_status(offer)
        
        # Determine next steps
        next_steps = ["Send offer to candidate", "Track candidate response"]
        
        # Combine offer with document, status, and next steps
        result = {
            "offer": offer,
            "document": document,
            "status": status,
            "next_steps": next_steps
        }
        
        logger.info(f"Offer {offer['offer_id']} finalized")
        return result
    
    def process_offer_response(self, offer: Dict[str, Any], accepted: bool, response_details: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """
        Process candidate's response to the offer.
        
        Args:
            offer: Offer data
            accepted: Whether the offer was accepted
            response_details: Optional response details
            
        Returns:
            Updated offer with next steps
        """
        logger.info(f"Processing candidate response for offer {offer['offer_id']}: {'accepted' if accepted else 'declined'}")
        
        # Record response
        updated_offer = self.offer_system.record_candidate_response(offer, accepted, response_details)
        
        # Determine next steps
        next_steps = []
        if accepted:
            next_steps.append("Initiate onboarding process")
            next_steps.append("Close recruitment for this position")
        else:
            next_steps.append("Review decline reasons")
            next_steps.append("Consider alternative candidates")
        
        # Combine offer with next steps
        result = {
            "offer": updated_offer,
            "next_steps": next_steps
        }
        
        logger.info(f"Offer response processed, status: {updated_offer['status']}")
        return result
    
    def initiate_onboarding(self, candidate_id: str, job_id: str, offer_id: str, plan_type: str = "standard") -> Dict[str, Any]:
        """
        Initiate the onboarding process for a new hire.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            offer_id: Offer identifier
            plan_type: Type of onboarding plan
            
        Returns:
            Created onboarding plan
        """
        logger.info(f"Initiating {plan_type} onboarding for candidate {candidate_id}")
        
        # Create onboarding plan
        plan = self.onboarding_system.create_onboarding_plan(
            candidate_id, job_id, offer_id, plan_type
        )
        
        # Determine next steps
        next_steps = ["Set start date", "Assign task owners", "Prepare welcome package"]
        
        # Combine plan with next steps
        result = {
            "plan": plan,
            "next_steps": next_steps
        }
        
        logger.info(f"Onboarding initiated for candidate {candidate_id}, plan ID: {plan['plan_id']}")
        return result
    
    def schedule_onboarding(self, plan: Dict[str, Any], start_date: str) -> Dict[str, Any]:
        """
        Schedule onboarding with a start date.
        
        Args:
            plan: Onboarding plan
            start_date: Start date (ISO format)
            
        Returns:
            Updated onboarding plan
        """
        logger.info(f"Scheduling onboarding plan {plan['plan_id']} for {start_date}")
        
        # Set start date
        updated_plan = self.onboarding_system.set_start_date(plan, start_date)
        
        # Generate report
        report = self.onboarding_system.generate_onboarding_report(updated_plan)
        
        # Determine next steps
        next_steps = ["Notify task owners", "Prepare for day one", "Schedule welcome meeting"]
        
        # Combine plan with report and next steps
        result = {
            "plan": updated_plan,
            "report": report,
            "next_steps": next_steps
        }
        
        logger.info(f"Onboarding scheduled for plan {plan['plan_id']}")
        return result
    
    def track_onboarding_progress(self, plan: Dict[str, Any]) -> Dict[str, Any]:
        """
        Track onboarding progress and generate report.
        
        Args:
            plan: Onboarding plan
            
        Returns:
            Onboarding progress report
        """
        logger.info(f"Tracking onboarding progress for plan {plan['plan_id']}")
        
        # Generate report
        report = self.onboarding_system.generate_onboarding_report(plan)
        
        # Determine next steps based on progress
        next_steps = []
        if plan["status"] == "completed":
            next_steps.append("Conduct post-onboarding review")
            next_steps.append("Transition to regular performance management")
        elif plan["status"] == "in_progress":
            next_steps.append("Follow up on incomplete tasks")
            next_steps.append("Address any bottlenecks")
        elif plan["status"] == "scheduled":
            next_steps.append("Prepare for employee start date")
        
        # Add recommendations as next steps
        next_steps.extend(report.get("recommendations", []))
        
        # Combine report with next steps
        result = {
            "plan": plan,
            "report": report,
            "next_steps": next_steps
        }
        
        logger.info(f"Onboarding progress tracked for plan {plan['plan_id']}")
        return result
    
    def _determine_workflow_status(self, recommendation: Dict[str, Any]) -> Dict[str, Any]:
        """
        Determine workflow status based on hiring recommendation.
        
        Args:
            recommendation: Hiring recommendation
            
        Returns:
            Workflow status
        """
        rec = recommendation["recommendation"]
        
        if rec in ["Strong Hire", "Hire"]:
            return {
                "status": "proceed_to_offer",
                "next_steps": ["Prepare offer", "Conduct final reference checks"]
            }
        elif rec in ["Lean Hire", "Borderline"]:
            return {
                "status": "additional_evaluation",
                "next_steps": ["Schedule follow-up interview", "Review concerns with hiring manager"]
            }
        else:  # No Hire recommendations
            return {
                "status": "reject",
                "next_steps": ["Prepare rejection communication", "Document decision rationale"]
            }
    
    def _generate_workflow_next_steps(self, comparison: Dict[str, Any]) -> List[str]:
        """
        Generate workflow next steps based on candidate comparison.
        
        Args:
            comparison: Candidate comparison
            
        Returns:
            List of next steps
        """
        next_steps = []
        
        decision = comparison.get("final_recommendation", {}).get("decision", "")
        
        if decision == "Proceed with top candidate":
            next_steps.append("Prepare offer for top candidate")
            next_steps.append("Conduct final reference checks")
        elif decision == "Additional evaluation needed":
            next_steps.append("Schedule additional interviews for top candidates")
            next_steps.append("Prepare focused assessment areas")
        elif decision == "Consider top candidate with caution":
            next_steps.append("Review concerns with hiring manager")
            next_steps.append("Consider preparing contingent offer")
        elif decision == "No suitable candidates":
            next_steps.append("Reopen job requisition")
            next_steps.append("Review sourcing strategy")
        
        return next_steps


# Example usage
if __name__ == "__main__":
    # Initialize hiring workflow manager
    workflow_manager = HiringWorkflowManager()
    
    # Example candidate assessments
    assessments = {
        "resume_assessment": {
            "overall_score": 85,
            "skills_match": 0.8,
            "experience_relevance": 0.9
        },
        "technical_assessment": {
            "overall_score": 78,
            "coding_score": 0.75,
            "problem_solving": 0.8,
            "strengths": ["Strong algorithm knowledge", "Excellent database design"],
            "weaknesses": ["Limited experience with cloud services"]
        },
        "interview_assessment": {
            "overall_scores": {
                "overall": 0.82,
                "technical": 0.78,
                "communication": 0.85,
                "relevance": 0.83
            },
            "insights": [
                "Demonstrates strong technical knowledge across questions",
                "Communicates with exceptional clarity and structure"
            ]
        },
        "cultural_fit": {
            "overall_fit": 0.76,
            "strengths": [
                {"value_id": "collaboration", "value_name": "Collaboration"},
                {"value_id": "innovation", "value_name": "Innovation"}
            ],
            "gaps": [
                {"value_id": "customer_focus", "value_name": "Customer Focus"}
            ]
        },
        "references": {
            "overall_score": 4.5,
            "feedback": "Strong positive references from previous managers"
        }
    }
    
    # Process candidate evaluation
    evaluation_result = workflow_manager.process_candidate_evaluation(
        "candidate_12345", "job_54321", assessments
    )
    
    print("Hiring Recommendation:")
    print(f"Recommendation: {evaluation_result['recommendation']['recommendation']}")
    print(f"Confidence: {evaluation_result['recommendation']['confidence']:.2f}")
    print(f"Overall Score: {evaluation_result['recommendation']['overall_score']:.2f}")
    print(f"Workflow Status: {evaluation_result['workflow_status']['status']}")
    print("Next Steps:")
    for step in evaluation_result['workflow_status']['next_steps']:
        print(f"- {step}")
    
    # Example offer details
    offer_details = {
        "offer_type": "standard",
        "salary": 120000,
        "bonus": 10000,
        "equity": "1000 RSUs",
        "start_date": "2023-06-01",
        "position": "Senior Software Engineer",
        "department": "Engineering",
        "manager": "Jane Smith",
        "validity_days": 7
    }
    
    # Initiate offer process
    offer_result = workflow_manager.initiate_offer_process(
        "candidate_12345", "job_54321", offer_details
    )
    
    print("\nOffer Created:")
    print(f"Offer ID: {offer_result['offer']['offer_id']}")
    print(f"Status: {offer_result['offer']['status']}")
    print(f"Expiration: {offer_result['offer']['expiration_date']}")
    
    # Process offer approval
    approval_result = workflow_manager.process_offer_approval(
        offer_result['offer'], "hiring_manager", True, "Excellent candidate, fully approve"
    )
    
    print("\nOffer Approval:")
    print(f"Status: {approval_result['offer']['status']}")
    print(f"Pending Approvers: {', '.join(approval_result['status']['pending_approvers'])}")
    
    # Process second approval
    final_approval_result = workflow_manager.process_offer_approval(
        approval_result['offer'], "hr_manager", True, "Compensation within guidelines, approved"
    )
    
    print("\nFinal Approval:")
    print(f"Status: {final_approval_result['offer']['status']}")
    print("Next Steps:")
    for step in final_approval_result['next_steps']:
        print(f"- {step}")
    
    # Finalize offer
    finalized_offer = workflow_manager.finalize_offer(final_approval_result['offer'])
    
    print("\nFinalized Offer:")
    print(f"Document ID: {finalized_offer['document']['document_id']}")
    print(f"Document URL: {finalized_offer['document']['document_url']}")
    
    # Process offer acceptance
    acceptance_result = workflow_manager.process_offer_response(
        finalized_offer['offer'], True, {"start_date": "2023-06-01", "comments": "Excited to join the team!"}
    )
    
    print("\nOffer Acceptance:")
    print(f"Status: {acceptance_result['offer']['status']}")
    print("Next Steps:")
    for step in acceptance_result['next_steps']:
        print(f"- {step}")
    
    # Initiate onboarding
    onboarding_result = workflow_manager.initiate_onboarding(
        "candidate_12345", "job_54321", finalized_offer['offer']['offer_id']
    )
    
    print("\nOnboarding Initiated:")
    print(f"Plan ID: {onboarding_result['plan']['plan_id']}")
    print(f"Plan Type: {onboarding_result['plan']['plan_type']}")
    print(f"Tasks: {onboarding_result['plan']['progress']['total_tasks']}")
    
    # Schedule onboarding
    scheduled_onboarding = workflow_manager.schedule_onboarding(
        onboarding_result['plan'], "2023-06-01"
    )
    
    print("\nOnboarding Scheduled:")
    print(f"Start Date: {scheduled_onboarding['plan']['start_date']}")
    print(f"Status: {scheduled_onboarding['plan']['status']}")
    print("Recommendations:")
    for rec in scheduled_onboarding['report']['recommendations']:
        print(f"- {rec}")
    
    # Update task status (simulate progress)
    updated_plan = scheduled_onboarding['plan']
    for i, task in enumerate(updated_plan['tasks']):
        if i < 3:  # Complete first 3 tasks
            updated_plan = workflow_manager.onboarding_system.update_task_status(
                updated_plan, task['task_id'], "completed", "Completed successfully"
            )
    
    # Track onboarding progress
    progress_result = workflow_manager.track_onboarding_progress(updated_plan)
    
    print("\nOnboarding Progress:")
    print(f"Completed: {progress_result['report']['overall_progress']['completed_tasks']} of {progress_result['report']['overall_progress']['total_tasks']}")
    print(f"Percentage: {progress_result['report']['overall_progress']['percentage']:.1f}%")
    print("Next Steps:")
    for step in progress_result['next_steps'][:3]:
        print(f"- {step}")
