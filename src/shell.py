import os
import pty
import select
import subprocess
import re

class Shell:
    ANSI_RE = re.compile(r'\x1B(?:[@-Z\\-_]|\[[0-?]*[ -/]*[@-~])')
    def __init__(self):
        self.master_fd, slave_fd = pty.openpty()
        self.process = subprocess.Popen(
            ["bash"],
            stdin=slave_fd,
            stdout=slave_fd,
            stderr=slave_fd,    
        )

        os.close(slave_fd)
        self.read()
    def send(self,text):
        os.write(self.master_fd, (text + "\n").encode())
    def send_key(self, letter):
        os.write(self.master_fd, bytes([ord(letter.upper()) - 64]))
    def read(self, timeout=0.3):
        output = b""
        while True:
            ready, _, _ = select.select([self.master_fd], [], [], timeout)
            if not ready:
                break
            output += os.read(self.master_fd, 65536)
        text = output.decode(errors="ignore")
        return self.ANSI_RE.sub("", text)