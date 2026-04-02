from openpyxl import Workbook
import csv
from datetime import datetime, timedelta


def save_to_csv(results, filename="leads.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "website",
            "email",
            "phone",
            "country",
            "keyword",
            "contact_page"
        ])

        for row in results:
            writer.writerow([
                row.get("website", ""),
                row.get("email", ""),
                row.get("phone", ""),
                row.get("country", ""),
                row.get("keyword", ""),
                row.get("contact_page", "")
            ])

    print(f"Saved results to {filename}")


def save_to_excel(results, filename="leads.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"

    ws.append([
        "Company Website",
        "Email",
        "Phone",
        "Country",
        "Keyword",
        "Contact Page",
        "Status",
        "First Contact Date",
        "Next Follow-up",
        "Notes"
    ])

    today = datetime.today().date()
    followup = today + timedelta(days=3)

    for row in results:
        ws.append([
            row.get("website", ""),
            row.get("email", ""),
            row.get("phone", ""),
            row.get("country", ""),
            row.get("keyword", ""),
            row.get("contact_page", ""),
            "new",
            today.isoformat(),
            followup.isoformat(),
            ""
        ])

    wb.save(filename)
    print(f"Saved results to {filename}")
