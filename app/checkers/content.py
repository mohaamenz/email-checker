import re
from urllib.parse import urlparse

SHORTENERS = {"bit.ly", "tinyurl.com", "t.co", "goo.gl", "cutt.ly", "is.gd"}
RISKY_TLDS = {".zip", ".mov", ".top", ".xyz", ".click", ".link"}

def lint_subject(subject: str) -> list[str]:
    issues = []
    if len(subject) > 60:
        issues.append("Subject twil (>60 chars) — kayt9te3 f mobile")
    letters = [c for c in subject if c.isalpha()]
    if letters and sum(c.isupper() for c in letters) / len(letters) > 0.4:
        issues.append("Bzzaf dyal MAJUSCULES")
    if subject.count("!") >= 3:
        issues.append("Trop de '!!!'")
    for w in ["free", "urgent", "act now", "click here", "100%", "win"]:
        if w in subject.lower():
            issues.append(f"Keyword risky: '{w}'")
    return issues

def lint_body(body: str) -> list[str]:
    issues = []
    if not body.strip():
        return ["Body khawi"]
    urls = re.findall(r"https?://[^\s\"'>]+", body)
    for url in urls:
        host = urlparse(url).netloc.lower()
        if host in SHORTENERS:
            issues.append(f"URL shortener: {host}")
        if any(host.endswith(t) for t in RISKY_TLDS):
            issues.append(f"TLD mkhater: {host}")
    if "unsubscribe" not in body.lower() and "désabonnement" not in body.lower():
        issues.append("Ma kaynch lien unsubscribe")
    if len(re.findall(r"\b[A-Z]{4,}\b", body)) > 2:
        issues.append("Bzzaf dyal mots en MAJUSCULES")
    if body.count("!") > 5:
        issues.append("Trop de '!'")
    return issues