
## What it does

- Full, persistent bash session controlled from a Telegram chat
- `cd`, environment variables, and running processes stay alive across messages — it's one continuous shell, not one-off command execution
- Terminal control keys (`Ctrl+C`, `Ctrl+X`, `Ctrl+Z`, ...) work, so interactive programs (`nano`, `top`) can be driven and exited
- Output is stripped of ANSI escape sequences and rendered monospace in Telegram

## Security model

The host runs on a bridged network with an unrestricted shell. Full access was a deliberate requirement, not an oversight. Because of that, every layer of protection sits at the front door.

| Layer | Mechanism |
|---|---|
| Identity | Telegram numeric user ID allowlist — the bot silently ignores anyone else |
| Second factor | TOTP (RFC 6238), compatible with Google Authenticator |
| Replay protection | Each accepted 30-second code window is consumed once |
| Brute-force protection | 3 failed attempts → 10-minute lockout |
| Session | 15-minute idle timeout, or manual `/logout` |
| Secrets | `totp.secret` and bot token stored outside version control, file mode `600` |

**This is not a hardened multi-tenant system.** It grants one person full shell access to one machine. Treat the TOTP secret and bot token with the same care as an SSH private key.

## Commands

| Command | Effect |
|---|---|
| `/login <code>` | Opens a 15-minute session; requires the current TOTP code |
| `/logout` | Ends the session immediately |
| `/ctrl <letter>` | Sends a control key, e.g. `/ctrl C` for Ctrl+C |
| *(any text)* | Sent to the shell as a command; output is returned |

## Setup

```bash
git clone https://github.com/javidanagha/termiphone.git
cd termiphone
python3 -m venv venv
./venv/bin/pip install -r requirements.txt
```

Create `.env`:
