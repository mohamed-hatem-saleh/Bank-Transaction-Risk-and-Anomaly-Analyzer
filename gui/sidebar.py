"""
Sidebar navigation widget with menu items and execute button
"""

from PyQt5.QtWidgets import (QWidget, QVBoxLayout, QPushButton, QLabel, 
                             QFrame, QSpacerItem, QSizePolicy)
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QPalette, QColor


class MenuButton(QPushButton):
    """Custom styled menu button"""
    
    def __init__(self, text, parent=None):
        super().__init__(text, parent)
        self.setCheckable(True)
        self.setStyleSheet("""
            QPushButton {
                text-align: left;
                padding: 12px 20px;
                border: none;
                background-color: transparent;
                color: #333;
                font-size: 14px;
            }
            QPushButton:hover {
                background-color: #e8e8e8;
            }
            QPushButton:checked {
                background-color: #d0d0d0;
                font-weight: bold;
                border-left: 4px solid #0066cc;
            }
        """)


class Sidebar(QWidget):
    """
    Sidebar widget containing navigation menu and action buttons
    """
    
    # Signals
    menu_clicked = pyqtSignal(str)  # menu item name
    execute_clicked = pyqtSignal()
    reset_clicked = pyqtSignal()
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self._setup_ui()
        self._execution_completed = False
    
    def _setup_ui(self):
        """Setup the sidebar UI"""
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)
        
        # Set sidebar background
        self.setAutoFillBackground(True)
        palette = self.palette()
        palette.setColor(QPalette.Window, QColor(240, 240, 240))
        self.setPalette(palette)
        
        # Header
        header = QLabel("Navigation")
        header.setStyleSheet("""
            QLabel {
                padding: 20px;
                font-size: 18px;
                font-weight: bold;
                color: #0066cc;
                background-color: #f0f0f0;
                border-bottom: 2px solid #d0d0d0;
            }
        """)
        layout.addWidget(header)
        
        # Menu items
        menu_items = [
            "Dashboard",
            "Execute Analysis",
            "Data Overview",
            "Risk Scores",
            "Flagged Transactions",
            "Reports"
        ]
        
        self.menu_buttons = []
        for item in menu_items:
            btn = MenuButton(f"  {item}")
            btn.clicked.connect(lambda checked, name=item: self._on_menu_button_clicked(name))
            layout.addWidget(btn)
            self.menu_buttons.append(btn)
        
        # Set Dashboard as initially selected
        self.menu_buttons[0].setChecked(True)
        
        # Separator
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setFrameShadow(QFrame.Sunken)
        separator.setStyleSheet("background-color: #d0d0d0;")
        layout.addWidget(separator)
        
        # Spacer
        layout.addItem(QSpacerItem(20, 20, QSizePolicy.Minimum, QSizePolicy.Expanding))
        
        # Action buttons section
        actions_label = QLabel("Actions")
        actions_label.setStyleSheet("""
            QLabel {
                padding: 10px 20px;
                font-size: 14px;
                font-weight: bold;
                color: #666;
            }
        """)
        layout.addWidget(actions_label)
        
        # Execute button
        self.execute_button = QPushButton("▶ Start Analysis")
        self.execute_button.setStyleSheet("""
            QPushButton {
                padding: 15px 20px;
                margin: 10px 15px;
                background-color: #0066cc;
                color: white;
                border: none;
                border-radius: 5px;
                font-size: 14px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #0052a3;
            }
            QPushButton:pressed {
                background-color: #003d7a;
            }
            QPushButton:disabled {
                background-color: #cccccc;
                color: #666666;
            }
        """)
        self.execute_button.clicked.connect(self._on_execute_clicked)
        layout.addWidget(self.execute_button)
        
        # Reset button
        self.reset_button = QPushButton("↻ Reset")
        self.reset_button.setStyleSheet("""
            QPushButton {
                padding: 12px 20px;
                margin: 5px 15px 15px 15px;
                background-color: #f0f0f0;
                color: #333;
                border: 1px solid #d0d0d0;
                border-radius: 5px;
                font-size: 13px;
            }
            QPushButton:hover {
                background-color: #e0e0e0;
                border-color: #b0b0b0;
            }
            QPushButton:pressed {
                background-color: #d0d0d0;
            }
        """)
        self.reset_button.clicked.connect(self._on_reset_clicked)
        layout.addWidget(self.reset_button)
        
        # Status indicator
        self.status_label = QLabel("Status: Ready")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px 20px;
                font-size: 12px;
                color: #666;
                background-color: #f8f8f8;
                border-top: 1px solid #d0d0d0;
            }
        """)
        layout.addWidget(self.status_label)
    
    def _on_menu_button_clicked(self, menu_item: str):
        """Handle menu button clicks"""
        # Uncheck all other buttons
        for btn in self.menu_buttons:
            if btn.text().strip() != menu_item:
                btn.setChecked(False)
        
        # Emit signal
        self.menu_clicked.emit(menu_item)
    
    def _on_execute_clicked(self):
        """Handle execute button click"""
        self.execute_clicked.emit()
    
    def _on_reset_clicked(self):
        """Handle reset button click"""
        self.reset_clicked.emit()
    
    def set_execution_completed(self):
        """Update UI when execution is completed"""
        self._execution_completed = True
        self.execute_button.setText("✓ Analysis Complete")
        self.execute_button.setEnabled(False)
        self.status_label.setText("Status: Completed")
        self.status_label.setStyleSheet("""
            QLabel {
                padding: 10px 20px;
                font-size: 12px;
                color: #006600;
                background-color: #e6ffe6;
                border-top: 1px solid #00cc00;
                font-weight: bold;
            }
        """)
    
    def disable_execute_button(self):
        """Disable execute button during processing"""
        self.execute_button.setEnabled(False)
        self.execute_button.setText("⟳ Processing...")
        self.status_label.setText("Status: Running")
    
    def enable_execute_button(self):
        """Enable execute button"""
        if not self._execution_completed:
            self.execute_button.setEnabled(True)
            self.execute_button.setText("▶ Start Analysis")
            self.status_label.setText("Status: Ready")