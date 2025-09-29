from cryptography.fernet import Fernet
from django.conf import settings

fernet = Fernet(settings.FER_KEY)

def encrypt_text(text):
    """Encrypt a string to a URL-safe token"""
    return fernet.encrypt(text.encode()).decode()

def decrypt_text(token):
    """Decrypt a token back to the original string"""
    return fernet.decrypt(token.encode()).decode()
