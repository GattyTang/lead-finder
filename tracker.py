import csv
from datetime import datetime, timedelta


def create_followup_file(results, filename="followup.csv"):
    unique_targets = []
    seen = set()

    for row in results:
        key = (row["website"], row["email"])
        if key not in seen:
            seen.add(key)
            unique_targets.append(row)

    today = datetime.today().date()
    followup_date = today + timedelta(days=3)

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

        for row in unique_targets:
            writer.writerow([
                row["website"],
                row["email"],
                row["keyword"],
                "new",
                today.isoformat(),
                followup_date.isoformat(),
                ""
            ])

    print(f"Saved follow-up tracker to {filename}")
