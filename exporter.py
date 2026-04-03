import csv
from datetime import datetime, timedelta
from pathlib import Path
from typing import Iterable

from openpyxl import Workbook
from openpyxl.styles import Font

from config import FINAL_FOLLOWUP_DAYS, INITIAL_FOLLOWUP_DAYS

CSV_FIELDS = [
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
]


def save_to_csv(results: Iterable[dict], filename="leads.csv"):
    filename = Path(filename)
    with filename.open("w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(CSV_FIELDS)
        for row in results:
            writer.writerow([row.get(field, "") for field in CSV_FIELDS])
    print(f"Saved results to {filename}")


def save_to_excel(results: Iterable[dict], filename="leads.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"

    headers = [
        "Company Name",
        "Company Website",
        "Email",
        "Email Quality",
        "Email Quality Reason",
        "Phone",
        "Country",
        "Keyword",
        "Search Source",
        "Source Count",
        "Contact Page",
        "Lead Score",
        "Score Reason",
        "Status",
        "First Contact Date",
        f"Follow-up (+{INITIAL_FOLLOWUP_DAYS}d)",
        f"Final Follow-up (+{FINAL_FOLLOWUP_DAYS}d)",
        "Notes",
    ]
    ws.append(headers)

    for cell in ws[1]:
        cell.font = Font(bold=True)

    today = datetime.today().date()
    followup_1 = today + timedelta(days=INITIAL_FOLLOWUP_DAYS)
    followup_2 = today + timedelta(days=FINAL_FOLLOWUP_DAYS)

    for row in results:
        ws.append([
            row.get("company_name", ""),
            row.get("website", ""),
            row.get("email", ""),
            row.get("email_quality", ""),
            row.get("email_quality_reason", ""),
            row.get("phone", ""),
            row.get("country", ""),
            row.get("keyword", ""),
            row.get("search_source", ""),
            row.get("source_count", ""),
            row.get("contact_page", ""),
            row.get("score", ""),
            row.get("score_reason", ""),
            "new",
            today.isoformat(),
            followup_1.isoformat(),
            followup_2.isoformat(),
            "",
        ])

    widths = [24, 30, 28, 14, 28, 14, 14, 32, 20, 12, 35, 12, 45, 12, 16, 16, 18, 20]
    for idx, width in enumerate(widths, start=1):
        ws.column_dimensions[chr(64 + idx)].width = width

    wb.save(filename)
    print(f"Saved results to {filename}")
