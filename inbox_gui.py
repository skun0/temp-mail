from PyQt5.QtWidgets import (
    QApplication, QWidget, QPushButton, QLabel, QVBoxLayout,
    QMessageBox, QListWidget, QListWidgetItem, QHBoxLayout,
    QLineEdit, QFormLayout, QDialog, QTextBrowser
)
from PyQt5.QtGui import QFont
from PyQt5.QtCore import Qt, QTimer
from mailtm import Email
import sys
import threading
from xml.sax.saxutils import escape

class EmailApp(QWidget):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Temp Email GUI")
        self.setGeometry(300, 300, 500, 520)
        self.setStyleSheet("background-color: #1e1e2f;")

        self.email_client = None
        self.email_address = ""
        self.messages = []

        self.layout = QVBoxLayout()

        self.label = QLabel("Temporary Email Service")
        self.label.setFont(QFont("Arial", 18, QFont.Bold))
        self.label.setStyleSheet("color: white;")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)

        form_layout = QFormLayout()

        self.username_input = QLineEdit()
        self.username_input.setPlaceholderText("Enter username")
        self.username_input.setStyleSheet("""
            color: white;
            padding: 5px;
            border-radius: 5px;
            background-color: #2b2b3d;
        """)
        self.username_input.setStyleSheet(self.username_input.styleSheet() + 
            "QLineEdit { color: white; } QLineEdit:!focus { color: rgba(255, 255, 255, 0.7); }")

        self.password_input = QLineEdit()
        self.password_input.setPlaceholderText("Enter password")
        self.password_input.setEchoMode(QLineEdit.Password)
        self.password_input.setText("")
        self.password_input.setStyleSheet("""
            color: white;
            padding: 5px;
            border-radius: 5px;
            background-color: #2b2b3d;
        """)
        self.password_input.setStyleSheet(self.password_input.styleSheet() + 
            "QLineEdit { color: white; } QLineEdit:!focus { color: rgba(255, 255, 255, 0.7); }")

        form_layout.addRow(self.make_label("Username:"), self.username_input)
        form_layout.addRow(self.make_label("Password:"), self.password_input)
        self.layout.addLayout(form_layout)

        button_layout = QHBoxLayout()
        self.email_button = self.create_button("Start Email Listener", self.start_listener)
        self.credits_button = self.create_button("Credits", self.show_credits)
        self.exit_button = self.create_button("Exit", self.close_app)

        button_layout.addWidget(self.email_button)
        button_layout.addWidget(self.credits_button)
        button_layout.addWidget(self.exit_button)
        self.layout.addLayout(button_layout)

        self.address_label = QLabel("")
        self.address_label.setFont(QFont("Arial", 10))
        self.address_label.setStyleSheet("color: white; margin-top: 10px;")
        self.address_label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.address_label)

        self.inbox_list = QListWidget()
        self.inbox_list.setStyleSheet("""
            QListWidget {
                background-color: #2b2b3d;
                color: white;
                border-radius: 10px;
                padding: 5px;
            }
            QListWidget::item:selected {
                background-color: #5c6bc0;
            }
        """)
        self.inbox_list.itemClicked.connect(self.show_email_content)
        self.layout.addWidget(self.inbox_list)

        self.setLayout(self.layout)

    def make_label(self, text):
        label = QLabel(text)
        label.setStyleSheet("color: white;")
        return label

    def create_button(self, text, callback):
        button = QPushButton(text)
        button.clicked.connect(callback)
        button.setFont(QFont("Segoe UI", 11))
        button.setCursor(Qt.PointingHandCursor)
        button.setStyleSheet("""
            QPushButton {
                background-color: #5c6bc0;
                color: white;
                padding: 10px;
                border-radius: 15px;
            }
            QPushButton:hover {
                background-color: #7986cb;
            }
        """)
        return button

    def show_credits(self):
        QMessageBox.information(self, "Credits", "Made by Skuno")

    def close_app(self):
        self.close()

    def start_listener(self):
        self.email_button.setText("Generating Email...")
        self.email_button.setEnabled(False)
        thread = threading.Thread(target=self.run_email_listener, daemon=True)
        thread.start()

    def run_email_listener(self):
        self.email_client = Email()

        username = self.username_input.text().strip()
        password = self.password_input.text().strip()

        try:
            if username:
                self.email_client.register(username=username, password=password)
            else:
                self.email_client.register(password=password)
            self.email_address = str(self.email_client.address)
        except Exception as e:
            QTimer.singleShot(0, lambda: QMessageBox.warning(self, "Error", f"Registration failed:\n{e}"))
            QTimer.singleShot(0, self.reset_email_button)
            return

        QTimer.singleShot(0, self.after_email_created)

        def listener(message):
            subject = message['subject']
            content = message['text'] if message['text'] else message['html']
            display_text = f"{subject or '(No Subject)'}"
            self.messages.append((subject, content))
            self.inbox_list.addItem(QListWidgetItem(display_text))

        self.email_client.start(listener)

    def reset_email_button(self):
        self.email_button.setText("Start Email Listener")
        self.email_button.setEnabled(True)

    def after_email_created(self):
        self.address_label.setText(f"Your Email Address:\n{self.email_address}")
        self.email_button.setText("Listening for emails...")

        clipboard = QApplication.clipboard()
        clipboard.setText(self.email_address)

        QMessageBox.information(self, "Copied", "Email address copied to clipboard successfully!")

    def show_email_content(self, item):
        index = self.inbox_list.row(item)
        subject, content = self.messages[index]

        dlg = QDialog(self)
        dlg.setWindowTitle(subject or "No Subject")
        dlg.setStyleSheet("background-color: #2b2b3d; color: white;")

        layout = QVBoxLayout()

        text_browser = QTextBrowser()
        text_browser.setStyleSheet("""
            QTextBrowser {
                background-color: #2b2b3d;
                color: white;
                border: none;
                padding: 10px;
                font-family: Segoe UI;
                font-size: 10pt;
            }
            a {
                color: #5c6bc0;
                text-decoration: none;
            }
            a:hover {
                color: #7986cb;
                text-decoration: underline;
            }
        """)

        if content:
            if '<a ' in content or '<html' in content:
                text_browser.setHtml(content)
            else:
                safe_text = escape(content).replace('\n', '<br>')
                text_browser.setHtml(safe_text)
        else:
            text_browser.setText("(No Content)")

        text_browser.setOpenExternalLinks(True)

        layout.addWidget(text_browser)
        dlg.setLayout(layout)
        dlg.resize(450, 350)
        dlg.exec_()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = EmailApp()
    window.show()
    sys.exit(app.exec_())