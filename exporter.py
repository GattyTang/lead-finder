import csv
from openpyxl import Workbook


def save_to_csv(results, filename="leads.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow(["keyword", "website", "email", "contact_page"])

        for row in results:
            writer.writerow([
                row["keyword"],
                row["website"],
                row["email"],
                row["contact_page"]
            ])

    print(f"Saved results to {filename}")


def save_to_excel(results, filename="leads.xlsx"):
    wb = Workbook()
    ws = wb.active
    ws.title = "Leads"

    ws.append(["keyword", "website", "email", "contact_page"])

    for row in results:
        ws.append([
            row["keyword"],
            row["website"],
            row["email"],
            row["contact_page"]
        ])

    wb.save(filename)
    print(f"Saved results to {filename}")
