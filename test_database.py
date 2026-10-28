
from database import add_transaction, get_transactions

# Add sample income
add_transaction(
    "2026-10-01",
    "Income",
    "Scholarship",
    15000,
    "Monthly scholarship"
)

# Add sample expense
add_transaction(
    "2026-10-02",
    "Expense",
    "Food",
    300,
    "College lunch"
)

# Retrieve all transactions
records = get_transactions()

# Display the records
print("Transactions stored in database:")

for record in records:
    print(record)
