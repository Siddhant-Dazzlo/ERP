from flask import current_app, render_template
from flask_mail import Mail, Message
from threading import Thread
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email import encoders
import os
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

class EmailService:
    def __init__(self, app=None):
        self.mail = Mail()
        if app is not None:
            self.init_app(app)
    
    def init_app(self, app):
        self.mail.init_app(app)
    
    def send_async_email(self, app, msg):
        """Send email asynchronously"""
        with app.app_context():
            try:
                self.mail.send(msg)
            except Exception as e:
                current_app.logger.error(f"Failed to send email: {str(e)}")
    
    def send_email(self, subject: str, recipients: List[str], template: str, 
                   context: Dict[str, Any] = None, attachments: List[Dict] = None, 
                   async_send: bool = True):
        """Send email with template"""
        try:
            msg = Message(
                subject=subject,
                recipients=recipients,
                sender=current_app.config['MAIL_DEFAULT_SENDER']
            )
            
            # Render HTML template
            if context is None:
                context = {}
            
            html_content = render_template(f'emails/{template}.html', **context)
            msg.html = html_content
            
            # Add plain text version
            text_content = render_template(f'emails/{template}.txt', **context)
            msg.body = text_content
            
            # Add attachments
            if attachments:
                for attachment in attachments:
                    with open(attachment['path'], 'rb') as f:
                        msg.attach(
                            filename=attachment['filename'],
                            content_type=attachment.get('content_type', 'application/octet-stream'),
                            data=f.read()
                        )
            
            if async_send:
                Thread(target=self.send_async_email, args=(current_app._get_current_object(), msg)).start()
            else:
                self.mail.send(msg)
                
            return True
            
        except Exception as e:
            current_app.logger.error(f"Email sending failed: {str(e)}")
            return False
    
    def send_welcome_email(self, user_email: str, user_name: str, role: str):
        """Send welcome email to new users"""
        context = {
            'user_name': user_name,
            'role': role,
            'login_url': current_app.config.get('LOGIN_URL', 'http://localhost:8080/login'),
            'support_email': current_app.config.get('SUPPORT_EMAIL', 'support@trivantaedge.com')
        }
        
        return self.send_email(
            subject=f"Welcome to Trivanta Edge ERP - {user_name}",
            recipients=[user_email],
            template='welcome',
            context=context
        )
    
    def send_password_reset_email(self, user_email: str, reset_token: str, user_name: str):
        """Send password reset email"""
        reset_url = f"{current_app.config.get('BASE_URL', 'http://localhost:8080')}/reset-password?token={reset_token}"
        
        context = {
            'user_name': user_name,
            'reset_url': reset_url,
            'expiry_hours': 24
        }
        
        return self.send_email(
            subject="Password Reset Request - Trivanta Edge ERP",
            recipients=[user_email],
            template='password_reset',
            context=context
        )
    
    def send_2fa_setup_email(self, user_email: str, user_name: str, qr_code_data: str):
        """Send 2FA setup email with QR code"""
        context = {
            'user_name': user_name,
            'qr_code_data': qr_code_data,
            'setup_url': f"{current_app.config.get('BASE_URL', 'http://localhost:8080')}/setup-2fa"
        }
        
        return self.send_email(
            subject="Two-Factor Authentication Setup - Trivanta Edge ERP",
            recipients=[user_email],
            template='2fa_setup',
            context=context
        )
    
    def send_project_notification(self, project_data: Dict[str, Any], recipients: List[str], notification_type: str):
        """Send project-related notifications"""
        context = {
            'project': project_data,
            'notification_type': notification_type,
            'project_url': f"{current_app.config.get('BASE_URL', 'http://localhost:8080')}/projects/{project_data['id']}"
        }
        
        subject_map = {
            'created': f"New Project Created: {project_data['name']}",
            'updated': f"Project Updated: {project_data['name']}",
            'completed': f"Project Completed: {project_data['name']}",
            'assigned': f"Project Assigned: {project_data['name']}"
        }
        
        return self.send_email(
            subject=subject_map.get(notification_type, f"Project Notification: {project_data['name']}"),
            recipients=recipients,
            template='project_notification',
            context=context
        )
    
    def send_attendance_report(self, report_data: Dict[str, Any], recipients: List[str], report_type: str = 'daily'):
        """Send attendance reports"""
        context = {
            'report': report_data,
            'report_type': report_type,
            'date': datetime.now().strftime('%Y-%m-%d')
        }
        
        subject = f"Attendance Report - {report_type.title()} - {datetime.now().strftime('%Y-%m-%d')}"
        
        return self.send_email(
            subject=subject,
            recipients=recipients,
            template='attendance_report',
            context=context
        )
    
    def send_analytics_report(self, analytics_data: Dict[str, Any], recipients: List[str], report_type: str = 'weekly'):
        """Send analytics reports"""
        context = {
            'analytics': analytics_data,
            'report_type': report_type,
            'generated_at': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        subject = f"Analytics Report - {report_type.title()} - {datetime.now().strftime('%Y-%m-%d')}"
        
        return self.send_email(
            subject=subject,
            recipients=recipients,
            template='analytics_report',
            context=context
        )
    
    def send_lead_notification(self, lead_data: Dict[str, Any], recipients: List[str], notification_type: str):
        """Send lead-related notifications"""
        context = {
            'lead': lead_data,
            'notification_type': notification_type,
            'lead_url': f"{current_app.config.get('BASE_URL', 'http://localhost:8080')}/leads/{lead_data['id']}"
        }
        
        subject_map = {
            'new': f"New Lead: {lead_data['name']}",
            'assigned': f"Lead Assigned: {lead_data['name']}",
            'converted': f"Lead Converted: {lead_data['name']}"
        }
        
        return self.send_email(
            subject=subject_map.get(notification_type, f"Lead Notification: {lead_data['name']}"),
            recipients=recipients,
            template='lead_notification',
            context=context
        )
    
    def send_system_alert(self, alert_data: Dict[str, Any], recipients: List[str]):
        """Send system alerts"""
        context = {
            'alert': alert_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.send_email(
            subject=f"System Alert: {alert_data.get('type', 'Unknown')}",
            recipients=recipients,
            template='system_alert',
            context=context
        )
    
    def send_backup_notification(self, backup_data: Dict[str, Any], recipients: List[str]):
        """Send backup completion notifications"""
        context = {
            'backup': backup_data,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        }
        
        return self.send_email(
            subject=f"Backup {backup_data.get('status', 'Unknown')}: {backup_data.get('filename', 'Unknown')}",
            recipients=recipients,
            template='backup_notification',
            context=context
        )

# Initialize email service
email_service = EmailService()
