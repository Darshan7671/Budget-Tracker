import sqlite3
from datetime import datetime, timedelta
import matplotlib.pyplot as plt
from openpyxl import Workbook

# ---------------- Database Setup ----------------

conn = sqlite3.connect("budget_tracker.db")
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS users (
    username TEXT PRIMARY KEY,
    password TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT,
    type TEXT,
    amount REAL,
    category TEXT,
    description TEXT,
    date TEXT
)
""")

conn.commit()

budget_limit = 5000

# ---------------- User Functions ----------------

def register():
    username = input("Enter username: ")
    password = input("Enter password: ")

    try:
        cursor.execute(
            "INSERT INTO users (username, password) VALUES (?, ?)",
            (username, password)
        )
        conn.commit()
        print("Registration successful!\n")
    except:
        print("Username already exists!\n")


def login():
    username = input("Enter username: ")
    password = input("Enter password: ")

    cursor.execute(
        "SELECT * FROM users WHERE username=? AND password=?",
        (username, password)
    )

    if cursor.fetchone():
        print("Login successful!\n")
        return username
    else:
        print("Invalid credentials!\n")
        return None


# ---------------- Transaction Functions ----------------

def add_transaction(username, t_type):
    amount = float(input("Enter amount: "))
    category = input("Enter category: ")
    description = input("Enter description: ")
    date = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        """INSERT INTO transactions
        (username, type, amount, category, description, date)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (username, t_type, amount, category, description, date)
    )

    conn.commit()

    print(f"{t_type} added successfully!\n")

    if t_type == "Expense":
        check_budget(username)


def view_transactions(username):
    cursor.execute(
        "SELECT * FROM transactions WHERE username=?",
        (username,)
    )

    records = cursor.fetchall()

    if records:
        print("\nTransaction History:")
        for r in records:
            print(r)
        print()
    else:
        print("No transactions found.\n")


def edit_transaction(username):
    tid = input("Enter Transaction ID to edit: ")

    new_amount = float(input("Enter new amount: "))
    new_category = input("Enter new category: ")
    new_description = input("Enter new description: ")

    cursor.execute(
        """UPDATE transactions
        SET amount=?, category=?, description=?
        WHERE id=? AND username=?""",
        (new_amount, new_category, new_description, tid, username)
    )

    conn.commit()

    print("Transaction updated successfully!\n")


def delete_transaction(username):
    tid = input("Enter Transaction ID to delete: ")

    cursor.execute(
        "DELETE FROM transactions WHERE id=? AND username=?",
        (tid, username)
    )

    conn.commit()

    print("Transaction deleted successfully!\n")


# ---------------- Reports ----------------

def check_budget(username):
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE username=? AND type='Expense'",
        (username,)
    )

    total_expense = cursor.fetchone()[0] or 0

    if total_expense > budget_limit:
        print("⚠ Warning: Budget limit exceeded!")


def view_balance(username):
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE username=? AND type='Income'",
        (username,)
    )
    income = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE username=? AND type='Expense'",
        (username,)
    )
    expense = cursor.fetchone()[0] or 0

    balance = income - expense

    print("\nTotal Income:", income)
    print("Total Expense:", expense)
    print("Current Balance:", balance)


def daily_summary(username):
    today = datetime.now().strftime("%Y-%m-%d")

    cursor.execute(
        """SELECT SUM(amount)
        FROM transactions
        WHERE username=? AND type='Expense' AND date=?""",
        (username, today)
    )

    total = cursor.fetchone()[0] or 0

    print("Today's Expense:", total)


def summary_by_days(username):
    days = int(input("Enter number of days: "))

    end_date = datetime.now()
    start_date = end_date - timedelta(days=days)

    cursor.execute(
        """SELECT SUM(amount)
        FROM transactions
        WHERE username=?
        AND type='Expense'
        AND date BETWEEN ? AND ?""",
        (
            username,
            start_date.strftime("%Y-%m-%d"),
            end_date.strftime("%Y-%m-%d"),
        )
    )

    total = cursor.fetchone()[0] or 0

    print(f"Total expense for last {days} days:", total)


def sort_transactions(username):
    cursor.execute(
        """SELECT * FROM transactions
        WHERE username=?
        ORDER BY amount DESC""",
        (username,)
    )

    records = cursor.fetchall()

    print("\nTransactions sorted by amount:")
    for r in records:
        print(r)


def set_budget_limit():
    global budget_limit

    budget_limit = float(input("Enter new budget limit: "))

    print("Budget limit updated!")


def top_spending_category(username):
    cursor.execute(
        """SELECT category, SUM(amount)
        FROM transactions
        WHERE username=? AND type='Expense'
        GROUP BY category
        ORDER BY SUM(amount) DESC
        LIMIT 1""",
        (username,)
    )

    result = cursor.fetchone()

    if result:
        print("Top spending category:", result)


def least_spending_category(username):
    cursor.execute(
        """SELECT category, SUM(amount)
        FROM transactions
        WHERE username=? AND type='Expense'
        GROUP BY category
        ORDER BY SUM(amount) ASC
        LIMIT 1""",
        (username,)
    )

    result = cursor.fetchone()

    if result:
        print("Least spending category:", result)


def income_vs_expense_percentage(username):
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE username=? AND type='Income'",
        (username,)
    )
    income = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE username=? AND type='Expense'",
        (username,)
    )
    expense = cursor.fetchone()[0] or 0

    total = income + expense

    if total > 0:
        print("Income %:", (income / total) * 100)
        print("Expense %:", (expense / total) * 100)


def average_daily_expense(username):
    cursor.execute(
        """SELECT SUM(amount), COUNT(DISTINCT date)
        FROM transactions
        WHERE username=? AND type='Expense'""",
        (username,)
    )

    total, days = cursor.fetchone()

    total = total or 0
    days = days or 1

    print("Average daily expense:", total / days)


def highest_single_transaction(username):
    cursor.execute(
        """SELECT * FROM transactions
        WHERE username=?
        ORDER BY amount DESC
        LIMIT 1""",
        (username,)
    )

    record = cursor.fetchone()

    if record:
        print("Highest transaction:", record)


def category_wise_report(username):
    cursor.execute(
        """SELECT category, SUM(amount)
        FROM transactions
        WHERE username=? AND type='Expense'
        GROUP BY category""",
        (username,)
    )

    records = cursor.fetchall()

    print("\nCategory-wise Report:")
    for r in records:
        print(r)


def export_to_excel(username):
    wb = Workbook()
    ws = wb.active

    ws.append(
        ["ID", "Username", "Type", "Amount", "Category", "Description", "Date"]
    )

    cursor.execute(
        "SELECT * FROM transactions WHERE username=?",
        (username,)
    )

    for row in cursor.fetchall():
        ws.append(row)

    wb.save("transactions.xlsx")

    print("Exported to Excel successfully!")


def show_chart(username):
    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE username=? AND type='Income'",
        (username,)
    )
    income = cursor.fetchone()[0] or 0

    cursor.execute(
        "SELECT SUM(amount) FROM transactions WHERE username=? AND type='Expense'",
        (username,)
    )
    expense = cursor.fetchone()[0] or 0

    labels = ["Income", "Expense"]
    values = [income, expense]

    plt.bar(labels, values)
    plt.title("Income vs Expense")
    plt.show()


# ---------------- Menu ----------------

def user_menu(username):
    while True:
        print("\n===== Budget Tracker Menu =====")
        print("1. Add Income")
        print("2. Add Expense")
        print("3. View Transactions")
        print("4. Edit Transaction")
        print("5. Delete Transaction")
        print("6. View Balance")
        print("7. Daily Summary")
        print("8. Summary by Days")
        print("9. Sort Transactions")
        print("10. Set Budget Limit")
        print("11. Top Spending Category")
        print("12. Least Spending Category")
        print("13. Income vs Expense %")
        print("14. Average Daily Expense")
        print("15. Highest Transaction")
        print("16. Category-wise Report")
        print("17. Export to Excel")
        print("18. Show Chart")
        print("19. Logout")

        choice = input("Enter choice: ")

        if choice == "1":
            add_transaction(username, "Income")

        elif choice == "2":
            add_transaction(username, "Expense")

        elif choice == "3":
            view_transactions(username)

        elif choice == "4":
            edit_transaction(username)

        elif choice == "5":
            delete_transaction(username)

        elif choice == "6":
            view_balance(username)

        elif choice == "7":
            daily_summary(username)

        elif choice == "8":
            summary_by_days(username)

        elif choice == "9":
            sort_transactions(username)

        elif choice == "10":
            set_budget_limit()

        elif choice == "11":
            top_spending_category(username)

        elif choice == "12":
            least_spending_category(username)

        elif choice == "13":
            income_vs_expense_percentage(username)

        elif choice == "14":
            average_daily_expense(username)

        elif choice == "15":
            highest_single_transaction(username)

        elif choice == "16":
            category_wise_report(username)

        elif choice == "17":
            export_to_excel(username)

        elif choice == "18":
            show_chart(username)

        elif choice == "19":
            break

        else:
            print("Invalid choice!")


def main():
    while True:
        print("\n===== Budget Tracker =====")
        print("1. Register")
        print("2. Login")
        print("3. Exit")

        choice = input("Enter choice: ")

        if choice == "1":
            register()

        elif choice == "2":
            user = login()

            if user:
                user_menu(user)

        elif choice == "3":
            print("Thank you for using Budget Tracker!")
            break

        else:
            print("Invalid choice!")


if __name__ == "__main__":
    main()