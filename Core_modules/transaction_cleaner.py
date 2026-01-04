"""
TransactionCleaner class for data cleaning and preparation
"""

import pandas as pd

class TransactionCleaner:
    def __init__(self, data):
        self.data = data.copy()
        self.cleaned_data = None
        self.cleaning_report = []
        
    def clean_data(self):
        print("\n--- Starting Data Cleaning ---")
        
        initial_rows = len(self.data)
        self.cleaned_data = self.data.copy()
        
        self._handle_missing_values()
        self._remove_duplicates()
        self._handle_invalid_values()
        self._convert_data_types()
        self._create_timestamps()
        
        final_rows = len(self.cleaned_data)
        rows_removed = initial_rows - final_rows
        
        print(f"\n✓ Cleaning complete:")
        print(f"  - Initial rows: {initial_rows:,}")
        print(f"  - Final rows: {final_rows:,}")
        print(f"  - Rows removed: {rows_removed:,} ({rows_removed/initial_rows*100:.2f}%)")
        
        return self.cleaned_data
    
    def _handle_missing_values(self):
        null_counts = self.cleaned_data.isnull().sum()
        total_nulls = null_counts.sum()
        
        if total_nulls > 0:
            print(f"  Handling {total_nulls} missing values...")
            
            amt_nulls = self.cleaned_data['amount'].isnull().sum()
            if amt_nulls > 0:
                self.cleaned_data = self.cleaned_data.dropna(subset=['amount'])
                self.cleaning_report.append(f"Removed {amt_nulls} rows with missing amount")
            
            cat_cols = ['type', 'nameOrig', 'nameDest']
            for col in cat_cols:
                null_count = self.cleaned_data[col].isnull().sum()
                if null_count > 0:
                    self.cleaned_data[col].fillna('UNKNOWN', inplace=True)
                    self.cleaning_report.append(f"Filled {null_count} nulls in {col}")
        else:
            print(f"  ✓ No missing values found")
    
    def _remove_duplicates(self):
        duplicates = self.cleaned_data.duplicated().sum()
        
        if duplicates > 0:
            print(f"  Removing {duplicates} duplicate rows...")
            self.cleaned_data = self.cleaned_data.drop_duplicates()
            self.cleaning_report.append(f"Removed {duplicates} duplicate rows")
        else:
            print(f"  ✓ No duplicates found")
    
    def _handle_invalid_values(self):
        initial_len = len(self.cleaned_data)
        
        negative_amt = (self.cleaned_data['amount'] < 0).sum()
        if negative_amt > 0:
            self.cleaned_data = self.cleaned_data[self.cleaned_data['amount'] >= 0]
            self.cleaning_report.append(f"Removed {negative_amt} rows with negative amounts")
        
        removed = initial_len - len(self.cleaned_data)
        if removed > 0:
            print(f"  Removed {removed} invalid records")
        else:
            print(f"  ✓ No invalid values found")
    
    def _convert_data_types(self):
        print(f"  Converting data types...")
        numeric_cols = ['step', 'amount']
        for col in numeric_cols:
            self.cleaned_data[col] = pd.to_numeric(self.cleaned_data[col], errors='coerce')
        
        cat_cols = ['type', 'nameOrig', 'nameDest']
        for col in cat_cols:
            self.cleaned_data[col] = self.cleaned_data[col].astype(str)
        
        self.cleaning_report.append("Converted columns to appropriate data types")
    
    def _create_timestamps(self):
        self.cleaned_data['hour'] = self.cleaned_data['step'] % 24
        self.cleaned_data['day'] = self.cleaned_data['step'] // 24
        
        self.cleaned_data['time_period'] = pd.cut(
            self.cleaned_data['hour'],
            bins=[0, 6, 12, 18, 24],
            labels=['Night', 'Morning', 'Afternoon', 'Evening'],
            include_lowest=True
        )
        
        self.cleaning_report.append("Created timestamp features (hour, day, time_period)")
    
    def get_cleaning_report(self):
        report = "\n--- Data Cleaning Report ---\n"
        if self.cleaning_report:
            for item in self.cleaning_report:
                report += f"• {item}\n"
        else:
            report += "No cleaning actions performed.\n"
        return report
    
    def get_cleaned_data(self):
        if self.cleaned_data is None:
            raise ValueError("Data has not been cleaned yet. Call clean_data() first.")
        return self.cleaned_data