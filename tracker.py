import csv
import os
from datetime import datetime, timedelta


def load_existing_followup(filename):
    rows = []
    if not os.path.exists(filename):
        return rows

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            rows.append(row)

    return rows


def merge_new_leads_into_followup(existing_rows, new_results):
    existing_keys = set()
    merged = []

    for row in existing_rows:
        key = (row["website"], row["email"])
        existing_keys.add(key)
        merged.append(row)

    today = datetime.today().date()
    followup_date = today + timedelta(days=3)

    for row in new_results:
        key = (row["website"], row["email"])
        if key not in existing_keys:
            merged.append({
                "website": row["website"],
                "email": row["email"],
                "keyword": row["keyword"],
                "status": "new",
                "first_contact_date": today.isoformat(),
                "next_followup_date": followup_date.isoformat(),
                "notes": ""
            })
            existing_keys.add(key)

    return merged


def create_followup_file(rows, filename="followup.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "website",
            "email",
            "keyword",
            "status",
            "first_contact_date",
            "next_followup_date",
            "notes"
        ])

        for row in rows:
            writer.writerow([
                row["website"],
                row["email"],
                row["keyword"],
                row["status"],
                row["first_contact_date"],
                row["next_followup_date"],
                row["notes"]
            ])

    print(f"Saved follow-up tracker to {filename}")


def export_due_followups(filename="followup.csv", output_filename="due_followups.csv"):
    due_rows = []
    today = datetime.today().date().isoformat()

    if not os.path.exists(filename):
        return due_rows

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row["next_followup_date"] <= today and row["status"] != "replied":
                due_rows.append(row)

    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.writer(f)
        writer.writerow([
            "website",
            "email",
            "keyword",
            "status",
            "first_contact_date",
            "next_followup_date",
            "notes"
        ])
        for row in due_rows:
            writer.writerow([
                row["website"],
                row["email"],
                row["keyword"],
                row["status"],
                row["first_contact_date"],
                row["next_followup_date"],
                row["notes"]
            ])

    print(f"Saved due follow-ups to {output_filename}")
    return due_rows
