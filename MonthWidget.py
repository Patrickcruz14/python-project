
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
            # Get expenses grouped by category
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

            # Get all individual expenses for detailed display
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
                    # Add category header if this is a new category
                    if current_category is not None:
                        # Add category total
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

                    # Add new category header
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

                # Add expense item
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

                # Update the total for the current category
                category_total += price
                total += price

            # After the loop, add the total for the last category
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

        # Update the overall total label
        self.total_label.setText(f"Total: ₱{total:,.2f}")
