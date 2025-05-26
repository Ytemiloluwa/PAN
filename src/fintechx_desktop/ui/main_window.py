import sys
import logging
from PySide6.QtWidgets import (
    QApplication, QMainWindow, QStatusBar, QLabel, QVBoxLayout, QWidget, QPushButton, 
    QStackedWidget, QLineEdit, QFormLayout, QSpinBox, QTextEdit, QMessageBox, 
    QGroupBox, QHBoxLayout, QComboBox
)
from PySide6.QtCore import Qt, Slot

# Import the native C++ module
try:
    from fintechx_desktop.infrastructure import fintechx_native
    NATIVE_MODULE_AVAILABLE = True
except ImportError:
    logging.error("Native C++ module (fintechx_native) not found. Ensure it's built and installed.")
    # Define dummy native module for UI development if needed
    class DummyNative:
        def luhn_check(self, pan): return False
        def generate_pan(self, prefix, length): return None
        def generate_pan_batch(self, prefix, length, count): return []
    fintechx_native = DummyNative()
    NATIVE_MODULE_AVAILABLE = False

# Placeholder Widgets for other views
class LoginWidget(QWidget):
    # Keep the previous simple placeholder for now
    # Authentication logic will be connected later
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Login Screen Placeholder"))
        self.setLayout(layout)

class DashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        layout = QVBoxLayout(self)
        layout.addWidget(QLabel("Dashboard Placeholder"))
        self.setLayout(layout)

# --- PAN Tools Widget --- 
class PanToolsWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        main_layout = QVBoxLayout(self)

        # --- Validation Group --- 
        validation_group = QGroupBox("Validate PAN")
        validation_layout = QFormLayout()
        self.pan_validate_input = QLineEdit()
        self.pan_validate_input.setPlaceholderText("Enter PAN to validate")
        self.validate_button = QPushButton("Validate")
        self.validate_result_label = QLabel("Result: ")
        validation_layout.addRow("PAN:", self.pan_validate_input)
        validation_layout.addRow(self.validate_button)
        validation_layout.addRow(self.validate_result_label)
        validation_group.setLayout(validation_layout)

        # --- Generation Group --- 
        generation_group = QGroupBox("Generate PAN(s)")
        generation_layout = QFormLayout()
        self.pan_prefix_input = QLineEdit()
        self.pan_prefix_input.setPlaceholderText("e.g., 4, 51, 37")
        self.pan_length_combo = QComboBox()
        self.pan_length_combo.addItems(["16 (Visa/Mastercard)", "15 (Amex)", "13 (Visa)"])
        self.pan_count_spinbox = QSpinBox()
        self.pan_count_spinbox.setRange(1, 1000)
        self.pan_count_spinbox.setValue(1)
        self.generate_button = QPushButton("Generate")
        self.generated_pans_output = QTextEdit()
        self.generated_pans_output.setReadOnly(True)

        generation_layout.addRow("Prefix (IIN):", self.pan_prefix_input)
        generation_layout.addRow("Length:", self.pan_length_combo)
        generation_layout.addRow("Count:", self.pan_count_spinbox)
        generation_layout.addRow(self.generate_button)
        generation_layout.addRow("Generated PANs:", self.generated_pans_output)
        generation_group.setLayout(generation_layout)

        main_layout.addWidget(validation_group)
        main_layout.addWidget(generation_group)
        self.setLayout(main_layout)

        # --- Connect Signals --- 
        self.validate_button.clicked.connect(self.validate_pan)
        self.generate_button.clicked.connect(self.generate_pans)

    @Slot()
    def validate_pan(self):
        pan_to_validate = self.pan_validate_input.text().strip().replace(" ", "") # Remove spaces
        if not pan_to_validate:
            self.validate_result_label.setText("Result: Please enter a PAN.")
            return
        if not pan_to_validate.isdigit():
             self.validate_result_label.setText("Result: PAN must contain only digits.")
             return

        try:
            is_valid = fintechx_native.luhn_check(pan_to_validate)
            if is_valid:
                self.validate_result_label.setText("Result: <font color='green'>Valid (Luhn Check Passed)</font>")
            else:
                self.validate_result_label.setText("Result: <font color='red'>Invalid (Luhn Check Failed)</font>")
        except Exception as e:
            logging.error(f"Error during PAN validation: {e}")
            self.validate_result_label.setText("Result: <font color='red'>Error during validation.</font>")
            QMessageBox.warning(self, "Validation Error", f"An error occurred: {e}")

    @Slot()
    def generate_pans(self):
        prefix = self.pan_prefix_input.text().strip()
        count = self.pan_count_spinbox.value()
        length_text = self.pan_length_combo.currentText()
        
        # Extract length from combo box text
        try:
            length = int(length_text.split(" ")[0])
        except (ValueError, IndexError):
             QMessageBox.warning(self, "Input Error", "Invalid length selected.")
             return

        if not prefix:
            QMessageBox.warning(self, "Input Error", "Please enter a PAN prefix.")
            return
        if not prefix.isdigit():
             QMessageBox.warning(self, "Input Error", "Prefix must contain only digits.")
             return
        if len(prefix) >= length:
             QMessageBox.warning(self, "Input Error", "Prefix length must be less than total PAN length.")
             return

        try:
            if count == 1:
                pan = fintechx_native.generate_pan(prefix, length)
                if pan:
                    self.generated_pans_output.setText(pan)
                else:
                    self.generated_pans_output.setText("Failed to generate PAN (check prefix/length).")
            else:
                pans = fintechx_native.generate_pan_batch(prefix, length, count)
                if pans:
                    self.generated_pans_output.setText("\n".join(pans))
                else:
                    self.generated_pans_output.setText("Failed to generate PAN batch (check prefix/length).")
        except Exception as e:
            logging.error(f"Error during PAN generation: {e}")
            self.generated_pans_output.setText("Error during generation.")
            QMessageBox.warning(self, "Generation Error", f"An error occurred: {e}")

# --- Main Window --- 
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()

        self.setWindowTitle("FinTechX Desktop")
        self.setGeometry(100, 100, 800, 600) # x, y, width, height

        # Central Widget to hold different views
        self.central_widget = QStackedWidget()
        self.setCentralWidget(self.central_widget)

        # Create view instances
        self.login_view = LoginWidget()
        self.dashboard_view = DashboardWidget()
        self.pan_tools_view = PanToolsWidget() # Now includes functionality

        # Add views to the stacked widget
        self.central_widget.addWidget(self.login_view)
        self.central_widget.addWidget(self.dashboard_view)
        self.central_widget.addWidget(self.pan_tools_view)

        # --- Navigation --- 
        # Initially show login screen (will be changed later)
        # For now, let's add a way to switch views for testing
        self.setup_menus() # Setup menu bar for navigation
        self.show_login_screen() # Start with login

        # --- Status Bar --- 
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")

    def showEvent(self, event):
        """Called when the window is shown."""
        super().showEvent(event)
        # Show native module warning if needed
        if not NATIVE_MODULE_AVAILABLE:
            QMessageBox.warning(self, "Warning", "Native C++ module not found. PAN features will use dummy implementations.")

    def setup_menus(self):
        menu_bar = self.menuBar()
        
        # File Menu
        file_menu = menu_bar.addMenu("&File")
        # Add login/logout actions later
        exit_action = file_menu.addAction("E&xit")
        exit_action.triggered.connect(self.close)

        # View Menu (for testing navigation)
        view_menu = menu_bar.addMenu("&View")
        login_action = view_menu.addAction("Login Screen")
        dashboard_action = view_menu.addAction("Dashboard")
        pan_tools_action = view_menu.addAction("PAN Tools")

        login_action.triggered.connect(self.show_login_screen)
        dashboard_action.triggered.connect(self.show_dashboard)
        pan_tools_action.triggered.connect(self.show_pan_tools)
        
        # Add other menus (Tools, Help) later

    def show_login_screen(self):
        self.central_widget.setCurrentWidget(self.login_view)
        self.statusBar().showMessage("Please Login")

    def show_dashboard(self):
        # This would be called after successful login
        self.central_widget.setCurrentWidget(self.dashboard_view)
        self.statusBar().showMessage("Dashboard Active")

    def show_pan_tools(self):
        self.central_widget.setCurrentWidget(self.pan_tools_view)
        self.statusBar().showMessage("PAN Tools Active")

    def closeEvent(self, event):
        # Add cleanup code here if needed (e.g., close DB connection)
        logging.info("Closing application...")
        event.accept()

# Main application entry point (typically in a separate main.py)
# def run_app():
#     logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
#     app = QApplication(sys.argv)
#     main_window = MainWindow()
#     main_window.show()
#     sys.exit(app.exec())

# if __name__ == "__main__":
#     run_app()

