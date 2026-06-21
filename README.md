# PwnedChecker

🌐 **Live demo:** [pwned-checker.onrender.com](https://pwned-checker.onrender.com)

A cybersecurity tool that checks whether your password has appeared in known data breaches, using the **k-Anonymity** model to ensure your password **never leaves your device**.

---

## How k-Anonymity works

This is the core technical concept that makes the tool secure.

**The naive approach (wrong):** Sending your password — or its full hash — to an external server creates a new security risk. Any network interceptor, server log, or vulnerability in the third-party service could expose it.

**The solution — k-Anonymity:**

```
Password: "MyPassword123!"
           ↓
SHA-1 Hash: A94C3B2F8E1D5C7F9A2B4E6D8F0C1A3B5E7D9F2A
           ↓
Prefix (5 chars):  A94C3   ← Only this is sent over the network
Suffix (35 chars): B2F8E1D5C7F9A2B4E6D8F0C1A3B5E7D9F2A  ← Stays local
           ↓
HIBP API returns ~500 hashes that start with "A94C3"
           ↓
The suffix is looked up locally in that list
           ↓
Result: Found/Not found — without ever revealing the actual password
```

**Why is this secure?** With only 5 hex characters, there are 16⁵ = 1,048,576 possible prefixes. The HIBP server returns ~500 hashes per prefix, meaning your password hides among ~500 candidates. It is mathematically impossible for the server to determine which password you checked.

---

## Features

| Feature | Description |
|---------|-------------|
| k-Anonymity | Only 5 SHA-1 hash characters leave the device |
| Strength meter | Evaluates 6 criteria in real time, client-side |
| Password reveal | Toggle to show/hide characters |
| Secure generator | Uses `window.crypto.getRandomValues()` with rejection sampling — never `Math.random()` |
| Rate limiting | Max 10 requests per minute per IP |
| Visual feedback | Green screen (safe) or red + scanlines (compromised) |
| No JS frameworks | Pure vanilla JS, instant load |

---

## Local setup

```bash
# 1. Clone the repository
git clone https://github.com/your-username/pwned-checker
cd pwned-checker

# 2. Create a virtual environment
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate

# 3. Install dependencies
pip install -r requirements.txt

# 4. Run the server
python app.py

# 5. Open http://localhost:8000
```

---

## Project structure

```
pwned-checker/
├── app.py           # FastAPI backend — SHA-1 logic + HIBP integration
├── index.html       # Frontend — UI + strength meter + vanilla JS
├── requirements.txt # Python dependencies
└── README.md
```

---

## Deployment

### Backend (Render)
1. Push the code to a public GitHub repository
2. On [render.com](https://render.com), create a new **Web Service**
3. Connect your repository
4. Configure:
   - **Build Command:** `pip install -r requirements.txt`
   - **Start Command:** `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Deploy 

The frontend is served directly by FastAPI, so there is no separate deployment step.

---

## Tech stack

- **Backend:** Python 3.11+ · FastAPI · httpx · slowapi
- **Frontend:** HTML5 · CSS3 · Vanilla JavaScript
- **Security:** SHA-1 via `hashlib` · k-Anonymity model · Web Crypto API
- **External API:** [Have I Been Pwned v3](https://haveibeenpwned.com/API/v3)

### Why `crypto.getRandomValues()` instead of `Math.random()`?

`Math.random()` is a deterministic PRNG — given the same internal state, it produces the same sequence. An attacker with enough information could predict its output.

`window.crypto.getRandomValues()` uses the operating system's CSPRNG, which collects real entropy from hardware interrupts, mouse movement, and I/O timing. The output is cryptographically unpredictable.

The generator also applies **rejection sampling** to eliminate modulo bias: if the character set size doesn't divide evenly into the Uint32 range, the first few characters would appear slightly more often. Rejection sampling discards values outside the exact usable range, guaranteeing a uniform distribution.

---

## References

- [HIBP k-Anonymity model](https://haveibeenpwned.com/API/v3#SearchingPwnedPasswordsByRange)
- [Troy Hunt — Introducing 306 Million Freely Downloadable Pwned Passwords](https://www.troyhunt.com/introducing-306-million-freely-downloadable-pwned-passwords/)
- [Cloudflare — Validating leaked passwords with k-anonymity](https://blog.cloudflare.com/validating-leaked-passwords-with-k-anonymity/)

---

*Built with Python + FastAPI · No password is ever stored or transmitted.*
