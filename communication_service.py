"""
Communication System for Automated Interview Scheduling

This module handles all communications with candidates and interviewers,
including email templates, notification workflows, and response tracking.
"""

import logging
import os
import json
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import jinja2
import requests

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class TemplateEngine:
    """Template engine for rendering communication templates."""
    
    def __init__(self, templates_dir: Optional[str] = None):
        """
        Initialize the template engine.
        
        Args:
            templates_dir: Directory containing template files
        """
        self.templates_dir = templates_dir or os.path.join(os.getcwd(), 'templates')
        
        # Create Jinja2 environment
        self.env = jinja2.Environment(
            loader=jinja2.FileSystemLoader(self.templates_dir),
            autoescape=jinja2.select_autoescape(['html', 'xml'])
        )
        
        logger.info(f"Template engine initialized with templates directory: {self.templates_dir}")
    
    def render(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a template with the given context.
        
        Args:
            template_name: Name of the template file
            context: Dictionary of context variables
            
        Returns:
            Rendered template as string
        """
        try:
            # Add file extension if not provided
            if not template_name.endswith(('.html', '.txt')):
                template_name += '.html'
            
            template = self.env.get_template(template_name)
            return template.render(**context)
        except Exception as e:
            logger.error(f"Error rendering template {template_name}: {str(e)}")
            # Fallback to simple template
            return self._render_fallback_template(template_name, context)
    
    def _render_fallback_template(self, template_name: str, context: Dict[str, Any]) -> str:
        """
        Render a fallback template when the main template fails.
        
        Args:
            template_name: Name of the template file
            context: Dictionary of context variables
            
        Returns:
            Rendered fallback template as string
        """
        # Simple fallback template
        if 'interview_invitation' in template_name:
            return f"""
            Interview Invitation
            
            Dear {context.get('candidate_name', 'Candidate')},
            
            You have been invited to an interview for the {context.get('position', '')} position at {context.get('company', '')}.
            
            Date: {context.get('interview_date', '')}
            Time: {context.get('interview_time', '')}
            Duration: {context.get('interview_duration', '')} minutes
            
            {context.get('additional_info', '')}
            
            To schedule your interview, please visit: {context.get('scheduling_link', '')}
            
            Best regards,
            {context.get('company', 'The Recruitment Team')}
            """
        elif 'interview_confirmation' in template_name:
            return f"""
            Interview Confirmation
            
            Dear {context.get('recipient_name', 'Participant')},
            
            Your interview has been confirmed.
            
            Position: {context.get('position', '')}
            Date: {context.get('interview_date', '')}
            Time: {context.get('interview_time', '')}
            Location: {context.get('location', '')}
            
            {context.get('additional_info', '')}
            
            Best regards,
            {context.get('company', 'The Recruitment Team')}
            """
        elif 'interview_reminder' in template_name:
            return f"""
            Interview Reminder
            
            Dear {context.get('recipient_name', 'Participant')},
            
            This is a reminder about your upcoming interview.
            
            Position: {context.get('position', '')}
            Date: {context.get('interview_date', '')}
            Time: {context.get('interview_time', '')}
            Location: {context.get('location', '')}
            
            {context.get('additional_info', '')}
            
            Best regards,
            {context.get('company', 'The Recruitment Team')}
            """
        elif 'interview_reschedule' in template_name:
            return f"""
            Interview Rescheduled
            
            Dear {context.get('recipient_name', 'Participant')},
            
            Your interview has been rescheduled.
            
            Position: {context.get('position', '')}
            New Date: {context.get('interview_date', '')}
            New Time: {context.get('interview_time', '')}
            Location: {context.get('location', '')}
            
            Reason: {context.get('reason', '')}
            
            {context.get('additional_info', '')}
            
            Best regards,
            {context.get('company', 'The Recruitment Team')}
            """
        elif 'interview_cancellation' in template_name:
            return f"""
            Interview Cancelled
            
            Dear {context.get('recipient_name', 'Participant')},
            
            Your interview has been cancelled.
            
            Position: {context.get('position', '')}
            
            Reason: {context.get('reason', '')}
            
            {context.get('additional_info', '')}
            
            Best regards,
            {context.get('company', 'The Recruitment Team')}
            """
        else:
            return f"""
            Notification
            
            Dear {context.get('recipient_name', 'User')},
            
            {context.get('message', 'This is a notification from the recruitment system.')}
            
            Best regards,
            {context.get('company', 'The Recruitment Team')}
            """


class EmailService:
    """Email service for sending email communications."""
    
    def __init__(self, 
                smtp_host: str = None, 
                smtp_port: int = None, 
                smtp_user: str = None, 
                smtp_password: str = None,
                from_email: str = None,
                from_name: str = None):
        """
        Initialize the email service.
        
        Args:
            smtp_host: SMTP server hostname
            smtp_port: SMTP server port
            smtp_user: SMTP username
            smtp_password: SMTP password
            from_email: Default sender email
            from_name: Default sender name
        """
        self.smtp_host = smtp_host or os.environ.get('SMTP_HOST', 'smtp.example.com')
        self.smtp_port = smtp_port or int(os.environ.get('SMTP_PORT', '587'))
        self.smtp_user = smtp_user or os.environ.get('SMTP_USER', 'user@example.com')
        self.smtp_password = smtp_password or os.environ.get('SMTP_PASSWORD', 'password')
        self.from_email = from_email or os.environ.get('FROM_EMAIL', 'recruitment@example.com')
        self.from_name = from_name or os.environ.get('FROM_NAME', 'Recruitment Team')
        
        logger.info(f"Email service initialized with SMTP server: {self.smtp_host}:{self.smtp_port}")
    
    def send(self, 
            to: str, 
            subject: str, 
            content: str, 
            content_type: str = 'html',
            cc: Optional[List[str]] = None,
            bcc: Optional[List[str]] = None,
            from_email: Optional[str] = None,
            from_name: Optional[str] = None) -> bool:
        """
        Send an email.
        
        Args:
            to: Recipient email address
            subject: Email subject
            content: Email content
            content_type: Content type ('html' or 'plain')
            cc: List of CC recipients
            bcc: List of BCC recipients
            from_email: Sender email (overrides default)
            from_name: Sender name (overrides default)
            
        Returns:
            True if email was sent successfully
        """
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = f"{from_name or self.from_name} <{from_email or self.from_email}>"
            msg['To'] = to
            
            if cc:
                msg['Cc'] = ', '.join(cc)
            
            # Attach content
            content_part = MIMEText(content, content_type)
            msg.attach(content_part)
            
            # Prepare recipients
            recipients = [to]
            if cc:
                recipients.extend(cc)
            if bcc:
                recipients.extend(bcc)
            
            # Send email
            with smtplib.SMTP(self.smtp_host, self.smtp_port) as server:
                server.starttls()
                server.login(self.smtp_user, self.smtp_password)
                server.sendmail(from_email or self.from_email, recipients, msg.as_string())
            
            logger.info(f"Email sent to {to}, subject: {subject}")
            return True
        
        except Exception as e:
            logger.error(f"Error sending email to {to}: {str(e)}")
            return False


class SMSService:
    """SMS service for sending text message communications."""
    
    def __init__(self, 
                api_key: str = None, 
                api_secret: str = None,
                from_number: str = None):
        """
        Initialize the SMS service.
        
        Args:
            api_key: API key for SMS provider
            api_secret: API secret for SMS provider
            from_number: Default sender phone number
        """
        self.api_key = api_key or os.environ.get('SMS_API_KEY', 'api_key')
        self.api_secret = api_secret or os.environ.get('SMS_API_SECRET', 'api_secret')
        self.from_number = from_number or os.environ.get('SMS_FROM_NUMBER', '+15551234567')
        
        logger.info("SMS service initialized")
    
    def send(self, to: str, content: str, from_number: Optional[str] = None) -> bool:
        """
        Send an SMS.
        
        Args:
            to: Recipient phone number
            content: SMS content
            from_number: Sender phone number (overrides default)
            
        Returns:
            True if SMS was sent successfully
        """
        try:
            # In a real implementation, this would use a service like Twilio
            # For this example, we'll simulate it
            logger.info(f"SMS sent to {to}: {content[:30]}...")
            return True
        
        except Exception as e:
            logger.error(f"Error sending SMS to {to}: {str(e)}")
            return False


class CommunicationService:
    """
    Communication service for managing all communications with candidates and interviewers.
    """
    
    def __init__(self, 
                email_service: Optional[EmailService] = None,
                sms_service: Optional[SMSService] = None,
                template_engine: Optional[TemplateEngine] = None):
        """
        Initialize the communication service.
        
        Args:
            email_service: Email service
            sms_service: SMS service
            template_engine: Template engine
        """
        self.email_service = email_service or EmailService()
        self.sms_service = sms_service or SMSService()
        self.template_engine = template_engine or TemplateEngine()
        
        # In a real system, these would be stored in a database
        self.communication_history = []
        
        logger.info("Communication service initialized")
    
    def send_scheduling_invitation(self, 
                                 candidate_id: str,
                                 job_id: str,
                                 scheduling_link: str,
                                 communication_preferences: Optional[Dict[str, Any]] = None) -> bool:
        """
        Send a scheduling invitation to a candidate.
        
        Args:
            candidate_id: Candidate identifier
            job_id: Job identifier
            scheduling_link: Link for self-scheduling
            communication_preferences: Communication preferences
            
        Returns:
            True if invitation was sent successfully
        """
        logger.info(f"Sending scheduling invitation to candidate {candidate_id} for job {job_id}")
        
        # In a real system, this would retrieve candidate and job data from a database
        # For this example, we'll simulate it
        candidate_name = f"Candidate {candidate_id}"
        candidate_email = f"{candidate_id}@example.com"
        candidate_phone = f"+1555{candidate_id[-4:]}" if len(candidate_id) >= 4 else "+15551234"
        
        job_title = f"Position {job_id}"
        company_name = "Example Company"
        
        # Prepare context for template
        context = {
            "candidate_name": candidate_name,
            "position": job_title,
            "company": company_name,
            "scheduling_link": scheduling_link,
            "expiration_date": (datetime.now() + timedelta(days=7)).strftime("%A, %B %d, %Y")
        }
        
        # Render email template
        email_template = "interview_invitation"
        email_content = self.template_engine.render(email_template, context)
        
        # Send email
        email_sent = self.email_service.send(
            to=candidate_email,
            subject=f"Interview Invitation: {job_title} at {company_name}",
            content=email_content
        )
        
        # Send SMS if enabled in preferences
        sms_sent = False
        if communication_preferences and communication_preferences.get('sms_enabled', False):
            sms_template = "interview_invitation_sms"
            sms_content = self.template_engine.render(sms_template, context)
            sms_sent = self.sms_service.send(to=candidate_phone, content=sms_content)
        
        # Record communication
        self._record_communication(
            recipient_id=candidate_id,
            communication_type="scheduling_invitation",
            job_id=job_id,
            channels=["email"] + (["sms"] if sms_sent else []),
            status="sent" if email_sent or sms_sent else "failed",
            content=context
        )
        
        return email_sent or sms_sent
    
    def send_interview_confirmation(self,
                                  interview_id: str,
                                  job_id: str,
                                  candidate_id: str,
                                  interviewer_ids: List[str],
                                  start_time: datetime,
                                  end_time: datetime,
                                  location: str,
                                  interview_type: str,
                                  additional_info: str = "") -> bool:
        """
        Send interview confirmation to all participants.
        
        Args:
            interview_id: Interview identifier
            job_id: Job identifier
            candidate_id: Candidate identifier
            interviewer_ids: List of interviewer identifiers
            start_time: Interview start time
            end_time: Interview end time
            location: Interview location
            interview_type: Type of interview
            additional_info: Additional information
            
        Returns:
            True if confirmations were sent successfully
        """
        logger.info(f"Sending interview confirmation for interview {interview_id}")
        
        # In a real system, this would retrieve data from a database
        # For this example, we'll simulate it
        job_title = f"Position {job_id}"
        company_name = "Example Company"
        
        # Format date and time
        interview_date = start_time.strftime("%A, %B %d, %Y")
        interview_time = start_time.strftime("%I:%M %p")
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        # Send confirmation to candidate
        candidate_name = f"Candidate {candidate_id}"
        candidate_email = f"{candidate_id}@example.com"
        
        candidate_context = {
            "recipient_name": candidate_name,
            "recipient_type": "candidate",
            "position": job_title,
            "company": company_name,
            "interview_date": interview_date,
            "interview_time": interview_time,
            "duration_minutes": duration_minutes,
            "location": location,
            "interview_type": interview_type,
            "additional_info": additional_info
        }
        
        candidate_content = self.template_engine.render("interview_confirmation_candidate", candidate_context)
        
        candidate_sent = self.email_service.send(
            to=candidate_email,
            subject=f"Interview Confirmation: {job_title} at {company_name}",
            content=candidate_content
        )
        
        # Record communication
        self._record_communication(
            recipient_id=candidate_id,
            communication_type="interview_confirmation",
            job_id=job_id,
            interview_id=interview_id,
            channels=["email"],
            status="sent" if candidate_sent else "failed",
            content=candidate_context
        )
        
        # Send confirmation to interviewers
        interviewer_sent = True
        for interviewer_id in interviewer_ids:
            interviewer_name = f"Interviewer {interviewer_id}"
            interviewer_email = f"{interviewer_id}@example.com"
            
            interviewer_context = {
                "recipient_name": interviewer_name,
                "recipient_type": "interviewer",
                "candidate_name": candidate_name,
                "position": job_title,
                "company": company_name,
                "interview_date": interview_date,
                "interview_time": interview_time,
                "duration_minutes": duration_minutes,
                "location": location,
                "interview_type": interview_type,
                "additional_info": additional_info
            }
            
            interviewer_content = self.template_engine.render("interview_confirmation_interviewer", interviewer_context)
            
            sent = self.email_service.send(
                to=interviewer_email,
                subject=f"Interview Scheduled: {candidate_name} for {job_title}",
                content=interviewer_content
            )
            
            interviewer_sent = interviewer_sent and sent
            
            # Record communication
            self._record_communication(
                recipient_id=interviewer_id,
                communication_type="interview_confirmation",
                job_id=job_id,
                interview_id=interview_id,
                channels=["email"],
                status="sent" if sent else "failed",
                content=interviewer_context
            )
        
        return candidate_sent and interviewer_sent
    
    def send_interview_reminder(self,
                              interview_id: str,
                              recipient_id: str,
                              recipient_type: str,
                              job_id: str,
                              start_time: datetime,
                              location: str,
                              additional_info: str = "") -> bool:
        """
        Send an interview reminder.
        
        Args:
            interview_id: Interview identifier
            recipient_id: Recipient identifier
            recipient_type: Recipient type ('candidate' or 'interviewer')
            job_id: Job identifier
            start_time: Interview start time
            location: Interview location
            additional_info: Additional information
            
        Returns:
            True if reminder was sent successfully
        """
        logger.info(f"Sending interview reminder for interview {interview_id} to {recipient_type} {recipient_id}")
        
        # In a real system, this would retrieve data from a database
        # For this example, we'll simulate it
        job_title = f"Position {job_id}"
        company_name = "Example Company"
        
        recipient_name = f"{'Candidate' if recipient_type == 'candidate' else 'Interviewer'} {recipient_id}"
        recipient_email = f"{recipient_id}@example.com"
        
        # Format date and time
        interview_date = start_time.strftime("%A, %B %d, %Y")
        interview_time = start_time.strftime("%I:%M %p")
        
        # Prepare context
        context = {
            "recipient_name": recipient_name,
            "recipient_type": recipient_type,
            "position": job_title,
            "company": company_name,
            "interview_date": interview_date,
            "interview_time": interview_time,
            "location": location,
            "additional_info": additional_info
        }
        
        # Render template
        template_name = f"interview_reminder_{recipient_type}"
        content = self.template_engine.render(template_name, context)
        
        # Send email
        sent = self.email_service.send(
            to=recipient_email,
            subject=f"Interview Reminder: {job_title} at {company_name}",
            content=content
        )
        
        # Record communication
        self._record_communication(
            recipient_id=recipient_id,
            communication_type="interview_reminder",
            job_id=job_id,
            interview_id=interview_id,
            channels=["email"],
            status="sent" if sent else "failed",
            content=context
        )
        
        return sent
    
    def send_reschedule_notification(self,
                                   interview_id: str,
                                   start_time: datetime,
                                   end_time: datetime,
                                   reason: str = "") -> bool:
        """
        Send notifications about a rescheduled interview.
        
        Args:
            interview_id: Interview identifier
            start_time: New start time
            end_time: New end time
            reason: Reason for rescheduling
            
        Returns:
            True if notifications were sent successfully
        """
        logger.info(f"Sending reschedule notification for interview {interview_id}")
        
        # In a real system, this would retrieve interview data from a database
        # For this example, we'll simulate it
        job_id = "job_12345"
        job_title = f"Position {job_id}"
        company_name = "Example Company"
        location = "Conference Room A"
        
        candidate_id = "candidate_67890"
        interviewer_ids = ["interviewer_11111", "interviewer_22222"]
        
        # Format date and time
        interview_date = start_time.strftime("%A, %B %d, %Y")
        interview_time = start_time.strftime("%I:%M %p")
        duration_minutes = int((end_time - start_time).total_seconds() / 60)
        
        # Send notification to all participants
        all_participants = [candidate_id] + interviewer_ids
        all_sent = True
        
        for participant_id in all_participants:
            participant_type = "candidate" if participant_id == candidate_id else "interviewer"
            participant_name = f"{'Candidate' if participant_type == 'candidate' else 'Interviewer'} {participant_id}"
            participant_email = f"{participant_id}@example.com"
            
            # Prepare context
            context = {
                "recipient_name": participant_name,
                "recipient_type": participant_type,
                "position": job_title,
                "company": company_name,
                "interview_date": interview_date,
                "interview_time": interview_time,
                "duration_minutes": duration_minutes,
                "location": location,
                "reason": reason
            }
            
            # Add candidate name for interviewers
            if participant_type == "interviewer":
                context["candidate_name"] = f"Candidate {candidate_id}"
            
            # Render template
            template_name = f"interview_reschedule_{participant_type}"
            content = self.template_engine.render(template_name, context)
            
            # Send email
            sent = self.email_service.send(
                to=participant_email,
                subject=f"Interview Rescheduled: {job_title} at {company_name}",
                content=content
            )
            
            all_sent = all_sent and sent
            
            # Record communication
            self._record_communication(
                recipient_id=participant_id,
                communication_type="interview_reschedule",
                job_id=job_id,
                interview_id=interview_id,
                channels=["email"],
                status="sent" if sent else "failed",
                content=context
            )
        
        return all_sent
    
    def send_cancellation_notification(self,
                                     interview_id: str,
                                     reason: str = "") -> bool:
        """
        Send notifications about a cancelled interview.
        
        Args:
            interview_id: Interview identifier
            reason: Reason for cancellation
            
        Returns:
            True if notifications were sent successfully
        """
        logger.info(f"Sending cancellation notification for interview {interview_id}")
        
        # In a real system, this would retrieve interview data from a database
        # For this example, we'll simulate it
        job_id = "job_12345"
        job_title = f"Position {job_id}"
        company_name = "Example Company"
        
        candidate_id = "candidate_67890"
        interviewer_ids = ["interviewer_11111", "interviewer_22222"]
        
        # Send notification to all participants
        all_participants = [candidate_id] + interviewer_ids
        all_sent = True
        
        for participant_id in all_participants:
            participant_type = "candidate" if participant_id == candidate_id else "interviewer"
            participant_name = f"{'Candidate' if participant_type == 'candidate' else 'Interviewer'} {participant_id}"
            participant_email = f"{participant_id}@example.com"
            
            # Prepare context
            context = {
                "recipient_name": participant_name,
                "recipient_type": participant_type,
                "position": job_title,
                "company": company_name,
                "reason": reason
            }
            
            # Add candidate name for interviewers
            if participant_type == "interviewer":
                context["candidate_name"] = f"Candidate {candidate_id}"
            
            # Render template
            template_name = f"interview_cancellation_{participant_type}"
            content = self.template_engine.render(template_name, context)
            
            # Send email
            sent = self.email_service.send(
                to=participant_email,
                subject=f"Interview Cancelled: {job_title} at {company_name}",
                content=content
            )
            
            all_sent = all_sent and sent
            
            # Record communication
            self._record_communication(
                recipient_id=participant_id,
                communication_type="interview_cancellation",
                job_id=job_id,
                interview_id=interview_id,
                channels=["email"],
                status="sent" if sent else "failed",
                content=context
            )
        
        return all_sent
    
    def send_feedback_request(self,
                            interview_id: str,
                            recipient_id: str,
                            feedback_link: str) -> bool:
        """
        Send a feedback request after an interview.
        
        Args:
            interview_id: Interview identifier
            recipient_id: Recipient identifier (interviewer)
            feedback_link: Link to feedback form
            
        Returns:
            True if request was sent successfully
        """
        logger.info(f"Sending feedback request for interview {interview_id} to interviewer {recipient_id}")
        
        # In a real system, this would retrieve interview data from a database
        # For this example, we'll simulate it
        job_id = "job_12345"
        job_title = f"Position {job_id}"
        company_name = "Example Company"
        
        candidate_id = "candidate_67890"
        candidate_name = f"Candidate {candidate_id}"
        
        interviewer_name = f"Interviewer {recipient_id}"
        interviewer_email = f"{recipient_id}@example.com"
        
        # Prepare context
        context = {
            "interviewer_name": interviewer_name,
            "candidate_name": candidate_name,
            "position": job_title,
            "company": company_name,
            "feedback_link": feedback_link,
            "deadline": (datetime.now() + timedelta(days=2)).strftime("%A, %B %d, %Y")
        }
        
        # Render template
        content = self.template_engine.render("interview_feedback_request", context)
        
        # Send email
        sent = self.email_service.send(
            to=interviewer_email,
            subject=f"Feedback Request: {candidate_name} for {job_title}",
            content=content
        )
        
        # Record communication
        self._record_communication(
            recipient_id=recipient_id,
            communication_type="feedback_request",
            job_id=job_id,
            interview_id=interview_id,
            channels=["email"],
            status="sent" if sent else "failed",
            content=context
        )
        
        return sent
    
    def _record_communication(self,
                            recipient_id: str,
                            communication_type: str,
                            channels: List[str],
                            status: str,
                            content: Dict[str, Any],
                            job_id: Optional[str] = None,
                            interview_id: Optional[str] = None) -> None:
        """
        Record a communication in the history.
        
        Args:
            recipient_id: Recipient identifier
            communication_type: Type of communication
            channels: List of communication channels used
            status: Status of the communication
            content: Content of the communication
            job_id: Job identifier
            interview_id: Interview identifier
        """
        record = {
            "id": f"comm_{len(self.communication_history) + 1}",
            "recipient_id": recipient_id,
            "communication_type": communication_type,
            "channels": channels,
            "status": status,
            "content": content,
            "timestamp": datetime.now().isoformat()
        }
        
        if job_id:
            record["job_id"] = job_id
        
        if interview_id:
            record["interview_id"] = interview_id
        
        self.communication_history.append(record)
    
    def get_communication_history(self,
                                user_id: Optional[str] = None,
                                job_id: Optional[str] = None,
                                interview_id: Optional[str] = None,
                                communication_type: Optional[str] = None,
                                start_date: Optional[datetime] = None,
                                end_date: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get communication history with optional filters.
        
        Args:
            user_id: Filter by user identifier
            job_id: Filter by job identifier
            interview_id: Filter by interview identifier
            communication_type: Filter by communication type
            start_date: Filter by start date
            end_date: Filter by end date
            
        Returns:
            List of communication records
        """
        filtered_history = self.communication_history.copy()
        
        # Apply filters
        if user_id:
            filtered_history = [record for record in filtered_history if record["recipient_id"] == user_id]
        
        if job_id:
            filtered_history = [record for record in filtered_history if record.get("job_id") == job_id]
        
        if interview_id:
            filtered_history = [record for record in filtered_history if record.get("interview_id") == interview_id]
        
        if communication_type:
            filtered_history = [record for record in filtered_history if record["communication_type"] == communication_type]
        
        if start_date:
            filtered_history = [record for record in filtered_history if datetime.fromisoformat(record["timestamp"]) >= start_date]
        
        if end_date:
            filtered_history = [record for record in filtered_history if datetime.fromisoformat(record["timestamp"]) <= end_date]
        
        return filtered_history


# Example usage
if __name__ == "__main__":
    # Create template directory and sample templates
    os.makedirs("templates", exist_ok=True)
    
    # Sample interview invitation template
    with open("templates/interview_invitation.html", "w") as f:
        f.write("""
        <!DOCTYPE html>
        <html>
        <head>
            <style>
                body { font-family: Arial, sans-serif; line-height: 1.6; }
                .container { width: 600px; margin: 0 auto; }
                .header { background-color: #f8f9fa; padding: 20px; text-align: center; }
                .content { padding: 20px; }
                .button { display: inline-block; background-color: #007bff; color: white; padding: 10px 20px; text-decoration: none; border-radius: 5px; }
                .footer { background-color: #f8f9fa; padding: 20px; text-align: center; font-size: 12px; }
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h2>Interview Invitation</h2>
                </div>
                <div class="content">
                    <p>Dear {{ candidate_name }},</p>
                    
                    <p>We are pleased to invite you to interview for the <strong>{{ position }}</strong> position at {{ company }}.</p>
                    
                    <p>Please use the link below to select a time that works best for you:</p>
                    
                    <p style="text-align: center;">
                        <a href="{{ scheduling_link }}" class="button">Schedule Your Interview</a>
                    </p>
                    
                    <p>This scheduling link will expire on {{ expiration_date }}.</p>
                    
                    <p>If you have any questions, please don't hesitate to contact us.</p>
                    
                    <p>Best regards,<br>
                    {{ company }} Recruitment Team</p>
                </div>
                <div class="footer">
                    <p>This is an automated message. Please do not reply to this email.</p>
                </div>
            </div>
        </body>
        </html>
        """)
    
    # Initialize services
    template_engine = TemplateEngine(templates_dir="templates")
    
    # Mock email service that logs instead of sending
    class MockEmailService:
        def send(self, to, subject, content, **kwargs):
            print(f"\nMock Email:")
            print(f"To: {to}")
            print(f"Subject: {subject}")
            print(f"Content length: {len(content)} characters")
            return True
    
    # Mock SMS service
    class MockSMSService:
        def send(self, to, content, **kwargs):
            print(f"\nMock SMS:")
            print(f"To: {to}")
            print(f"Content: {content}")
            return True
    
    # Initialize communication service with mocks
    communication_service = CommunicationService(
        email_service=MockEmailService(),
        sms_service=MockSMSService(),
        template_engine=template_engine
    )
    
    # Example: Send scheduling invitation
    print("\n=== Sending Scheduling Invitation ===")
    communication_service.send_scheduling_invitation(
        candidate_id="candidate_12345",
        job_id="job_67890",
        scheduling_link="https://example.com/schedule?token=abc123",
        communication_preferences={"sms_enabled": True}
    )
    
    # Example: Send interview confirmation
    print("\n=== Sending Interview Confirmation ===")
    communication_service.send_interview_confirmation(
        interview_id="interview_12345",
        job_id="job_67890",
        candidate_id="candidate_12345",
        interviewer_ids=["interviewer_11111", "interviewer_22222"],
        start_time=datetime.now() + timedelta(days=3, hours=10),
        end_time=datetime.now() + timedelta(days=3, hours=11),
        location="Conference Room A",
        interview_type="Technical Interview",
        additional_info="Please prepare to discuss your experience with Python and React."
    )
    
    # Example: Get communication history
    print("\n=== Communication History ===")
    history = communication_service.get_communication_history(
        user_id="candidate_12345"
    )
    
    print(f"Found {len(history)} communications for candidate_12345")
    for record in history:
        print(f"- {record['communication_type']} via {', '.join(record['channels'])} on {record['timestamp']}")
