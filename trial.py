import os
import django

# Set the Django settings module environment variable
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'Banking.settings')  # replace 'yourproject'!

# Setup Django
django.setup()

from django.core.mail import send_mail
from django.conf import settings

def send_test_email(to_email):
    subject = 'Test Email from Django Script'
    message = 'This is a test email sent from a standalone Django script.'
    from_email = settings.DEFAULT_FROM_EMAIL
    recipient_list = [to_email]

    send_mail(subject, message, from_email, recipient_list, fail_silently=False)
    print("Email sent!")

if __name__ == '__main__':
    send_test_email('hackerdev042@gmail.com')
