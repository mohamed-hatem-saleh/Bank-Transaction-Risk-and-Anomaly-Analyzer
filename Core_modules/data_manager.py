"""
DataManager class for handling file loading and validation
"""

import pandas as pd

class DataManager:    
    def __init__(self):
        self.transaction_data = None
        self.is_loaded = False
        
    def load_transactions(self, filepath):
        try:
            print(f"Loading transaction data from: {filepath}")
            self.transaction_data = pd.read_csv(filepath)
            
            print(f"✓ Loaded {len(self.transaction_data)} transactions")
            print(f"✓ Columns: {list(self.transaction_data.columns)}")
            
            self.is_loaded = True
            return True
          
        except Exception as e:
            print(f"Error loading transactions failed: {e}")
            return False
    
    
    def validate_data(self):
        if not self.is_loaded:
            print("Error: No data loaded yet.")
            return False
        
        print("\n--- Data Validation Report ---")
        
        # Check for required columns
        required_cols = ['step', 'type', 'amount', 'nameOrig', 'nameDest']
        missing_cols = [col for col in required_cols if col not in self.transaction_data.columns]
        
        if missing_cols:
            print(f"✗ Missing required columns: {missing_cols}")
            return False
        
        print(f"✓ All required columns present")
        rows, cols = self.transaction_data.shape
        print(f"✓ Data shape: {rows} rows × {cols} columns")
        
        # Check for null values
        null_counts = self.transaction_data.isnull().sum()
        total_nulls = null_counts.sum()
        
        if total_nulls > 0:
            print(f"⚠ Found {total_nulls} null values:")
            for col, count in null_counts[null_counts > 0].items():
                print(f"  - {col}: {count} nulls")
        else:
            print(f"✓ No null values found")
        
        # Check for duplicates
        duplicates = self.transaction_data.duplicated().sum()
        if duplicates > 0:
            print(f"⚠ Found {duplicates} duplicate rows")
        else:
            print(f"✓ No duplicate rows found")
        
        # Basic statistics
        print(f"\nTransaction amount statistics:")
        print(f"  - Min: ${self.transaction_data['amount'].min():,.2f}")
        print(f"  - Max: ${self.transaction_data['amount'].max():,.2f}")
        print(f"  - Mean: ${self.transaction_data['amount'].mean():,.2f}")
        print(f"  - Median: ${self.transaction_data['amount'].median():,.2f}")
        
        return True
    
    def get_transaction_data(self):
        if not self.is_loaded:
            raise ValueError("No data loaded yet.")
        return self.transaction_data.sample(frac=0.01)
    
    def get_data_summary(self):
        if not self.is_loaded:
            return "No data loaded"
        
        summary = f"""
        Data Summary:
        - Transactions: {len(self.transaction_data):,}
        - Unique customers (origin): {self.transaction_data['nameOrig'].nunique():,}
        - Unique customers (destination): {self.transaction_data['nameDest'].nunique():,}
        - Transaction types: {self.transaction_data['type'].nunique()}
        - Date range: Step {self.transaction_data['step'].min()} to {self.transaction_data['step'].max()}
        """
        return summary.strip()