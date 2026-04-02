from scraper import collect_leads
from exporter import save_to_csv, save_to_excel
from letter_generator import generate_letters
from tracker import (
    create_followup_file,
    load_existing_followup,
    merge_new_leads_into_followup,
    export_due_followups
)
from mailer import send_bulk_emails
from config import KEYWORDS, AUTO_SEND_EMAILS


def main():
    print("Starting lead finder...")

    results = collect_leads(KEYWORDS)

    save_to_csv(results, "leads.csv")
    save_to_excel(results, "leads.xlsx")
    generate_letters(results, "letters.txt")

    # 跟进表：如果已存在就追加，不存在就创建
    followup_file = "followup.csv"
    existing = load_existing_followup(followup_file)
    merged = merge_new_leads_into_followup(existing, results)
    create_followup_file(merged, followup_file)

    # 导出今天需要跟进的客户
    due_rows = export_due_followups(followup_file, "due_followups.csv")

    # 自动发开发信
    if AUTO_SEND_EMAILS:
        send_bulk_emails(results)

    print("\nDone.")
    print("Generated files:")
    print("- leads.csv")
    print("- leads.xlsx")
    print("- letters.txt")
    print("- followup.csv")
    print("- due_followups.csv")
    print(f"Due follow-ups today: {len(due_rows)}")


if __name__ == "__main__":
    main()
