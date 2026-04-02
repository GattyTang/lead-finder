import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from config import SMTP_SERVER, SMTP_PORT, SENDER_EMAIL, SENDER_PASSWORD, EMAIL_SUBJECT


def build_email_body(row):
    keyword = row["keyword"]
    return f"""
Dear Sir/Madam,

We found your company through your website and understand that your business may be related to {keyword}.

We are a supplier of glass beads and related road marking materials, and we would like to explore possible cooperation with your company.

Our products may be suitable for:
- road marking applications
- reflective traffic materials
- abrasive / blasting use
- related industrial uses

If you are interested, we can send you:
- product catalog
- specifications
- photos
- quotation

Looking forward to your reply.

Best regards
""".strip()


def send_email(to_email, body):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = EMAIL_SUBJECT

    msg.attach(MIMEText(body, "plain"))

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    server.quit()


def send_bulk_emails(results):
    unique_targets = []
    seen = set()

    for row in results:
        key = (row["website"], row["email"])
        if key not in seen:
            seen.add(key)
            unique_targets.append(row)

    for row in unique_targets:
        email = row["email"]
        body = build_email_body(row)

        try:
            send_email(email, body)
            print(f"Email sent to {email}")
        except Exception as e:
            print(f"Failed to send email to {email}: {e}")
