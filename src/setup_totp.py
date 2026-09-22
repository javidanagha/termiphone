import pyotp
from pathlib import Path

path = Path("totp.secret")

if path.exists():
    raise SystemExit("Secret already exists")

secret = pyotp.random_base32()

path.write_text(secret)

print("Secret written to totp.secret")
