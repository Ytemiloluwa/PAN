import logging
import random  # Keep for potential future examples, but don't use for default plot
from PyQt6.QtWidgets import QWidget, QVBoxLayout, QGroupBox, QLabel
from PyQt6.QtCore import pyqtSlot

from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib.pyplot as plt


class AnalyticsDashboardWidget(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.logger = logging.getLogger("fintechx_desktop.ui.analytics_dashboard")
        main_layout = QVBoxLayout(self)
        dashboard_group = QGroupBox("Payment Analytics Dashboard")
        self.dashboard_layout = QVBoxLayout()  # instance variable to allow clearing/adding widgets

        self.figure = Figure(figsize=(5, 4), dpi=100)
        self.canvas = FigureCanvas(self.figure)
        self.dashboard_layout.addWidget(self.canvas)

        # Add a label for status messages (e.g., "No data")
        self.status_label = QLabel("")
        self.dashboard_layout.addWidget(self.status_label)

        dashboard_group.setLayout(self.dashboard_layout)
        main_layout.addWidget(dashboard_group)
        self.setLayout(main_layout)

        # Load data when the widget is initialized/shown
        self.load_and_plot_data()

    def fetch_analytics_data(self):
        self.logger.info("Simulating fetching analytics data (currently returns empty)...")
        volume_data = {}
        trend_data = {}
        return volume_data, trend_data

    def load_and_plot_data(self):
        self.figure.clear()
        self.status_label.setText("")  # Clear status
        volume_data, trend_data = self.fetch_analytics_data()

        # Check if data was fetched successfully (even if empty)
        if volume_data is None or trend_data is None:
            self.status_label.setText("Error loading analytics data.")
            self.canvas.draw()
            return

        # Check if there is any data to plot
        has_volume_data = bool(volume_data)
        has_trend_data = bool(trend_data)

        if not has_volume_data and not has_trend_data:
            self.status_label.setText("No analytics data available to display.")
            # Optionally add placeholder text directly on the canvas
            ax = self.figure.add_subplot(111)
            ax.text(0.5, 0.5, "No Data Available", ha="center", va="center", fontsize=12, color="gray")
            ax.axis("off") # Hide axes
            self.canvas.draw()
            return

        # --- Plotting Logic ---
        if has_volume_data:
            ax1 = self.figure.add_subplot(121 if has_trend_data else 111)
            categories = list(volume_data.keys())
            volumes = list(volume_data.values())
            ax1.bar(categories, volumes, color="skyblue")
            ax1.set_title("Transaction Volume by Category")
            ax1.set_ylabel("Volume ($)")
            ax1.tick_params(axis="x", rotation=45)

            # Plot trend data if available
            if has_trend_data:
                ax2 = self.figure.add_subplot(122 if has_volume_data else 111)
            months = list(trend_data.keys())
            spending = list(trend_data.values())
            ax2.plot(months, spending, marker="o", linestyle="-", color="green")
            ax2.set_title("Monthly Spending Trend")
            ax2.set_ylabel("Total Spending ($)")
            ax2.grid(True)

            self.figure.tight_layout()
            self.canvas.draw()
            self.logger.info("Analytics dashboard plots updated.")

    def refresh_dashboard(self):
        self.load_and_plot_data()
