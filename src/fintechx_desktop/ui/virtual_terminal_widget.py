import logging
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QGroupBox, QFormLayout, QLineEdit, QPushButton, QLabel,
    QMessageBox, QComboBox, QDoubleSpinBox, QDateEdit
)
from PyQt6.QtCore import pyqtSlot, QDate

try:
    from fintechx_desktop.infrastructure import fintechx_native
except ImportError:
    logging.error("Native C++ module (fintechx_native) not found. PAN validation disabled.")

    class DummyNative:
        def luhn_check(self, pan): return True # Assume valid for UI dev
    fintechx_native = DummyNative()


class VirtualTerminalWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("fintechx_desktop.ui.virtual_terminal")
        main_layout = QVBoxLayout(self)

        vt_group = QGroupBox("Virtual Terminal (Local Validation Only)")
        form_layout = QFormLayout()

        self.pan_input = QLineEdit()
        self.pan_input.setPlaceholderText("Enter card number")
        self.expiry_input = QDateEdit()
        self.expiry_input.setDisplayFormat("MM/yy")
        self.expiry_input.setCalendarPopup(True)
        self.expiry_input.setMinimumDate(QDate.currentDate().addMonths(1))
        self.cvv_input = QLineEdit()
        self.cvv_input.setPlaceholderText("3 or 4 digits")
        self.cvv_input.setMaxLength(4)
        self.cvv_input.setEchoMode(QLineEdit.EchoMode.Password)
        self.amount_input = QDoubleSpinBox()
        self.amount_input.setRange(0.01, 1000000.00)
        self.amount_input.setDecimals(2)
        self.amount_input.setPrefix("$") # Example currency
        self.currency_input = QComboBox()
        self.currency_input.addItems(["USD", "EUR", "GBP", "CAD"]) # Example currencies
        self.description_input = QLineEdit()
        self.description_input.setPlaceholderText("Optional description")

        self.submit_button = QPushButton("Submit (Simulated)")
        self.clear_button = QPushButton("Clear")
        self.result_label = QLabel("Status: Ready")

        form_layout.addRow("Card Number:", self.pan_input)
        form_layout.addRow("Expiry Date (MM/YY):", self.expiry_input)
        form_layout.addRow("CVV:", self.cvv_input)
        form_layout.addRow("Amount:", self.amount_input)
        form_layout.addRow("Currency:", self.currency_input)
        form_layout.addRow("Description:", self.description_input)
        button_layout = QVBoxLayout()
        button_layout.addWidget(self.submit_button)
        button_layout.addWidget(self.clear_button)
        form_layout.addRow(button_layout)
        form_layout.addRow(self.result_label)

        vt_group.setLayout(form_layout)
        main_layout.addWidget(vt_group)
        self.setLayout(main_layout)

        # Connect signals
        self.submit_button.clicked.connect(self.submit_simulated_payment)
        self.clear_button.clicked.connect(self.clear_form)

    def clear_form(self):
        self.pan_input.clear()
        self.expiry_input.setDate(QDate.currentDate().addMonths(1))
        self.cvv_input.clear()
        self.amount_input.setValue(0.01)
        self.currency_input.setCurrentIndex(0)
        self.description_input.clear()
        self.result_label.setText("Status: Ready")

    @pyqtSlot()
    def submit_simulated_payment(self):
        pan = self.pan_input.text().strip().replace(" ", "")
        expiry_date = self.expiry_input.date()
        cvv = self.cvv_input.text().strip()
        amount = self.amount_input.value()
        currency = self.currency_input.currentText()
        description = self.description_input.text().strip()

        # --- Input Validation ---
        if not pan or not pan.isdigit():
            QMessageBox.warning(self, "Input Error", "Invalid Card Number format.")
            return
        if not cvv or not cvv.isdigit() or not (3 <= len(cvv) <= 4):
            QMessageBox.warning(self, "Input Error", "Invalid CVV format (must be 3 or 4 digits).")
            return
        if expiry_date < QDate.currentDate():
             QMessageBox.warning(self, "Input Error", "Card has expired.")
             return
        if amount <= 0:
             QMessageBox.warning(self, "Input Error", "Amount must be positive.")
             return

        # --- PAN Luhn Check ---
        try:
            if not fintechx_native.luhn_check(pan):
                self.result_label.setText("Status: <font color=\'red\'>Failed (Invalid Card Number - Luhn Check)</font>")
                self.logger.warning(f"Virtual terminal submission failed for PAN ending {pan[-4:]}: Luhn check failed.")
                return
        except Exception as e:
            self.logger.error(f"Error during PAN validation: {e}")
            self.result_label.setText("Status: <font color=\'red\'>Error during validation.</font>")
            QMessageBox.warning(self, "Validation Error", f"An error occurred during PAN check: {e}")
            return

        success = True
        message = "Local Validation OK - Transaction Simulated Successfully."
        self.logger.info(f"Virtual terminal submission simulated for PAN ending {pan[-4:]}, Amount: {amount} {currency}")

        if success:
            self.result_label.setText(f"Status: <font color=\'green\'>{message}</font>")

        else:
            self.result_label.setText(f"Status: <font color=\'red\'>Failed ({message})</font>")