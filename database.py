import csv
from pathlib import Path
from typing import Dict, Iterable, List, Set, Tuple
from urllib.parse import urlparse

from config import (
    FREE_EMAIL_DOMAINS,
    GENERIC_EMAIL_PREFIXES,
    KEYWORD_SCORE_HINTS,
)

MASTER_FIELDS = [
    "company_name",
    "website",
    "email",
    "email_quality",
    "email_quality_reason",
    "phone",
    "country",
    "keyword",
    "search_source",
    "source_count",
    "contact_page",
    "score",
    "score_reason",
    "status",
]


def normalize_key(website: str, email: str) -> Tuple[str, str]:
    return website.strip().lower().rstrip("/"), email.strip().lower()


def load_csv_rows(path: Path) -> List[Dict[str, str]]:
    if not path.exists():
        return []
    with path.open("r", encoding="utf-8", newline="") as f:
        return list(csv.DictReader(f))


def ensure_master_file(path: Path) -> None:
    if path.exists():
        return
    with path.open("w", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS)
        writer.writeheader()


def load_master_keys(path: Path) -> Set[Tuple[str, str]]:
    rows = load_csv_rows(path)
    return {
        normalize_key(row.get("website", ""), row.get("email", ""))
        for row in rows
        if row.get("website") and row.get("email")
    }


def _extract_domain(value: str) -> str:
    value = (value or "").strip().lower()
    if not value:
        return ""
    if "://" in value:
        host = urlparse(value).netloc.lower()
    else:
        host = value.split("@")[-1]
    return host.removeprefix("www.")


def score_lead(row: Dict[str, str]) -> Dict[str, str]:
    keyword = row.get("keyword", "").lower()
    email = row.get("email", "").lower()
    website = row.get("website", "").lower()
    contact_page = row.get("contact_page", "").lower()
    quality = row.get("email_quality", "").lower()

    score = 40
    reasons: List[str] = ["base:40"]

    for hint, points in KEYWORD_SCORE_HINTS.items():
        if hint in keyword:
            score += points
            reasons.append(f"keyword:{hint}+{points}")

    local = email.split("@")[0] if "@" in email else ""
    email_domain = _extract_domain(email)
    website_domain = _extract_domain(website)

    if local in GENERIC_EMAIL_PREFIXES:
        score -= 10
        reasons.append("generic_email:-10")
    else:
        score += 8
        reasons.append("person_like_email:+8")

    if quality == "high":
        score += 16
        reasons.append("email_quality:high+16")
    elif quality == "medium":
        score += 8
        reasons.append("email_quality:medium+8")
    elif quality == "low":
        score -= 10
        reasons.append("email_quality:low-10")

    if contact_page and contact_page != website:
        score += 8
        reasons.append("contact_page:+8")

    if row.get("country"):
        score += 5
        reasons.append("country_match:+5")

    if email_domain and website_domain and email_domain == website_domain:
        score += 10
        reasons.append("domain_match:+10")
    elif email_domain in FREE_EMAIL_DOMAINS:
        score -= 6
        reasons.append("free_email:-6")

    source_count = int(row.get("source_count", "0") or 0)
    if source_count >= 2:
        bonus = min(10, source_count * 3)
        score += bonus
        reasons.append(f"multi_engine:+{bonus}")

    if row.get("company_name"):
        score += 4
        reasons.append("company_name:+4")

    score = max(0, min(100, score))
    row["score"] = str(score)
    row["score_reason"] = "; ".join(reasons)
    row["status"] = row.get("status", "new") or "new"
    return row


def score_leads(rows: Iterable[Dict[str, str]]) -> List[Dict[str, str]]:
    return [score_lead(dict(row)) for row in rows]


def append_new_leads_to_master(path: Path, rows: Iterable[Dict[str, str]]) -> int:
    ensure_master_file(path)
    existing = load_master_keys(path)
    new_rows: List[Dict[str, str]] = []

    for row in rows:
        key = normalize_key(row.get("website", ""), row.get("email", ""))
        if not all(key) or key in existing:
            continue
        existing.add(key)
        new_rows.append({field: row.get(field, "") for field in MASTER_FIELDS})

    if not new_rows:
        return 0

    with path.open("a", encoding="utf-8", newline="") as f:
        writer = csv.DictWriter(f, fieldnames=MASTER_FIELDS)
        for row in new_rows:
            writer.writerow(row)
    return len(new_rows)
