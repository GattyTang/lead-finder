import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from typing import Dict, Iterable, Set, Tuple

from config import (
    EMAIL_SUBJECT,
    FOLLOWUP_SUBJECT_30D,
    FOLLOWUP_SUBJECT_7D,
    SENDER_EMAIL,
    SENDER_PASSWORD,
    SMTP_PORT,
    SMTP_SERVER,
)
from letter_generator import _build_followup_letter, _build_initial_letter


def _extract_body(full_letter: str) -> str:
    marker = "\n\n"
    parts = full_letter.split(marker, 2)
    return parts[-1].strip() if len(parts) >= 3 else full_letter


def build_email_body(row: Dict[str, str]) -> str:
    return _extract_body(_build_initial_letter(row))


def build_followup_body(row: Dict[str, str], stage: int) -> str:
    return _extract_body(_build_followup_letter(row, stage))


def _send_message(to_email: str, subject: str, body: str):
    msg = MIMEMultipart()
    msg["From"] = SENDER_EMAIL
    msg["To"] = to_email
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    if SMTP_PORT == 465:
        server = smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT, timeout=20)
    else:
        server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT, timeout=20)
        server.starttls()

    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, to_email, msg.as_string())
    server.quit()


def send_initial_emails(results: Iterable[Dict[str, str]]):
    sent = 0
    for row in results:
        try:
            _send_message(row["email"], EMAIL_SUBJECT, build_email_body(row))
            print(f"Initial email sent to {row['email']}")
            sent += 1
        except Exception as e:
            print(f"Failed to send initial email to {row['email']}: {e}")
    return sent


def send_due_followups(rows: Iterable[Dict[str, str]]) -> Set[Tuple[str, str]]:
    sent_keys: Set[Tuple[str, str]] = set()
    for row in rows:
        stage = int(row.get("followup_stage", "0") or 0)
        subject = FOLLOWUP_SUBJECT_7D if stage < 1 else FOLLOWUP_SUBJECT_30D
        next_stage = 1 if stage < 1 else 2
        try:
            _send_message(row["email"], subject, build_followup_body(row, next_stage))
            key = (row["website"].strip().lower(), row["email"].strip().lower())
            sent_keys.add(key)
            print(f"Follow-up stage {next_stage} sent to {row['email']}")
        except Exception as e:
            print(f"Failed to send follow-up to {row['email']}: {e}")
    return sent_keys
