# === Register Page ===

class RegisterPage(QWidget):
    switch_to_login = pyqtSignal()

    def __init__(self):
        super().__init__()
        self.initUI()

    def initUI(self):
        self.setStyleSheet("background-color: #f4f8fb;")
        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(50, 30, 50, 30)
        self.setLayout(main_layout)

        form_container = QFrame()
        form_container.setStyleSheet("""
            background-color: white; 
            border-radius: 10px; 
            border: 1px solid #ddd;
        """)
        form_layout = QVBoxLayout(form_container)
        form_layout.setContentsMargins(30, 30, 30, 30)
        form_layout.setSpacing(15)

        title_label = QLabel("Create Account")
        title_label.setFont(QFont("Segoe UI", 18, QFont.Bold))
        title_label.setStyleSheet("color: #2c3e50;")
        subtitle_label = QLabel("Start tracking your expenses today")
        subtitle_label.setFont(QFont("Segoe UI", 10))
        subtitle_label.setStyleSheet("color: #7f8c8d;")

        form_layout.addWidget(title_label, alignment=Qt.AlignCenter)
        form_layout.addWidget(subtitle_label, alignment=Qt.AlignCenter)
        form_layout.addSpacing(15)

        self.name_field = self._create_form_field("Full Name")
        self.username_field = self._create_form_field("Username")
        self.email_field = self._create_form_field("Email")
        self.password_field = self._create_form_field("Password", is_password=True)

        form_layout.addLayout(self.name_field)
        form_layout.addLayout(self.username_field)
        form_layout.addLayout(self.email_field)
        form_layout.addLayout(self.password_field)
        form_layout.addSpacing(10)

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
