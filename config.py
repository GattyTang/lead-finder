from pathlib import Path

BASE_DIR = Path(__file__).resolve().parent

KEYWORDS_FILE = BASE_DIR / "keywords.txt"
LEADS_CSV = BASE_DIR / "leads.csv"
LEADS_XLSX = BASE_DIR / "leads.xlsx"
LETTERS_TXT = BASE_DIR / "letters.txt"
FOLLOWUP_CSV = BASE_DIR / "followup.csv"
DUE_FOLLOWUPS_CSV = BASE_DIR / "due_followups.csv"
LEADS_MASTER_CSV = BASE_DIR / "leads_master.csv"
MAC_LAUNCHD_PLIST = BASE_DIR / "com.leadfinder.daily.plist"

KEYWORDS = [
    "glass beads importer saudi arabia",
    "glass beads distributor uae",
    "road marking contractor saudi arabia",
    "traffic safety company dubai",
    "road marking paint supplier indonesia",
    "thermoplastic road marking company malaysia",
    "road marking contractor mexico",
    "traffic safety company brazil",
    "glass beads importer turkey",
    "road marking company thailand",
]

# =====================
# Search behavior
# =====================
SEARCH_ENGINES = ["duckduckgo", "bing", "google"]
MAX_RESULTS_PER_ENGINE = 6
REQUEST_TIMEOUT = 15
ENABLE_HOMEPAGE_SCRAPE = True
MAX_CONTACT_PAGES = 8
MAX_LEADS_PER_KEYWORD = 30

# =====================
# Product / letter settings
# =====================
PRODUCT_NAME = "glass beads for road marking"
PRODUCT_SHORT_NAME = "glass beads"
PRODUCT_APPLICATIONS = [
    "drop-on and premix road marking",
    "reflective traffic paint and thermoplastic marking",
    "airport / highway / municipal safety marking",
    "abrasive blasting and related industrial use",
]
EMAIL_ATTACHMENTS_OFFER = [
    "product catalog",
    "specification sheet",
    "packing details",
    "quotation",
]
SENDER_COMPANY = "Your Company"
SENDER_NAME = "Your Name"
SENDER_TITLE = "Sales Manager"
SENDER_WHATSAPP = "+86-000-0000-0000"
SENDER_EMAIL_SIGNATURE = "your_email@yourcompany.com"

# =====================
# Email sending
# =====================
AUTO_SEND_EMAILS = False
SEND_INITIAL_EMAILS = False
SEND_FOLLOWUP_EMAILS = False

SMTP_SERVER = "smtp.126.com"
SMTP_PORT = 465
SENDER_EMAIL = "your_email@yourcompany.com"
SENDER_PASSWORD = "your_smtp_authorization_code"
EMAIL_SUBJECT = "Supply of Glass Beads / Road Marking Materials"
FOLLOWUP_SUBJECT_7D = "Following up on glass beads / road marking materials"
FOLLOWUP_SUBJECT_30D = "Final follow-up regarding road marking materials"

INITIAL_FOLLOWUP_DAYS = 7
FINAL_FOLLOWUP_DAYS = 30

# =====================
# Lead filtering / scoring
# =====================
GENERIC_EMAIL_PREFIXES = {
    "info", "sales", "contact", "admin", "office", "enquiry", "inquiry", "support", "marketing",
    "service", "hello", "hi", "team", "business", "commercial", "purchase", "procurement",
}

BLOCKED_EMAIL_PREFIXES = {
    "noreply", "no-reply", "donotreply", "do-not-reply", "mailer-daemon", "postmaster",
    "test", "demo", "sample", "example",
}

FREE_EMAIL_DOMAINS = {
    "gmail.com", "outlook.com", "hotmail.com", "yahoo.com", "icloud.com", "163.com", "126.com",
    "qq.com", "aol.com", "proton.me", "protonmail.com",
}

DISPOSABLE_EMAIL_DOMAINS = {
    "mailinator.com", "guerrillamail.com", "10minutemail.com", "tempmail.com", "yopmail.com",
}

EMAIL_BLACKLIST_PARTS = [
    "example.com", "yourname@", "name@company", "test@", "demo@", "sample@",
    "noreply@", "no-reply@", "privacy@", "gdpr@", "unsubscribe@",
]

KEYWORD_SCORE_HINTS = {
    "importer": 18,
    "distributor": 16,
    "supplier": 14,
    "contractor": 12,
    "wholesaler": 15,
    "manufacturer": 6,
    "road marking": 12,
    "traffic safety": 10,
    "thermoplastic": 8,
    "glass beads": 8,
    "highway": 6,
    "airport": 6,
    "reflective": 6,
}

COUNTRY_HINTS = [
    "saudi arabia", "uae", "dubai", "abu dhabi", "qatar", "oman", "kuwait", "bahrain",
    "egypt", "morocco", "south africa", "kenya", "nigeria", "turkey",
    "indonesia", "malaysia", "thailand", "vietnam", "philippines", "singapore",
    "mexico", "brazil", "chile", "peru", "colombia", "argentina",
    "australia", "new zealand",
]
