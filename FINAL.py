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

    conn.commit()
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

# === Add Expense Dialog ===
class AddExpenseDialog(QDialog):
    def __init__(self, month, username):
        super().__init__()
        self.month = month
        self.username = username
        self.current_year = datetime.now().year
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Add Expense for {self.month}")
        self.setFixedWidth(400)
        self.setStyleSheet("QDialog { background-color: white; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel(f"Add New Expense for {self.month}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Enter item")
        self.item_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        form.addRow("Item:", self.item_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        regex = QRegExp(r'^\d*\.?\d{0,2}$')
        validator = QRegExpValidator(regex)
        self.price_input.setValidator(validator)
        form.addRow("Price:", self.price_input)

        self.category_combo = QComboBox()
        self.category_combo.setEditable(True)  # Make the combo box editable
        self.load_categories()  # Load categories from the database
        form.addRow("Category:", self.category_combo)

        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_num = months.index(self.month) + 1
        days_in_month = get_days_in_month(self.current_year, month_num)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate(self.current_year, month_num, 1))
        self.date_input.setMinimumDate(QDate(self.current_year, month_num, 1))
        self.date_input.setMaximumDate(QDate(self.current_year, month_num, days_in_month))
        self.date_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        form.addRow("Date:", self.date_input)

        layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1; 
                color: #2c3e50; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #bdc3c7;
            }
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Expense")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_expense)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)

    def load_categories(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM categories")
        categories = [row[0] for row in c.fetchall()]
        self.category_combo.addItems(categories)
        conn.close()

    def save_expense(self):
        item = self.item_input.text().strip()
        price_text = self.price_input.text().strip().replace(',', '')

        if not item:
            QMessageBox.warning(self, "Missing Item", "Please enter an item description.")
            return

        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            QMessageBox.warning(self, "Invalid Price", "Please enter a valid price.")
            return

        category = self.category_combo.currentText()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # Check if the category exists
        c.execute("SELECT id FROM categories WHERE name = ?", (category,))
        category_id = c.fetchone()

        if category_id is None:  # If category does not exist, insert it
            c.execute("INSERT INTO categories (name) VALUES (?)", (category,))
            conn.commit()
            category_id = c.lastrowid  # Get the new category ID
        else:
            category_id = category_id[0]  # Get the existing category ID

        c.execute("INSERT INTO expenses (username, item, price, date, category_id) VALUES (?, ?, ?, ?, ?)",
                  (self.username, item, price, self.date_input.date().toString("yyyy-MM-dd"), category_id))

        conn.commit()
        conn.close()

        self.accept()


# === Register Page ===
class RegisterPage(QWidget):
    switch_to_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #f0f4f8;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(0, 30, 0, 30)
        main_layout.setAlignment(Qt.AlignCenter)

        form_container = QFrame()
        form_container.setFixedWidth(420)
        form_container.setStyleSheet("""
            background-color: white;
            border-radius: 16px;
            border: 1px solid #dfe6e9;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(40, 40, 40, 40)
        form_layout.setSpacing(20)

        title_label = QLabel("Create Your Account")
        title_label.setFont(QFont("Poppins", 20, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")

        subtitle_label = QLabel("Start tracking your expenses today")
        subtitle_label.setFont(QFont("Poppins", 11))
        subtitle_label.setStyleSheet("color: #7f8c8d;")

        form_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        form_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        form_layout.addSpacing(10)

        self.name_input = self._create_input("Full Name")
        self.username_input = self._create_input("Username")
        self.email_input = self._create_input("Email")
        self.password_input = self._create_input("Password", is_password=True)

        form_layout.addWidget(self.name_input)
        form_layout.addWidget(self.username_input)
        form_layout.addWidget(self.email_input)
        form_layout.addWidget(self.password_input)

        register_btn = QPushButton("Sign Up")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                font-size: 15px;
                padding: 12px;
                font-weight: bold;
                border-radius: 10px;
            }
            QPushButton:hover {
                background-color: #2471a3;
            }
        """)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(self.register)
        form_layout.addWidget(register_btn)

        login_container = QHBoxLayout()
        login_container.setAlignment(Qt.AlignCenter)

        login_text = QLabel("Already have an account?")
        login_text.setFont(QFont("Poppins", 9))

        login_btn = QPushButton("Log In")
        login_btn.setFont(QFont("Poppins", 9, QFont.Bold))
        login_btn.setStyleSheet("""
            QPushButton {
                color: #2980b9;
                background-color: transparent;
                border: none;
                text-decoration: underline;
            }
            QPushButton:hover {
                color: #21618c;
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.switch_to_login.emit)

        login_container.addWidget(login_text)
        login_container.addWidget(login_btn)
        form_layout.addLayout(login_container)

        main_layout.addWidget(form_container, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)

    def _create_input(self, placeholder, is_password=False):
        entry = QLineEdit()
        entry.setPlaceholderText(placeholder)
        entry.setFont(QFont("Poppins", 10))
        entry.setStyleSheet("""
            QLineEdit {
                padding: 12px;
                border: 1px solid #ccc;
                border-radius: 8px;
                font-size: 14px;
            }
            QLineEdit:focus {
                border: 1px solid #3498db;
                outline: none;
            }
        """)
        if is_password:
            entry.setEchoMode(QLineEdit.Password)
        return entry

    def register(self):
        name = self.name_input.text().strip()
        username = self.username_input.text().strip()
        email = self.email_input.text().strip()
        password = self.password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self, "Missing Fields", "Username and password are required.")
            return

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ?", (username,))
        if c.fetchone():
            QMessageBox.warning(self, "Username Exists", "Username already exists.")
            conn.close()
            return

        c.execute("INSERT INTO users (username, name, email, password) VALUES (?, ?, ?, ?)",
                  (username, name, email, password))
        conn.commit()
        conn.close()

        QMessageBox.information(self, "Success", "Registered Successfully!")
        self.switch_to_login.emit()


# === Login Page ===
class LoginPage(QWidget):
    switch_to_register = pyqtSignal()
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #ecf0f3;")
        main_layout = QVBoxLayout()
        main_layout.setAlignment(Qt.AlignCenter)

        title_label = QLabel("Welcome Back!")
        title_label.setFont(QFont("Segoe UI", 26, QFont.Bold))
        title_label.setStyleSheet("color: #2d3436;")

        login_box = QFrame()
        login_box.setStyleSheet("""
            QFrame {
                background-color: white;
                border-radius: 20px;
                padding: 30px;
                border: 1px solid #dcdde1;
            }
        """)
        login_box.setFixedWidth(400)
        login_layout = QVBoxLayout(login_box)
        login_layout.setSpacing(15)

        subtitle_label = QLabel("Expense Tracker Login System")
        subtitle_label.setFont(QFont("Segoe UI", 11, QFont.StyleItalic))
        subtitle_label.setStyleSheet("color: #7f8c8d;")
        login_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)

        self.username_entry = QLineEdit()
        self.username_entry.setPlaceholderText("Username")
        self.username_entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #2980b9;
                background-color: #ecf6fc;
            }
        """)
        login_layout.addWidget(self.username_entry)

        self.password_entry = QLineEdit()
        self.password_entry.setPlaceholderText("Password")
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet("""
            QLineEdit {
                border: 1px solid #bdc3c7;
                border-radius: 10px;
                padding: 10px;
                font-size: 14px;
                background-color: #f9f9f9;
            }
            QLineEdit:focus {
                border: 1px solid #2980b9;
                background-color: #ecf6fc;
            }
        """)
        login_layout.addWidget(self.password_entry)

        login_btn = QPushButton("Log In")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2980b9;
                color: white;
                border-radius: 10px;
                padding: 12px;
                font-size: 16px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2471a3;
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        login_layout.addWidget(login_btn)

        divider = QFrame()
        divider.setFrameShape(QFrame.HLine)
        divider.setStyleSheet("color: #ccc;")
        login_layout.addWidget(divider)

        register_label = QLabel("Don't have an account? <a href='#'>Sign Up</a>")
        register_label.setFont(QFont("Segoe UI", 10))
        register_label.setStyleSheet("""
            QLabel {
                color: #2980b9;
                text-align: center;
            }
            QLabel:hover {
                color: #2471a3;
            }
        """)
        register_label.setAlignment(Qt.AlignCenter)
        register_label.setOpenExternalLinks(False)
        register_label.linkActivated.connect(self.redirect_to_register)
        login_layout.addWidget(register_label)

        main_layout.addWidget(title_label)
        main_layout.addWidget(login_box, alignment=Qt.AlignCenter)
        self.setLayout(main_layout)

    def redirect_to_register(self, link):
        self.switch_to_register.emit()

    def login(self):
        username = self.username_entry.text().strip()
        password = self.password_entry.text().strip()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT * FROM users WHERE username = ? AND password = ?", (username, password))
        user = c.fetchone()
        conn.close()

        if user:
            QMessageBox.information(self, "Login Success", f"Welcome, {user[1]}!")
            self.login_successful.emit(username)
        else:
            QMessageBox.critical(self, "Login Failed", "Invalid username or password.")


# === Month Card Widget ===

class MonthCard(QFrame):
    month_clicked = pyqtSignal(str)

    def __init__(self, month, is_current=False):
        super().__init__()
        self.month = month
        self.is_current = is_current
        self.initUI()

    def initUI(self):
        self.setActiveStyle(self.is_current)
        self.setCursor(Qt.PointingHandCursor)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        self.month_label = QLabel(self.month)
        self.month_label.setAlignment(Qt.AlignCenter)
        self.month_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        layout.addWidget(self.month_label)
        self.setFixedSize(120, 80)

    def setActiveStyle(self, active):
        if active:
            self.setStyleSheet("""
                QFrame { 
                    background-color: #3498db; 
                    border-radius: 10px; 
                    padding: 10px;
                    border: 2px solid #2980b9;
                }
                QLabel {
                    color: white;
                }
            """)
        else:
            self.setStyleSheet("""
                QFrame { 
                    background-color: #ecf0f1; 
                    border-radius: 8px; 
                    padding: 10px;
                    border: 1px solid #ddd;
                }
                QFrame:hover { 
                    background-color: #d6dbdf; 
                }
                QLabel {
                    color: #2c3e50;
                }
            """)
        self.is_current = active

    def mousePressEvent(self, event):
        self.month_clicked.emit(self.month)
        super().mousePressEvent(event)


# === Add Expense Dialog ===
class AddExpenseDialog(QDialog):
    def __init__(self, month, username):
        super().__init__()
        self.month = month
        self.username = username
        self.current_year = datetime.now().year
        self.initUI()

    def initUI(self):
        self.setWindowTitle(f"Add Expense for {self.month}")
        self.setFixedWidth(400)
        self.setStyleSheet("QDialog { background-color: white; }")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        title = QLabel(f"Add New Expense for {self.month}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title)

        form = QFormLayout()
        form.setSpacing(10)

        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("Enter item")
        self.item_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        form.addRow("Item:", self.item_input)

        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        regex = QRegExp(r'^\d*\.?\d{0,2}$')
        validator = QRegExpValidator(regex)
        self.price_input.setValidator(validator)
        form.addRow("Price:", self.price_input)

        self.category_combo = QComboBox()
        self.category_combo.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")

        # Get categories from database
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM categories ORDER BY id")
        categories = [row[0] for row in c.fetchall()]
        conn.close()

        self.category_combo.addItems(categories)
        form.addRow("Category:", self.category_combo)

        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_num = months.index(self.month) + 1
        days_in_month = get_days_in_month(self.current_year, month_num)

        self.date_input = QDateEdit()
        self.date_input.setCalendarPopup(True)
        self.date_input.setDisplayFormat("yyyy-MM-dd")
        self.date_input.setDate(QDate(self.current_year, month_num, 1))
        self.date_input.setMinimumDate(QDate(self.current_year, month_num, 1))
        self.date_input.setMaximumDate(QDate(self.current_year, month_num, days_in_month))
        self.date_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        form.addRow("Date:", self.date_input)

        layout.addLayout(form)

        buttons_layout = QHBoxLayout()
        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton {
                background-color: #ecf0f1; 
                color: #2c3e50; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #bdc3c7;
            }
        """)
        cancel_btn.setCursor(Qt.PointingHandCursor)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Expense")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        save_btn.setCursor(Qt.PointingHandCursor)
        save_btn.clicked.connect(self.save_expense)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)

    def save_expense(self):
        item = self.item_input.text().strip()
        price_text = self.price_input.text().strip().replace(',', '')

        if not item:
            QMessageBox.warning(self, "Missing Item", "Please enter an item description.")
            return

        try:
            price = float(price_text)
            if price <= 0:
                raise ValueError("Price must be positive")
        except ValueError:
            QMessageBox.warning(self, "Invalid Price", "Please enter a valid price.")
            return

        category_name = self.category_combo.currentText()

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        # First get the category ID
        c.execute("SELECT id FROM categories WHERE name = ?", (category_name,))
        category_id = c.fetchone()

        if not category_id:
            QMessageBox.warning(self, "Invalid Category", "Selected category doesn't exist in database.")
            conn.close()
            return

        category_id = category_id[0]

        # Then insert the expense with the correct category_id
        c.execute("INSERT INTO expenses (username, item, price, date, category_id) VALUES (?, ?, ?, ?, ?)",
                  (self.username, item, price, self.date_input.date().toString("yyyy-MM-dd"), category_id))

        conn.commit()
        conn.close()

        self.accept()


# === Month Detail Widget ===

class MonthDetailWidget(QWidget):
    def __init__(self, month, username):
        super().__init__()
        self.month = month
        self.username = username
        self.current_year = datetime.now().year
        self.initUI()

    def initUI(self):
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        header_layout = QHBoxLayout()
        month_label = QLabel(f"{self.month} {self.current_year}")
        month_label.setFont(QFont("Segoe UI", 16, QFont.Bold))
        month_label.setStyleSheet("color: #2c3e50;")

        add_btn = QPushButton("+ Add Expense")
        add_btn.setStyleSheet("""
            QPushButton { 
                background-color: #3498db; 
                color: white; 
                border-radius: 5px; 
                padding: 8px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #2980b9; 
            }
        """)
        add_btn.setCursor(Qt.PointingHandCursor)
        add_btn.clicked.connect(self.add_expense)

        header_layout.addWidget(month_label)
        header_layout.addStretch()
        header_layout.addWidget(add_btn)
        main_layout.addLayout(header_layout)

        expenses_container = QScrollArea()
        expenses_container.setWidgetResizable(True)
        expenses_container.setFrameShape(QFrame.NoFrame)
        expenses_container.setStyleSheet("background-color: transparent;")

        self.expenses_widget = QWidget()
        self.expenses_layout = QVBoxLayout(self.expenses_widget)
        self.expenses_layout.setContentsMargins(0, 0, 0, 0)
        self.expenses_layout.setSpacing(10)
        self.expenses_layout.addStretch()

        expenses_container.setWidget(self.expenses_widget)
        main_layout.addWidget(expenses_container)

        self.total_label = QLabel("Total: ₱0.00")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #16a085; padding: 10px 0;")
        self.total_label.setAlignment(Qt.AlignRight)
        main_layout.addWidget(self.total_label)

        self.load_expenses()

    def add_expense(self):
        dialog = AddExpenseDialog(self.month, self.username)
        result = dialog.exec_()
        if result == QDialog.Accepted:
            self.load_expenses()

    def delete_expense(self, expense_id):
        reply = QMessageBox.question(self, "Confirm Delete",
                                     "Are you sure you want to delete this expense?",
                                     QMessageBox.Yes | QMessageBox.No, QMessageBox.No)

        if reply == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            conn.close()
            self.load_expenses()

    def load_expenses(self):
        while self.expenses_layout.count() > 1:
            item = self.expenses_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_num = months.index(self.month) + 1

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        try:
            c.execute("""
                     SELECT c.name, SUM(e.price), GROUP_CONCAT(e.id), GROUP_CONCAT(e.item), 
                            GROUP_CONCAT(e.price), GROUP_CONCAT(e.date)
                     FROM expenses e
                     JOIN categories c ON e.category_id = c.id
                     WHERE e.username = ? 
                     AND strftime('%m', e.date) = ?
                     AND strftime('%Y', e.date) = ?
                     GROUP BY c.name
                     ORDER BY c.id
                 """, (self.username, f"{month_num:02d}", str(self.current_year)))

            category_data = c.fetchall()

            c.execute("""
                     SELECT e.id, e.item, e.price, e.date, c.name
                     FROM expenses e
                     JOIN categories c ON e.category_id = c.id
                     WHERE e.username = ? 
                     AND strftime('%m', e.date) = ?
                     AND strftime('%Y', e.date) = ?
                     ORDER BY c.id, e.date
                 """, (self.username, f"{month_num:02d}", str(self.current_year)))

            expenses = c.fetchall()
        except sqlite3.OperationalError as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load expenses: {str(e)}")
            category_data = []
            expenses = []

        conn.close()

        total = 0

        if not expenses:
            empty_label = QLabel("No expenses recorded for this month.\nClick '+ Add Expense' to get started.")
            empty_label.setFont(QFont("Segoe UI", 11))
            empty_label.setStyleSheet("color: #95a5a6; padding: 20px 0;")
            empty_label.setAlignment(Qt.AlignCenter)
            self.expenses_layout.insertWidget(0, empty_label)
        else:
            current_category = None
            category_total = 0

            for expense_id, item, price, date_str, category in expenses:
                if category != current_category:
                    if current_category is not None:
                        cat_total_frame = QFrame()
                        cat_total_frame.setStyleSheet("""
                                 QFrame { 
                                     background-color: #e8f4f8; 
                                     border-radius: 5px; 
                                     padding: 10px;
                                 }
                             """)
                        cat_total_layout = QHBoxLayout(cat_total_frame)

                        cat_total_label = QLabel(f"{current_category} Total:")
                        cat_total_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                        cat_total_label.setStyleSheet("color: #2980b9;")

                        cat_total_value = QLabel(f"₱{category_total:,.2f}")
                        cat_total_value.setFont(QFont("Segoe UI", 10, QFont.Bold))
                        cat_total_value.setStyleSheet("color: #2980b9;")
                        cat_total_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                        cat_total_layout.addWidget(cat_total_label)
                        cat_total_layout.addStretch()
                        cat_total_layout.addWidget(cat_total_value)

                        self.expenses_layout.insertWidget(self.expenses_layout.count() - 1, cat_total_frame)

                    current_category = category
                    category_total = 0

                    category_header = QLabel(current_category)
                    category_header.setFont(QFont("Segoe UI", 12, QFont.Bold))
                    category_header.setStyleSheet("""
                             QLabel { 
                                 color: #2c3e50; 
                                 padding: 5px 0;
                                 border-bottom: 2px solid #3498db;
                             }
                         """)
                    self.expenses_layout.insertWidget(self.expenses_layout.count() - 1, category_header)

                expense_frame = QFrame()
                expense_frame.setStyleSheet("""
                         QFrame { 
                             background-color: #f9f9f9; 
                             border-radius: 5px; 
                             padding: 10px;
                         }
                     """)

                expense_layout = QHBoxLayout(expense_frame)
                expense_layout.setContentsMargins(10, 10, 10, 10)

                date = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date.strftime("%b %d, %Y")

                date_label = QLabel(formatted_date)
                date_label.setFont(QFont("Segoe UI", 10))
                date_label.setStyleSheet("color: #7f8c8d;")
                date_label.setFixedWidth(120)

                item_label = QLabel(item)
                item_label.setFont(QFont("Segoe UI", 11))
                item_label.setStyleSheet("color: #2c3e50;")

                price_label = QLabel(f"₱{price:,.2f}")
                price_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                price_label.setStyleSheet("color: #16a085;")
                price_label.setFixedWidth(100)
                price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                delete_btn = QPushButton("×")
                delete_btn.setStyleSheet("""
                    QPushButton { 
                        background-color: #e74c3c; 
                        color: white; 
                        border-radius: 10px; 
                        font-weight: bold; 
                        width: 20px; 
                        height: 20px;
                    }
                    QPushButton:hover { 
                        background-color: #c0392b; 
                    }
                """)
                delete_btn.setCursor(Qt.PointingHandCursor)
                delete_btn.setFixedSize(20, 20)
                delete_btn.clicked.connect(lambda checked, eid=expense_id: self.delete_expense(eid))

                expense_layout.addWidget(date_label)
                expense_layout.addWidget(item_label)
                expense_layout.addWidget(price_label)
                expense_layout.addWidget(delete_btn)

                self.expenses_layout.insertWidget(self.expenses_layout.count() - 1, expense_frame)

                category_total += price
                total += price

            if current_category is not None:
                cat_total_frame = QFrame()
                cat_total_frame.setStyleSheet("""
                    QFrame { 
                        background-color: #e8f4f8; 
                        border-radius: 5px; 
                        padding: 10px;
                    }
                """)
                cat_total_layout = QHBoxLayout(cat_total_frame)

                cat_total_label = QLabel(f"{current_category} Total:")
                cat_total_label.setFont(QFont("Segoe UI", 10, QFont.Bold))
                cat_total_label.setStyleSheet("color: #2980b9;")

                cat_total_value = QLabel(f"₱{category_total:,.2f}")
                cat_total_value.setFont(QFont("Segoe UI", 10, QFont.Bold))
                cat_total_value.setStyleSheet("color: #2980b9;")
                cat_total_value.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                cat_total_layout.addWidget(cat_total_label)
                cat_total_layout.addStretch()
                cat_total_layout.addWidget(cat_total_value)

                self.expenses_layout.insertWidget(self.expenses_layout.count() - 1, cat_total_frame)

        self.total_label.setText(f"Total: ₱{total:,.2f}")


# === Main Expense Tracker Window ===

class ExpenseTrackerWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.current_year = datetime.now().year
        self.months = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        self.current_month = self.months[datetime.now().month - 1]
        self.month_cards = {}
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: white;")

        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        header = QFrame()
        header.setStyleSheet("background-color: #3498db;")
        header.setFixedHeight(60)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        app_title = QLabel("Expense Tracker")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        app_title.setStyleSheet("color: white;")

        user_label = QLabel(f"Welcome, {self.username}")
        user_label.setFont(QFont("Segoe UI", 12))
        user_label.setStyleSheet("color: white;")

        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(user_label)

        main_layout.addWidget(header)

        months_scroll = QScrollArea()
        months_scroll.setWidgetResizable(True)
        months_scroll.setFrameShape(QFrame.NoFrame)
        months_scroll.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        months_scroll.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        months_scroll.setFixedHeight(100)
        months_scroll.setStyleSheet("background-color: #f8f9fa;")

        months_widget = QWidget()
        months_layout = QHBoxLayout(months_widget)
        months_layout.setContentsMargins(20, 10, 20, 10)
        months_layout.setSpacing(15)

        for month in self.months:
            is_current = month == self.current_month
            month_card = MonthCard(month, is_current)
            month_card.month_clicked.connect(self.show_month_detail)
            months_layout.addWidget(month_card)
            self.month_cards[month] = month_card

        months_layout.addStretch()
        months_scroll.setWidget(months_widget)

        main_layout.addWidget(months_scroll)

        self.month_detail_stack = QStackedWidget()

        for month in self.months:
            detail_widget = MonthDetailWidget(month, self.username)
            self.month_detail_stack.addWidget(detail_widget)

        current_month_index = self.months.index(self.current_month)
        self.month_detail_stack.setCurrentIndex(current_month_index)

        main_layout.addWidget(self.month_detail_stack)

        self.setCentralWidget(main_widget)

    def show_month_detail(self, month):
        if month in self.month_cards:
            for m, card in self.month_cards.items():
                card.setActiveStyle(m == month)

            idx = self.months.index(month)
            self.month_detail_stack.setCurrentIndex(idx)


# === Main Application ===

class ExpenseTrackerApp(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.initApp()

    def initApp(self):
        setup_database()

        self.auth_window = QMainWindow()
        self.auth_window.setWindowTitle("Expense Tracker - Login")
        self.auth_window.setGeometry(100, 100, 500, 700)

        self.auth_stack = QStackedWidget()

        login_page = LoginPage()
        register_page = RegisterPage()

        register_page.switch_to_login.connect(lambda: self.auth_stack.setCurrentWidget(login_page))
        login_page.switch_to_register.connect(lambda: self.auth_stack.setCurrentWidget(register_page))
        login_page.login_successful.connect(self.launch_expense_tracker)

        self.auth_stack.addWidget(login_page)
        self.auth_stack.addWidget(register_page)
        self.auth_stack.setCurrentIndex(0)

        self.auth_window.setCentralWidget(self.auth_stack)
        self.auth_window.show()

    def launch_expense_tracker(self, username):
        self.auth_window.hide()
        self.expense_tracker = ExpenseTrackerWindow(username)
        self.expense_tracker.show()

# === Run Application ===

if __name__ == "__main__":
    app = ExpenseTrackerApp(sys.argv)
    sys.exit(app.exec_())

