"""
Scheduling Engine for Automated Interview Scheduling System

This module implements the core scheduling algorithms for finding optimal interview times
based on various constraints and preferences.
"""

import logging
import json
import os
from typing import Dict, List, Any, Optional, Tuple, Set
from datetime import datetime, timedelta
import pytz
from dateutil import parser as date_parser
import heapq
import random

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class SchedulingConstraint:
    """Base class for scheduling constraints."""
    
    def __init__(self, weight: float = 1.0):
        """
        Initialize the constraint.
        
        Args:
            weight: Weight of this constraint in the overall score (0.0-1.0)
        """
        self.weight = weight
    
    def evaluate(self, slot: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Evaluate a time slot against this constraint.
        
        Args:
            slot: Time slot to evaluate
            context: Additional context for evaluation
            
        Returns:
            Score between 0.0 (constraint violated) and 1.0 (constraint satisfied)
        """
        raise NotImplementedError("Subclasses must implement evaluate")


class BusinessHoursConstraint(SchedulingConstraint):
    """Constraint for scheduling within business hours."""
    
    def __init__(self, 
                start_hour: int = 9, 
                end_hour: int = 17, 
                business_days: Set[int] = {0, 1, 2, 3, 4},  # Monday=0, Sunday=6
                weight: float = 1.0):
        """
        Initialize the business hours constraint.
        
        Args:
            start_hour: Start of business hours (24-hour format)
            end_hour: End of business hours (24-hour format)
            business_days: Set of business days (0=Monday, 6=Sunday)
            weight: Weight of this constraint in the overall score
        """
        super().__init__(weight)
        self.start_hour = start_hour
        self.end_hour = end_hour
        self.business_days = business_days
    
    def evaluate(self, slot: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Evaluate if a time slot is within business hours.
        
        Args:
            slot: Time slot to evaluate
            context: Additional context for evaluation
            
        Returns:
            1.0 if within business hours, 0.0 otherwise
        """
        timezone = context.get('timezone', 'UTC')
        
        # Parse start time
        start_time = date_parser.parse(slot['start_time'])
        start_time = start_time.astimezone(pytz.timezone(timezone))
        
        # Check day of week
        day_of_week = start_time.weekday()  # Monday=0, Sunday=6
        if day_of_week not in self.business_days:
            return 0.0
        
        # Check hour
        hour = start_time.hour
        if hour < self.start_hour or hour >= self.end_hour:
            return 0.0
        
        return 1.0


class TimePreferenceConstraint(SchedulingConstraint):
    """Constraint for preferred time of day."""
    
    def __init__(self, 
                preference: str = 'any',  # 'morning', 'afternoon', 'any'
                weight: float = 0.5):
        """
        Initialize the time preference constraint.
        
        Args:
            preference: Preferred time of day ('morning', 'afternoon', 'any')
            weight: Weight of this constraint in the overall score
        """
        super().__init__(weight)
        self.preference = preference.lower()
    
    def evaluate(self, slot: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Evaluate if a time slot matches the preferred time of day.
        
        Args:
            slot: Time slot to evaluate
            context: Additional context for evaluation
            
        Returns:
            Score between 0.0 and 1.0 based on preference match
        """
        if self.preference == 'any':
            return 1.0
        
        timezone = context.get('timezone', 'UTC')
        
        # Parse start time
        start_time = date_parser.parse(slot['start_time'])
        start_time = start_time.astimezone(pytz.timezone(timezone))
        
        hour = start_time.hour
        
        if self.preference == 'morning' and 9 <= hour < 12:
            return 1.0
        elif self.preference == 'afternoon' and 12 <= hour < 17:
            return 1.0
        elif self.preference == 'evening' and 17 <= hour < 20:
            return 1.0
        
        # Partial scores for close matches
        if self.preference == 'morning' and 8 <= hour < 9:
            return 0.8
        elif self.preference == 'morning' and 12 <= hour < 13:
            return 0.6
        elif self.preference == 'afternoon' and 11 <= hour < 12:
            return 0.8
        elif self.preference == 'afternoon' and 17 <= hour < 18:
            return 0.6
        elif self.preference == 'evening' and 16 <= hour < 17:
            return 0.8
        elif self.preference == 'evening' and 20 <= hour < 21:
            return 0.6
        
        return 0.3  # Low score for non-matching times


class DayAvoidanceConstraint(SchedulingConstraint):
    """Constraint for avoiding specific days."""
    
    def __init__(self, 
                days_to_avoid: Set[int] = set(),  # Monday=0, Sunday=6
                weight: float = 0.7):
        """
        Initialize the day avoidance constraint.
        
        Args:
            days_to_avoid: Set of days to avoid (0=Monday, 6=Sunday)
            weight: Weight of this constraint in the overall score
        """
        super().__init__(weight)
        self.days_to_avoid = days_to_avoid
    
    def evaluate(self, slot: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Evaluate if a time slot avoids specified days.
        
        Args:
            slot: Time slot to evaluate
            context: Additional context for evaluation
            
        Returns:
            1.0 if day is not avoided, 0.0 otherwise
        """
        timezone = context.get('timezone', 'UTC')
        
        # Parse start time
        start_time = date_parser.parse(slot['start_time'])
        start_time = start_time.astimezone(pytz.timezone(timezone))
        
        # Check day of week
        day_of_week = start_time.weekday()  # Monday=0, Sunday=6
        if day_of_week in self.days_to_avoid:
            return 0.0
        
        return 1.0


class DateRangeConstraint(SchedulingConstraint):
    """Constraint for preferred date range."""
    
    def __init__(self, 
                earliest_date: Optional[datetime] = None,
                latest_date: Optional[datetime] = None,
                preferred_start_date: Optional[datetime] = None,
                preferred_end_date: Optional[datetime] = None,
                weight: float = 0.8):
        """
        Initialize the date range constraint.
        
        Args:
            earliest_date: Earliest acceptable date
            latest_date: Latest acceptable date
            preferred_start_date: Start of preferred date range
            preferred_end_date: End of preferred date range
            weight: Weight of this constraint in the overall score
        """
        super().__init__(weight)
        self.earliest_date = earliest_date
        self.latest_date = latest_date
        self.preferred_start_date = preferred_start_date
        self.preferred_end_date = preferred_end_date
    
    def evaluate(self, slot: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Evaluate if a time slot is within the preferred date range.
        
        Args:
            slot: Time slot to evaluate
            context: Additional context for evaluation
            
        Returns:
            Score between 0.0 and 1.0 based on date range match
        """
        timezone = context.get('timezone', 'UTC')
        
        # Parse start time
        start_time = date_parser.parse(slot['start_time'])
        start_time = start_time.astimezone(pytz.timezone(timezone))
        
        # Check hard constraints
        if self.earliest_date and start_time < self.earliest_date:
            return 0.0
        
        if self.latest_date and start_time > self.latest_date:
            return 0.0
        
        # Check preferred range
        if self.preferred_start_date and self.preferred_end_date:
            if self.preferred_start_date <= start_time <= self.preferred_end_date:
                return 1.0
            
            # Calculate distance from preferred range
            if start_time < self.preferred_start_date:
                days_diff = (self.preferred_start_date - start_time).days
                return max(0.5, 1.0 - (days_diff * 0.1))
            
            if start_time > self.preferred_end_date:
                days_diff = (start_time - self.preferred_end_date).days
                return max(0.5, 1.0 - (days_diff * 0.1))
        
        return 1.0


class MinimumNoticeConstraint(SchedulingConstraint):
    """Constraint for minimum notice period."""
    
    def __init__(self, 
                minimum_hours: int = 24,
                weight: float = 0.9):
        """
        Initialize the minimum notice constraint.
        
        Args:
            minimum_hours: Minimum notice period in hours
            weight: Weight of this constraint in the overall score
        """
        super().__init__(weight)
        self.minimum_hours = minimum_hours
    
    def evaluate(self, slot: Dict[str, Any], context: Dict[str, Any]) -> float:
        """
        Evaluate if a time slot provides minimum notice.
        
        Args:
            slot: Time slot to evaluate
            context: Additional context for evaluation
            
        Returns:
            1.0 if minimum notice is provided, 0.0 otherwise
        """
        # Parse start time
        start_time = date_parser.parse(slot['start_time'])
        
        # Calculate notice period
        now = datetime.now(start_time.tzinfo)
        notice_hours = (start_time - now).total_seconds() / 3600
        
        if notice_hours < self.minimum_hours:
            return 0.0
        
        return 1.0


class ConstraintBasedScheduler:
    """
    Constraint-based scheduler for finding optimal interview times.
    """
    
    def __init__(self, calendar_service):
        """
        Initialize the constraint-based scheduler.
        
        Args:
            calendar_service: Calendar service for availability data
        """
        self.calendar_service = calendar_service
        self.default_constraints = self._create_default_constraints()
        
        logger.info("Constraint-based scheduler initialized")
    
    def _create_default_constraints(self) -> List[SchedulingConstraint]:
        """
        Create default scheduling constraints.
        
        Returns:
            List of default constraints
        """
        return [
            BusinessHoursConstraint(weight=1.0),
            MinimumNoticeConstraint(weight=0.9)
        ]
    
    def find_available_slots(self,
                           participants: List[str],
                           duration_minutes: int,
                           date_range: Tuple[datetime, datetime],
                           constraints: Optional[List[SchedulingConstraint]] = None,
                           preferences: Optional[Dict[str, Any]] = None,
                           timezone: str = "UTC",
                           max_slots: int = 10) -> List[Dict[str, Any]]:
        """
        Find available time slots based on constraints and preferences.
        
        Args:
            participants: List of participant identifiers
            duration_minutes: Duration of the interview in minutes
            date_range: Tuple of (start_date, end_date)
            constraints: List of scheduling constraints
            preferences: Dictionary of scheduling preferences
            timezone: Timezone for scheduling
            max_slots: Maximum number of slots to return
            
        Returns:
            List of available time slots ranked by score
        """
        logger.info(f"Finding available slots for {len(participants)} participants")
        
        # Get common availability
        start_date, end_date = date_range
        common_slots = self.calendar_service.get_common_availability(
            user_ids=participants,
            start_time=start_date,
            end_time=end_date,
            duration_minutes=duration_minutes,
            timezone=timezone
        )
        
        if not common_slots:
            logger.warning("No common availability found")
            return []
        
        # Apply constraints
        all_constraints = self._prepare_constraints(constraints, preferences)
        
        # Create context for constraint evaluation
        context = {
            'timezone': timezone,
            'duration_minutes': duration_minutes,
            'participants': participants,
            'preferences': preferences or {}
        }
        
        # Score and rank slots
        scored_slots = self._score_slots(common_slots, all_constraints, context)
        
        # Sort by score (descending) and limit results
        ranked_slots = sorted(scored_slots, key=lambda x: x['score'], reverse=True)[:max_slots]
        
        logger.info(f"Found {len(ranked_slots)} ranked slots")
        return ranked_slots
    
    def _prepare_constraints(self,
                           constraints: Optional[List[SchedulingConstraint]],
                           preferences: Optional[Dict[str, Any]]) -> List[SchedulingConstraint]:
        """
        Prepare constraints based on provided constraints and preferences.
        
        Args:
            constraints: List of explicit constraints
            preferences: Dictionary of scheduling preferences
            
        Returns:
            List of all applicable constraints
        """
        # Start with default constraints
        all_constraints = list(self.default_constraints)
        
        # Add explicit constraints
        if constraints:
            all_constraints.extend(constraints)
        
        # Add constraints from preferences
        if preferences:
            # Time of day preference
            if 'preferred_time_of_day' in preferences:
                all_constraints.append(
                    TimePreferenceConstraint(
                        preference=preferences['preferred_time_of_day'],
                        weight=0.7
                    )
                )
            
            # Day avoidance
            days_to_avoid = set()
            if preferences.get('avoid_mondays', False):
                days_to_avoid.add(0)  # Monday
            if preferences.get('avoid_fridays', False):
                days_to_avoid.add(4)  # Friday
            if preferences.get('avoid_weekends', False):
                days_to_avoid.add(5)  # Saturday
                days_to_avoid.add(6)  # Sunday
            
            if days_to_avoid:
                all_constraints.append(
                    DayAvoidanceConstraint(
                        days_to_avoid=days_to_avoid,
                        weight=0.8
                    )
                )
            
            # Preferred date range
            if 'preferred_start_date' in preferences and 'preferred_end_date' in preferences:
                preferred_start = preferences['preferred_start_date']
                preferred_end = preferences['preferred_end_date']
                
                # Convert to datetime if strings
                if isinstance(preferred_start, str):
                    preferred_start = date_parser.parse(preferred_start)
                if isinstance(preferred_end, str):
                    preferred_end = date_parser.parse(preferred_end)
                
                all_constraints.append(
                    DateRangeConstraint(
                        preferred_start_date=preferred_start,
                        preferred_end_date=preferred_end,
                        weight=0.6
                    )
                )
        
        return all_constraints
    
    def _score_slots(self,
                   slots: List[Dict[str, Any]],
                   constraints: List[SchedulingConstraint],
                   context: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Score time slots based on constraints.
        
        Args:
            slots: List of time slots
            constraints: List of constraints to apply
            context: Context for constraint evaluation
            
        Returns:
            List of slots with scores
        """
        scored_slots = []
        
        for slot in slots:
            # Calculate weighted score
            total_weight = sum(constraint.weight for constraint in constraints)
            weighted_score = 0
            
            constraint_scores = {}
            
            for constraint in constraints:
                score = constraint.evaluate(slot, context)
                weighted_score += score * constraint.weight
                
                # Store individual constraint scores for debugging
                constraint_name = constraint.__class__.__name__
                constraint_scores[constraint_name] = score
            
            # Normalize score
            if total_weight > 0:
                normalized_score = weighted_score / total_weight
            else:
                normalized_score = 1.0
            
            # Add score to slot
            scored_slot = slot.copy()
            scored_slot['score'] = normalized_score
            scored_slot['constraint_scores'] = constraint_scores
            
            scored_slots.append(scored_slot)
        
        return scored_slots


class InterviewScheduler:
    """
    Interview scheduler for managing the interview scheduling process.
    """
    
    def __init__(self, calendar_service, communication_service=None):
        """
        Initialize the interview scheduler.
        
        Args:
            calendar_service: Calendar service for availability and event management
            communication_service: Communication service for notifications
        """
        self.calendar_service = calendar_service
        self.communication_service = communication_service
        self.scheduler = ConstraintBasedScheduler(calendar_service)
        
        logger.info("Interview scheduler initialized")
    
    def find_available_slots(self,
                           job_id: str,
                           candidate_id: str,
                           interviewer_ids: List[str],
                           duration_minutes: int,
                           date_range: Tuple[datetime, datetime],
                           preferences: Optional[Dict[str, Any]] = None,
                           timezone: str = "UTC",
                           max_slots: int = 10) -> List[Dict[str, Any]]:
        """
        Find available interview slots.
        
        Args:
            job_id: Job identifier
            candidate_id: Candidate identifier
            interviewer_ids: List of interviewer identifiers
            duration_minutes: Duration of the interview in minutes
            date_range: Tuple of (start_date, end_date)
            preferences: Dictionary of scheduling preferences
            timezone: Timezone for scheduling
            max_slots: Maximum number of slots to return
            
        Returns:
            List of available interview slots
        """
        logger.info(f"Finding available slots for job {job_id}, candidate {candidate_id}")
        
        # Combine all participants
        participants = interviewer_ids.copy()
        if candidate_id:
            participants.append(candidate_id)
        
        # Find available slots
        available_slots = self.scheduler.find_available_slots(
            participants=participants,
            duration_minutes=duration_minutes,
            date_range=date_range,
            preferences=preferences,
            timezone=timezone,
            max_slots=max_slots
        )
        
        # Enrich slots with additional information
        enriched_slots = []
        for slot in available_slots:
            enriched_slot = slot.copy()
            enriched_slot['job_id'] = job_id
            enriched_slot['candidate_id'] = candidate_id
            enriched_slot['interviewer_ids'] = interviewer_ids
            enriched_slot['slot_id'] = self._generate_slot_id()
            
            enriched_slots.append(enriched_slot)
        
        return enriched_slots
    
    def _generate_slot_id(self) -> str:
        """
        Generate a unique slot identifier.
        
        Returns:
            Unique slot identifier
        """
        # Simple implementation - in production, use UUID or similar
        timestamp = int(datetime.now().timestamp())
        random_part = random.randint(1000, 9999)
        return f"slot_{timestamp}_{random_part}"
    
    def schedule_interview(self,
                         job_id: str,
                         candidate_id: str,
                         interviewer_ids: List[str],
                         start_time: datetime,
                         end_time: datetime,
                         location: str,
                         interview_type: str,
                         additional_info: str = "",
                         timezone: str = "UTC") -> Dict[str, Any]:
        """
        Schedule an interview.
        
        Args:
            job_id: Job identifier
            candidate_id: Candidate identifier
            interviewer_ids: List of interviewer identifiers
            start_time: Interview start time
            end_time: Interview end time
            location: Interview location
            interview_type: Type of interview
            additional_info: Additional information
            timezone: Timezone for scheduling
            
        Returns:
            Scheduled interview details
        """
        logger.info(f"Scheduling interview for job {job_id}, candidate {candidate_id}")
        
        # Create interview details
        interview_id = self._generate_interview_id()
        
        # Get participant details (in a real system, this would come from a user service)
        candidate_name = f"Candidate {candidate_id}"
        candidate_email = f"{candidate_id}@example.com"
        
        interviewer_names = [f"Interviewer {interviewer_id}" for interviewer_id in interviewer_ids]
        interviewer_emails = [f"{interviewer_id}@example.com" for interviewer_id in interviewer_ids]
        
        # Create calendar event for each participant
        events = {}
        
        # Prepare attendees
        all_attendees = interviewer_emails.copy()
        all_attendees.append(candidate_email)
        
        # Create event details
        event_details = {
            "title": f"Interview: {interview_type} for Job {job_id}",
            "location": location,
            "description": f"Interview with {candidate_name}\n\nType: {interview_type}\n\n{additional_info}",
            "start_time": start_time,
            "end_time": end_time,
            "timezone": timezone,
            "attendees": all_attendees
        }
        
        # Create event for each interviewer
        for interviewer_id in interviewer_ids:
            try:
                event = self.calendar_service.create_event(
                    user_id=interviewer_id,
                    event_details=event_details
                )
                events[interviewer_id] = event
            except Exception as e:
                logger.error(f"Error creating event for interviewer {interviewer_id}: {str(e)}")
        
        # Create event for candidate
        try:
            event = self.calendar_service.create_event(
                user_id=candidate_id,
                event_details=event_details
            )
            events[candidate_id] = event
        except Exception as e:
            logger.error(f"Error creating event for candidate {candidate_id}: {str(e)}")
        
        # Send notifications if communication service is available
        if self.communication_service:
            try:
                self.communication_service.send_interview_confirmation(
                    interview_id=interview_id,
                    job_id=job_id,
                    candidate_id=candidate_id,
                    interviewer_ids=interviewer_ids,
                    start_time=start_time,
                    end_time=end_time,
                    location=location,
                    interview_type=interview_type,
                    additional_info=additional_info
                )
            except Exception as e:
                logger.error(f"Error sending interview confirmation: {str(e)}")
        
        # Create interview record
        interview = {
            "id": interview_id,
            "job_id": job_id,
            "candidate_id": candidate_id,
            "interviewer_ids": interviewer_ids,
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "timezone": timezone,
            "location": location,
            "interview_type": interview_type,
            "additional_info": additional_info,
            "status": "scheduled",
            "created_at": datetime.now().isoformat(),
            "events": events,
            "participant_names": [candidate_name] + interviewer_names
        }
        
        logger.info(f"Interview scheduled: {interview_id}")
        return interview
    
    def _generate_interview_id(self) -> str:
        """
        Generate a unique interview identifier.
        
        Returns:
            Unique interview identifier
        """
        # Simple implementation - in production, use UUID or similar
        timestamp = int(datetime.now().timestamp())
        random_part = random.randint(1000, 9999)
        return f"interview_{timestamp}_{random_part}"
    
    def reschedule_interview(self,
                           interview_id: str,
                           start_time: datetime,
                           end_time: datetime,
                           reason: str = "") -> Dict[str, Any]:
        """
        Reschedule an interview.
        
        Args:
            interview_id: Interview identifier
            start_time: New start time
            end_time: New end time
            reason: Reason for rescheduling
            
        Returns:
            Updated interview details
        """
        logger.info(f"Rescheduling interview {interview_id}")
        
        # In a real system, this would retrieve the interview from a database
        # For this example, we'll simulate it
        interview = {
            "id": interview_id,
            "job_id": "job_12345",
            "candidate_id": "candidate_67890",
            "interviewer_ids": ["interviewer_11111", "interviewer_22222"],
            "events": {
                "candidate_67890": {"id": "event_1"},
                "interviewer_11111": {"id": "event_2"},
                "interviewer_22222": {"id": "event_3"}
            },
            "timezone": "UTC"
        }
        
        # Update calendar events
        events = {}
        
        # Update event for each participant
        for participant_id, event_data in interview["events"].items():
            try:
                event_details = {
                    "start_time": start_time,
                    "end_time": end_time,
                    "description": f"RESCHEDULED: {reason}"
                }
                
                updated_event = self.calendar_service.update_event(
                    user_id=participant_id,
                    event_id=event_data["id"],
                    event_details=event_details
                )
                
                events[participant_id] = updated_event
            except Exception as e:
                logger.error(f"Error updating event for participant {participant_id}: {str(e)}")
        
        # Send notifications if communication service is available
        if self.communication_service:
            try:
                self.communication_service.send_reschedule_notification(
                    interview_id=interview_id,
                    start_time=start_time,
                    end_time=end_time,
                    reason=reason
                )
            except Exception as e:
                logger.error(f"Error sending reschedule notification: {str(e)}")
        
        # Update interview record
        updated_interview = interview.copy()
        updated_interview.update({
            "start_time": start_time.isoformat(),
            "end_time": end_time.isoformat(),
            "status": "rescheduled",
            "reschedule_reason": reason,
            "updated_at": datetime.now().isoformat(),
            "events": events
        })
        
        logger.info(f"Interview rescheduled: {interview_id}")
        return updated_interview
    
    def cancel_interview(self,
                       interview_id: str,
                       reason: str = "") -> Dict[str, Any]:
        """
        Cancel an interview.
        
        Args:
            interview_id: Interview identifier
            reason: Reason for cancellation
            
        Returns:
            Cancelled interview details
        """
        logger.info(f"Cancelling interview {interview_id}")
        
        # In a real system, this would retrieve the interview from a database
        # For this example, we'll simulate it
        interview = {
            "id": interview_id,
            "job_id": "job_12345",
            "candidate_id": "candidate_67890",
            "interviewer_ids": ["interviewer_11111", "interviewer_22222"],
            "events": {
                "candidate_67890": {"id": "event_1"},
                "interviewer_11111": {"id": "event_2"},
                "interviewer_22222": {"id": "event_3"}
            }
        }
        
        # Delete calendar events
        for participant_id, event_data in interview["events"].items():
            try:
                self.calendar_service.delete_event(
                    user_id=participant_id,
                    event_id=event_data["id"]
                )
            except Exception as e:
                logger.error(f"Error deleting event for participant {participant_id}: {str(e)}")
        
        # Send notifications if communication service is available
        if self.communication_service:
            try:
                self.communication_service.send_cancellation_notification(
                    interview_id=interview_id,
                    reason=reason
                )
            except Exception as e:
                logger.error(f"Error sending cancellation notification: {str(e)}")
        
        # Update interview record
        cancelled_interview = interview.copy()
        cancelled_interview.update({
            "status": "cancelled",
            "cancellation_reason": reason,
            "cancelled_at": datetime.now().isoformat()
        })
        
        logger.info(f"Interview cancelled: {interview_id}")
        return cancelled_interview


class CandidateSchedulingService:
    """
    Service for candidate self-scheduling.
    """
    
    def __init__(self, calendar_service, communication_service=None):
        """
        Initialize the candidate scheduling service.
        
        Args:
            calendar_service: Calendar service for availability and event management
            communication_service: Communication service for notifications
        """
        self.calendar_service = calendar_service
        self.communication_service = communication_service
        self.interview_scheduler = InterviewScheduler(calendar_service, communication_service)
        
        # In a real system, these would be stored in a database
        self.tokens = {}
        self.available_slots = {}
        
        logger.info("Candidate scheduling service initialized")
    
    def generate_scheduling_token(self,
                                candidate_id: str,
                                job_id: str,
                                expiration: datetime) -> str:
        """
        Generate a scheduling token for a candidate.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            expiration: Token expiration date
            
        Returns:
            Scheduling token
        """
        logger.info(f"Generating scheduling token for candidate {candidate_id}, job {job_id}")
        
        # Generate token
        token = self._generate_token()
        
        # Store token data
        self.tokens[token] = {
            "candidate_id": candidate_id,
            "job_id": job_id,
            "expiration": expiration.isoformat(),
            "created_at": datetime.now().isoformat()
        }
        
        return token
    
    def _generate_token(self) -> str:
        """
        Generate a unique token.
        
        Returns:
            Unique token
        """
        # Simple implementation - in production, use UUID or similar
        timestamp = int(datetime.now().timestamp())
        random_part = random.randint(100000, 999999)
        return f"token_{timestamp}_{random_part}"
    
    def validate_token(self, token: str) -> Dict[str, Any]:
        """
        Validate a scheduling token.
        
        Args:
            token: Scheduling token
            
        Returns:
            Token data if valid, raises ValueError otherwise
        """
        # Check if token exists
        if token not in self.tokens:
            raise ValueError("Invalid token")
        
        # Get token data
        token_data = self.tokens[token]
        
        # Check expiration
        expiration = date_parser.parse(token_data["expiration"])
        if datetime.now(expiration.tzinfo) > expiration:
            raise ValueError("Token expired")
        
        return token_data
    
    def get_available_slots(self, token: str) -> List[Dict[str, Any]]:
        """
        Get available slots for a candidate.
        
        Args:
            token: Scheduling token
            
        Returns:
            List of available slots
        """
        logger.info(f"Getting available slots for token {token}")
        
        # Validate token
        token_data = self.validate_token(token)
        
        # Get job and candidate data
        job_id = token_data["job_id"]
        candidate_id = token_data["candidate_id"]
        
        # In a real system, this would retrieve job and interviewer data from a database
        # For this example, we'll simulate it
        interviewer_ids = ["interviewer_11111", "interviewer_22222"]
        duration_minutes = 60
        start_date = datetime.now() + timedelta(days=1)
        end_date = datetime.now() + timedelta(days=10)
        timezone = "UTC"
        
        # Find available slots
        available_slots = self.interview_scheduler.find_available_slots(
            job_id=job_id,
            candidate_id=candidate_id,
            interviewer_ids=interviewer_ids,
            duration_minutes=duration_minutes,
            date_range=(start_date, end_date),
            timezone=timezone
        )
        
        # Store available slots for this token
        self.available_slots[token] = available_slots
        
        return available_slots
    
    def confirm_slot(self, token: str, slot_id: str) -> Dict[str, Any]:
        """
        Confirm a slot selection.
        
        Args:
            token: Scheduling token
            slot_id: Selected slot identifier
            
        Returns:
            Scheduled interview details
        """
        logger.info(f"Confirming slot {slot_id} for token {token}")
        
        # Validate token
        token_data = self.validate_token(token)
        
        # Get job and candidate data
        job_id = token_data["job_id"]
        candidate_id = token_data["candidate_id"]
        
        # Check if slots are available for this token
        if token not in self.available_slots:
            raise ValueError("No available slots for this token")
        
        # Find selected slot
        selected_slot = None
        for slot in self.available_slots[token]:
            if slot["slot_id"] == slot_id:
                selected_slot = slot
                break
        
        if not selected_slot:
            raise ValueError("Invalid slot ID")
        
        # Parse times
        start_time = date_parser.parse(selected_slot["start_time"])
        end_time = date_parser.parse(selected_slot["end_time"])
        
        # In a real system, this would retrieve additional data from a database
        # For this example, we'll simulate it
        interviewer_ids = selected_slot["interviewer_ids"]
        location = "Conference Room A"
        interview_type = "Technical Interview"
        additional_info = "Please prepare to discuss your experience with Python and React."
        timezone = "UTC"
        
        # Schedule the interview
        interview = self.interview_scheduler.schedule_interview(
            job_id=job_id,
            candidate_id=candidate_id,
            interviewer_ids=interviewer_ids,
            start_time=start_time,
            end_time=end_time,
            location=location,
            interview_type=interview_type,
            additional_info=additional_info,
            timezone=timezone
        )
        
        # Clean up
        del self.available_slots[token]
        del self.tokens[token]
        
        return interview


# Example usage
if __name__ == "__main__":
    # This would be replaced with actual calendar service in production
    class MockCalendarService:
        def get_common_availability(self, user_ids, start_time, end_time, duration_minutes, timezone):
            # Mock implementation returning sample data
            return [
                {
                    "start_time": (datetime.now() + timedelta(days=2, hours=10)).isoformat(),
                    "end_time": (datetime.now() + timedelta(days=2, hours=11)).isoformat(),
                    "duration_minutes": 60
                },
                {
                    "start_time": (datetime.now() + timedelta(days=3, hours=14)).isoformat(),
                    "end_time": (datetime.now() + timedelta(days=3, hours=15)).isoformat(),
                    "duration_minutes": 60
                }
            ]
        
        def create_event(self, user_id, event_details):
            # Mock implementation
            return {
                "id": f"event_{random.randint(1000, 9999)}",
                "title": event_details["title"],
                "start_time": event_details["start_time"].isoformat() if isinstance(event_details["start_time"], datetime) else event_details["start_time"],
                "end_time": event_details["end_time"].isoformat() if isinstance(event_details["end_time"], datetime) else event_details["end_time"]
            }
    
    # Initialize services
    calendar_service = MockCalendarService()
    scheduler = ConstraintBasedScheduler(calendar_service)
    
    # Example: Find available slots
    participants = ["user1@example.com", "user2@example.com", "candidate@example.com"]
    start_date = datetime.now() + timedelta(days=1)
    end_date = start_date + timedelta(days=7)
    
    preferences = {
        "preferred_time_of_day": "morning",
        "avoid_mondays": True,
        "preferred_start_date": start_date + timedelta(days=2),
        "preferred_end_date": start_date + timedelta(days=5)
    }
    
    available_slots = scheduler.find_available_slots(
        participants=participants,
        duration_minutes=60,
        date_range=(start_date, end_date),
        preferences=preferences,
        timezone="America/New_York"
    )
    
    print(f"Found {len(available_slots)} available slots")
    
    for i, slot in enumerate(available_slots):
        print(f"\nSlot {i+1}:")
        print(f"Start time: {slot['start_time']}")
        print(f"End time: {slot['end_time']}")
        print(f"Score: {slot['score']:.2f}")
        print("Constraint scores:")
        for constraint, score in slot['constraint_scores'].items():
            print(f"  {constraint}: {score:.2f}")
    
    # Example: Schedule an interview
    interview_scheduler = InterviewScheduler(calendar_service)
    
    if available_slots:
        selected_slot = available_slots[0]
        start_time = date_parser.parse(selected_slot["start_time"])
        end_time = date_parser.parse(selected_slot["end_time"])
        
        interview = interview_scheduler.schedule_interview(
            job_id="job_12345",
            candidate_id="candidate_67890",
            interviewer_ids=["interviewer_11111", "interviewer_22222"],
            start_time=start_time,
            end_time=end_time,
            location="Conference Room A",
            interview_type="Technical Interview",
            additional_info="Please prepare to discuss your experience with Python and React."
        )
        
        print("\nInterview scheduled:")
        print(f"ID: {interview['id']}")
        print(f"Start time: {interview['start_time']}")
        print(f"End time: {interview['end_time']}")
        print(f"Participants: {', '.join(interview['participant_names'])}")
    
    # Example: Candidate self-scheduling
    candidate_scheduling = CandidateSchedulingService(calendar_service)
    
    # Generate token
    token = candidate_scheduling.generate_scheduling_token(
        candidate_id="candidate_67890",
        job_id="job_12345",
        expiration=datetime.now() + timedelta(days=7)
    )
    
    print(f"\nGenerated scheduling token: {token}")
    
    # Get available slots
    candidate_slots = candidate_scheduling.get_available_slots(token)
    
    print(f"\nFound {len(candidate_slots)} slots for candidate")
    
    # Confirm slot
    if candidate_slots:
        interview = candidate_scheduling.confirm_slot(token, candidate_slots[0]["slot_id"])
        
        print("\nCandidate self-scheduled interview:")
        print(f"ID: {interview['id']}")
        print(f"Start time: {interview['start_time']}")
        print(f"End time: {interview['end_time']}")
        print(f"Status: {interview['status']}")
