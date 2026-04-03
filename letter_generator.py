from typing import Iterable

from config import (
    EMAIL_ATTACHMENTS_OFFER,
    PRODUCT_APPLICATIONS,
    PRODUCT_NAME,
    PRODUCT_SHORT_NAME,
    SENDER_COMPANY,
    SENDER_EMAIL_SIGNATURE,
    SENDER_NAME,
    SENDER_TITLE,
    SENDER_WHATSAPP,
)


def _business_hint(keyword: str) -> str:
    k = keyword.lower()
    if "importer" in k:
        return "importing and sourcing"
    if "distributor" in k or "wholesaler" in k:
        return "distribution and resale"
    if "contractor" in k:
        return "project contracting and execution"
    if "manufacturer" in k:
        return "manufacturing and supply"
    return "traffic safety and road marking"


def _market_hint(row: dict) -> str:
    country = row.get("country", "")
    if country:
        return f" in {country}"
    return ""


def _salutation(row: dict) -> str:
    company = row.get("company_name") or "there"
    return f"Dear {company} Team,"


def _signature() -> str:
    return f"""
Best regards,
{SENDER_NAME}
{SENDER_TITLE}
{SENDER_COMPANY}
Email: {SENDER_EMAIL_SIGNATURE}
WhatsApp: {SENDER_WHATSAPP}
""".strip()


def _build_initial_letter(row: dict) -> str:
    website = row["website"]
    email = row["email"]
    keyword = row["keyword"]
    score = row.get("score", "")
    company = row.get("company_name", "")
    business_hint = _business_hint(keyword)
    market_hint = _market_hint(row)
    apps = "\n".join([f"- {item}" for item in PRODUCT_APPLICATIONS])
    offers = "\n".join([f"- {item}" for item in EMAIL_ATTACHMENTS_OFFER])

    return f"""
==================================================
Company: {company}
Website: {website}
Email: {email}
Keyword: {keyword}
Lead Score: {score}
Email Quality: {row.get('email_quality', '')}
Search Source: {row.get('search_source', '')}
==================================================

Subject: Reliable Supply of {PRODUCT_SHORT_NAME.title()} for Road Marking

{_salutation(row)}

We found your company through public search results and noticed that your business may be related to {business_hint}{market_hint}.

We are a China-based supplier of {PRODUCT_NAME}, and we would like to explore whether there may be a fit between your current sourcing needs and our product range.

Our materials are commonly used for:
{apps}

If this line is relevant for your team, we can send:
{offers}

If possible, please let us know your target specification, annual volume, and destination port so we can prepare a more accurate offer.

{_signature()}
""".strip()


def _build_followup_letter(row: dict, stage: int) -> str:
    company = row.get("company_name", "")
    if stage == 1:
        subject = f"Following up on {PRODUCT_SHORT_NAME} supply"
        body = f"""
{_salutation(row)}

Just following up on my previous email regarding {PRODUCT_NAME}.

Since your company appears to be active in { _business_hint(row['keyword']) }{ _market_hint(row) }, I thought this might still be relevant for your team.

If you have any ongoing demand, we can send specification options, packing details, and a quotation for reference.

{_signature()}
""".strip()
    else:
        subject = f"Final follow-up regarding {PRODUCT_SHORT_NAME}"
        body = f"""
{_salutation(row)}

This is one last follow-up from my side regarding {PRODUCT_NAME}.

If {company or 'your team'} has any demand now or later, I would be glad to stay in touch and prepare a suitable offer whenever needed.

Thank you for your time.

{_signature()}
""".strip()

    return f"""
==================================================
Company: {row.get('company_name', '')}
Website: {row['website']}
Email: {row['email']}
Stage: follow-up {stage}
==================================================

Subject: {subject}

{body}
""".strip()


def generate_letters(results: Iterable[dict], filename="letters.txt"):
    unique_targets = []
    seen = set()

    for row in results:
        key = (row["website"], row["email"])
        if key not in seen:
            seen.add(key)
            unique_targets.append(row)

    with open(filename, "w", encoding="utf-8") as f:
        for row in unique_targets:
            f.write(_build_initial_letter(row) + "\n\n")
            f.write(_build_followup_letter(row, 1) + "\n\n")
            f.write(_build_followup_letter(row, 2) + "\n\n")

    print(f"Saved letters to {filename}")
