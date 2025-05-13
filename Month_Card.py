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
                    padding:  10px;
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
