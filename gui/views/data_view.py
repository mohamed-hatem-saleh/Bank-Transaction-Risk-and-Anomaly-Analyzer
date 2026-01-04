"""
Data View - Display cleaned transaction data (optimized)
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTableWidget, 
                             QTableWidgetItem, QHeaderView, QFrame, QHBoxLayout,
                             QPushButton, QSpinBox)
from PyQt5.QtCore import Qt, QTimer
from app_state_manager import AppStateManager


class DataView(QWidget):
    """View for displaying cleaned transaction data with pagination"""
    
    def __init__(self, state_manager: AppStateManager, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.current_page = 0
        self.rows_per_page = 100  # Reduced for better performance
        self.data_cache = None
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the data view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Transaction Data Overview")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #0066cc; padding-bottom: 10px;")
        layout.addWidget(header)
        
        # Stats row
        stats_layout = QHBoxLayout()
        self.total_label = QLabel("Total Transactions: —")
        self.total_label.setStyleSheet("font-size: 14px; color: #333; padding: 10px;")
        stats_layout.addWidget(self.total_label)
        
        self.customers_label = QLabel("Unique Customers: —")
        self.customers_label.setStyleSheet("font-size: 14px; color: #333; padding: 10px;")
        stats_layout.addWidget(self.customers_label)
        
        self.volume_label = QLabel("Total Volume: —")
        self.volume_label.setStyleSheet("font-size: 14px; color: #333; padding: 10px;")
        stats_layout.addWidget(self.volume_label)
        
        stats_layout.addStretch()
        layout.addLayout(stats_layout)
        
        # Pagination controls
        pagination_layout = QHBoxLayout()
        
        self.prev_button = QPushButton("◀ Previous")
        self.prev_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton:disabled { background-color: #f8f8f8; color: #999; }
        """)
        self.prev_button.clicked.connect(self._previous_page)
        pagination_layout.addWidget(self.prev_button)
        
        self.page_label = QLabel("Page 1")
        self.page_label.setStyleSheet("font-size: 14px; padding: 0 15px;")
        pagination_layout.addWidget(self.page_label)
        
        self.next_button = QPushButton("Next ▶")
        self.next_button.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #f0f0f0;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
            }
            QPushButton:hover { background-color: #e0e0e0; }
            QPushButton:disabled { background-color: #f8f8f8; color: #999; }
        """)
        self.next_button.clicked.connect(self._next_page)
        pagination_layout.addWidget(self.next_button)
        
        pagination_layout.addStretch()
        
        # Rows per page selector
        pagination_layout.addWidget(QLabel("Rows per page:"))
        self.rows_spinbox = QSpinBox()
        self.rows_spinbox.setRange(50, 500)
        self.rows_spinbox.setSingleStep(50)
        self.rows_spinbox.setValue(100)
        self.rows_spinbox.valueChanged.connect(self._on_rows_per_page_changed)
        pagination_layout.addWidget(self.rows_spinbox)
        
        layout.addLayout(pagination_layout)
        
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
        self.table.setEditTriggers(QTableWidget.NoEditTriggers)  # Make read-only
        layout.addWidget(self.table)
        
        # No data label
        self.no_data_label = QLabel("No data available. Please run the analysis first.")
        self.no_data_label.setStyleSheet("font-size: 14px; color: #999; padding: 20px;")
        self.no_data_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.no_data_label)
        
        self.table.hide()
    
    def _connect_signals(self):
        """Connect to state manager signals"""
        self.state_manager.data_updated.connect(self._on_data_updated)
    
    def _on_data_updated(self, key: str):
        """Handle data updates"""
        if key == 'cleaned_data':
            self.data_cache = None  # Clear cache
            self.current_page = 0
    
    def _on_rows_per_page_changed(self, value):
        """Handle rows per page change"""
        self.rows_per_page = value
        self.current_page = 0
        self._load_data()
    
    def _previous_page(self):
        """Go to previous page"""
        if self.current_page > 0:
            self.current_page -= 1
            self._load_data()
    
    def _next_page(self):
        """Go to next page"""
        if self.data_cache is not None:
            max_page = (len(self.data_cache) - 1) // self.rows_per_page
            if self.current_page < max_page:
                self.current_page += 1
                self._load_data()
    
    def _load_data(self):
        """Load and display cleaned data with pagination"""
        # Get data from cache or state manager
        if self.data_cache is None:
            self.data_cache = self.state_manager.get_data('cleaned_data')
        
        data = self.data_cache
        
        if data is None or data.empty:
            self.table.hide()
            self.no_data_label.show()
            self.prev_button.setEnabled(False)
            self.next_button.setEnabled(False)
            return
        
        self.no_data_label.hide()
        self.table.show()
        
        # Update stats (only once)
        self.total_label.setText(f"Total Transactions: {len(data):,}")
        self.customers_label.setText(f"Unique Customers: {data['nameOrig'].nunique():,}")
        self.volume_label.setText(f"Total Volume: ${data['amount'].sum():,.2f}")
        
        # Calculate pagination
        start_idx = self.current_page * self.rows_per_page
        end_idx = min(start_idx + self.rows_per_page, len(data))
        max_page = (len(data) - 1) // self.rows_per_page
        
        # Update pagination controls
        self.page_label.setText(f"Page {self.current_page + 1} of {max_page + 1} (Rows {start_idx + 1}-{end_idx} of {len(data):,})")
        self.prev_button.setEnabled(self.current_page > 0)
        self.next_button.setEnabled(self.current_page < max_page)
        
        # Get page data
        display_data = data.iloc[start_idx:end_idx]
        
        # Setup table efficiently
        self.table.clearContents()
        self.table.setRowCount(len(display_data))
        self.table.setColumnCount(len(display_data.columns))
        self.table.setHorizontalHeaderLabels(display_data.columns.tolist())
        
        # Populate table (optimized)
        for i, row in enumerate(display_data.itertuples(index=False)):
            for j, value in enumerate(row):
                # Format value efficiently
                if isinstance(value, float):
                    text = f"{value:.2f}" if value < 1000000 else f"{value:.2e}"
                else:
                    text = str(value)
                
                item = QTableWidgetItem(text)
                self.table.setItem(i, j, item)
        
        # Resize columns to contents (only first time)
        if self.current_page == 0:
            QTimer.singleShot(100, lambda: self.table.horizontalHeader().setSectionResizeMode(QHeaderView.Interactive))
    
    def showEvent(self, event):
        """Load data when view is shown"""
        super().showEvent(event)
        if self.data_cache is None or self.table.rowCount() == 0:
            # Use QTimer to defer loading slightly
            QTimer.singleShot(100, self._load_data)