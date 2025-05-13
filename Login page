# === Login Page ===

class LoginPage(QWidget):
    switch_to_register = pyqtSignal()
    login_successful = pyqtSignal(str)

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #f4f8fb;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 50, 50, 50)
        self.setLayout(main_layout)

        form_container = QFrame()
        form_container.setStyleSheet("""
            background-color: white; 
            border-radius: 10px; 
            border: 1px solid #ddd;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 40, 30, 40)
        form_layout.setSpacing(15)

        title_label = QLabel("Login")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        subtitle_label = QLabel("Welcome back!")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")

        form_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        form_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        form_layout.addSpacing(15)

        username_layout = QVBoxLayout()
        username_label = QLabel("Username")
        username_label.setFont(QFont("Segoe UI", 9))
        self.username_entry = QLineEdit()
        self.username_entry.setStyleSheet("padding: 8px; border: 1px solid #ddd; border-radius: 4px;")
        username_layout.addWidget(username_label)
        username_layout.addWidget(self.username_entry)
        form_layout.addLayout(username_layout)

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

        register_btn = QPushButton("Create New Account")
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
