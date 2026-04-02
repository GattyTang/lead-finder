from scraper import collect_leads
from exporter import save_to_csv, save_to_excel
from letter_generator import generate_letters
from tracker import create_followup_file


if __name__ == "__main__":
    keywords = [
        "glass beads importer",
        "reflective material distributor",
        "road marking contractor company",
        "traffic safety company",
        "road marking paint supplier",
        "thermoplastic road marking company"
    ]

    results = collect_leads(keywords)

    save_to_csv(results, "leads.csv")
    save_to_excel(results, "leads.xlsx")
    generate_letters(results, "letters.txt")
    create_followup_file(results, "followup.csv")

    print("\nDone.")
    print("Generated files:")
    print("- leads.csv")
    print("- leads.xlsx")
    print("- letters.txt")
    print("- followup.csv")
