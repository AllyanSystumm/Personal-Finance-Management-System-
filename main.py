import sqlite3
import hashlib
import matplotlib.pyplot as plt

# Database setup
conn = sqlite3.connect('finance_manager.db')
cursor = conn.cursor()

# Creating tables for users, income, expenses, and budgets
cursor.execute('''
CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    username TEXT NOT NULL,
    password TEXT NOT NULL
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS income (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL NOT NULL,
    description TEXT,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS expenses (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    amount REAL NOT NULL,
    category TEXT,
    description TEXT,
    date TEXT,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

cursor.execute('''
CREATE TABLE IF NOT EXISTS budgets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER,
    category TEXT NOT NULL,
    amount REAL NOT NULL,
    FOREIGN KEY(user_id) REFERENCES users(id)
)
''')

# User Authentication Functions
def register_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("INSERT INTO users (username, password) VALUES (?, ?)", (username, hashed_password))
    conn.commit()
    print("User registered successfully!")

def login_user():
    username = input("Enter username: ")
    password = input("Enter password: ")
    hashed_password = hashlib.sha256(password.encode()).hexdigest()

    cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (username, hashed_password))
    user = cursor.fetchone()
    if user:
        print(f"Welcome {username}!")
        return user[0]  # Return user_id
    else:
        print("Invalid credentials!")
        return None

def authenticate():
    while True:
        choice = input("1. Register\n2. Login\nChoose option: ")
        if choice == '1':
            register_user()
        elif choice == '2':
            user_id = login_user()
            if user_id:
                return user_id
        else:
            print("Invalid option.")

# Income Tracker Functions
def add_income(user_id):
    amount = float(input("Enter income amount: "))
    description = input("Enter income description: ")
    date = input("Enter date (YYYY-MM-DD): ")

    cursor.execute("INSERT INTO income (user_id, amount, description, date) VALUES (?, ?, ?, ?)",
                   (user_id, amount, description, date))
    conn.commit()
    print("Income added successfully!")

def view_income(user_id):
    cursor.execute("SELECT * FROM income WHERE user_id=?", (user_id,))
    income_records = cursor.fetchall()
    print("\nIncome Records:")
    for record in income_records:
        print(f"Amount: {record[2]}, Description: {record[3]}, Date: {record[4]}")
    print()

# Expense Tracker Functions
def add_expense(user_id):
    amount = float(input("Enter expense amount: "))
    category = input("Enter category (e.g., Food, Rent, Travel): ")
    description = input("Enter expense description: ")
    date = input("Enter date (YYYY-MM-DD): ")

    cursor.execute("INSERT INTO expenses (user_id, amount, category, description, date) VALUES (?, ?, ?, ?, ?)",
                   (user_id, amount, category, description, date))
    conn.commit()
    print("Expense added successfully!")

def view_expenses(user_id):
    cursor.execute("SELECT * FROM expenses WHERE user_id=?", (user_id,))
    expense_records = cursor.fetchall()
    print("\nExpense Records:")
    for record in expense_records:
        print(f"Amount: {record[2]}, Category: {record[3]}, Description: {record[4]}, Date: {record[5]}")
    print()

# Budgeting Functions
def set_budget(user_id):
    category = input("Enter budget category (e.g., Food, Rent): ")
    amount = float(input(f"Enter budget amount for {category}: "))

    cursor.execute("INSERT INTO budgets (user_id, category, amount) VALUES (?, ?, ?)",
                   (user_id, category, amount))
    conn.commit()
    print("Budget set successfully!")

def check_budget(user_id):
    cursor.execute("SELECT category, amount FROM budgets WHERE user_id=?", (user_id,))
    budget_records = cursor.fetchall()

    for budget in budget_records:
        category = budget[0]
        limit = budget[1]

        cursor.execute("SELECT SUM(amount) FROM expenses WHERE user_id=? AND category=?", (user_id, category))
        total_spent = cursor.fetchone()[0] or 0

        print(f"Budget for {category}: {limit}, Spent: {total_spent}")
        if total_spent > limit:
            print(f"Warning: You have exceeded the budget for {category}!")

# Report Generation with Matplotlib
def generate_expense_report(user_id):
    cursor.execute("SELECT category, SUM(amount) FROM expenses WHERE user_id=? GROUP BY category", (user_id,))
    data = cursor.fetchall()
    
    if not data:
        print("No expenses to generate report.")
        return
    
    categories = [item[0] for item in data]
    amounts = [item[1] for item in data]

    plt.pie(amounts, labels=categories, autopct='%1.1f%%')
    plt.title("Expense Breakdown")
    plt.show()

# Main Application Flow
def main():
    user_id = authenticate()  # Get the logged-in user's ID
    while True:
        print("\n1. Add Income")
        print("2. View Income")
        print("3. Add Expense")
        print("4. View Expenses")
        print("5. Set Budget")
        print("6. Check Budget")
        print("7. Generate Expense Report")
        print("0. Exit")
        
        choice = input("Choose option: ")
        if choice == '1':
            add_income(user_id)
        elif choice == '2':
            view_income(user_id)
        elif choice == '3':
            add_expense(user_id)
        elif choice == '4':
            view_expenses(user_id)
        elif choice == '5':
            set_budget(user_id)
        elif choice == '6':
            check_budget(user_id)
        elif choice == '7':
            generate_expense_report(user_id)
        elif choice == '0':
            print("Exiting the system.")
            break
        else:
            print("Invalid option. Try again.")

# Run the application
if __name__ == "__main__":
    main()
