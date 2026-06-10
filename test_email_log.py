#!/usr/bin/env python
"""Test script to verify email sending and EmailLog status update."""
import os
import django
from django.contrib.auth import get_user_model

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "config.settings")
django.setup()

from learning.services.email_service import send_welcome_email
from learning.models import EmailLog


def test_email_logging():
    User = get_user_model()
    test_user, _ = User.objects.get_or_create(
        username="test_email_user",
        defaults={"email": "test@example.com"}
    )
    
    print(f"Testing email logging for user: {test_user.username} ({test_user.email})")
    print("="*60)
    
    # Send test email
    try:
        email_log = send_welcome_email(test_user)
        print(f"OK: Email sent successfully (log ID: {email_log.id})")
    except Exception as e:
        print(f"ERROR: Failed to send email: {str(e)}")
        return
    
    # Refresh the log from DB and verify status
    email_log.refresh_from_db()
    print(f"\nVerifying log status:")
    print(f"- Status: {email_log.status}")
    print(f"- Sent at: {email_log.sent_at}")
    print(f"- Response: {email_log.response}")
    
    if email_log.status == 'sent':
        print("\nSUCCESS: EmailLog status correctly updated to 'sent'!")
    else:
        print(f"\nFAILURE: EmailLog status is '{email_log.status}', expected 'sent'")
    
    # List all recent logs
    print("\nRecent EmailLogs:")
    for log in EmailLog.objects.all().order_by('-created_at')[:5]:
        print(f"- {log.recipient} | {log.subject} | {log.status}")


if __name__ == "__main__":
    test_email_logging()
