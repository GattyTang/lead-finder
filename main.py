import pandas as pd

columns = ["Company", "Website", "Email", "Phone", "Country"]
df = pd.DataFrame(columns=columns)

df.to_excel("leads.xlsx", index=False)

print("leads.xlsx created successfully")
