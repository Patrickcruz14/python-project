import os
import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QStackedWidget,
                             QComboBox, QDialog, QFormLayout, QMessageBox, QDateEdit)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QRegExpValidator

# === SQLite Database Setup ===

DB_PATH = 'expense_tracker.db'

def setup_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create Users table
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    password TEXT)''')

    # Create Categories table
    c.execute('''CREATE TABLE IF NOT EXISTS categories (
                    id INTEGER PRIMARY KEY,
                    name TEXT UNIQUE)''')

    # Clear existing categories and insert new ones in exact order
    c.execute("DELETE FROM categories")  # Clear any existing categories

    # Insert categories in specific order with manual IDs
    categories = [
        (1, 'Food'),
        (2, 'Utilities'),
        (3, 'Necessities'),
        (4, 'Transportation')
    ]

    for cat_id, cat_name in categories:
        c.execute("INSERT OR IGNORE INTO categories (id, name) VALUES (?, ?)",
                  (cat_id, cat_name))

    # Create Expenses table with category_id
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    item TEXT,
                    price REAL,
                    date TEXT,
                    category_id INTEGER,
                    FOREIGN KEY (username) REFERENCES users(username),
                    FOREIGN KEY (category_id) REFERENCES categories(id))''')

    # Migration code for old schema
    c.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in c.fetchall()]

    if 'date' not in columns:
        try:
            c.execute("ALTER TABLE expenses ADD COLUMN date TEXT")
            if 'month' in columns and 'day' in columns:
                current_year = datetime.now().year
                c.execute("SELECT id, month, day FROM expenses WHERE date IS NULL")
                for expense_id, month, day in c.fetchall():
                    months = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                    month_num = months.index(month) + 1
                    date_str = f"{current_year}-{month_num:02d}-{day:02d}"
                    c.execute("UPDATE expenses SET date=? WHERE id=?", (date_str, expense_id))
            if 'month' in columns:
                c.execute("CREATE TABLE expenses_new AS SELECT id, username, item, price, date FROM expenses")
                c.execute("DROP TABLE expenses")
                c.execute("ALTER TABLE expenses_new RENAME TO expenses")
        except sqlite3.Error as e:
            print(f"Database migration error: {e}")
            conn.rollback()
        else:
            conn.commit()

    # Add category_id column if it doesn't exist
    if 'category_id' not in columns:
        try:
            c.execute("ALTER TABLE expenses ADD COLUMN category_id INTEGER DEFAULT 1")  # Default to Food
            conn.commit()
        except sqlite3.Error as e:
            print(f"Error adding category_id column: {e}")

    conn.close()

# === Helper Functions ===

def get_days_in_month(year, month):
    if month == 2:
        return 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    return 31

def format_currency(amount):
    return f"₱{amount:,.2f}"
