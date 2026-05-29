from dataclasses import dataclass


@dataclass(frozen=True)
class Lead:
    company: str
    industry: str
    country: str
    employees: int
    website: str

    def normalized_industry(self) -> str:
        return self.industry.strip().lower()

    def normalized_country(self) -> str:
        return self.country.strip().upper()
