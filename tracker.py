import csv
import os
from datetime import datetime, timedelta
from typing import Dict, List

from config import FINAL_FOLLOWUP_DAYS, INITIAL_FOLLOWUP_DAYS

FOLLOWUP_FIELDS = [
    "company_name",
    "website",
    "email",
    "keyword",
    "score",
    "email_quality",
    "status",
    "followup_stage",
    "first_contact_date",
    "last_contact_date",
    "next_followup_date",
    "notes",
]


def today_iso() -> str:
    return datetime.today().date().isoformat()


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
    merged: List[Dict[str, str]] = []

    for row in existing_rows:
        key = (row["website"].strip().lower(), row["email"].strip().lower())
        existing_keys.add(key)
        normalized = {field: row.get(field, "") for field in FOLLOWUP_FIELDS}
        if not normalized.get("followup_stage"):
            normalized["followup_stage"] = "0"
        merged.append(normalized)

    today = datetime.today().date()
    first_followup = today + timedelta(days=INITIAL_FOLLOWUP_DAYS)

    for row in new_results:
        key = (row["website"].strip().lower(), row["email"].strip().lower())
        if key not in existing_keys:
            merged.append({
                "company_name": row.get("company_name", ""),
                "website": row["website"],
                "email": row["email"],
                "keyword": row["keyword"],
                "score": row.get("score", ""),
                "email_quality": row.get("email_quality", ""),
                "status": "new",
                "followup_stage": "0",
                "first_contact_date": today.isoformat(),
                "last_contact_date": "",
                "next_followup_date": first_followup.isoformat(),
                "notes": "",
            })
            existing_keys.add(key)

    return merged


def create_followup_file(rows, filename="followup.csv"):
    with open(filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FOLLOWUP_FIELDS)
        writer.writeheader()
        for row in rows:
            writer.writerow({field: row.get(field, "") for field in FOLLOWUP_FIELDS})
    print(f"Saved follow-up tracker to {filename}")


def export_due_followups(filename="followup.csv", output_filename="due_followups.csv"):
    due_rows = []
    today = today_iso()

    if not os.path.exists(filename):
        return due_rows

    with open(filename, "r", encoding="utf-8") as f:
        reader = csv.DictReader(f)
        for row in reader:
            if row.get("status") == "replied":
                continue
            if row.get("next_followup_date") and row["next_followup_date"] <= today:
                due_rows.append(row)

    with open(output_filename, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=FOLLOWUP_FIELDS)
        writer.writeheader()
        for row in due_rows:
            writer.writerow({field: row.get(field, "") for field in FOLLOWUP_FIELDS})

    print(f"Saved due follow-ups to {output_filename}")
    return due_rows


def update_rows_after_followup_send(rows: List[Dict[str, str]], sent_keys):
    today = datetime.today().date()
    for row in rows:
        key = (row.get("website", "").strip().lower(), row.get("email", "").strip().lower())
        if key not in sent_keys:
            continue

        current_stage = int(row.get("followup_stage", "0") or 0)
        next_stage = current_stage + 1
        row["followup_stage"] = str(next_stage)
        row["last_contact_date"] = today.isoformat()

        if next_stage == 1:
            row["status"] = "followup_1_sent"
            row["next_followup_date"] = (today + timedelta(days=FINAL_FOLLOWUP_DAYS - INITIAL_FOLLOWUP_DAYS)).isoformat()
        elif next_stage >= 2:
            row["status"] = "followup_2_sent"
            row["next_followup_date"] = ""
    return rows
