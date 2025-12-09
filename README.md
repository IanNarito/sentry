# SENTRY - Advanced Reconnaissance Platform

![Sentry Dashboard](img/dsentry.png)
**SENTRY** is a full-stack, automated cybersecurity reconnaissance framework designed for Red Team operations and Bug Bounty hunting. It integrates multiple scanning modules into a unified dashboard, automating the "Discovery" and "Enumeration" phases of an engagement.

Unlike passive scanners, SENTRY actively analyzes targets, identifies vulnerabilities (CVEs), detects defenses (WAFs), and visualizes infrastructure topology.

---

## 🚀 Key Features

### 🔍 Active & Passive Recon
* **Nmap Port Scanning:** Fast, asynchronous port discovery and service versioning.
* **Subdomain Enumeration:** Passive gathering via Certificate Transparency logs (crt.sh).
* **DNS Resolution:** Automatic A/AAAA/CNAME record resolution.
* **Directory Fuzzing:** Active brute-forcing of common hidden paths (`/.env`, `/admin`, `/backup`).

### 🛡️ Threat Intelligence & Analysis
* **CVE Mapping:** Automatically correlates detected software versions with known vulnerabilities (NVD/CVSS).
* **WAF Detection:** Fingerprints firewalls (Cloudflare, AWS, Akamai) to advise on evasion limits.
* **Honeypot Detection:** Heuristic analysis to identify deceptive trap servers.
* **SSL/TLS Audit:** Checks for expired certificates, weak ciphers, and self-signed chains.

### 📊 Visualization & Reporting
* **Network Topology Graph:** Interactive 2D node-link diagram of domains, subdomains, and IPs.
* **Professional Reporting:** Generates audit-ready PDF reports with Executive Summaries and Remediation steps.
* **Dashboard Analytics:** Real-time charts for severity distribution and scan activity.

---

## 🛠️ Tech Stack

* **Frontend:** React 18 (Vite), Tailwind CSS, Recharts, React-Force-Graph.
* **Backend:** Python 3.10, FastAPI, SQLAlchemy.
* **Database:** PostgreSQL.
* **Task Queue:** Celery + Redis.
* **Scanning Engine:** Nmap, Wafw00f, Whois, Requests, SSL.

---

## 📦 Installation (Docker - Recommended)

The easiest way to run SENTRY is via Docker Compose. This handles the database, Redis, and all dependencies (including Nmap) automatically.

### Prerequisites
* Docker & Docker Compose installed.

### Steps
1.  **Clone the repository**
    ```bash
    git clone https://github.com/IanNarito/sentry.git
    cd sentry
    ```

2.  **Start the Stack**
    ```bash
    docker-compose up --build
    ```

3.  **Access the Platform**
    * **Frontend:** [http://localhost:5173](http://localhost:5173)
    * **API Docs:** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🔧 Installation (Manual / Kali Linux)

If you prefer running it natively (e.g., on Kali Linux without Docker):

### Prerequisites
* Python 3.10+
* Node.js 18+
* PostgreSQL & Redis (Running locally)
* **Nmap** (`sudo apt install nmap`)

### 1. Backend Setup
```bash
cd backend
python -m venv .venv
source .venv/bin/activate  # or .venv\Scripts\activate on Windows
pip install -r requirements.txt
cd ..
uvicorn backend.app.main:app --reload
```

### 2. Worker Setup (Open new terminal)
```bash
source .venv/bin/activate
# On Linux/Mac:
celery -A backend.app.workers.celery worker --loglevel=info
# On Windows:
celery -A backend.app.workers.celery worker --loglevel=info --pool=solo
```

### 3. Frontend Setup (Open new terminal)
```bash
cd frontend
npm install
npm run dev
```
