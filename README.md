# Bank Transaction Risk & Anomaly Analyzer - Version 1.1

## Project Overview

A comprehensive desktop application for analyzing banking transaction data to detect risky customers and anomalous transactions using advanced data analysis, statistical techniques, and a professional PyQt5 GUI interface.

## ✨ Version 1.1 Features

### Core Analysis Engine
- **Data Management**: Robust data loading and validation
- **Data Cleaning**: Comprehensive data preprocessing and quality assurance
- **Feature Engineering**: Advanced customer-level feature creation
- **Risk Scoring**: Statistical risk assessment using z-scores and composite metrics
- **Anomaly Detection**: Multi-criteria suspicious transaction flagging
- **Report Generation**: Automated CSV and text report creation

### GUI Enhancements
- **Modern Desktop Interface**: Professional PyQt5-based windowed application
- **Persistent Sidebar Navigation**: Fixed sidebar with menu items and action buttons
- **Single-Cycle Execution**: One-directional pipeline from data loading to report generation
- **Real-Time Progress Monitoring**: Live execution logs and progress indicators
- **Persistent State Management**: Results preserved across view navigation
- **Thread-Safe Operations**: Non-blocking UI during long-running analysis

## 🛠 Technology Stack

### Required Libraries
- **Pandas**: Data manipulation, aggregation, and feature engineering
- **NumPy**: Numerical operations and array processing
- **SciPy**: Statistical analysis and z-score calculations
- **PyQt5**: Modern GUI framework for desktop application

### Dataset
The application is designed to work with the **PaySim Mobile Money Transaction** dataset from Kaggle:
- Dataset: [PaySim - Mobile Money Transactions](https://www.kaggle.com/datasets/ealaxi/paysim1)
- Format: CSV
- Expected columns: `step`, `type`, `amount`, `nameOrig`, `nameDest`, `oldbalanceOrg`, `newbalanceOrig`, `oldbalanceDest`, `newbalanceDest`, `isFraud`, `isFlaggedFraud`

## 📥 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Install Dependencies

```bash
pip install pandas numpy scipy PyQt5 os
```

Or install from requirements file:
```bash
pip install -r requirements.txt
```

### Download the Dataset
1. Download the PaySim dataset from Kaggle
2. Place the CSV file in your desired directory
3. Default filename: `PS_20174392719_1491204439457_log.csv`

## 📁 Project Structure

```
bank_analyzer_v1.1/
│
├── main.py                      # Application entry point
├── app_state_manager.py         # Centralized state management
├── analysis_controller.py       # Business logic controller with threading
│
├── gui/
│   ├── main_window.py           # Main application window
│   ├── sidebar.py               # Navigation sidebar widget
│   └── views/
│       ├── dashboard_view.py    # Dashboard overview
│       ├── execution_view.py    # Real-time execution monitor
│       ├── data_view.py         # Transaction data viewer
│       ├── risk_view.py         # Customer risk scores
│       ├── transactions_view.py # Flagged transactions
│       └── reports_view.py      # Report access interface
│
├── Core analysis modules:
│   ├── data_manager.py          # Data loading and validation
│   ├── transaction_cleaner.py   # Data cleaning and preprocessing
│   ├── feature_builder.py       # Feature engineering
│   ├── risk_scorer.py          # Risk scoring algorithms
│   ├── transaction_flagger.py   # Anomaly detection
│   └── report_generator.py     # Report generation
│
├── requirements.txt            # Python dependencies
├── README.md                  # This documentation
│
└── reports/                   # Generated reports directory
    ├── flagged_transactions.csv
    ├── customer_risk_summary.csv
    └── report.txt
```

## 🚀 Running the Application

```bash
python main.py
```

## 🎨 User Interface Overview

### 1. Dashboard View
- Application overview and welcome screen
- Real-time statistics cards
- Feature highlights
- Status indicators

### 2. Sidebar Navigation
**Menu Items:**
- Dashboard
- Execute Analysis
- Data Overview
- Risk Scores
- Flagged Transactions
- Reports

**Action Buttons:**
- **Start Analysis**: Initiates the complete analysis pipeline
- **Reset**: Clears all data and resets application state

### 3. Execution View
- Real-time progress bar
- Live execution logs with console-style output
- Step-by-step progress tracking
- Completion notifications

### 4. Data Overview
- Cleaned transaction data display
- Summary statistics
- Tabular data viewer (first 1000 rows)

### 5. Risk Scores View
- Customer risk profiles
- Risk band filtering (Critical/High/Medium/Low)
- Color-coded risk visualization
- Sortable risk score table

### 6. Flagged Transactions View
- Suspicious transaction listing
- Suspicion scores and reasons
- Color-coded by risk level
- Statistical summary

### 7. Reports View
- Access to generated CSV and text reports
- One-click file opening
- Folder navigation
- File status indicators

## 🔄 Workflow

### Single-Cycle Execution Model

The application follows a **one-directional execution cycle**:

```
Start → Load Data → Clean Data → Build Features → Score Customers → Flag Transactions → Generate Reports → Complete
```

**Key Characteristics:**
1. **Single Execution**: Pipeline runs once per button click
2. **Non-Reentrant**: Cannot re-execute until reset
3. **Persistent Results**: All outputs preserved in memory
4. **View Navigation**: Switch between views without losing data
5. **Reset Required**: Use Reset button to clear and start new analysis

### Typical User Flow

1. **Launch Application**
   ```bash
   python main.py
   ```

2. **Review Dashboard**
   - Check application status
   - Review feature information

3. **Execute Analysis**
   - Click "Start Analysis" in sidebar
   - Select transaction CSV file
   - Monitor progress in Execution View

4. **Explore Results**
   - Navigate to different views using sidebar menu
   - Results persist across navigation
   - Data remains loaded until reset

5. **Access Reports**
   - Open generated CSV files
   - Review text report
   - Export/share results

6. **Reset (Optional)**
   - Click "Reset" to clear all data
   - Start new analysis with different dataset

## 🏗️ Technical Architecture

### Object-Oriented Design

1. **DataManager**: Handles file I/O and initial data validation
2. **TransactionCleaner**: Performs comprehensive data cleaning
3. **FeatureBuilder**: Engineers customer-level features
4. **RiskScorer**: Computes statistical risk scores
5. **TransactionFlagger**: Identifies suspicious transactions
6. **ReportGenerator**: Creates comprehensive reports
7. **AppStateManager**: Centralized state management
8. **AnalysisController**: Business logic controller with threading

### State Management

**AppStateManager** maintains:
- Execution state (idle, running, completed, error)
- Data store (raw data, cleaned data, features, scores, flags)
- Execution logs
- Step completion status

### Signal-Slot Pattern

All UI updates use Qt's signal-slot mechanism for responsive, event-driven architecture:
```python
# State Manager → UI
state_manager.state_changed.connect(ui_update_handler)

# Controller → Views
controller.progress_updated.connect(progress_bar_update)
controller.log_updated.connect(log_append)

# Sidebar → Main Window
sidebar.execute_clicked.connect(start_analysis)
sidebar.menu_clicked.connect(switch_view)
```

### Thread Safety

Long-running operations execute in `QThread`:
- UI remains responsive during analysis
- Progress updates via signals
- Graceful cancellation support
- Error propagation to main thread

## 📊 Methodology

### Feature Engineering

The application creates comprehensive customer profiles using:

- **Transaction Metrics**: Count, frequency, diversity
- **Amount Statistics**: Sum, mean, median, max, standard deviation
- **Velocity Indicators**: Transactions per day, amount per day
- **Temporal Patterns**: Night transactions, weekend activity
- **Behavioral Patterns**: Transaction regularity, amount volatility
- **Rolling Statistics**: Moving averages and trends

### Risk Scoring

Risk assessment employs:

1. **Z-Score Normalization**: Standardize features across customers
2. **Weighted Composite Scoring**: Combine multiple risk indicators
3. **Percentile Ranking**: Relative risk assessment
4. **Risk Band Classification**:
   - **Low Risk**: Bottom 75th percentile
   - **Medium Risk**: 75th-90th percentile
   - **High Risk**: 90th-95th percentile
   - **Critical Risk**: Top 5th percentile

### Anomaly Detection

Multiple criteria identify suspicious transactions:

1. **Statistical Outliers**: Z-score > 3 for transaction amounts
2. **Timing Anomalies**: Late-night or unusual timing patterns
3. **Velocity Anomalies**: Rapid successive transactions
4. **Structuring Patterns**: Multiple transactions near thresholds
5. **High-Risk Association**: Transactions from risky customers

## 📄 Output Files

### 1. flagged_transactions.csv
Contains all suspicious transactions with:
- Transaction details (amount, type, parties)
- Suspicion score and reasons
- Associated customer risk level

### 2. customer_risk_summary.csv
Comprehensive customer risk profiles with:
- Risk scores and bands
- Transaction statistics
- Behavioral metrics
- Flagged transaction counts

### 3. report.txt
Detailed analysis report including:
- Executive summary
- Risk distribution
- Top risky customers
- Methodology explanation
- Recommendations

## 🎨 Design Principles

### Visual Design
- **Modern Interface**: Clean, professional appearance
- **Color Coding**: Risk levels visualized with colors
  - Critical: Light Red (#ffc8c8)
  - High: Light Orange (#ffe6c8)
  - Medium: Light Yellow (#ffffe6)
  - Low: Light Green (#dcffdc)
- **Consistent Spacing**: 30px margins, 15px padding
- **Typography**: Clear hierarchy with appropriate font sizes
- **Responsive Layout**: Adapts to window resizing

### Performance Considerations
- **Vectorized Operations**: NumPy for efficient calculations
- **Grouped Aggregations**: Pandas groupby for customer-level metrics
- **Memory Management**: Chunked processing for large datasets
- **Background Threading**: Non-blocking UI during analysis
- **Optimized Algorithms**: O(n log n) sorting where necessary

## 🔧 Configuration

### Execution Parameters

Modify in `transaction_flagger.py`:
```python
# Z-score threshold (default: 3.0)
z_threshold = 3.0
```

### UI Customization

Adjust in view files:
```python
# Table row limits
display_data = data.head(1000)  # Adjust number

# Color schemes
color_map = {
    'Critical': QColor(255, 200, 200),
    # Customize colors...
}
```

## 🔐 Best Practices

### Code Organization
1. **Separation of Concerns**: UI ↔ Logic ↔ Data
2. **Single Responsibility**: Each class has one purpose
3. **DRY Principle**: Reusable components
4. **Type Hints**: Where appropriate for clarity

### User Experience
1. **Progress Feedback**: Always show what's happening
2. **Error Messages**: Clear, actionable error information
3. **State Preservation**: No data loss on navigation
4. **Confirmation Dialogs**: Prevent accidental data loss

## 🧪 Testing

### Manual Testing Checklist
- [ ] Application launches without errors
- [ ] File selection dialog works
- [ ] Execution completes successfully
- [ ] Progress updates in real-time
- [ ] All views display correct data
- [ ] Navigation preserves state
- [ ] Reports are generated
- [ ] Reset clears all data
- [ ] Error handling works
- [ ] Application closes cleanly

## 📝 Known Limitations

1. **Dataset Size**: Optimized for datasets up to 10M rows
2. **Display Limits**: Tables show first 500-1000 rows
3. **Single Analysis**: One execution at a time
4. **File Format**: CSV only (PaySim format)
5. **Platform**: Tested on Windows/macOS/Linux

## 🚀 Future Enhancements

Potential improvements include:

1. **Machine Learning Models**: Supervised classification for fraud detection
2. **Network Analysis**: Graph-based relationship detection
3. **Real-Time Processing**: Stream processing capabilities
4. **Interactive Visualizations**: Dashboard with charts and graphs
5. **Automated Alerts**: Email/SMS notifications for critical events
6. **Historical Trending**: Time-series analysis of risk patterns
7. **Multi-Language Support**: Internationalization
8. **Plugin Architecture**: Extensible analysis modules

## 🔄 Version History

### v1.1 (Current)
- Complete GUI interface with PyQt5
- Single-cycle execution model
- Persistent state management
- Thread-safe operations
- Real-time monitoring
- All core analysis features from console version

### v1.0
- Console application with menu interface
- Core analysis engine
- Report generation system

## 📄 License

This project is developed for educational purposes as part of a course assignment.

## 🙏 Acknowledgments

- **PyQt5**: Qt Company for the GUI framework
- **Pandas/NumPy/SciPy**: Data science libraries
- **PaySim Dataset**: NTNU for the synthetic data
- Methodology: Based on financial fraud detection research

## 📧 Support

For technical issues or questions:
- Review execution logs in Execution View
- Check console output for errors
- Verify dataset format matches PaySim specification
- Ensure all dependencies are installed

---

**Built with ❤️ for Financial Risk Analysis**