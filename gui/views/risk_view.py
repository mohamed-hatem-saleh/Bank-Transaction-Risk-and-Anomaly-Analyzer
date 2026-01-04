"""
Risk View - Display customer risk scores and analysis (optimized)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QTableWidget, QTableWidgetItem, QHeaderView, 
                             QFrame, QComboBox, QPushButton)
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QColor
from app_state_manager import AppStateManager


class RiskView(QWidget):
    """View for displaying customer risk scores with pagination"""
    
    def __init__(self, state_manager: AppStateManager, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.current_page = 0
        self.rows_per_page = 100
        self.full_data = None
        self.filtered_data = None
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the risk view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Customer Risk Scores")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #0066cc; padding-bottom: 10px;")
        layout.addWidget(header)
        
        # Controls row
        controls_layout = QHBoxLayout()
        
        filter_label = QLabel("Filter by Risk Band:")
        filter_label.setStyleSheet("font-size: 14px; padding: 5px;")
        controls_layout.addWidget(filter_label)
        
        self.risk_filter = QComboBox()
        self.risk_filter.addItems(["All", "Critical", "High", "Medium", "Low"])
        self.risk_filter.currentTextChanged.connect(self._apply_filter)
        self.risk_filter.setStyleSheet("""
            QComboBox {
                padding: 5px 10px;
                border: 1px solid #d0d0d0;
                border-radius: 3px;
                min-width: 120px;
            }
        """)
        controls_layout.addWidget(self.risk_filter)
        
        controls_layout.addStretch()
        
        # Pagination controls
        self.prev_button = QPushButton("◀ Prev")
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
        controls_layout.addWidget(self.prev_button)
        
        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet("font-size: 13px; padding: 0 10px;")
        controls_layout.addWidget(self.page_label)
        
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
        controls_layout.addWidget(self.next_button)
        
        # Stats labels
        self.total_label = QLabel("Total: —")
        self.total_label.setStyleSheet("font-size: 14px; padding: 5px 0 5px 15px;")
        controls_layout.addWidget(self.total_label)
        
        self.showing_label = QLabel("Showing: —")
        self.showing_label.setStyleSheet("font-size: 14px; padding: 5px;")
        controls_layout.addWidget(self.showing_label)
        
        layout.addLayout(controls_layout)
        
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
        self.no_data_label = QLabel("No risk scores available. Please run the analysis first.")
        self.no_data_label.setStyleSheet("font-size: 14px; color: #999; padding: 20px;")
        self.no_data_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.no_data_label)
        
        self.table.hide()
    
    def _connect_signals(self):
        """Connect to state manager signals"""
        self.state_manager.data_updated.connect(self._on_data_updated)
    
    def _on_data_updated(self, key: str):
        """Handle data updates"""
        if key == 'risk_scores':
            self.full_data = None
            self.filtered_data = None
            self.current_page = 0
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._display_page()
    
    def _next_page(self):
        """Go to next page"""
        if self.filtered_data is not None:
            max_page = (len(self.filtered_data) - 1) // self.rows_per_page
            if self.current_page < max_page:
                self.current_page += 1
                self._display_page()
    
    def _load_data(self):
        """Load and cache risk scores"""
        if self.full_data is None:
            data = self.state_manager.get_data('risk_scores')
            
            if data is None or data.empty:
                self.table.hide()
                self.no_data_label.show()
                return
            
            self.full_data = data.sort_values('risk_score_normalized', ascending=False)
        
        self._apply_filter()
    
    def _apply_filter(self):
        """Apply risk band filter and reset to first page"""
        if self.full_data is None:
            return
        
        self.current_page = 0
        filter_value = self.risk_filter.currentText()
        
        if filter_value == "All":
            self.filtered_data = self.full_data
        else:
            self.filtered_data = self.full_data[self.full_data['risk_band'] == filter_value]
        
        self._display_page()
    
    def _display_page(self):
        """Display current page of filtered data"""
        if self.filtered_data is None or self.filtered_data.empty:
            self.table.hide()
            self.no_data_label.show()
            return
        
        self.no_data_label.hide()
        self.table.show()
        
        # Calculate pagination
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(self.filtered_data))
        max_page = (len(self.filtered_data) - 1) // self.rows_per_page
        
        # Update labels
        self.total_label.setText(f"Total: {len(self.full_data):,}")
        self.showing_label.setText(f"Showing: {len(self.filtered_data):,}")
        self.page_label.setText(f"Page {self.current_page + 1}/{max_page + 1}")
        
        # Update pagination buttons
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < max_page)
        
        # Get page data
        display_data = self.filtered_data.iloc[start_idx:end_idx]
        
        # Select relevant columns
        columns = ['risk_score_normalized', 'risk_band', 'transaction_count', 
                  'total_amount', 'avg_amount', 'transactions_per_day']
        available_columns = [col for col in columns if col in display_data.columns]
        display_data = display_data[available_columns]
        
        # Setup table
        self.table.clearContents()
        self.table.setRowCount(len(display_data))
        self.table.setColumnCount(len(display_data.columns) + 1)
        headers = ['Customer ID'] + display_data.columns.tolist()
        self.table.setHorizontalHeaderLabels(headers)
        
        # Color map
        color_map = {
            'Critical': QColor(255, 200, 200),
            'High': QColor(255, 230, 200),
            'Medium': QColor(255, 255, 200),
            'Low': QColor(220, 255, 220)
        }
        
        # Populate table
        for i, (customer_id, row) in enumerate(display_data.iterrows()):
            # Customer ID
            item = QTableWidgetItem(str(customer_id))
            self.table.setItem(i, 0, item)
            
            # Get color
            risk_band = row.get('risk_band', 'Low')
            row_color = color_map.get(risk_band, QColor(255, 255, 255))
            
            # Data columns
            for j, value in enumerate(row):
                text = f"{value:.2f}" if isinstance(value, float) else str(value)
                item = QTableWidgetItem(text)
                item.setBackground(row_color)
                self.table.setItem(i, j + 1, item)
        
        # Resize columns
        if self.current_page == 0:
            QTimer.singleShot(50, lambda: self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive))
    
    def showEvent(self, event):
        """Load data when view is shown"""
        super().showEvent(event)
        if self.full_data is None:
            QTimer.singleShot(100, self._load_data)