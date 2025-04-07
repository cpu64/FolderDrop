#pip install PyQt6
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QTextEdit, QWidget, QGridLayout, QSystemTrayIcon, QMenu, QCheckBox
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt, QCoreApplication
import signal


class SetupWindow(QWidget):
    def __init__(self, config):
        super().__init__()
        self.config=config
        self.setWindowTitle("FolderDrop - Setup")
        self.setWindowIcon(QIcon("static/FolderDrop-icon.svg"))
        self.setGeometry(200, 200, 300, 400)

        main_layout = QVBoxLayout()

        top_layout = QVBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)
# TODO: add port choice.
# Directory selection
        directory_grid = QGridLayout()
        directory_grid.addWidget(QLabel("Directory:"), 0, 0)
        self.directory_text = QLineEdit()
        self.directory_text.setPlaceholderText(f"Default: {self.config.directory}")
        directory_grid.addWidget(self.directory_text, 1, 0)
        self.directory_button = QPushButton("Select directory")
        self.directory_button.clicked.connect(self.select_directory)
        directory_grid.addWidget(self.directory_button, 1, 1)
        top_layout.addLayout(directory_grid)

# Password input
        self.check_password = QCheckBox("Require password")
        self.check_password.setChecked(len(self.config.password) > 0)
        self.check_password.stateChanged.connect(self.toggle_password_fields)
        top_layout.addWidget(self.check_password)

        self.password_grid = QGridLayout()
        self.password_grid.addWidget(QLabel("Password:"), 0, 0)
        self.password_text = QLineEdit()
        self.password_text.setText(self.config.password)
        # TODO: make a 'reveal password' button
        self.password_text.setEchoMode(QLineEdit.EchoMode.Password)
        self.password_grid.addWidget(self.password_text, 1, 0)
        self.toggle_password_fields()

        top_layout.addLayout(self.password_grid)

# Checkboxes
        top_layout.addWidget(QLabel("Permissions:"))

        self.check_downloading = QCheckBox("Allow downloading files")
        self.check_downloading.setChecked(self.config.downloading)
        top_layout.addWidget(self.check_downloading)

        self.check_uploading = QCheckBox("Allow uploading files")
        self.check_uploading.setChecked(self.config.uploading)
        top_layout.addWidget(self.check_uploading)

        self.check_renaming = QCheckBox("Allow renaming files")
        self.check_renaming.setChecked(self.config.renaming)
        top_layout.addWidget(self.check_renaming)

        self.check_deleting = QCheckBox("Allow deleting files")
        self.check_deleting.setChecked(self.config.deleting)
        top_layout.addWidget(self.check_deleting)

        main_layout.addLayout(top_layout)



        bottom_layout = QVBoxLayout()
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)
        # TODO: add funcionality or remove.
        self.check_remember = QCheckBox("Remember settings")
        self.check_remember.setChecked(False)
        bottom_layout.addWidget(self.check_remember)

# Start button
        self.start_button = QPushButton("Start FolderDrop")
        self.start_button.setMinimumHeight(50)
        self.start_button.clicked.connect(self.close_and_return)
        bottom_layout.addWidget(self.start_button)

        main_layout.addLayout(bottom_layout)

        self.setLayout(main_layout)

    def toggle_password_fields(self):
        enabled = self.check_password.isChecked()
        for i in range(self.password_grid.count()):
            widget = self.password_grid.itemAt(i).widget()
            if widget:
                widget.setVisible(enabled)

    def select_directory(self):
        self.directory_text.setText(QFileDialog.getExistingDirectory(self, 'Select Folder'))

    def closeEvent(self, event):
        QCoreApplication.exit(1)

    def close_and_return(self):
        self.config.directory = self.directory_text.text().strip() or self.config.directory
        self.config.password = self.password_text.text() if self.check_password.isChecked() else ""
        self.config.downloading = self.check_downloading.isChecked()
        self.config.uploading = self.check_uploading.isChecked()
        self.config.renaming = self.check_renaming.isChecked()
        self.config.deleting = self.check_deleting.isChecked()
        QCoreApplication.exit(0)


class MainWindow(QMainWindow):
    def __init__(self, ips, port):
        super().__init__()
        self.setWindowTitle("FolderDrop")
        self.setWindowIcon(QIcon("static/FolderDrop-icon.svg"))
        self.setGeometry(100, 100, 600, 300)

        central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(central_widget)  # Set it as the central widget

        main_layout = QVBoxLayout(central_widget)

# === TOP LAYOUT START ===
        top_layout = QHBoxLayout()
        top_layout.setAlignment(Qt.AlignmentFlag.AlignTop)

    # === LEFT PANEL START ===
        left_panel = QVBoxLayout()
        left_panel.setAlignment(Qt.AlignmentFlag.AlignLeft)

        link_grid = QGridLayout()

        # example: <a href='http://localhost:5000'>http://localhost:5000</a>
        self.link_localhost = QLabel(f"<a href='https://localhost:{port}'>https://localhost:{port}</a>")
        self.link_localhost.setTextFormat(Qt.TextFormat.RichText)
        self.link_localhost.setOpenExternalLinks(True)
        link_grid.addWidget(self.link_localhost, 0, 0)

        self.button_localhost = QPushButton("Copy to clipboard")
        self.button_localhost.clicked.connect(lambda: QApplication.clipboard().setText(self.link_localhost.text().split("'")[1].split("'")[0]))
        link_grid.addWidget(self.button_localhost, 0, 1)

        self.link_localnetwork = QLabel(f"<a href='https://{ips[1]}:{port}'>https://{ips[1]}:{port}</a>")
        self.link_localnetwork.setTextFormat(Qt.TextFormat.RichText)
        self.link_localnetwork.setOpenExternalLinks(True)
        link_grid.addWidget(self.link_localnetwork, 1, 0)

        self.button_localnetwork = QPushButton("Copy to clipboard")
        self.button_localnetwork.clicked.connect(lambda: QApplication.clipboard().setText(self.link_localnetwork.text().split("'")[1].split("'")[0]))
        link_grid.addWidget(self.button_localnetwork, 1, 1)
        # TODO: add a message that FolderDrop works in 'local mode' cause we enable port forwarding
        if len(ips) > 2:
            self.link_external = QLabel(f"<a href='https://{ips[2]}:{port}'>https://{ips[2]}:{port}</a>")
            self.link_external.setTextInteractionFlags(Qt.TextInteractionFlag.TextSelectableByMouse)
            self.link_external.setTextFormat(Qt.TextFormat.RichText)
            self.link_external.setOpenExternalLinks(True)
            link_grid.addWidget(self.link_external, 2, 0)

            self.button_external = QPushButton("Copy to clipboard")
            self.button_external.clicked.connect(lambda: QApplication.clipboard().setText(self.link_external.text().split("'")[1].split("'")[0]))
            link_grid.addWidget(self.button_external, 2, 1)

        left_panel.addLayout(link_grid)

        top_layout.addLayout(left_panel, 2)
    # === LEFT PANEL END ===

    # === RIGHT PANEL START ===
        right_panel = QVBoxLayout()
        right_panel.setAlignment(Qt.AlignmentFlag.AlignRight)
        right_panel.setAlignment(Qt.AlignmentFlag.AlignTop)

        self.stop_button = QPushButton("Stop FolderDrop")
        self.stop_button.setStyleSheet("color: red;")
        self.stop_button.clicked.connect(self.exit_app)
        right_panel.addWidget(self.stop_button)

        top_layout.addLayout(right_panel, 1)
    # === RIGHT PANEL END ===

        main_layout.addLayout(top_layout)
# === TOP LAYOUT END ===

# === BOTTOM LAYOUT START ===
        bottom_layout = QVBoxLayout()
        bottom_layout.setAlignment(Qt.AlignmentFlag.AlignBottom)

        self.log_button = QPushButton("Logs:")
        self.log_button.setMaximumSize(45, 30)
        self.log_button.clicked.connect(self.hideLogs)
        bottom_layout.addWidget(self.log_button)

        self.logs = QTextEdit()
        self.logs.setAlignment(Qt.AlignmentFlag.AlignBottom)
        self.logs.setMaximumHeight(200)
        self.logs.setReadOnly(True)
        bottom_layout.addWidget(self.logs)

        main_layout.addLayout(bottom_layout)
# === BOTTOM LAYOUT END ===

        # Create the system tray icon
        self.tray_icon = QSystemTrayIcon(QIcon("static/FolderDrop-icon.svg"), self)
        self.tray_icon.setToolTip("FolderDrop")

        # Create the context menu for the system tray icon
        tray_menu = QMenu()
        restore_action = QAction("Restore", self)
        restore_action.triggered.connect(self.show)
        tray_menu.addAction(restore_action)

        exit_action = QAction("Exit", self)
        exit_action.triggered.connect(self.exit_app)
        tray_menu.addAction(exit_action)

        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.on_tray_icon_activated)
        self.tray_icon.show()


    # Shows/hides the logs (readonly QTextEdit)
    def hideLogs(self):
        if self.logs.isVisible():
            self.logs.hide()
        else:
            self.logs.show()

    # Logs a message to the QTextEdit
    def log(self, message):
        self.logs.append(message)

    # Exits the window
    def exit_app(self):
        QCoreApplication.exit(0)

    # Hides the main window and shows the system tray icon
    # when the close button (X) in upper right corner is clicked
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # Shows the main window when the system tray icon is clicked
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

