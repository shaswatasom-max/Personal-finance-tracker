import pandas as pd
import random
from datetime import datetime, timedelta

# Number of rows
TOTAL_ROWS = 500

# Categories for expenses
expense_categories = [
    "Food", "Groceries", "Transport", "Shopping", "Bills",
    "Entertainment", "Health", "Snacks", "Fuel", "Rent",
    "Subscriptions", "Education", "Travel", "Household"
]

# Income categories
income_categories = ["Salary", "Freelancing", "Gift", "Bonus", "Part-time"]

# Starting date
start_date = datetime(2025, 1, 1)

rows = []

for i in range(TOTAL_ROWS):
    # Random date within 365 days
    random_days = random.randint(0, 364)
    date_value = start_date + timedelta(days=random_days)
    date_str = date_value.strftime("%Y-%m-%d")

    # 85% expenses, 15% income (realistic)
    if random.random() < 0.85:
        ttype = "expense"
        category = random.choice(expense_categories)
        amount = round(random.uniform(50, 5000), 2)
        description = f"{category} expense"
    else:
        ttype = "income"
        category = random.choice(income_categories)
        amount = round(random.uniform(1000, 50000), 2)
        description = f"{category} income"

    rows.append([date_str, ttype, amount, category, description])

# Create DataFrame
df = pd.DataFrame(rows, columns=["date", "type", "amount", "category", "description"])

# Save to CSV
df.to_csv("transactions.csv", index=False)

print("Generated 500 rows into transactions.csv successfully!")
