# utils.py
from django.utils import timezone
import secrets
import random


#Function to generate token 
def generate_reset_token():
    token = secrets.token_urlsafe(64)  # Generate a random URL-safe token
    timestamp = timezone.now()  # Get the current timestamp
    return token, timestamp



def generate_otp():
    return str(random.randint(1000, 9999))

