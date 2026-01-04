"""
Analysis Controller
Orchestrates business logic execution with state management
"""

from PyQt5.QtCore import QObject, pyqtSignal, QThread
from app_state_manager import AppStateManager, ExecutionState
from Core_modules.data_manager import DataManager
from Core_modules.transaction_cleaner import TransactionCleaner
from Core_modules.feature_builder import FeatureBuilder
from Core_modules.risk_scorer import RiskScorer
from Core_modules.transaction_flagger import TransactionFlagger
from Core_modules.report_generator import ReportGenerator


class AnalysisWorker(QObject):
    """
    Worker thread for executing analysis pipeline.
    Ensures UI remains responsive during long-running operations.
    """
    
    # Signals for communication with main thread
    progress = pyqtSignal(str, int)  # message, percentage
    finished = pyqtSignal(bool)  # success
    error = pyqtSignal(str)  # error_message
    log_message = pyqtSignal(str)  # log message
    
    def __init__(self, state_manager: AppStateManager, filepath: str):
        super().__init__()
        self.state_manager = state_manager
        self.filepath = filepath
        self._is_running = True
    
    def run(self):
        """Execute the complete analysis pipeline"""
        try:
            # Step 1: Load Data
            self.progress.emit("Loading transaction data...", 10)
            self.log_message.emit("=== Step 1: Loading Data ===")
            data_manager = DataManager()
            
            if not data_manager.load_transactions(self.filepath):
                self.error.emit("Failed to load transaction data")
                self.finished.emit(False)
                return
            
            if not data_manager.validate_data():
                self.error.emit("Data validation failed")
                self.finished.emit(False)
                return
            
            raw_data = data_manager.get_transaction_data()
            self.state_manager.set_data('raw_data', raw_data)
            self.state_manager.set_step_status('load_data', True)
            self.log_message.emit(f"✓ Loaded {len(raw_data):,} transactions")
            
            if not self._is_running:
                return
            
            # Step 2: Clean Data
            self.progress.emit("Cleaning and preparing data...", 25)
            self.log_message.emit("\n=== Step 2: Cleaning Data ===")
            self.state_manager.current_state = ExecutionState.CLEANING_DATA
            
            cleaner = TransactionCleaner(raw_data)
            cleaned_data = cleaner.clean_data()
            
            self.state_manager.set_data('cleaned_data', cleaned_data)
            self.state_manager.set_step_status('clean_data', True)
            self.log_message.emit(f"✓ Cleaned data: {len(cleaned_data):,} transactions")
            
            if not self._is_running:
                return
            
            # Step 3: Build Features
            self.progress.emit("Building customer features...", 40)
            self.log_message.emit("\n=== Step 3: Building Features ===")
            self.state_manager.current_state = ExecutionState.BUILDING_FEATURES
            
            feature_builder = FeatureBuilder(cleaned_data)
            features = feature_builder.build_features()
            
            self.state_manager.set_data('features', features)
            self.state_manager.set_step_status('build_features', True)
            self.log_message.emit(f"✓ Built features for {len(features):,} customers")
            
            if not self._is_running:
                return
            
            # Step 4: Score Customers
            self.progress.emit("Computing risk scores...", 60)
            self.log_message.emit("\n=== Step 4: Scoring Customers ===")
            self.state_manager.current_state = ExecutionState.SCORING_CUSTOMERS
            
            risk_scorer = RiskScorer(features)
            risk_scores = risk_scorer.compute_risk_scores()
            
            self.state_manager.set_data('risk_scores', risk_scores)
            self.state_manager.set_step_status('score_customers', True)
            self.log_message.emit(f"✓ Scored {len(risk_scores):,} customers")
            
            if not self._is_running:
                return
            
            # Step 5: Flag Transactions
            self.progress.emit("Flagging suspicious transactions...", 75)
            self.log_message.emit("\n=== Step 5: Flagging Suspicious Transactions ===")
            self.state_manager.current_state = ExecutionState.FLAGGING_TRANSACTIONS
            
            transaction_flagger = TransactionFlagger(cleaned_data, risk_scores)
            flagged_transactions = transaction_flagger.flag_suspicious_transactions()
            
            self.state_manager.set_data('flagged_transactions', flagged_transactions)
            self.state_manager.set_step_status('flag_transactions', True)
            self.log_message.emit(f"✓ Flagged {len(flagged_transactions):,} suspicious transactions")
            
            if not self._is_running:
                return
            
            # Step 6: Generate Reports
            self.progress.emit("Generating reports...", 90)
            self.log_message.emit("\n=== Step 6: Generating Reports ===")
            self.state_manager.current_state = ExecutionState.GENERATING_REPORTS
            
            report_generator = ReportGenerator(risk_scores, flagged_transactions, cleaned_data)
            report_generator.generate_all_reports()
            
            self.state_manager.set_data('reports_generated', True)
            self.state_manager.set_step_status('generate_reports', True)
            self.log_message.emit("✓ All reports generated successfully")
            
            # Complete
            self.progress.emit("Analysis complete!", 100)
            self.log_message.emit("\n=== Execution Complete ===")
            self.state_manager.current_state = ExecutionState.COMPLETED
            self.state_manager.execution_completed = True
            
            self.finished.emit(True)
            
        except Exception as e:
            error_msg = f"Analysis failed: {str(e)}"
            self.log_message.emit(f"\n✗ ERROR: {error_msg}")
            self.error.emit(error_msg)
            self.finished.emit(False)
    
    def stop(self):
        """Stop the worker thread"""
        self._is_running = False


class AnalysisController(QObject):
    """
    Controller for analysis pipeline execution.
    Manages worker threads and coordinates with state manager.
    """
    
    # Signals
    execution_started = pyqtSignal()
    execution_finished = pyqtSignal(bool)  # success
    progress_updated = pyqtSignal(str, int)  # message, percentage
    log_updated = pyqtSignal(str)  # log message
    
    def __init__(self, state_manager: AppStateManager):
        super().__init__()
        self.state_manager = state_manager
        self.worker = None
        self.thread = None
    
    def execute_analysis(self, filepath: str):
        """
        Execute the complete analysis pipeline in a separate thread
        
        Args:
            filepath (str): Path to transaction CSV file
        """
        if self.state_manager.execution_completed:
            self.log_updated.emit("Analysis already completed. Please reset to run again.")
            return
        
        if self.thread and self.thread.isRunning():
            self.log_updated.emit("Analysis already in progress")
            return
        
        # Create worker and thread
        self.thread = QThread()
        self.worker = AnalysisWorker(self.state_manager, filepath)
        self.worker.moveToThread(self.thread)
        
        # Connect signals
        self.thread.started.connect(self.worker.run)
        self.worker.finished.connect(self._on_finished)
        self.worker.progress.connect(self._on_progress)
        self.worker.error.connect(self._on_error)
        self.worker.log_message.connect(self._on_log_message)
        self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.worker.deleteLater)
        self.thread.finished.connect(self.thread.deleteLater)
        
        # Start execution
        self.state_manager.current_state = ExecutionState.LOADING_DATA
        self.execution_started.emit()
        self.thread.start()
    
    def _on_progress(self, message: str, percentage: int):
        """Handle progress updates from worker"""
        self.state_manager.emit_progress(message, percentage)
        self.progress_updated.emit(message, percentage)
    
    def _on_log_message(self, message: str):
        """Handle log messages from worker"""
        self.state_manager.add_log(message)
        self.log_updated.emit(message)
    
    def _on_error(self, error_message: str):
        """Handle errors from worker"""
        self.state_manager.emit_error(error_message)
    
    def _on_finished(self, success: bool):
        """Handle completion of worker"""
        self.execution_finished.emit(success)
        self.thread = None
        self.worker = None
    
    def stop_execution(self):
        """Stop the current execution"""
        if self.worker:
            self.worker.stop()
        if self.thread and self.thread.isRunning():
            self.thread.quit()
            self.thread.wait()