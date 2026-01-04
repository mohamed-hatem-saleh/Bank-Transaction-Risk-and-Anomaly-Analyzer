"""
Dashboard View - Overview and welcome screen
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QFrame, QGridLayout)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont
from app_state_manager import AppStateManager


class StatCard(QFrame):
    """Statistical card widget"""
    
    def __init__(self, title, value, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            StatCard {
                background-color: white;
                border: 1px solid #e0e0e0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("color: #666; font-size: 13px;")
        layout.addWidget(title_label)
        
        # Value
        self.value_label = QLabel(value)
        self.value_label.setStyleSheet("color: #0066cc; font-size: 28px; font-weight: bold;")
        layout.addWidget(self.value_label)
    
    def set_value(self, value):
        """Update the card value"""
        self.value_label.setText(value)


class DashboardView(QWidget):
    """Dashboard view showing application overview"""
    
    def __init__(self, state_manager: AppStateManager, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the dashboard UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Bank Transaction Risk & Anomaly Analyzer")
        header.setStyleSheet("""
            QLabel {
                font-size: 28px;
                font-weight: bold;
                color: #0066cc;
                padding-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Welcome message
        welcome = QLabel(
            "Welcome to the Bank Transaction Risk Analyzer!\n\n"
        )
        welcome.setStyleSheet("font-size: 14px; color: #333; padding: 20px 0;")
        welcome.setWordWrap(True)
        layout.addWidget(welcome)
        
        # Statistics grid
        stats_label = QLabel("Current Status")
        stats_label.setStyleSheet("font-size: 18px; font-weight: bold; padding: 10px 0;")
        layout.addWidget(stats_label)
        
        stats_grid = QGridLayout()
        stats_grid.setSpacing(15)
        
        self.card_transactions = StatCard("Total Transactions", "—")
        self.card_customers = StatCard("Customers Analyzed", "—")
        self.card_flagged = StatCard("Flagged Transactions", "—")
        self.card_status = StatCard("Analysis Status", "Not Started")
        
        stats_grid.addWidget(self.card_transactions, 0, 0)
        stats_grid.addWidget(self.card_customers, 0, 1)
        stats_grid.addWidget(self.card_flagged, 1, 0)
        stats_grid.addWidget(self.card_status, 1, 1)
        
        layout.addLayout(stats_grid)
        
        # Spacer
        layout.addStretch()
        
    
    def _connect_signals(self):
        """Connect to state manager signals"""
        self.state_manager.data_updated.connect(self._update_stats)
        self.state_manager.state_changed.connect(self._update_status)
    
    def _update_stats(self):
        """Update statistics cards"""
        stats = self.state_manager.get_summary_stats()
        
        if 'total_transactions' in stats:
            self.card_transactions.set_value(f"{stats['total_transactions']:,}")
        
        if 'total_customers' in stats:
            self.card_customers.set_value(f"{stats['total_customers']:,}")
        
        if 'flagged_count' in stats:
            self.card_flagged.set_value(f"{stats['flagged_count']:,}")
    
    def _update_status(self, state):
        """Update status card"""
        status_map = {
            "idle": "Ready",
            "loading_data": "Loading...",
            "cleaning_data": "Cleaning...",
            "building_features": "Building...",
            "scoring_customers": "Scoring...",
            "flagging_transactions": "Flagging...",
            "generating_reports": "Generating...",
            "completed": "✓ Complete",
            "error": "✗ Error"
        }
        self.card_status.set_value(status_map.get(state.value, "Processing"))