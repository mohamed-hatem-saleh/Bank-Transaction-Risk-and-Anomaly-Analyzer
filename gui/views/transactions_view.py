"""
Transactions View - Display flagged suspicious transactions (optimized)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from app_state_manager import AppStateManager


class TransactionsView(QWidget):
    """View for displaying flagged transactions with pagination"""
    
    def __init__(self, state_manager: AppStateManager, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.current_page = 0
        self.rows_per_page = 100
        self.data_cache = None
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the transactions view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Flagged Suspicious Transactions")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #0066cc; padding-bottom: 10px;")
        layout.addWidget(header)
        
        # Stats row
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total Flagged: —")
        self.total_label.setStyleSheet("font-size: 14px; padding: 5px;")
        stats_layout.addWidget(self.total_label)
        
        self.percentage_label = QLabel("Percentage: —")
        self.percentage_label.setStyleSheet("font-size: 14px; padding: 5px;")
        stats_layout.addWidget(self.percentage_label)
        
        self.volume_label = QLabel("Flagged Volume: —")
        self.volume_label.setStyleSheet("font-size: 14px; padding: 5px;")
        stats_layout.addWidget(self.volume_label)
        
        stats_layout.addStretch()
        
        # Pagination controls
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.clicked.connect(self._previous_page)
        self.prev_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton:disabled { background-color: #f8f8f8; color: #999; }
        """)
        stats_layout.addWidget(self.prev_button)
        
        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet("font-size: 13px; padding: 0 10px;")
        stats_layout.addWidget(self.page_label)
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.clicked.connect(self._next_page)
        self.next_button.setStyleSheet("""
            QPushButton {
                padding: 5px 10px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton:disabled { background-color: #f8f8f8; color: #999; }
        """)
        stats_layout.addWidget(self.next_button)
        
        layout.addLayout(stats_layout)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Table
        self.table = QTableWidget()
        self.table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #d0d0d0;
                gridline-color: #e0e0e0;
                background-color: white;
            }
            QHeaderView::section {
                background-color: #f0f0f0;
                padding: 8px;
                border: 1px solid #d0d0d0;
                font-weight: bold;
            }
        """)
        self.table.setAlternatingRowColors(True)
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)
        layout.addWidget(self.table)
        
        # No data label
        self.no_data_label = QLabel("No flagged transactions. Please run the analysis first.")
        self.no_data_label.setStyleSheet("font-size: 14px; color: #999; padding: 20px;")
        self.no_data_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.no_data_label)
        
        self.table.hide()
    
    def _connect_signals(self):
        """Connect to state manager signals"""
        self.state_manager.data_updated.connect(self._on_data_updated)
    
    def _on_data_updated(self, key: str):
        """Handle data updates"""
        if key == 'flagged_transactions':
            self.data_cache = None
            self.current_page = 0
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._display_page()
    
    def _next_page(self):
        """Go to next page"""
        if self.data_cache is not None:
            max_page = (len(self.data_cache) - 1) // self.rows_per_page
            if self.current_page < max_page:
                self.current_page += 1
                self._display_page()
    
    def _load_data(self):
        """Load and cache flagged transactions"""
        if self.data_cache is None:
            self.data_cache = self.state_manager.get_data('flagged_transactions')
        
        flagged_data = self.data_cache
        all_data = self.state_manager.get_data('cleaned_data')
        
        if flagged_data is None or flagged_data.empty:
            self.table.hide()
            self.no_data_label.show()
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
        
        # Update stats (only once)
        total_flagged = len(flagged_data)
        total_transactions = len(all_data) if all_data is not None else 0
        percentage = (total_flagged / total_transactions * 100) if total_transactions > 0 else 0
        flagged_volume = flagged_data['amount'].sum()
        
        self.total_label.setText(f"Total Flagged: {total_flagged:,}")
        self.percentage_label.setText(f"Percentage: {percentage:.2f}%")
        self.volume_label.setText(f"Flagged Volume: ${flagged_volume:,.2f}")
        
        self._display_page()
    
    def _display_page(self):
        """Display current page"""
        if self.data_cache is None or self.data_cache.empty:
            return
        
        self.no_data_label.hide()
        self.table.show()
        
        # Calculate pagination
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.data_cache))
        max_page = (len(self.data_cache) - 1) // self.rows_per_page
        
        # Update pagination controls
        self.page_label.setText(f"Page {self.current_page + 1}/{max_page + 1} (Rows {start_idx + 1}-{end_idx})")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < max_page)
        
        # Get page data
        display_data = self.data_cache.iloc[start_idx:end_idx]
        
        # Select relevant columns
        columns = ['nameOrig', 'amount', 'type', 'suspicion_score', 
                  'risk_band', 'suspicion_reasons']
        available_columns = [col for col in columns if col in display_data.columns]
        display_data = display_data[available_columns]
        
        # Setup table
        self.table.clearContents()
        self.table.setRowCount(len(display_data))
        self.table.setColumnCount(len(display_data.columns))
        self.table.setHorizontalHeaderLabels(display_data.columns.tolist())
        
        # Color map
        color_map = {
            'Critical': QColor(255, 200, 200),
            'High': QColor(255, 230, 200),
            'Medium': QColor(255, 255, 200),
            'Low': QColor(220, 255, 220)
        }
        
        # Populate table
        for i, row in enumerate(display_data.itertuples(index=False)):
            # Get risk band for color
            risk_band_idx = available_columns.index('risk_band') if 'risk_band' in available_columns else -1
            risk_band = row[risk_band_idx] if risk_band_idx >= 0 else 'Low'
            row_color = color_map.get(risk_band, QColor(255, 255, 255))
            
            for j, value in enumerate(row):
                text = f"{value:.2f}" if isinstance(value, float) else str(value)
                item = QTableWidgetItem(text)
                item.setBackground(row_color)
                self.table.setItem(i, j, item)
        
        # Resize columns
        if self.current_page == 0:
            QTimer.singleShot(50, lambda: self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive))
    
    def showEvent(self, event):
        """Load data when view is shown"""
        super().showEvent(event)
        if self.data_cache is None:
            QTimer.singleShot(100, self._load_data)