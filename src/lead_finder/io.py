from __future__ import annotations

import csv
from pathlib import Path
from typing import Iterable

from .models import Lead


REQUIRED_COLUMNS = {"company", "industry", "country", "employees", "website"}


def read_leads(path: str | Path) -> list[Lead]:
    csv_path = Path(path)
    with csv_path.open("r", newline="", encoding="utf-8") as fh:
        reader = csv.DictReader(fh)
        headers = set(reader.fieldnames or [])
        missing = REQUIRED_COLUMNS - headers
        if missing:
            missing_cols = ", ".join(sorted(missing))
            raise ValueError(f"Missing required columns: {missing_cols}")

        leads: list[Lead] = []
        for row in reader:
            leads.append(
                Lead(
                    company=row["company"].strip(),
                    industry=row["industry"].strip(),
                    country=row["country"].strip(),
                    employees=int(row["employees"]),
                    website=row["website"].strip(),
                )
            )
    return leads


def write_leads(path: str | Path, leads: Iterable[Lead]) -> None:
    csv_path = Path(path)
    with csv_path.open("w", newline="", encoding="utf-8") as fh:
        writer = csv.DictWriter(
            fh,
            fieldnames=["company", "industry", "country", "employees", "website"],
        )
        writer.writeheader()
        for lead in leads:
            writer.writerow(
                {
                    "company": lead.company,
                    "industry": lead.industry,
                    "country": lead.country,
                    "employees": lead.employees,
                    "website": lead.website,
                }
            )
