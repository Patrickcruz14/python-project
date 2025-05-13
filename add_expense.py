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

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("SELECT id, name FROM categories ORDER BY id")
        categories = c.fetchall()
        conn.close()

        for cat_id, cat_name in categories:
            self.category_combo.addItem(cat_name, cat_id)

        form.addRow("Category:", self.category_combo)

        # Create date input with proper month constraints
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
        category_id = self.category_combo.currentData()

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

        date_str = self.date_input.date().toString("yyyy-MM-dd")

        conn = sqlite3.connect(DB_PATH)
        c = conn.cursor()
        c.execute("INSERT INTO expenses (username, item, price, date, category_id) VALUES (?, ?, ?, ?, ?)",
                  (self.username, item, price, date_str, category_id))
        conn.commit()
        conn.close()

        self.accept()
