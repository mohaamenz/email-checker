import dns.resolver

def txt_records(name: str) -> list[str]:
    try:
        return [r.to_text().strip('"') for r in dns.resolver.resolve(name, "TXT")]
    except Exception:
        return []

def check_email_auth(domain: str, dkim_selector: str = "default") -> dict:
    spf = [t for t in txt_records(domain) if t.startswith("v=spf1")]
    dkim = txt_records(f"{dkim_selector}._domainkey.{domain}")
    dmarc = [t for t in txt_records(f"_dmarc.{domain}") if t.startswith("v=DMARC1")]
    return {
        "spf":   {"found": bool(spf), "records": spf},
        "dkim":  {"found": bool(dkim), "records": dkim},
        "dmarc": {"found": bool(dmarc), "records": dmarc},
        "score": sum([bool(spf), bool(dkim), bool(dmarc)]),  # 0/3
    }