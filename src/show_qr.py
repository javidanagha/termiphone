import pyotp
import qrcode
from pathlib import Path

secret = Path("totp.secret").read_text().strip()

uri = pyotp.TOTP(secret).provisioning_uri(name="parrot_vm", issuer_name="Termiphone")

qr = qrcode.QRCode()
qr.add_data(uri)
qr.print_ascii(invert=True)