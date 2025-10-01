from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.FER_KEY)

def encrypt_text(text):
    """Encrypt a string to a URL-safe token"""
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(token):
    """Decrypt a token back to the original string"""
    return fernet.decrypt(token.encode()).decode()

# utils.py
import secrets
import string
from django.core.mail import send_mail

def generate_password(length=8):
    alphabet = string.ascii_letters + string.digits
    return ''.join(secrets.choice(alphabet) for i in range(length))

def send_credentials_email(to_email, user_id, password):
    subject = "Your Account Credentials"
    message = f"Hello,\n\nYour account has been created.\nUser ID: {user_id}\nPassword: {password}\n\nPlease login and change your password."
    send_mail(subject, message, 'harshsolanki2804@gmail.com', [to_email])
