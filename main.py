from pathlib import Path

from config import (
    AUTO_SEND_EMAILS,
    DUE_FOLLOWUPS_CSV,
    FOLLOWUP_CSV,
    KEYWORDS,
    KEYWORDS_FILE,
    LEADS_CSV,
    LEADS_MASTER_CSV,
    LEADS_XLSX,
    LETTERS_TXT,
    MAC_LAUNCHD_PLIST,
    SEND_FOLLOWUP_EMAILS,
    SEND_INITIAL_EMAILS,
)
from database import append_new_leads_to_master, load_master_keys, score_leads
from exporter import save_to_csv, save_to_excel
from letter_generator import generate_letters
from mailer import send_due_followups, send_initial_emails
from scraper import collect_leads
from tracker import (
    create_followup_file,
    export_due_followups,
    load_existing_followup,
    merge_new_leads_into_followup,
    update_rows_after_followup_send,
)


def load_keywords() -> list[str]:
    if Path(KEYWORDS_FILE).exists():
        lines = Path(KEYWORDS_FILE).read_text(encoding="utf-8").splitlines()
        file_keywords = [line.strip() for line in lines if line.strip() and not line.strip().startswith("#")]
        if file_keywords:
            return file_keywords
    return KEYWORDS


def write_mac_launchd_template(target_path: Path):
    project_dir = target_path.parent
    content = f"""<?xml version=\"1.0\" encoding=\"UTF-8\"?>
<!DOCTYPE plist PUBLIC \"-//Apple//DTD PLIST 1.0//EN\" \"http://www.apple.com/DTDs/PropertyList-1.0.dtd\">
<plist version=\"1.0\">
<dict>
    <key>Label</key>
    <string>com.leadfinder.daily</string>
    <key>ProgramArguments</key>
    <array>
        <string>/usr/bin/python3</string>
        <string>{project_dir / 'main.py'}</string>
    </array>
    <key>WorkingDirectory</key>
    <string>{project_dir}</string>
    <key>StartCalendarInterval</key>
    <dict>
        <key>Hour</key>
        <integer>9</integer>
        <key>Minute</key>
        <integer>0</integer>
    </dict>
    <key>StandardOutPath</key>
    <string>{project_dir / 'leadfinder.log'}</string>
    <key>StandardErrorPath</key>
    <string>{project_dir / 'leadfinder.error.log'}</string>
    <key>RunAtLoad</key>
    <true/>
</dict>
</plist>
"""
    target_path.write_text(content, encoding="utf-8")


def main():
    print("Starting lead finder...")
    keywords = load_keywords()
    print(f"Keywords loaded: {len(keywords)}")

    existing_master_keys = load_master_keys(Path(LEADS_MASTER_CSV))
    print(f"Known leads in master DB: {len(existing_master_keys)}")

    results = collect_leads(keywords, existing_master_keys)
    results = score_leads(results)

    save_to_csv(results, LEADS_CSV)
    save_to_excel(results, LEADS_XLSX)
    generate_letters(results, LETTERS_TXT)

    added_to_master = append_new_leads_to_master(Path(LEADS_MASTER_CSV), results)

    existing_followup = load_existing_followup(FOLLOWUP_CSV)
    merged_followup = merge_new_leads_into_followup(existing_followup, results)
    create_followup_file(merged_followup, FOLLOWUP_CSV)
    due_rows = export_due_followups(FOLLOWUP_CSV, DUE_FOLLOWUPS_CSV)

    if AUTO_SEND_EMAILS and SEND_INITIAL_EMAILS and results:
        send_initial_emails(results)
    else:
        print("Initial email auto-send is OFF.")

    if AUTO_SEND_EMAILS and SEND_FOLLOWUP_EMAILS and due_rows:
        sent_keys = send_due_followups(due_rows)
        if sent_keys:
            updated_rows = update_rows_after_followup_send(load_existing_followup(FOLLOWUP_CSV), sent_keys)
            create_followup_file(updated_rows, FOLLOWUP_CSV)
            due_rows = export_due_followups(FOLLOWUP_CSV, DUE_FOLLOWUPS_CSV)
    else:
        print("Follow-up auto-send is OFF.")

    write_mac_launchd_template(Path(MAC_LAUNCHD_PLIST))

    print("\nDone.")
    print(f"New leads found today: {len(results)}")
    print(f"New leads appended to master DB: {added_to_master}")
    print(f"Due follow-ups today: {len(due_rows)}")
    print("Generated files:")
    print(f"- {LEADS_CSV.name}")
    print(f"- {LEADS_XLSX.name}")
    print(f"- {LETTERS_TXT.name}")
    print(f"- {FOLLOWUP_CSV.name}")
    print(f"- {DUE_FOLLOWUPS_CSV.name}")
    print(f"- {Path(LEADS_MASTER_CSV).name}")
    print(f"- {Path(MAC_LAUNCHD_PLIST).name}")


if __name__ == "__main__":
    main()
