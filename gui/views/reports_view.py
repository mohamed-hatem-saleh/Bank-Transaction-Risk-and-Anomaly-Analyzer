"""
Reports View - Access and view generated reports
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QHBoxLayout, QLabel, 
                             QPushButton, QFrame, QMessageBox)
from PyQt5.QtCore import Qt
import os
from app_state_manager import AppStateManager


class ReportCard(QFrame):
    """Card widget for each report file"""
    
    def __init__(self, title, description, filepath, parent=None):
        super().__init__(parent)
        self.filepath = filepath
        self.parent_widget = parent  # Store parent reference
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            ReportCard {
                background-color: white;
                border: 1px solid #d0d0d0;
                border-radius: 8px;
                padding: 15px;
            }
        """)
        
        layout = QVBoxLayout(self)
        
        # Title
        title_label = QLabel(title)
        title_label.setStyleSheet("font-size: 16px; font-weight: bold; color: #0066cc;")
        layout.addWidget(title_label)
        
        # Description
        desc_label = QLabel(description)
        desc_label.setStyleSheet("font-size: 13px; color: #666; padding: 5px 0;")
        desc_label.setWordWrap(True)
        layout.addWidget(desc_label)
        
        # File path
        path_label = QLabel(f"Location: {filepath}")
        path_label.setStyleSheet("font-size: 11px; color: #999; padding: 5px 0;")
        layout.addWidget(path_label)
        
        # Buttons
        btn_layout = QHBoxLayout()
        
        self.open_btn = QPushButton("Open File")
        self.open_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.open_btn.clicked.connect(self._open_file)
        btn_layout.addWidget(self.open_btn)
        
        self.folder_btn = QPushButton("Open Folder")
        self.folder_btn.setStyleSheet("""
            QPushButton {
                padding: 8px 15px;
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #d0d0d0;
                border-radius: 4px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        self.folder_btn.clicked.connect(self._open_folder)
        btn_layout.addWidget(self.folder_btn)
        
        btn_layout.addStretch()
        layout.addLayout(btn_layout)
        
        self._check_file_exists()
    
    def _check_file_exists(self):
        """Check if file exists and enable/disable buttons"""
        exists = os.path.exists(self.filepath)
        self.open_btn.setEnabled(exists)
        if not exists:
            self.open_btn.setText("Not Generated")
    
    def _get_parent_widget(self):
        """Get a valid parent widget for message boxes"""
        # Try to find a valid parent widget
        widget = self.parent_widget
        if widget is None:
            widget = self
        return widget
    
    def _open_file(self):
        """Open the report file"""
        if not os.path.exists(self.filepath):
            QMessageBox.warning(
                self._get_parent_widget(), 
                "File Not Found", 
                f"The file does not exist:\n{self.filepath}"
            )
            return
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(self.filepath)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', self.filepath])
            else:  # Linux
                subprocess.call(['xdg-open', self.filepath])
        except AttributeError as e:
            # Handle missing os.startfile on non-Windows
            QMessageBox.warning(
                self._get_parent_widget(), 
                "Error", 
                f"Could not open file. Please open manually:\n{self.filepath}"
            )
        except Exception as e:
            QMessageBox.warning(
                self._get_parent_widget(), 
                "Error", 
                f"Could not open file: {str(e)}\n\nFile path: {self.filepath}"
            )
    
    def _open_folder(self):
        """Open the folder containing the report"""
        folder = os.path.dirname(os.path.abspath(self.filepath))
        
        if not os.path.exists(folder):
            QMessageBox.warning(
                self._get_parent_widget(), 
                "Folder Not Found", 
                f"The folder does not exist:\n{folder}"
            )
            return
        
        try:
            import subprocess
            import platform
            
            if platform.system() == 'Windows':
                os.startfile(folder)
            elif platform.system() == 'Darwin':  # macOS
                subprocess.call(['open', folder])
            else:  # Linux
                subprocess.call(['xdg-open', folder])
        except AttributeError as e:
            # Handle missing os.startfile on non-Windows
            QMessageBox.information(
                self._get_parent_widget(), 
                "Folder Location", 
                f"Please navigate to:\n{folder}"
            )
        except Exception as e:
            QMessageBox.warning(
                self._get_parent_widget(), 
                "Error", 
                f"Could not open folder: {str(e)}\n\nFolder path: {folder}"
            )
    
    def refresh(self):
        """Refresh file existence status"""
        self._check_file_exists()


class ReportsView(QWidget):
    """View for accessing generated reports"""
    
    def __init__(self, state_manager: AppStateManager, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the reports view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Generated Reports")
        header.setStyleSheet("font-size: 24px; font-weight: bold; color: #0066cc; padding-bottom: 10px;")
        layout.addWidget(header)
        
        description = QLabel(
            "Access the generated analysis reports. Reports are automatically created "
            "when the analysis completes."
        )
        description.setStyleSheet("font-size: 14px; color: #666; padding-bottom: 20px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Report cards
        self.card_flagged = ReportCard(
            "Flagged Transactions Report",
            "Complete list of all suspicious transactions with suspicion scores and reasons.",
            "reports\\flagged_transactions.csv",
            self
        )
        layout.addWidget(self.card_flagged)
        
        self.card_risk = ReportCard(
            "Customer Risk Summary",
            "Comprehensive customer risk profiles with scores, bands, and statistics.",
            "reports\\customer_risk_summary.csv",
            self
        )
        layout.addWidget(self.card_risk)
        
        self.card_text = ReportCard(
            "Detailed Analysis Report",
            "Full text report with executive summary, findings, and recommendations.",
            "reports\\report.txt",
            self
        )
        layout.addWidget(self.card_text)
        
        # Spacer
        layout.addStretch()
        
        # Refresh button
        refresh_btn = QPushButton("🔄 Refresh Status")
        refresh_btn.setStyleSheet("""
            QPushButton {
                padding: 10px 20px;
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
            }
        """)
        refresh_btn.clicked.connect(self._refresh_all)
        layout.addWidget(refresh_btn)
    
    def _connect_signals(self):
        """Connect to state manager signals"""
        self.state_manager.data_updated.connect(self._on_data_updated)
    
    def _on_data_updated(self, key: str):
        """Handle data updates"""
        if key == 'reports_generated':
            self._refresh_all()
    
    def _refresh_all(self):
        """Refresh all report cards"""
        self.card_flagged.refresh()
        self.card_risk.refresh()
        self.card_text.refresh()
    
    def showEvent(self, event):
        """Refresh when view is shown"""
        super().showEvent(event)
        self._refresh_all()