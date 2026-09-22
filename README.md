# Termiphone

Remote terminal access to a Linux host over Telegram, gated by a TOTP, no SSH, no open ports, no inbound connection at all.

![Python](https://img.shields.io/badge/Python-3.13-3776AB)
![python--telegram--bot](https://img.shields.io/badge/python--telegram--bot-21-26A5E4)
![pyotp](https://img.shields.io/badge/pyotp-TOTP-6E4C1E)
![PTY](https://img.shields.io/badge/shell-persistent%20PTY-333333)

---

## Overview

The bot never listens on a port. It only makes outbound connections to Telegram. The attack surface is the Telegram account and the TOTP secret, not an open network service.

phone ▶ Telegram servers ▶ long polling ▶ bot.py ▶ auth.py (TOTP gate) ▶ shell.py (PTY) ▶ bash

A message only reaches `bash` if it passes two checks: the sender's Telegram user ID is on the allowlist, and a session is currently open.

---

## Tech stack

| Layer | Component | Purpose |
|---|---|---|
| Transport | `python-telegram-bot` | Receives commands, sends output, no open inbound port |
| Identity | Telegram numeric user ID allowlist | Silently ignores anyone not on the list |
| Second factor | `pyotp` | Google Authenticator–compatible, ±30s window, replay-protected |
| Shell | `pty` + `subprocess` | Persistent bash session — `cd`, env vars, and running processes survive across messages |
| Output | `re` + `html` | Strips ANSI escape sequences, escapes HTML for safe monospace rendering in Telegram |

---

## Repository structure

src/
├── bot.py # Telegram handlers — /login, /logout, /ctrl, text → shell
├── auth.py # TOTP verification, session timeout, lockout logic
├── shell.py # PTY-backed persistent bash session
├── setup_totp.py # One-time TOTP secret generation
├── show_qr.py # Displays the pairing QR code in-terminal
├── test_auth.py # Standalone script to verify TOTP setup before running the bot
└── requirements.txt
.gitignore
LICENSE
README.md

---

## Security model

The host runs on a bridged network with an unrestricted shell. Full access was a deliberate requirement, not an oversight. Every layer of protection sits at the front door instead.

| Control | Detail |
|---|---|
| Identity | Telegram user ID allowlist |
| Second factor | TOTP, 30s window ± 1 step tolerance |
| Replay protection | Each accepted code window is consumed once (`last_step`) |
| Brute-force protection | 3 failed attempts → 10-minute lockout |
| Session | 15-minute idle timeout, or manual `/logout` |
| Secrets | `totp.secret` and bot token stored outside version control, mode `600` |

This is not a hardened multi-tenant system. It grants one person full shell access to one machine. The TOTP secret and bot token should be treated with the same care as an SSH private key.

---

## Errors you might encounter

**TOTP codes always rejected, even when correct.** The VM's clock had drifted from the phone's. TOTP is time-based, so a few seconds of skew is enough to break it. Fixed by confirming `System clock synchronized: yes` via `timedatectl` on the host and forcing the phone to resync its network time.

**Command output arrived scrambled or belonged to the previous command.** The first version of `shell.read()` did a single non-blocking read with a fixed timeout, so it sometimes fired before bash had finished writing, or caught the tail end of an earlier command sitting in the buffer. Fixed by looping the read until the pseudo-terminal goes quiet for the timeout window, instead of reading once.

**`<UP,BROADCAST,RUNNING,MULTICAST>` in `ifconfig` output broke every subsequent message.** Output is rendered as `<pre>` HTML for monospace formatting; Telegram tried to parse `<UP,...>` as an unrecognized tag and rejected the whole message. Fixed by `html.escape()`-ing shell output before wrapping it in `<pre>`.

**Interactive programs (`nano`) get corrupted input.** `shell.send()` writes an entire line at once; a real terminal delivers keystrokes one at a time, which full-screen programs depend on. A `/ctrl <letter>` command was added to send individual control keys, but line-buffered `send()` is still not a substitute for real per-keystroke input.

---

## Security note

`totp.secret` and `.env` are excluded via `.gitignore` and were never committed. Cloning this repo gets you the code, not access — you generate your own TOTP secret and supply your own token.

---

## License

MIT — see [`LICENSE`](LICENSE).
