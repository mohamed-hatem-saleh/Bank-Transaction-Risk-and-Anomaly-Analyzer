"""
Main Window for Bank Transaction Risk Analyzer
"""

from PyQt5.QtWidgets import (QMainWindow, QWidget, QHBoxLayout,
                             QStackedWidget, QMessageBox, 
                             QFileDialog, QStatusBar)

from app_state_manager import AppStateManager, ExecutionState
from analysis_controller import AnalysisController
from gui.sidebar import Sidebar
from gui.views.dashboard_view import DashboardView
from gui.views.execution_view import ExecutionView
from gui.views.data_view import DataView
from gui.views.risk_view import RiskView
from gui.views.transactions_view import TransactionsView
from gui.views.reports_view import ReportsView


class MainWindow(QMainWindow):
    """Main application window with sidebar navigation and content area"""
    
    def __init__(self):
        super().__init__()
        
        # Initialize state manager and controller
        self.state_manager = AppStateManager()
        self.controller = AnalysisController(self.state_manager)
        
        # Current file path
        self.current_filepath = None
        
        # Setup UI
        self._setup_ui()
        self._connect_signals()
        
    def _setup_ui(self):
        """Initialize the user interface"""
        self.setWindowTitle("Bank Transaction Risk & Anomaly Analyzer v4")
        self.setMinimumSize(1200, 800)
        
        # Create central widget with stacked layout for views
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(0, 0, 0, 0)
        main_layout.setSpacing(0)
        
        # Create stacked widget for different views
        self.content_stack = QStackedWidget()
        
        # Create views
        self.dashboard_view = DashboardView(self.state_manager)
        self.execution_view = ExecutionView(self.state_manager, self.controller)
        self.data_view = DataView(self.state_manager)
        self.risk_view = RiskView(self.state_manager)
        self.transactions_view = TransactionsView(self.state_manager)
        self.reports_view = ReportsView(self.state_manager)
        
        # Add views to stack
        self.content_stack.addWidget(self.dashboard_view)  # 0
        self.content_stack.addWidget(self.execution_view)   # 1
        self.content_stack.addWidget(self.data_view)        # 2
        self.content_stack.addWidget(self.risk_view)        # 3
        self.content_stack.addWidget(self.transactions_view)  # 4
        self.content_stack.addWidget(self.reports_view)     # 5
        
        # Create sidebar
        self.sidebar = Sidebar()
        self.sidebar.setFixedWidth(250)
        
        # Add to layout
        main_layout.addWidget(self.sidebar)
        main_layout.addWidget(self.content_stack)
        
        # Status bar
        self.status_bar = QStatusBar()
        self.setStatusBar(self.status_bar)
        self.status_bar.showMessage("Ready")
        
        # Set initial view
        self.content_stack.setCurrentIndex(0)
        
    def _connect_signals(self):
        """Connect signals and slots"""
        # Sidebar navigation
        self.sidebar.menu_clicked.connect(self._on_menu_clicked)
        self.sidebar.execute_clicked.connect(self._on_execute_clicked)
        self.sidebar.reset_clicked.connect(self._on_reset_clicked)
        
        # State manager signals
        self.state_manager.state_changed.connect(self._on_state_changed)
        self.state_manager.progress_updated.connect(self._on_progress_updated)
        self.state_manager.error_occurred.connect(self._on_error_occurred)
        
        # Controller signals
        self.controller.execution_started.connect(self._on_execution_started)
        self.controller.execution_finished.connect(self._on_execution_finished)
    
    def _on_menu_clicked(self, menu_item: str):
        """Handle sidebar menu navigation"""
        menu_map = {
            'Dashboard': 0,
            'Execute Analysis': 1,
            'Data Overview': 2,
            'Risk Scores': 3,
            'Flagged Transactions': 4,
            'Reports': 5
        }
        
        index = menu_map.get(menu_item, 0)
        self.content_stack.setCurrentIndex(index)
        self.status_bar.showMessage(f"Viewing: {menu_item}")
    
    def _on_execute_clicked(self):
        """Handle execute button click"""
        # Check if already executed
        if self.state_manager.execution_completed:
            QMessageBox.information(
                self,
                "Already Executed",
                "Analysis has already been completed.\n\n"
                "Use the 'Reset' button to start a new analysis."
            )
            return
        
        # Check if execution is in progress
        if self.state_manager.current_state not in [ExecutionState.IDLE, ExecutionState.ERROR]:
            QMessageBox.warning(
                self,
                "Execution In Progress",
                "Analysis is currently running. Please wait for completion."
            )
            return
        
        # Prompt for file selection
        filepath, _ = QFileDialog.getOpenFileName(
            self,
            "Select Transaction Data File",
            "",
            "CSV Files (*.csv);;All Files (*)"
        )
        
        if filepath:
            self.current_filepath = filepath
            # Switch to execution view
            self.content_stack.setCurrentIndex(1)
            # Start execution
            self.controller.execute_analysis(filepath)
        else:
            self.status_bar.showMessage("File selection cancelled")
    
    def _on_reset_clicked(self):
        """Handle reset button click"""
        reply = QMessageBox.question(
            self,
            "Reset Application",
            "This will clear all data and reset the application to initial state.\n\n"
            "Are you sure you want to continue?",
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            self.state_manager.reset_state()
            self.current_filepath = None
            self.content_stack.setCurrentIndex(0)
            self.status_bar.showMessage("Application reset successfully")
            QMessageBox.information(
                self,
                "Reset Complete",
                "Application has been reset. You can now start a new analysis."
            )
    
    def _on_state_changed(self, state: ExecutionState):
        """Handle state changes"""
        state_messages = {
            ExecutionState.IDLE: "Ready",
            ExecutionState.LOADING_DATA: "Loading data...",
            ExecutionState.CLEANING_DATA: "Cleaning data...",
            ExecutionState.BUILDING_FEATURES: "Building features...",
            ExecutionState.SCORING_CUSTOMERS: "Scoring customers...",
            ExecutionState.FLAGGING_TRANSACTIONS: "Flagging transactions...",
            ExecutionState.GENERATING_REPORTS: "Generating reports...",
            ExecutionState.COMPLETED: "Analysis completed successfully",
            ExecutionState.ERROR: "Error occurred"
        }
        
        message = state_messages.get(state, "Processing...")
        self.status_bar.showMessage(message)
        
        # Update sidebar button state
        if state == ExecutionState.COMPLETED:
            self.sidebar.set_execution_completed()
        elif state in [ExecutionState.IDLE, ExecutionState.ERROR]:
            self.sidebar.enable_execute_button()
        else:
            self.sidebar.disable_execute_button()
    
    def _on_progress_updated(self, message: str, percentage: int):
        """Handle progress updates"""
        self.status_bar.showMessage(f"{message} ({percentage}%)")
    
    def _on_error_occurred(self, error_message: str):
        """Handle errors"""
        QMessageBox.critical(
            self,
            "Error",
            f"An error occurred during execution:\n\n{error_message}"
        )
        self.status_bar.showMessage("Error occurred")
    
    def _on_execution_started(self):
        """Handle execution start"""
        self.status_bar.showMessage("Analysis started...")
        self.sidebar.disable_execute_button()
    
    def _on_execution_finished(self, success: bool):
        """Handle execution completion"""
        if success:
            self.status_bar.showMessage("Analysis completed successfully!")
            QMessageBox.information(
                self,
                "Success",
                "Analysis completed successfully!\n\n"
                "You can now view the results in different sections using the sidebar menu."
            )
        else:
            self.status_bar.showMessage("Analysis failed")
    
    def closeEvent(self, event):
        """Handle window close event"""
        if self.state_manager.current_state not in [ExecutionState.IDLE, ExecutionState.COMPLETED, ExecutionState.ERROR]:
            reply = QMessageBox.question(
                self,
                "Analysis In Progress",
                "Analysis is currently running. Are you sure you want to exit?",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                event.ignore()
                return
            else:
                self.controller.stop_execution()
        
        event.accept()