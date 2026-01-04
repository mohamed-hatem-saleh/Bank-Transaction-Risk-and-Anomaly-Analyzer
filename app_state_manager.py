"""
Application State Manager
Maintains execution state and persisted data across views
"""

from enum import Enum
from PyQt5.QtCore import QObject, pyqtSignal


class ExecutionState(Enum):
    """Application execution states"""
    IDLE = "idle"
    LOADING_DATA = "loading_data"
    CLEANING_DATA = "cleaning_data"
    BUILDING_FEATURES = "building_features"
    SCORING_CUSTOMERS = "scoring_customers"
    FLAGGING_TRANSACTIONS = "flagging_transactions"
    GENERATING_REPORTS = "generating_reports"
    COMPLETED = "completed"
    ERROR = "error"


class AppStateManager(QObject):
    """
    Centralized state management for the application.
    Maintains execution status and persisted data outputs.
    """
    
    # Signals for state changes
    state_changed = pyqtSignal(ExecutionState)
    progress_updated = pyqtSignal(str, int)  # message, percentage
    data_updated = pyqtSignal(str)  # data_key
    error_occurred = pyqtSignal(str)  # error_message
    
    def __init__(self):
        super().__init__()
        
        # Execution state
        self._current_state = ExecutionState.IDLE
        self._execution_completed = False
        
        # Persisted data outputs
        self._data_store = {
            'raw_data': None,
            'cleaned_data': None,
            'features': None,
            'risk_scores': None,
            'flagged_transactions': None,
            'reports_generated': False
        }
        
        # Execution logs
        self._execution_log = []
        
        # Step completion status
        self._step_status = {
            'load_data': False,
            'clean_data': False,
            'build_features': False,
            'score_customers': False,
            'flag_transactions': False,
            'generate_reports': False
        }
    
    @property
    def current_state(self):
        """Get current execution state"""
        return self._current_state
    
    @current_state.setter
    def current_state(self, state: ExecutionState):
        """Set current execution state and emit signal"""
        if self._current_state != state:
            self._current_state = state
            self.state_changed.emit(state)
    
    @property
    def execution_completed(self):
        """Check if full execution cycle is completed"""
        return self._execution_completed
    
    @execution_completed.setter
    def execution_completed(self, value: bool):
        """Set execution completion status"""
        self._execution_completed = value
    
    def get_data(self, key: str):
        """
        Retrieve persisted data by key
        
        Args:
            key (str): Data identifier
            
        Returns:
            Data object or None
        """
        return self._data_store.get(key)
    
    def set_data(self, key: str, value):
        """
        Store data with key and emit update signal
        
        Args:
            key (str): Data identifier
            value: Data to store
        """
        self._data_store[key] = value
        self.data_updated.emit(key)
    
    def clear_data(self, key: str = None):
        """
        Clear stored data
        
        Args:
            key (str, optional): Specific key to clear, or all if None
        """
        if key:
            self._data_store[key] = None
        else:
            for k in self._data_store.keys():
                self._data_store[k] = None if k != 'reports_generated' else False
    
    def add_log(self, message: str):
        """
        Add message to execution log
        
        Args:
            message (str): Log message
        """
        self._execution_log.append(message)
    
    def get_log(self):
        """Get full execution log"""
        return self._execution_log.copy()
    
    def clear_log(self):
        """Clear execution log"""
        self._execution_log.clear()
    
    def set_step_status(self, step: str, completed: bool):
        """
        Update step completion status
        
        Args:
            step (str): Step identifier
            completed (bool): Completion status
        """
        if step in self._step_status:
            self._step_status[step] = completed
    
    def get_step_status(self, step: str):
        """Get completion status of a step"""
        return self._step_status.get(step, False)
    
    def is_ready_for_execution(self):
        """Check if prerequisites for full execution are met"""
        return not self._execution_completed
    
    def reset_state(self):
        """Reset application to initial state"""
        self.current_state = ExecutionState.IDLE
        self._execution_completed = False
        self.clear_data()
        self.clear_log()
        for step in self._step_status:
            self._step_status[step] = False
        self.add_log("Application state reset")
    
    def emit_progress(self, message: str, percentage: int):
        """
        Emit progress update signal
        
        Args:
            message (str): Progress message
            percentage (int): Progress percentage (0-100)
        """
        self.progress_updated.emit(message, percentage)
    
    def emit_error(self, error_message: str):
        """
        Emit error signal and log error
        
        Args:
            error_message (str): Error description
        """
        self.current_state = ExecutionState.ERROR
        self.add_log(f"ERROR: {error_message}")
        self.error_occurred.emit(error_message)
    
    def get_summary_stats(self):
        """
        Get summary statistics of current data state
        
        Returns:
            dict: Summary statistics
        """
        stats = {
            'has_raw_data': self.get_data('raw_data') is not None,
            'has_cleaned_data': self.get_data('cleaned_data') is not None,
            'has_features': self.get_data('features') is not None,
            'has_risk_scores': self.get_data('risk_scores') is not None,
            'has_flagged_transactions': self.get_data('flagged_transactions') is not None,
            'reports_generated': self.get_data('reports_generated'),
            'execution_completed': self._execution_completed
        }
        
        # Add counts if data exists
        if stats['has_raw_data']:
            stats['total_transactions'] = len(self.get_data('raw_data'))
        
        if stats['has_risk_scores']:
            stats['total_customers'] = len(self.get_data('risk_scores'))
        
        if stats['has_flagged_transactions']:
            stats['flagged_count'] = len(self.get_data('flagged_transactions'))
        
        return stats