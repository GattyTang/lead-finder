from lead_finder.models import Lead
from lead_finder.service import LeadFilter, filter_leads, rank_leads


def test_filter_leads_by_industry_country_and_size() -> None:
    leads = [
        Lead("Acme", "SaaS", "US", 100, "https://acme.example"),
        Lead("Beta", "Fintech", "US", 80, "https://beta.example"),
        Lead("Gamma", "SaaS", "CA", 300, "https://gamma.example"),
    ]

    filtered = filter_leads(
        leads,
        LeadFilter(industry="saas", country="US", min_employees=50, max_employees=150),
    )

    assert [lead.company for lead in filtered] == ["Acme"]


def test_rank_leads_prioritizes_score() -> None:
    leads = [
        Lead("Small SaaS", "SaaS", "US", 30, "https://small.example"),
        Lead("Large Retail", "Retail", "US", 400, "https://large.example"),
        Lead("Large SaaS", "SaaS", "US", 350, "https://largesaas.example"),
    ]

    ranked = rank_leads(leads)

    assert [lead.company for lead in ranked] == ["Large SaaS", "Large Retail", "Small SaaS"]
