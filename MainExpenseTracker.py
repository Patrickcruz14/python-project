
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
            # Update active style for the month cards
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
