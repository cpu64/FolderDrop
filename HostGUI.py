#pip install PyQt6
import sys
from PyQt6.QtWidgets import QApplication, QMainWindow, QLabel, QPushButton, QFileDialog, QLineEdit, QVBoxLayout, QHBoxLayout, QTextEdit, QWidget, QGridLayout
from FolderDrop import FolderDrop

class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FolderDrop")
        self.setGeometry(100, 100, 600, 400)

        central_widget = QWidget()  # Create a central widget
        self.setCentralWidget(central_widget)  # Set it as the central widget

        main_layout = QVBoxLayout(central_widget)

# === TOP LAYOUT START ===
        top_layout = QHBoxLayout()

    # === LEFT PANEL START ===
        left_panel = QVBoxLayout()

        left_panel.addWidget(QLabel("Links go here"))

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

        self.folderdrop = None
        self.directory = None

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
            self.folderdrop = FolderDrop(directory=self.directory_text.text())
            self.folderdrop.run()
            self.logs.append("FolderDrop started.")
        else:
            self.logs.append("FolderDrop already running.")

    # Stops FolderDrop flask server
    def stop_folderdrop(self):
        if self.folderdrop:
            self.folderdrop.stop()
            self.folderdrop = None
            self.logs.append("FolderDrop stopped.")
        else:
            self.logs.append("FolderDrop not running.")

    # Exits the application
    def exit_app(self):
        self.stop_folderdrop()
        QApplication.instance().quit()

if __name__ == "__main__":
    app = QApplication(sys.argv)
    app.setStyle
    window = MainWindow()
    window.show()
    sys.exit(app.exec())