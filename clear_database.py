
import sqlite3

# Connect to your database
conn = sqlite3.connect("expenses.db")

# Create a cursor
cursor = conn.cursor()

# Delete all transaction records
cursor.execute("DELETE FROM transactions")

# Save changes
conn.commit()

# Close connection
conn.close()

print("All transactions have been deleted successfully.")
