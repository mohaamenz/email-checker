import subprocess, tempfile, os
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from .checkers.auth import check_email_auth
from .checkers.content import lint_subject, lint_body

app = FastAPI(title="Email Deliverability Checker")

class DomainCheck(BaseModel):
    domain: str
    dkim_selector: str = "default"

class ContentCheck(BaseModel):
    subject: str
    body: str = ""
    from_domain: str = ""

@app.get("/")
def home():
    return {"status": "ok", "docs": "/docs"}

@app.post("/check/domain")
def check_domain(req: DomainCheck):
    domain = req.domain.strip().lower()
    if not domain.replace("-", "").replace(".", "").isalnum():
        raise HTTPException(400, "Domain invalide")
    return check_email_auth(domain, req.dkim_selector)

@app.post("/check/content")
def check_content(req: ContentCheck):
    return {
        "subject_issues": lint_subject(req.subject),
        "body_issues": lint_body(req.body),
    }

@app.post("/check/spamassassin")
def check_sa(req: ContentCheck):
    eml = (
        f"From: test@{req.from_domain or 'example.com'}\n"
        f"To: test@example.com\nSubject: {req.subject}\n"
        f"MIME-Version: 1.0\nContent-Type: text/plain; charset=utf-8\n\n{req.body}"
    )
    with tempfile.NamedTemporaryFile("w", suffix=".eml", delete=False, encoding="utf-8") as f:
        f.write(eml)
        path = f.name
    try:
        r = subprocess.run(["spamassassin", "-t", path],
                           capture_output=True, text=True, timeout=30)
        return {"report": r.stdout[-3000:]}
    finally:
        os.unlink(path)