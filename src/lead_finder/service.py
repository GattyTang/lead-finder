from __future__ import annotations

from dataclasses import dataclass

from .models import Lead


@dataclass(frozen=True)
class LeadFilter:
    industry: str | None = None
    country: str | None = None
    min_employees: int | None = None
    max_employees: int | None = None

    def matches(self, lead: Lead) -> bool:
        if self.industry and lead.normalized_industry() != self.industry.strip().lower():
            return False
        if self.country and lead.normalized_country() != self.country.strip().upper():
            return False
        if self.min_employees is not None and lead.employees < self.min_employees:
            return False
        if self.max_employees is not None and lead.employees > self.max_employees:
            return False
        return True


def filter_leads(leads: list[Lead], filters: LeadFilter) -> list[Lead]:
    return [lead for lead in leads if filters.matches(lead)]


def score_lead(lead: Lead) -> int:
    base = 50
    employee_bonus = min(lead.employees // 10, 40)
    industry_bonus = 10 if lead.normalized_industry() in {"saas", "software"} else 0
    return base + employee_bonus + industry_bonus


def rank_leads(leads: list[Lead]) -> list[Lead]:
    return sorted(leads, key=score_lead, reverse=True)
