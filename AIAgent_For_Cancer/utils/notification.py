"""
Notification service for the Oncology AI Assistant System.
Provides methods to send notifications via different channels.
"""
import logging
import json
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from typing import List, Dict, Any, Optional

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


class NotificationService:
    """Service for sending notifications through various channels."""
    
    def __init__(self, config_path: str = None):
        """Initialize the notification service.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'config', 'notification_config.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return {
                'email': {
                    'smtp_server': 'smtp.gmail.com',
                    'smtp_port': 587,
                    'username': '',
                    'password': '',
                    'from_address': 'oncology.assistant@example.com'
                },
                'sms': {
                    'provider': 'twilio',
                    'account_sid': '',
                    'auth_token': '',
                    'from_number': ''
                },
                'dashboard': {
                    'store_path': os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                              'data', 'notifications')
                }
            }
    
    def send_email(self, subject: str, body: str, recipients: List[str], 
                  html_body: Optional[str] = None) -> bool:
        """Send an email notification.
        
        Args:
            subject: Email subject
            body: Email body (plain text)
            recipients: List of email addresses
            html_body: Optional HTML body
            
        Returns:
            True if successful, False otherwise
        """
        if not recipients:
            logger.warning("No recipients specified for email notification")
            return False
            
        email_config = self.config.get('email', {})
        smtp_server = email_config.get('smtp_server')
        smtp_port = email_config.get('smtp_port')
        username = email_config.get('username')
        password = email_config.get('password')
        from_address = email_config.get('from_address')
        
        if not all([smtp_server, smtp_port, username, password, from_address]):
            logger.error("Incomplete email configuration")
            return False
            
        try:
            # Create message
            msg = MIMEMultipart('alternative')
            msg['Subject'] = subject
            msg['From'] = from_address
            msg['To'] = ', '.join(recipients)
            
            # Add plain text body
            msg.attach(MIMEText(body, 'plain'))
            
            # Add HTML body if provided
            if html_body:
                msg.attach(MIMEText(html_body, 'html'))
                
            # Connect to SMTP server
            server = smtplib.SMTP(smtp_server, smtp_port)
            server.starttls()
            server.login(username, password)
            
            # Send email
            server.sendmail(from_address, recipients, msg.as_string())
            server.quit()
            
            logger.info(f"Email sent to {len(recipients)} recipients")
            return True
            
        except Exception as e:
            logger.error(f"Error sending email: {e}")
            return False
    
    def send_sms(self, message: str, recipients: List[str]) -> bool:
        """Send an SMS notification.
        
        Args:
            message: SMS message
            recipients: List of phone numbers
            
        Returns:
            True if successful, False otherwise
        """
        if not recipients:
            logger.warning("No recipients specified for SMS notification")
            return False
            
        sms_config = self.config.get('sms', {})
        provider = sms_config.get('provider')
        
        if provider == 'twilio':
            return self._send_twilio_sms(message, recipients)
        else:
            logger.error(f"Unsupported SMS provider: {provider}")
            return False
    
    def _send_twilio_sms(self, message: str, recipients: List[str]) -> bool:
        """Send SMS using Twilio.
        
        Args:
            message: SMS message
            recipients: List of phone numbers
            
        Returns:
            True if successful, False otherwise
        """
        sms_config = self.config.get('sms', {})
        account_sid = sms_config.get('account_sid')
        auth_token = sms_config.get('auth_token')
        from_number = sms_config.get('from_number')
        
        if not all([account_sid, auth_token, from_number]):
            logger.error("Incomplete Twilio configuration")
            return False
            
        try:
            # In a real implementation, this would use the Twilio SDK
            # For demonstration purposes, we'll just log the message
            logger.info(f"Would send SMS to {len(recipients)} recipients via Twilio: {message[:50]}...")
            return True
            
        except Exception as e:
            logger.error(f"Error sending SMS via Twilio: {e}")
            return False
    
    def send_dashboard_alert(self, alert_type: str, content: Any) -> bool:
        """Send an alert to the dashboard.
        
        Args:
            alert_type: Type of alert
            content: Alert content
            
        Returns:
            True if successful, False otherwise
        """
        dashboard_config = self.config.get('dashboard', {})
        store_path = dashboard_config.get('store_path')
        
        if not store_path:
            logger.error("No storage path configured for dashboard alerts")
            return False
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(store_path, exist_ok=True)
            
            # Create alert file
            alert_file = os.path.join(store_path, f"alert_{alert_type}_{int(os.time.time())}.json")
            
            with open(alert_file, 'w') as f:
                json.dump({
                    'type': alert_type,
                    'timestamp': os.time.time(),
                    'content': content
                }, f, indent=2)
                
            logger.info(f"Dashboard alert saved to {alert_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving dashboard alert: {e}")
            return False
    
    def send_dashboard_update(self, update_type: str, content: Any) -> bool:
        """Send an update to the dashboard.
        
        Args:
            update_type: Type of update
            content: Update content
            
        Returns:
            True if successful, False otherwise
        """
        dashboard_config = self.config.get('dashboard', {})
        store_path = dashboard_config.get('store_path')
        
        if not store_path:
            logger.error("No storage path configured for dashboard updates")
            return False
            
        try:
            # Create directory if it doesn't exist
            os.makedirs(store_path, exist_ok=True)
            
            # Create update file
            update_file = os.path.join(store_path, f"update_{update_type}.json")
            
            with open(update_file, 'w') as f:
                json.dump({
                    'type': update_type,
                    'timestamp': os.time.time(),
                    'content': content
                }, f, indent=2)
                
            logger.info(f"Dashboard update saved to {update_file}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving dashboard update: {e}")
            return False
    
    def send_update(self, update: Dict[str, Any], recipients: List[str] = None) -> bool:
        """Send an update through configured notification channels.
        
        Args:
            update: Update content
            recipients: List of recipients (email addresses, phone numbers)
            
        Returns:
            True if at least one notification was sent successfully
        """
        methods = self.config.get('notification_methods', ['dashboard'])
        success = False
        
        # Always send to dashboard
        if 'dashboard' in methods:
            success = self.send_dashboard_update('general_update', update) or success
            
        # Send email if configured
        if 'email' in methods and recipients:
            subject = f"Oncology Assistant Update: {update.get('timestamp', '')}"
            body = self._format_update_for_email(update)
            success = self.send_email(subject, body, recipients) or success
            
        # Send SMS if configured
        if 'sms' in methods and recipients:
            message = self._format_update_for_sms(update)
            success = self.send_sms(message, recipients) or success
            
        return success
    
    def _format_update_for_email(self, update: Dict[str, Any]) -> str:
        """Format an update for email notification."""
        formatted = "ONCOLOGY ASSISTANT UPDATE\n\n"
        
        formatted += f"Timestamp: {update.get('timestamp', '')}\n\n"
        
        if 'research' in update:
            research = update['research']
            formatted += f"RESEARCH PAPERS: {len(research)} new papers\n"
            for i, paper in enumerate(research[:3], 1):
                formatted += f"{i}. {paper.get('title', 'Unknown')}\n"
            if len(research) > 3:
                formatted += f"... and {len(research) - 3} more papers\n"
            formatted += "\n"
            
        if 'clinical_trials' in update:
            trials = update['clinical_trials']
            formatted += f"CLINICAL TRIALS: {len(trials)} new trials\n"
            for i, trial in enumerate(trials[:3], 1):
                formatted += f"{i}. {trial.get('title', 'Unknown')}\n"
            if len(trials) > 3:
                formatted += f"... and {len(trials) - 3} more trials\n"
            formatted += "\n"
            
        if 'therapies' in update:
            therapies = update['therapies']
            formatted += f"THERAPIES: {len(therapies)} new therapies\n"
            for i, therapy in enumerate(therapies[:3], 1):
                formatted += f"{i}. {therapy.get('name', 'Unknown')}\n"
            if len(therapies) > 3:
                formatted += f"... and {len(therapies) - 3} more therapies\n"
            formatted += "\n"
            
        formatted += "View the full update on the dashboard."
        
        return formatted
    
    def _format_update_for_sms(self, update: Dict[str, Any]) -> str:
        """Format an update for SMS notification."""
        counts = []
        
        if 'research' in update:
            counts.append(f"{len(update['research'])} papers")
            
        if 'clinical_trials' in update:
            counts.append(f"{len(update['clinical_trials'])} trials")
            
        if 'therapies' in update:
            counts.append(f"{len(update['therapies'])} therapies")
            
        counts_str = ", ".join(counts)
        
        return f"Oncology Assistant Update: New {counts_str}. Check dashboard for details."
