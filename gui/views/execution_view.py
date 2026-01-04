"""
Execution View - Real-time execution monitoring with logs
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QLabel, QTextEdit, 
                             QProgressBar, QFrame)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QFont, QTextCursor
from app_state_manager import AppStateManager
from analysis_controller import AnalysisController


class ExecutionView(QWidget):
    """View for monitoring analysis execution in real-time"""
    
    def __init__(self, state_manager: AppStateManager, controller: AnalysisController, parent=None):
        super().__init__(parent)
        self.state_manager = state_manager
        self.controller = controller
        self._setup_ui()
        self._connect_signals()
    
    def _setup_ui(self):
        """Setup the execution view UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(30, 30, 30, 30)
        
        # Header
        header = QLabel("Analysis Execution")
        header.setStyleSheet("""
            QLabel {
                font-size: 24px;
                font-weight: bold;
                color: #0066cc;
                padding-bottom: 10px;
            }
        """)
        layout.addWidget(header)
        
        # Description
        description = QLabel(
            "Monitor the real-time progress of the analysis pipeline. "
            "All steps are executed sequentially in a single cycle."
        )
        description.setStyleSheet("font-size: 14px; color: #666; padding-bottom: 20px;")
        description.setWordWrap(True)
        layout.addWidget(description)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        layout.addWidget(separator)
        
        # Progress section
        progress_label = QLabel("Progress")
        progress_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 15px 0 5px 0;")
        layout.addWidget(progress_label)
        
        # Progress bar
        self.progress_bar = QProgressBar()
        self.progress_bar.setStyleSheet("""
            QProgressBar {
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                text-align: center;
                height: 25px;
                background-color: #f0f0f0;
            }
            QProgressBar::chunk {
                background-color: #0066cc;
                border-radius: 4px;
            }
        """)
        self.progress_bar.setValue(0)
        layout.addWidget(self.progress_bar)
        
        # Status label
        self.status_label = QLabel("Ready to start analysis")
        self.status_label.setStyleSheet("font-size: 13px; color: #666; padding: 5px 0;")
        layout.addWidget(self.status_label)
        
        # Execution log section
        log_label = QLabel("Execution Log")
        log_label.setStyleSheet("font-size: 16px; font-weight: bold; padding: 15px 0 5px 0;")
        layout.addWidget(log_label)
        
        # Log text area
        self.log_text = QTextEdit()
        self.log_text.setReadOnly(True)
        self.log_text.setStyleSheet("""
            QTextEdit {
                background-color: #2b2b2b;
                color: #e0e0e0;
                font-family: 'Consolas', 'Courier New', monospace;
                font-size: 12px;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                padding: 10px;
            }
        """)
        self.log_text.setPlaceholderText("Execution logs will appear here...")
        layout.addWidget(self.log_text)
        
        # Initial message
        self._append_log("=== Bank Transaction Risk Analyzer v4 ===")
        self._append_log("Ready to execute analysis pipeline")
        self._append_log("\nClick 'Start Analysis' in the sidebar to begin...")
    
    def _connect_signals(self):
        """Connect to controller and state manager signals"""
        self.controller.progress_updated.connect(self._on_progress_updated)
        self.controller.log_updated.connect(self._on_log_updated)
        self.controller.execution_started.connect(self._on_execution_started)
        self.controller.execution_finished.connect(self._on_execution_finished)
        self.state_manager.state_changed.connect(self._on_state_changed)
    
    def _append_log(self, message: str):
        """Append message to log with auto-scroll"""
        self.log_text.append(message)
        # Auto-scroll to bottom
        cursor = self.log_text.textCursor()
        cursor.movePosition(QTextCursor.End)
        self.log_text.setTextCursor(cursor)
    
    def _on_progress_updated(self, message: str, percentage: int):
        """Handle progress updates"""
        self.progress_bar.setValue(percentage)
        self.status_label.setText(message)
    
    def _on_log_updated(self, message: str):
        """Handle log updates"""
        self._append_log(message)
    
    def _on_execution_started(self):
        """Handle execution start"""
        self.log_text.clear()
        self._append_log("=== Starting Analysis Pipeline ===")
        self._append_log(f"Timestamp: {self._get_timestamp()}\n")
        self.progress_bar.setValue(0)
        self.status_label.setText("Initializing...")
    
    def _on_execution_finished(self, success: bool):
        """Handle execution completion"""
        if success:
            self._append_log("\n" + "=" * 60)
            self._append_log("✓ ANALYSIS COMPLETED SUCCESSFULLY")
            self._append_log("=" * 60)
            self._append_log("\nYou can now view results in:")
            self._append_log("  • Data Overview - View cleaned transaction data")
            self._append_log("  • Risk Scores - Examine customer risk profiles")
            self._append_log("  • Flagged Transactions - Review suspicious activity")
            self._append_log("  • Reports - Access generated reports")
            self.progress_bar.setValue(100)
            self.status_label.setText("Analysis completed successfully!")
        else:
            self._append_log("\n" + "=" * 60)
            self._append_log("✗ ANALYSIS FAILED")
            self._append_log("=" * 60)
            self.status_label.setText("Analysis failed - check logs for details")
    
    def _on_state_changed(self, state):
        """Handle state changes"""
        state_messages = {
            "loading_data": "Loading transaction data...",
            "cleaning_data": "Cleaning and validating data...",
            "building_features": "Engineering customer features...",
            "scoring_customers": "Computing risk scores...",
            "flagging_transactions": "Detecting anomalies...",
            "generating_reports": "Generating reports..."
        }
        message = state_messages.get(state.value)
        if message:
            self.status_label.setText(message)
    
    def _get_timestamp(self):
        """Get current timestamp"""
        from datetime import datetime
        return datetime.now().strftime("%Y-%m-%d %H:%M:%S")