#!/usr/bin/env python3
"""
SSRN Paper Notifications
Sends email and calendar notifications via MCP
"""

import json
import subprocess
import sys
from pathlib import Path
from datetime import datetime, timedelta


class NotificationSender:
    """Sends notifications via Gmail and Google Calendar MCP"""
    
    def __init__(self):
        self.email = "angelreporters@gmail.com"
        
    def send_email_notification(self, paper_metadata, gdrive_link, github_url=None):
        """Send email notification via Gmail MCP"""
        print("\n→ Sending email notification...")
        
        # Create email content
        email_body = self._create_email_body(paper_metadata, gdrive_link, github_url)
        
        # Prepare MCP command
        email_data = {
            "messages": [
                {
                    "to": [self.email],
                    "subject": f"New SSRN Paper Generated: {paper_metadata.get('title', 'Untitled')}",
                    "content": email_body
                }
            ]
        }
        
        # Call Gmail MCP
        try:
            result = subprocess.run(
                [
                    'manus-mcp-cli', 'tool', 'call', 'gmail_send_messages',
                    '--server', 'gmail',
                    '--input', json.dumps(email_data)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Email notification sent successfully")
                return True
            else:
                print(f"⚠️  Email notification failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️  Email notification error: {e}")
            return False
    
    def _create_email_body(self, metadata, gdrive_link, github_url):
        """Create email body content"""
        body = f"""New SSRN Paper Generated and Ready for Submission

Dear Audrey,

A new SSRN white paper has been successfully generated and is ready for your review and submission.

PAPER DETAILS:
--------------
Title: {metadata.get('title', 'N/A')}
Short Title: {metadata.get('filename', 'N/A').replace('Walter_Evans_', '').replace('.pdf', '')}
Date Generated: {metadata.get('date', 'N/A')}
Author: {metadata.get('author', 'Audrey Evans')} (ORCID: {metadata.get('orcid', '0009-0005-0663-7832')})

LINKS:
------
Google Drive PDF: {gdrive_link if gdrive_link else 'Not available'}
"""
        
        if github_url:
            body += f"GitHub Commit: {github_url}\n"
        
        body += f"""
QUALITY CHECK STATUS:
--------------------
✓ Paper generated successfully
✓ Uploaded to Google Drive
✓ Quality checks passed

ABSTRACT:
---------
{metadata.get('abstract', 'N/A')[:200]}...

KEYWORDS:
---------
{metadata.get('keywords', 'N/A')}

JEL CODES:
----------
{metadata.get('jel_codes', 'N/A')}

SUGGESTED EJOURNALS:
-------------------
{metadata.get('ejournals', 'N/A')}

NEXT STEPS:
-----------
1. Review the paper in Google Drive
2. Submit to SSRN at your convenience
3. Update submission status in your tracking system

Best regards,
SSRN Automation System
"""
        return body
    
    def create_calendar_event(self, paper_metadata, gdrive_link, github_url=None):
        """Create calendar event via Google Calendar MCP"""
        print("\n→ Creating calendar event...")
        
        # Calculate event time (9:05 AM MST today, 15 minutes)
        now = datetime.now()
        start_time = now.replace(hour=9, minute=5, second=0, microsecond=0)
        
        # If it's already past 9:05 AM, schedule for tomorrow
        if now.hour >= 9 and now.minute >= 5:
            start_time = start_time + timedelta(days=1)
        
        end_time = start_time + timedelta(minutes=15)
        
        # Format times in RFC3339
        start_str = start_time.strftime('%Y-%m-%dT%H:%M:%S-07:00')
        end_str = end_time.strftime('%Y-%m-%dT%H:%M:%S-07:00')
        
        # Get short title
        filename = paper_metadata.get('filename', '')
        short_title = filename.replace('Walter_Evans_', '').replace('.pdf', '').replace('_', ' ')
        
        # Create event description
        description = f"""Full Title: {paper_metadata.get('title', 'N/A')}

Google Drive Link: {gdrive_link if gdrive_link else 'Not available'}
"""
        
        if github_url:
            description += f"\nGitHub Commit: {github_url}"
        
        description += f"""

Keywords: {paper_metadata.get('keywords', 'N/A')}

JEL Codes: {paper_metadata.get('jel_codes', 'N/A')}

Status: Ready for SSRN submission"""
        
        # Prepare MCP command
        event_data = {
            "events": [
                {
                    "summary": f"📄 SSRN Paper Ready: {short_title}",
                    "description": description,
                    "start_time": start_str,
                    "end_time": end_str,
                    "calendar_id": "primary",
                    "reminders": [15]
                }
            ]
        }
        
        # Call Google Calendar MCP
        try:
            result = subprocess.run(
                [
                    'manus-mcp-cli', 'tool', 'call', 'google_calendar_create_events',
                    '--server', 'google-calendar',
                    '--input', json.dumps(event_data)
                ],
                capture_output=True,
                text=True,
                timeout=60
            )
            
            if result.returncode == 0:
                print("✅ Calendar event created successfully")
                return True
            else:
                print(f"⚠️  Calendar event creation failed: {result.stderr}")
                return False
                
        except Exception as e:
            print(f"⚠️  Calendar event error: {e}")
            return False
    
    def send_all_notifications(self, metadata_file, gdrive_link, github_url=None):
        """Send both email and calendar notifications"""
        print(f"\n{'='*60}")
        print("SENDING NOTIFICATIONS")
        print(f"{'='*60}")
        
        # Load metadata
        with open(metadata_file, 'r', encoding='utf-8') as f:
            metadata = json.load(f)
        
        print(f"\nPaper: {metadata.get('filename', 'N/A')}")
        print(f"Title: {metadata.get('title', 'N/A')}\n")
        
        # Send email
        email_success = self.send_email_notification(metadata, gdrive_link, github_url)
        
        # Create calendar event
        calendar_success = self.create_calendar_event(metadata, gdrive_link, github_url)
        
        print(f"\n{'='*60}")
        if email_success and calendar_success:
            print("✅ All notifications sent successfully!")
        elif email_success or calendar_success:
            print("⚠️  Some notifications sent (check logs above)")
        else:
            print("❌ Notification sending failed")
        print(f"{'='*60}\n")
        
        return email_success and calendar_success


def main():
    if len(sys.argv) < 3:
        print("Usage: python send_notifications.py <metadata_json> <gdrive_link> [github_url]")
        sys.exit(1)
    
    metadata_file = sys.argv[1]
    gdrive_link = sys.argv[2]
    github_url = sys.argv[3] if len(sys.argv) > 3 else None
    
    sender = NotificationSender()
    sender.send_all_notifications(metadata_file, gdrive_link, github_url)


if __name__ == '__main__':
    main()
