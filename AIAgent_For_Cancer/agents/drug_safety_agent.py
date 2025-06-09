"""
Drug Safety Alert Agent
Function: Monitors FDA/EMA websites for new warnings or recalls for lung cancer drugs.
Features:
- Detects adverse effect reports or black-box warnings for lung cancer drugs
- Notifies doctors via dashboard or SMS/email
"""
import os
import json
import logging
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
import re
import requests
from bs4 import BeautifulSoup

from utils.api_clients import FDAClient, EMAClient
from utils.notification import NotificationService

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class DrugSafetyAgent:
    """Agent that monitors drug safety alerts for lung cancer medications."""
    
    def __init__(self, config_path: str = None):
        """Initialize the drug safety alert agent.
        
        Args:
            config_path: Path to the configuration file
        """
        self.config = self._load_config(config_path)
        self.fda_client = FDAClient()
        self.ema_client = EMAClient()
        self.notification_service = NotificationService()
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load configuration from file."""
        if not config_path:
            config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 
                                      'config', 'drug_safety_config.json')
        
        try:
            with open(config_path, 'r') as f:
                return json.load(f)
        except FileNotFoundError:
            logger.warning(f"Config file not found at {config_path}. Using default configuration.")
            return {
                'lung_cancer_drugs': [
                    # Targeted therapies
                    'osimertinib', 'erlotinib', 'gefitinib', 'afatinib', 'dacomitinib',  # EGFR inhibitors
                    'alectinib', 'brigatinib', 'ceritinib', 'crizotinib', 'lorlatinib',  # ALK inhibitors
                    'entrectinib', 'crizotinib',  # ROS1 inhibitors
                    'dabrafenib', 'trametinib',  # BRAF inhibitors
                    'capmatinib', 'tepotinib',  # MET inhibitors
                    'selpercatinib', 'pralsetinib',  # RET inhibitors
                    'larotrectinib', 'entrectinib',  # NTRK inhibitors
                    
                    # Immunotherapies
                    'pembrolizumab', 'nivolumab', 'atezolizumab', 'durvalumab', 'cemiplimab',
                    
                    # Chemotherapies commonly used for lung cancer
                    'cisplatin', 'carboplatin', 'paclitaxel', 'docetaxel', 'gemcitabine', 
                    'pemetrexed', 'vinorelbine', 'etoposide'
                ],
                'check_frequency_hours': 24,
                'days_lookback': 30,
                'alert_levels': ['recall', 'black box warning', 'safety alert', 'adverse event'],
                'notification_methods': ['dashboard', 'email'],
                'notification_recipients': [],
                'urgent_notification_threshold': 'black box warning'
            }
    
    def check_fda_alerts(self) -> List[Dict[str, Any]]:
        """Check FDA website for drug safety alerts related to lung cancer drugs."""
        alerts = []
        
        for drug in self.config.get('lung_cancer_drugs', []):
            logger.info(f"Checking FDA alerts for drug: {drug}")
            
            # Get drug safety alerts from FDA
            drug_alerts = self.fda_client.get_drug_alerts(
                drug_name=drug,
                days=self.config.get('days_lookback', 30)
            )
            
            # Add drug name to each alert
            for alert in drug_alerts:
                alert['drug'] = drug
                alerts.append(alert)
                
        return alerts
    
    def check_ema_alerts(self) -> List[Dict[str, Any]]:
        """Check EMA website for drug safety alerts related to lung cancer drugs."""
        alerts = []
        
        for drug in self.config.get('lung_cancer_drugs', []):
            logger.info(f"Checking EMA alerts for drug: {drug}")
            
            # Get drug safety alerts from EMA
            drug_alerts = self.ema_client.get_drug_alerts(
                drug_name=drug,
                days=self.config.get('days_lookback', 30)
            )
            
            # Add drug name to each alert
            for alert in drug_alerts:
                alert['drug'] = drug
                alerts.append(alert)
                
        return alerts
    
    def check_black_box_warnings(self) -> List[Dict[str, Any]]:
        """Check for new black box warnings for lung cancer drugs."""
        warnings = []
        
        for drug in self.config.get('lung_cancer_drugs', []):
            logger.info(f"Checking black box warnings for drug: {drug}")
            
            # Get black box warnings from FDA
            drug_warnings = self.fda_client.get_black_box_warnings(
                drug_name=drug,
                days=self.config.get('days_lookback', 30)
            )
            
            # Add drug name to each warning
            for warning in drug_warnings:
                warning['drug'] = drug
                warnings.append(warning)
                
        return warnings
    
    def check_adverse_events(self) -> List[Dict[str, Any]]:
        """Check for new adverse event reports for lung cancer drugs."""
        events = []
        
        for drug in self.config.get('lung_cancer_drugs', []):
            logger.info(f"Checking adverse events for drug: {drug}")
            
            # Get adverse events from FDA
            drug_events = self.fda_client.get_adverse_events(
                drug_name=drug,
                days=self.config.get('days_lookback', 30)
            )
            
            # Add drug name to each event
            for event in drug_events:
                event['drug'] = drug
                events.append(event)
                
        return events
    
    def categorize_alert_severity(self, alerts: List[Dict[str, Any]]) -> Dict[str, List[Dict[str, Any]]]:
        """Categorize alerts by severity level."""
        categorized = {
            'urgent': [],
            'high': [],
            'medium': [],
            'low': []
        }
        
        for alert in alerts:
            alert_type = alert.get('type', '').lower()
            
            if 'recall' in alert_type or 'black box' in alert_type:
                categorized['urgent'].append(alert)
            elif 'safety alert' in alert_type or 'serious' in alert_type:
                categorized['high'].append(alert)
            elif 'adverse event' in alert_type and alert.get('serious', False):
                categorized['medium'].append(alert)
            else:
                categorized['low'].append(alert)
                
        return categorized
    
    def generate_safety_report(self) -> Dict[str, Any]:
        """Generate a comprehensive safety report for lung cancer drugs."""
        # Get alerts from FDA
        fda_alerts = self.check_fda_alerts()
        
        # Get alerts from EMA
        ema_alerts = self.check_ema_alerts()
        
        # Get black box warnings
        black_box_warnings = self.check_black_box_warnings()
        
        # Get adverse events
        adverse_events = self.check_adverse_events()
        
        # Combine all alerts
        all_alerts = fda_alerts + ema_alerts + black_box_warnings
        
        # Categorize alerts by severity
        categorized_alerts = self.categorize_alert_severity(all_alerts)
        
        # Group alerts by drug
        alerts_by_drug = {}
        for alert in all_alerts:
            drug = alert.get('drug', 'Unknown')
            if drug not in alerts_by_drug:
                alerts_by_drug[drug] = []
            alerts_by_drug[drug].append(alert)
            
        # Generate report
        report = {
            'timestamp': datetime.now().isoformat(),
            'period': f"Past {self.config.get('days_lookback', 30)} days",
            'total_alerts': len(all_alerts),
            'total_adverse_events': len(adverse_events),
            'urgent_alerts': len(categorized_alerts['urgent']),
            'high_priority_alerts': len(categorized_alerts['high']),
            'categorized_alerts': categorized_alerts,
            'alerts_by_drug': alerts_by_drug,
            'adverse_events_summary': self._summarize_adverse_events(adverse_events)
        }
        
        return report
    
    def _summarize_adverse_events(self, events: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Summarize adverse events by type and severity."""
        summary = {
            'total': len(events),
            'serious': sum(1 for event in events if event.get('serious', False)),
            'by_drug': {},
            'by_reaction': {}
        }
        
        # Group by drug
        for event in events:
            drug = event.get('drug', 'Unknown')
            if drug not in summary['by_drug']:
                summary['by_drug'][drug] = {
                    'total': 0,
                    'serious': 0
                }
            summary['by_drug'][drug]['total'] += 1
            if event.get('serious', False):
                summary['by_drug'][drug]['serious'] += 1
                
        # Group by reaction
        for event in events:
            reactions = event.get('reactions', [])
            for reaction in reactions:
                if reaction not in summary['by_reaction']:
                    summary['by_reaction'][reaction] = {
                        'total': 0,
                        'serious': 0
                    }
                summary['by_reaction'][reaction]['total'] += 1
                if event.get('serious', False):
                    summary['by_reaction'][reaction]['serious'] += 1
                    
        return summary
    
    def send_alerts(self, report: Dict[str, Any]) -> bool:
        """Send alerts based on the safety report."""
        # Check if there are any urgent alerts
        has_urgent = report['urgent_alerts'] > 0
        
        # Determine notification methods
        methods = self.config.get('notification_methods', ['dashboard'])
        
        # Get recipients
        recipients = self.config.get('notification_recipients', [])
        
        # Send notifications
        if has_urgent:
            logger.info("Sending urgent drug safety alerts")
            urgent_alerts = report['categorized_alerts']['urgent']
            
            # Send urgent notifications
            for method in methods:
                if method == 'email':
                    self.notification_service.send_email(
                        subject="URGENT: Drug Safety Alert for Lung Cancer Medications",
                        body=self._format_urgent_alerts(urgent_alerts),
                        recipients=recipients
                    )
                elif method == 'sms':
                    self.notification_service.send_sms(
                        message=self._format_urgent_alerts_sms(urgent_alerts),
                        recipients=recipients
                    )
                elif method == 'dashboard':
                    self.notification_service.send_dashboard_alert(
                        alert_type="urgent_drug_safety",
                        content=urgent_alerts
                    )
        
        # Always send the full report to the dashboard
        self.notification_service.send_dashboard_update(
            update_type="drug_safety_report",
            content=report
        )
        
        return True
    
    def _format_urgent_alerts(self, alerts: List[Dict[str, Any]]) -> str:
        """Format urgent alerts for email notification."""
        formatted = "URGENT DRUG SAFETY ALERTS:\n\n"
        
        for alert in alerts:
            formatted += f"DRUG: {alert.get('drug', 'Unknown')}\n"
            formatted += f"TYPE: {alert.get('type', 'Unknown')}\n"
            formatted += f"DATE: {alert.get('date', 'Unknown')}\n"
            formatted += f"DESCRIPTION: {alert.get('description', 'No description available')}\n"
            formatted += f"SOURCE: {alert.get('source', 'Unknown')}\n"
            formatted += f"LINK: {alert.get('link', 'No link available')}\n\n"
            
        return formatted
    
    def _format_urgent_alerts_sms(self, alerts: List[Dict[str, Any]]) -> str:
        """Format urgent alerts for SMS notification."""
        drugs = set(alert.get('drug', 'Unknown') for alert in alerts)
        drug_list = ", ".join(drugs)
        
        return f"URGENT: {len(alerts)} new safety alert(s) for lung cancer drugs: {drug_list}. Check dashboard for details."
    
    def run_safety_check(self) -> None:
        """Run a complete safety check and send alerts if necessary."""
        logger.info("Running drug safety check for lung cancer medications")
        
        # Generate safety report
        report = self.generate_safety_report()
        
        # Send alerts if necessary
        if report['total_alerts'] > 0:
            self.send_alerts(report)
            logger.info(f"Sent alerts for {report['total_alerts']} drug safety issues")
        else:
            logger.info("No new drug safety alerts found")
            
        return report

if __name__ == "__main__":
    # For testing purposes
    agent = DrugSafetyAgent()
    report = agent.run_safety_check()
    
    print(f"Generated safety report for {report['period']}")
    print(f"Found {report['total_alerts']} alerts and {report['total_adverse_events']} adverse events")
    
    if report['urgent_alerts'] > 0:
        print("\nURGENT ALERTS:")
        for alert in report['categorized_alerts']['urgent']:
            print(f"- {alert['drug']}: {alert['type']} - {alert['description'][:100]}...")
