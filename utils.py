from datetime import datetime, timedelta
import string, random
from models import PasswordEntry

def check_strength(password):
    if len(password) < 8:
        return "Weak"
    elif len(password) < 12:
        return "Medium"
    return "Strong"

def generate_password(length):
    chars = string.ascii_letters + string.digits + string.punctuation
    return ''.join(random.choice(chars) for _ in range(length))

def is_reused(password):
    last_entry = PasswordEntry.query.order_by(PasswordEntry.created_at.desc()).first()
    return last_entry and last_entry.password == password

def is_expired():
    last_entry = PasswordEntry.query.order_by(PasswordEntry.created_at.desc()).first()
    if not last_entry:
        return False
    return datetime.now() - last_entry.created_at > timedelta(days=30)

def translate(msg, lang='en'):
    translations = {
        "Password reused, please choose a new one": {
            "es": "Contraseña reutilizada, por favor elige una nueva",
            "en": "Password reused, please choose a new one"
        },
        "Password expired, please change it": {
            "es": "Contraseña caducada, por favor cámbiala",
            "en": "Password expired, please change it"
        },
        "Password is weak": {
            "es": "La contraseña es débil",
            "en": "Password is weak"
        },
        "Password is medium": {
            "es": "La contraseña tiene una fuerza media",
            "en": "Password is medium"
        },
        "Password is strong": {
            "es": "La contraseña es fuerte",
            "en": "Password is strong"
        },
        "Password is not strong enough, generating a strong one": {
            "es": "La contraseña no es lo suficientemente fuerte, generando una fuerte",
            "en": "Password is not strong enough, generating a strong one"
        }
    }
    return translations.get(msg, {}).get(lang, msg)
