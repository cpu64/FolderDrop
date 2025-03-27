#pip install PyQt6
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QTextEdit, QWidget, QGridLayout, QSystemTrayIcon, QMenu
from PyQt6.QtGui import QIcon, QAction
from PyQt6.QtCore import Qt
from FolderDrop import FolderDrop

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.folderdrop = None
        self.directory = None
        self.link = None

        self.setWindowTitle("FolderDrop")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(central_widget)  # Set it as the central widget

        main_layout = QVBoxLayout(central_widget)

# === TOP LAYOUT START ===
        top_layout = QHBoxLayout()

    # === LEFT PANEL START ===
        left_panel = QVBoxLayout()

        link_grid = QGridLayout()

        # example: <a href='http://localhost:5000'>http://localhost:5000</a>
        self.link_localhost = QLabel("<a href='No Link Available'>No Link Available</a>")
        self.link_localhost.setTextFormat(Qt.TextFormat.RichText)
        self.link_localhost.setOpenExternalLinks(True)
        link_grid.addWidget(self.link_localhost, 0, 0)

        self.button_localhost = QPushButton("Copy to clipboard")
        self.button_localhost.clicked.connect(lambda: QApplication.clipboard().setText(self.link_localhost.text().split("'")[1].split("'")[0]))
        link_grid.addWidget(self.button_localhost, 0, 1)

        self.link_localnetwork = QLabel("<a href='No Link Available'>No Link Available</a>")
        self.link_localnetwork.setTextFormat(Qt.TextFormat.RichText)
        self.link_localnetwork.setOpenExternalLinks(True)
        link_grid.addWidget(self.link_localnetwork, 1, 0)

        self.button_localnetwork = QPushButton("Copy to clipboard")
        self.button_localnetwork.clicked.connect(lambda: QApplication.clipboard().setText(self.link_localnetwork.text().split("'")[1].split("'")[0]))
        link_grid.addWidget(self.button_localnetwork, 1, 1)

        self.link_external = QLabel("<a href='No Link Available'>No Link Available</a>")
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

       # START Directory selection grid 2x2
        directory_grid = QGridLayout()
        directory_grid.addWidget(QLabel("Directory:"), 0, 0)
        self.directory_text = QLineEdit()
        self.directory_text.resize(450, 30)
        directory_grid.addWidget(self.directory_text, 1, 0)

        self.directory_button = QPushButton("Select directory")
        self.directory_button.clicked.connect(self.select_directory)
        directory_grid.addWidget(self.directory_button, 1, 1)

        right_panel.addLayout(directory_grid)
       # END Directory selection grid

       # START Password selection grid 2x2
        password_grid = QGridLayout()
        password_grid.addWidget(QLabel("Password:"), 0, 0)
        self.password_text = QLineEdit()
        self.password_text.resize(450, 30)
        self.password_text.setEchoMode(QLineEdit.EchoMode.Password)
        password_grid.addWidget(self.password_text, 1, 0)

        right_panel.addLayout(password_grid)
       # END Password selection grid

        self.start_button = QPushButton("Start FolderDrop")
        self.start_button.clicked.connect(self.start_folderdrop)
        right_panel.addWidget(self.start_button)

        self.stop_button = QPushButton("Stop FolderDrop")
        self.stop_button.clicked.connect(self.stop_folderdrop)
        right_panel.addWidget(self.stop_button)

        top_layout.addLayout(right_panel, 1)
    # === RIGHT PANEL END ===

        main_layout.addLayout(top_layout)
# === TOP LAYOUT END ===

# === BOTTOM LAYOUT START ===
        bottom_layout = QVBoxLayout()
        self.log_button = QPushButton("Logs:")
        self.log_button.setMaximumSize(45, 30)
        self.log_button.clicked.connect(self.hideLogs)
        bottom_layout.addWidget(self.log_button)

        self.logs = QTextEdit()
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

    # Opens a file dialog to select a directory
    def select_directory(self):
        self.directory_text.setText(QFileDialog.getExistingDirectory(self, 'Select Folder'))

    # Starts FolderDrop flask server
    def start_folderdrop(self):
        if not self.folderdrop:
            if not self.directory_text.text():
                directory = './share'
            else:
                directory = self.directory_text.text()

            if not self.password_text.text():
                password = 'test'
            else:
                password = self.password_text.text()

            self.folderdrop = FolderDrop(directory=directory, password=password, host=self)
            self.link.setText(self.folderdrop.run())
        else:
            self.log("FolderDrop already running.")

    # Stops FolderDrop flask server
    def stop_folderdrop(self):
        if self.folderdrop:
            self.folderdrop.stop()
            self.folderdrop = None
        else:
            self.log("FolderDrop not running.")

    # Logs a message to the QTextEdit
    def log(self, message):
        self.logs.append(message)

    # Exits the application
    def exit_app(self):
        self.stop_folderdrop()
        QApplication.instance().quit()

    # Hides the main window and shows the system tray icon
    # when the close button (X) in upper right corner is clicked
    def closeEvent(self, event):
        event.ignore()
        self.hide()

    # Shows the main window when the system tray icon is clicked
    def on_tray_icon_activated(self, reason):
        if reason == QSystemTrayIcon.ActivationReason.Trigger:
            self.show()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle
    window = MainWindow()
    window.show()
    sys.exit(app.exec())
