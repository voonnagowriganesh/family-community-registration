import secrets
import base64

# Generate a secure random key (64 bytes = 512 bits)
SECRET_KEY = base64.urlsafe_b64encode(secrets.token_bytes(64)).decode()
