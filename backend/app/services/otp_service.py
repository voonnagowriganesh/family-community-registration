import random
from datetime import datetime, timedelta

def generate_otp() -> str:
    return str(random.randint(100000, 999999))

def get_expiry_time(minutes: int = 5):
    return datetime.utcnow() + timedelta(minutes=minutes)
