"""
FeatureBuilder class for creating customer-level features
"""

import pandas as pd
import numpy as np
import warnings
warnings.simplefilter(action='ignore', category=FutureWarning)

class FeatureBuilder:    
    def __init__(self, data):
        self.data = data.copy()
        self.customer_features = None
        
    def build_features(self):
        print("\n--- Building Customer Features ---")

        print("  Calculating features...")
        features = self._calculate_all_features_optimized()
        
        self.customer_features = features
        
        print(f"\n✓ Built features for {len(features):,} customers")
        print(f"✓ Total features: {len(features.columns)}")
        
        return self.customer_features
    
    def _calculate_all_features_optimized(self):

        agg_dict = {
            'step': 'count',
            'amount': ['sum', 'mean', 'median', 'max', 'min', 'std'],
            'type': lambda x: x.value_counts().to_dict(),
            'day': ['min', 'max', 'nunique'],
            'hour': lambda x: ((x >= 0) & (x < 6)).sum(),
            'nameDest': 'nunique'
        }
        
        features = self.data.groupby('nameOrig').agg(agg_dict)
        features.columns = ['_'.join(col).strip('_') if col[1] else col[0] 
                           for col in features.columns.values]
        
        # Expand transaction type counts
        type_counts = pd.json_normalize(features['type_<lambda>']).fillna(0)
        type_counts.index = features.index
        type_counts.columns = [f'count_{col}' for col in type_counts.columns]
        features = features.drop('type_<lambda>', axis=1).join(type_counts)
        
        # Rename for clarity
        features = features.rename(columns={
            'step_count': 'transaction_count',
            'amount_sum': 'total_amount',
            'amount_mean': 'avg_amount',
            'amount_median': 'median_amount',
            'amount_max': 'max_amount',
            'amount_min': 'min_amount',
            'amount_std': 'std_amount',
            'day_min': 'first_day',
            'day_max': 'last_day',
            'day_nunique': 'unique_days_active',
            'hour_<lambda>': 'night_transactions',
            'nameDest_nunique': 'unique_recipients'
        })
        
        
        # Feature Extraction
        features['days_since_first'] = features['last_day'] - features['first_day']
        features['days_since_first'] = features['days_since_first'].replace(0, 1)

        features['transactions_per_day'] = features['transaction_count'] / features['days_since_first']
        features['amount_per_day'] = features['total_amount'] / features['days_since_first']
        
        features['night_transaction_ratio'] = features['night_transactions'] / features['transaction_count']
        
        features['max_single_transaction_ratio'] = features['max_amount'] / features['total_amount']
        
        # Calculate high value transactions using quantile
        high_value_threshold = self.data['amount'].quantile(0.95)
        high_value_counts = self.data[self.data['amount'] > high_value_threshold].groupby('nameOrig').size()
        features['high_value_transactions'] = high_value_counts
        features['high_value_transactions'] = features['high_value_transactions'].fillna(0)
        features['high_value_ratio'] = features['high_value_transactions'] / features['transaction_count']
        
        # Transaction type diversity
        type_diversity = self.data.groupby('nameOrig')['type'].nunique()
        features['transaction_type_diversity'] = type_diversity
        
        # Simplified rolling statistics
        features['last_rolling_mean'] = features['avg_amount'] 
        features['last_rolling_std'] = features['std_amount']
        features['rolling_mean_trend'] = 0  
        
        # Weekend transactions
        self.data['is_weekend'] = (self.data['day'] % 7 >= 5)
        weekend_counts = self.data[self.data['is_weekend']].groupby('nameOrig').size()
        features['weekend_transactions'] = weekend_counts.fillna(0)
        
        features['transaction_regularity'] = features['std_amount'] / (features['avg_amount'] + 1)
        
        return features
    
    def get_features(self):
        if self.customer_features is None:
            raise ValueError("Features have not been built yet. Call build_features() first.")
        return self.customer_features
    
    def get_feature_summary(self):
        if self.customer_features is None:
            return "No features built yet."
        
        summary = f"""S
        Feature Summary:

        - Feature categories:
        * Transaction counts: {len([c for c in self.customer_features.columns if 'count' in c])}
        * Amount statistics: {len([c for c in self.customer_features.columns if 'amount' in c])}
        * Velocity metrics: {len([c for c in self.customer_features.columns if 'per_day' in c])}
        * Behavioral patterns: {len([c for c in self.customer_features.columns if 'ratio' in c])}
        
        Top features by variance:
        {self.customer_features.var().sort_values(ascending=False).head(5).to_string()}
        """
        return summary.strip()