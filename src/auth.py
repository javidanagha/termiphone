import pyotp
import time
import hmac
from pathlib import Path

SECRET_FILE = Path(__file__).parent / "totp.secret"

SESSION_TTL = 15 * 60
MAX_FAILS = 3
LOCKOUT = 10 * 60

class Auth:
    def __init__(self, allowed_id):
        self.totp = pyotp.TOTP(SECRET_FILE.read_text().strip())
        self.allowed_id = allowed_id
        self.session_until = 0.0
        self.locked_until = 0.0 
        self.fails = 0
        self.last_step = 0
    def is_allowed(self, uid):
        return uid == self.allowed_id
    def is_active(self):
        return time.time() < self.session_until
    def touch(self):
        self.session_until = time.time() + SESSION_TTL
    def logout(self):
        self.session_until = 0.0


        #LOGIN FUNCTION
    def login(self, code):
        code = code.replace(" ", "")
        now = time.time()
        if now < self.locked_until:
            return False
        step = int(now // 30)
        for s in (step - 1, step, step +1):
            expected = self.totp.at(s *30)
            if s > self.last_step and hmac.compare_digest(expected, code):
                self.last_step = s
                self.fails = 0
                self.touch()
                return True
            
        self.fails += 1
        if self.fails >= MAX_FAILS:
            self.locked_until = now + LOCKOUT
            self.fails = 0
        return False