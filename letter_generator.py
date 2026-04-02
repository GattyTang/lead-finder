def generate_letters(results, filename="letters.txt"):
    unique_targets = []
    seen = set()

    for row in results:
        key = (row["website"], row["email"])
        if key not in seen:
            seen.add(key)
            unique_targets.append(row)

    with open(filename, "w", encoding="utf-8") as f:
        for row in unique_targets:
            website = row["website"]
            email = row["email"]
            keyword = row["keyword"]

            letter = f"""
==================================================
Website: {website}
Email: {email}
Keyword: {keyword}
==================================================

Subject: Supply of Glass Beads / Road Marking Materials

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

-----------------------------------------------

""".strip()

            f.write(letter + "\n\n")

    print(f"Saved letters to {filename}")
