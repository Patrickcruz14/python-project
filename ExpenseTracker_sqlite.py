import os
import sys
import sqlite3
from datetime import datetime
from PyQt5.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
                             QLabel, QLineEdit, QPushButton, QScrollArea, QFrame, QGridLayout,
                             QMessageBox, QStackedWidget, QComboBox, QDialog, QFormLayout,
                             QSpinBox, QCalendarWidget)
from PyQt5.QtCore import Qt, QDate, pyqtSignal, QRegExp
from PyQt5.QtGui import QFont, QColor, QPalette, QIcon, QRegExpValidator

# === SQLite Database Setup ===
DB_PATH = 'expense_tracker.db'


def setup_database():
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()

    # Create Users table if it doesn't exist
    c.execute('''CREATE TABLE IF NOT EXISTS users (
                    username TEXT PRIMARY KEY,
                    name TEXT,
                    email TEXT,
                    password TEXT)''')

    # Create Expenses table with the new schema
    c.execute('''CREATE TABLE IF NOT EXISTS expenses (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    username TEXT,
                    item TEXT,
                    price REAL,
                    date TEXT,
                    FOREIGN KEY (username) REFERENCES users(username))''')

    # Check if we need to migrate from old schema
    c.execute("PRAGMA table_info(expenses)")
    columns = [column[1] for column in c.fetchall()]

    if 'date' not in columns:
        try:
            # Add the new date column
            c.execute("ALTER TABLE expenses ADD COLUMN date TEXT")

            # If there's existing data with month/day columns, migrate it
            if 'month' in columns and 'day' in columns:
                current_year = datetime.now().year
                c.execute("SELECT id, month, day FROM expenses WHERE date IS NULL")
                for expense_id, month, day in c.fetchall():
                    # Convert month name to number
                    months = ["January", "February", "March", "April", "May", "June",
                              "July", "August", "September", "October", "November", "December"]
                    month_num = months.index(month) + 1
                    date_str = f"{current_year}-{month_num:02d}-{day:02d}"
                    c.execute("UPDATE expenses SET date=? WHERE id=?", (date_str, expense_id))

            # Remove old columns if they exist
            if 'month' in columns:
                c.execute("CREATE TABLE expenses_new AS SELECT id, username, item, price, date FROM expenses")
                c.execute("DROP TABLE expenses")
                c.execute("ALTER TABLE expenses_new RENAME TO expenses")

        except sqlite3.Error as e:
            print(f"Database migration error: {e}")
            conn.rollback()
        else:
            conn.commit()

    conn.close()


# === Helper Functions ===
def get_days_in_month(year, month):
    """Return the number of days in a month accounting for leap years"""
    if month == 2:
        return 29 if (year % 4 == 0 and year % 100 != 0) or (year % 400 == 0) else 28
    elif month in [4, 6, 9, 11]:
        return 30
    return 31


def format_currency(amount):
    """Format number with commas and 2 decimal places"""
    return f"{amount:,.2f}"


# === Register Page ===
class RegisterPage(QWidget):
    switch_to_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #f4f8fb;")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 30)
        self.setLayout(main_layout)

        # Form container
        form_container = QFrame()
        form_container.setStyleSheet("""
            background-color: white; 
            border-radius: 10px; 
            border: 1px solid #ddd;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        # Title and subtitle
        title_label = QLabel("Create Account")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        subtitle_label = QLabel("Start tracking your expenses today")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")

        form_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        form_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        form_layout.addSpacing(15)

        # Form fields
        self.name_field = self._create_form_field("Full Name")
        self.username_field = self._create_form_field("Username")
        self.email_field = self._create_form_field("Email")
        self.password_field = self._create_form_field("Password", is_password=True)

        form_layout.addLayout(self.name_field)
        form_layout.addLayout(self.username_field)
        form_layout.addLayout(self.email_field)
        form_layout.addLayout(self.password_field)
        form_layout.addSpacing(10)

        # Register button
        register_btn = QPushButton("Register")
        register_btn.setStyleSheet("""
            QPushButton {
                background-color: #3498db; 
                color: white; 
                border-radius: 5px; 
                padding: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #2980b9;
            }
        """)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(self.register)
        form_layout.addWidget(register_btn)

        # Login link
        login_container = QHBoxLayout()
        login_text = QLabel("Already have an account?")
        login_text.setFont(QFont("Segoe UI", 9))
        login_btn = QPushButton("Go to Login")
        login_btn.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #3498db; 
                border: none; 
                text-decoration: underline;
            }
            QPushButton:hover { 
                color: #2980b9; 
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.switch_to_login.emit)

        login_container.addWidget(login_text)
        login_container.addWidget(login_btn)
        form_layout.addLayout(login_container)

        main_layout.addWidget(form_container)

    def _create_form_field(self, label_text, is_password=False):
        layout = QVBoxLayout()
        label = QLabel(label_text)
        label.setFont(QFont("Segoe UI", 9))
        entry = QLineEdit()
        entry.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        if is_password:
            entry.setEchoMode(QLineEdit.Password)

        layout.addWidget(label)
        layout.addWidget(entry)

        return layout

    def register(self):
        # Get values from form fields
        name = self.name_field.itemAt(1).widget().text().strip()
        username = self.username_field.itemAt(1).widget().text().strip()
        email = self.email_field.itemAt(1).widget().text().strip()
        password = self.password_field.itemAt(1).widget().text().strip()

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
        self.setStyleSheet("background-color: #f4f8fb;")

        # Main layout
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(main_layout)

        # Form container
        form_container = QFrame()
        form_container.setStyleSheet("""
            background-color: white; 
            border-radius: 10px; 
            border: 1px solid #ddd;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 40, 30, 40)
        form_layout.setSpacing(15)

        # Title and subtitle
        title_label = QLabel("Login")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        subtitle_label = QLabel("Welcome back!")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")

        form_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        form_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        form_layout.addSpacing(15)

        # Username field
        username_layout = QVBoxLayout()
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 9))
        self.username_entry = QLineEdit()
        self.username_entry.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_entry)
        form_layout.addLayout(username_layout)

        # Password field
        password_layout = QVBoxLayout()
        password_label = QLabel("Password")
        password_label.setFont(QFont("Segoe UI", 9))
        self.password_entry = QLineEdit()
        self.password_entry.setEchoMode(QLineEdit.Password)
        self.password_entry.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        password_layout.addWidget(password_label)
        password_layout.addWidget(self.password_entry)
        form_layout.addLayout(password_layout)

        form_layout.addSpacing(10)

        # Login button
        login_btn = QPushButton("Login")
        login_btn.setStyleSheet("""
            QPushButton {
                background-color: #2ecc71; 
                color: white; 
                border-radius: 5px; 
                padding: 10px; 
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #27ae60;
            }
        """)
        login_btn.setCursor(Qt.PointingHandCursor)
        login_btn.clicked.connect(self.login)
        form_layout.addWidget(login_btn)

        # Register link
        register_btn = QPushButton("Back to Register")
        register_btn.setStyleSheet("""
            QPushButton { 
                background-color: transparent; 
                color: #3498db; 
                border: none; 
                text-decoration: underline;
            }
            QPushButton:hover { 
                color: #2980b9; 
            }
        """)
        register_btn.setCursor(Qt.PointingHandCursor)
        register_btn.clicked.connect(self.switch_to_register.emit)
        form_layout.addWidget(register_btn, alignment=Qt.AlignCenter)

        main_layout.addWidget(form_container)

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
        # Set up the style for the month card
        if self.is_current:
            self.setStyleSheet("""
                QFrame { 
                    background-color: #3498db; 
                    border-radius: 8px; 
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

        self.setCursor(Qt.PointingHandCursor)

        # Layout
        layout = QVBoxLayout(self)
        layout.setContentsMargins(8, 8, 8, 8)

        # Month label
        month_label = QLabel(self.month)
        month_label.setAlignment(Qt.AlignCenter)
        month_label.setFont(QFont("Segoe UI", 12, QFont.Bold))

        layout.addWidget(month_label)
        self.setFixedSize(120, 80)

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
        self.setStyleSheet("""
            QDialog {
                background-color: white;
            }
        """)

        layout = QVBoxLayout(self)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(15)

        # Title
        title = QLabel(f"Add New Expense for {self.month}")
        title.setFont(QFont("Segoe UI", 14, QFont.Bold))
        title.setAlignment(Qt.AlignCenter)
        title.setStyleSheet("color: #2c3e50; margin-bottom: 15px;")
        layout.addWidget(title)

        # Form layout
        form = QFormLayout()
        form.setSpacing(10)

        # Item field
        self.item_input = QLineEdit()
        self.item_input.setPlaceholderText("What did you spend on?")
        self.item_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        form.addRow("Item:", self.item_input)

        # Price field
        self.price_input = QLineEdit()
        self.price_input.setPlaceholderText("0.00")
        self.price_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")

        # Set validator for price input (numbers and one decimal point)
        regex = QRegExp(r'^\d*\.?\d{0,2}$')
        validator = QRegExpValidator(regex)
        self.price_input.setValidator(validator)

        # Connect textChanged signal to format the input
        self.price_input.textChanged.connect(self.format_price_input)

        form.addRow("Price:", self.price_input)

        # Day field
        self.day_input = QSpinBox()
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_index = months.index(self.month) + 1
        max_days = get_days_in_month(self.current_year, month_index)
        self.day_input.setRange(1, max_days)
        self.day_input.setValue(datetime.now().day)
        self.day_input.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        form.addRow("Day:", self.day_input)

        layout.addLayout(form)

        # Calendar widget for selecting day
        calendar_label = QLabel("Or select a date:")
        layout.addWidget(calendar_label)

        self.calendar = QCalendarWidget()
        self.calendar.setGridVisible(True)

        # Customize calendar appearance
        self.calendar.setStyleSheet("""
            QCalendarWidget QAbstractItemView:enabled {
                color: black;
                selection-background-color: #3498db;
                selection-color: white;
            }
            QCalendarWidget QAbstractItemView:disabled {
                color: transparent;
                background: transparent;
            }
            QCalendarWidget QToolButton {
                color: black;
                font-weight: bold;
                font-size: 12px;
            }
            QCalendarWidget QWidget#qt_calendar_navigationbar {
                background-color: #f8f9fa;
            }
            QCalendarWidget QMenu {
                background-color: white;
                color: black;
            }
        """)

        # Hide navigation bar to prevent month changes
        self.calendar.setNavigationBarVisible(False)

        # Only show single letter day names
        self.calendar.setHorizontalHeaderFormat(QCalendarWidget.SingleLetterDayNames)

        # Hide vertical header (week numbers)
        self.calendar.setVerticalHeaderFormat(QCalendarWidget.NoVerticalHeader)

        # Disable dates from other months
        self.calendar.setDateEditEnabled(False)

        self.calendar.clicked.connect(self.update_day_from_calendar)
        layout.addWidget(self.calendar)

        # Set the calendar to current month and year
        self.calendar.setSelectedDate(QDate(self.current_year, month_index, self.day_input.value()))

        # Set date range to only allow dates in current month
        first_day = QDate(self.current_year, month_index, 1)
        last_day = QDate(self.current_year, month_index, max_days)
        self.calendar.setMinimumDate(first_day)
        self.calendar.setMaximumDate(last_day)

        # Buttons
        buttons_layout = QHBoxLayout()

        cancel_btn = QPushButton("Cancel")
        cancel_btn.setStyleSheet("""
            QPushButton { 
                background-color: #95a5a6; 
                color: white; 
                border-radius: 5px; 
                padding: 10px;
            }
            QPushButton:hover { 
                background-color: #7f8c8d; 
            }
        """)
        cancel_btn.clicked.connect(self.reject)

        save_btn = QPushButton("Save Expense")
        save_btn.setStyleSheet("""
            QPushButton { 
                background-color: #2ecc71; 
                color: white; 
                border-radius: 5px; 
                padding: 10px; 
                font-weight: bold;
            }
            QPushButton:hover { 
                background-color: #27ae60; 
            }
        """)
        save_btn.clicked.connect(self.save_expense)

        buttons_layout.addWidget(cancel_btn)
        buttons_layout.addWidget(save_btn)
        layout.addLayout(buttons_layout)

    def format_price_input(self, text):
        cursor_pos = self.price_input.cursorPosition()
        text = text.replace(',', '')  # Remove any existing commas

        if text:  # Only format if there's text
            try:
                # Try to convert to float to validate
                num = float(text)
                # Format with commas and 2 decimal places
                formatted = f"{num:,.2f}"
                # Remove .00 if it's a whole number
                if formatted.endswith(".00"):
                    formatted = formatted[:-3]
                self.price_input.blockSignals(True)
                self.price_input.setText(formatted)
                self.price_input.blockSignals(False)
                # Adjust cursor position
                new_pos = cursor_pos + (len(formatted) - len(text))
                self.price_input.setCursorPosition(min(new_pos, len(formatted)))
            except ValueError:
                pass

    def update_day_from_calendar(self, date):
        self.day_input.setValue(date.day())

    def save_expense(self):
        item = self.item_input.text().strip()
        price_text = self.price_input.text().strip().replace(',', '')  # Remove commas for processing

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

        # Get month number (1-12)
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_num = months.index(self.month) + 1

        # Format date as YYYY-MM-DD
        date_str = f"{self.current_year}-{month_num:02d}-{self.day_input.value():02d}"

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO expenses (username, item, price, date) VALUES (?, ?, ?, ?)",
                  (self.username, item, price, date_str))
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
        # Main layout
        main_layout = QVBoxLayout(self)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header
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

        # Expenses container
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

        # Total section
        self.total_label = QLabel("Total: ₱0.00")
        self.total_label.setFont(QFont("Segoe UI", 14, QFont.Bold))
        self.total_label.setStyleSheet("color: #16a085; padding: 10px 0;")
        self.total_label.setAlignment(Qt.AlignRight)

        main_layout.addWidget(self.total_label)

        # Load expenses
        self.load_expenses()

    def load_expenses(self):
        # Clear current expenses
        while self.expenses_layout.count() > 1:
            item = self.expenses_layout.takeAt(0)
            if item.widget():
                item.widget().deleteLater()

        # Get month number (1-12)
        months = ["January", "February", "March", "April", "May", "June",
                  "July", "August", "September", "October", "November", "December"]
        month_num = months.index(self.month) + 1

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()

        try:
            c.execute("""
                SELECT id, item, price, date 
                FROM expenses 
                WHERE username = ? 
                AND strftime('%m', date) = ?
                AND strftime('%Y', date) = ?
                ORDER BY date
            """, (self.username, f"{month_num:02d}", str(self.current_year)))
            expenses = c.fetchall()
        except sqlite3.OperationalError as e:
            QMessageBox.warning(self, "Database Error", f"Failed to load expenses: {str(e)}")
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
            for expense_id, item, price, date_str in expenses:
                expense_frame = QFrame()
                expense_frame.setStyleSheet("""
                    QFrame { 
                        background-color: #ecf0f1; 
                        border-radius: 5px; 
                        padding: 10px;
                    }
                """)

                expense_layout = QHBoxLayout(expense_frame)
                expense_layout.setContentsMargins(10, 10, 10, 10)

                # Parse date
                date = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date.strftime("%b %d, %Y")  # Format as "May 09, 2025"

                # Date label
                date_label = QLabel(formatted_date)
                date_label.setFont(QFont("Segoe UI", 10))
                date_label.setStyleSheet("color: #7f8c8d;")
                date_label.setFixedWidth(120)

                # Item
                item_label = QLabel(item)
                item_label.setFont(QFont("Segoe UI", 11))
                item_label.setStyleSheet("color: #2c3e50;")

                # Price (formatted with commas)
                price_label = QLabel(f"₱{price:,.2f}")
                price_label.setFont(QFont("Segoe UI", 11, QFont.Bold))
                price_label.setStyleSheet("color: #16a085;")
                price_label.setFixedWidth(100)
                price_label.setAlignment(Qt.AlignRight | Qt.AlignVCenter)

                # Delete button
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

                self.expenses_layout.insertWidget(0, expense_frame)
                total += price

        # Format total with commas
        self.total_label.setText(f"Total: ₱{total:,.2f}")

    def add_expense(self):
        dialog = AddExpenseDialog(self.month, self.username)
        if dialog.exec_() == QDialog.Accepted:
            self.load_expenses()

    def delete_expense(self, expense_id):
        confirm = QMessageBox.question(
            self, "Confirm Delete",
            "Are you sure you want to delete this expense?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if confirm == QMessageBox.Yes:
            conn = sqlite3.connect(DB_PATH)
            c = conn.cursor()
            c.execute("DELETE FROM expenses WHERE id = ?", (expense_id,))
            conn.commit()
            conn.close()
            self.load_expenses()


# === Main Expense Tracker Window ===
class ExpenseTrackerWindow(QMainWindow):
    def __init__(self, username):
        super().__init__()
        self.username = username
        self.current_year = datetime.now().year
        self.months = ["January", "February", "March", "April", "May", "June",
                       "July", "August", "September", "October", "November", "December"]
        self.current_month = self.months[datetime.now().month - 1]
        self.initUI()

    def initUI(self):
        self.setWindowTitle("Expense Tracker")
        self.setGeometry(100, 100, 1000, 700)
        self.setStyleSheet("background-color: white;")

        # Main widget and layout
        main_widget = QWidget()
        main_layout = QVBoxLayout(main_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #3498db;")
        header.setFixedHeight(60)

        header_layout = QHBoxLayout(header)
        header_layout.setContentsMargins(20, 0, 20, 0)

        app_title = QLabel("Expense Tracker")
        app_title.setFont(QFont("Segoe UI", 16, QFont.Bold))
        app_title.setStyleSheet("color: white;")

        user_label = QLabel(f"Welcome, {self.get_user_name()}")
        user_label.setFont(QFont("Segoe UI", 12))
        user_label.setStyleSheet("color: white;")

        header_layout.addWidget(app_title)
        header_layout.addStretch()
        header_layout.addWidget(user_label)

        main_layout.addWidget(header)

        # Month selection - horizontal scrollable
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

        months_layout.addStretch()
        months_scroll.setWidget(months_widget)

        main_layout.addWidget(months_scroll)

        # Month detail view
        self.month_detail_stack = QStackedWidget()

        # Create detail widgets for all months
        for month in self.months:
            detail_widget = MonthDetailWidget(month, self.username)
            self.month_detail_stack.addWidget(detail_widget)

        # Set initial month to current month
        current_month_index = self.months.index(self.current_month)
        self.month_detail_stack.setCurrentIndex(current_month_index)

        main_layout.addWidget(self.month_detail_stack)

        self.setCentralWidget(main_widget)

    def get_user_name(self):
        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT name FROM users WHERE username = ?", (self.username,))
        user = c.fetchone()
        conn.close()

        if user and user[0]:
            return user[0]
        return self.username

    def show_month_detail(self, month):
        month_index = self.months.index(month)
        self.month_detail_stack.setCurrentIndex(month_index)


# === Main Application ===
class ExpenseTrackerApp(QApplication):
    def __init__(self, args):
        super().__init__(args)
        self.initApp()

    def initApp(self):
        # Ensure database exists with correct schema
        setup_database()

        # Create auth window
        self.auth_window = QMainWindow()
        self.auth_window.setWindowTitle("Expense Tracker - Login")
        self.auth_window.setGeometry(100, 100, 500, 700)

        # Auth stacked widget
        self.auth_stack = QStackedWidget()

        # Create pages
        register_page = RegisterPage()
        login_page = LoginPage()

        # Connect signals
        register_page.switch_to_login.connect(lambda: self.auth_stack.setCurrentWidget(login_page))
        login_page.switch_to_register.connect(lambda: self.auth_stack.setCurrentWidget(register_page))
        login_page.login_successful.connect(self.launch_expense_tracker)

        # Add pages to stack
        self.auth_stack.addWidget(register_page)
        self.auth_stack.addWidget(login_page)

        # Set initial page to register
        self.auth_stack.setCurrentWidget(register_page)

        self.auth_window.setCentralWidget(self.auth_stack)
        self.auth_window.show()

    def launch_expense_tracker(self, username):
        self.auth_window.hide()
        self.expense_tracker = ExpenseTrackerWindow(username)
        self.expense_tracker.show()


# === Main Execution ===
if __name__ == "__main__":
    app = ExpenseTrackerApp(sys.argv)
    sys.exit(app.exec_())
