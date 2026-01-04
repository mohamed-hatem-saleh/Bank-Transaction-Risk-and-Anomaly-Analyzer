"""
TransactionFlagger class for flagging suspicious transactions
"""

import numpy as np

class TransactionFlagger:
    def __init__(self, data, risk_scores):
        self.data = data.copy()
        self.risk_scores = risk_scores
        self.flagged_transactions = None
        
    def flag_suspicious_transactions(self, z_threshold=3.0):
        print("\n--- Flagging Suspicious Transactions ---")
        
        self.data = self.data.merge(
            self.risk_scores[['risk_score_normalized', 'risk_band']],
            left_on='nameOrig',
            right_index=True,
            how='left'
        )
        
        self.data['is_suspicious'] = False
        self.data['suspicion_reasons'] = ''
        self.data['suspicion_score'] = 0.0
        
        # Apply multiple detection rules
        print("  Detecting high-value outliers...")
        self._flag_amount_outliers(z_threshold)
        
        print("  Detecting unusual timing patterns...")
        self._flag_timing_anomalies()
        
        print("  Detecting velocity anomalies...")
        self._flag_velocity_anomalies()
        
        print("  Detecting structuring patterns...")
        self._flag_structuring_patterns()
        
        print("  Detecting high-risk customer transactions...")
        self._flag_high_risk_customer_transactions()
        
        # Filter to suspicious transactions only
        self.flagged_transactions = self.data[self.data['is_suspicious']].copy()
        self.flagged_transactions = self.flagged_transactions.sort_values('suspicion_score', ascending=False)
        
        print(f"\n✓ Flagged {len(self.flagged_transactions):,} suspicious transactions")
        print(f"  ({len(self.flagged_transactions)/len(self.data)*100:.2f}% of all transactions)")
        
        return self.flagged_transactions
    
    def _flag_amount_outliers(self, z_threshold):
        amount_mean = self.data['amount'].mean()
        amount_std = self.data['amount'].std()
        
        if amount_std > 0:
            z_scores = (self.data['amount'] - amount_mean) / amount_std
            
            # Flag high z-scores
            outlier_mask = np.abs(z_scores) > z_threshold
            
            self.data.loc[outlier_mask, 'is_suspicious'] = True
            self.data.loc[outlier_mask, 'suspicion_score'] += np.abs(z_scores[outlier_mask]) * 10
            self.data.loc[outlier_mask, 'suspicion_reasons'] += 'High-value outlier; '
    
    def _flag_timing_anomalies(self):
        # Flag late night transactions (0-5 AM)
        night_mask = (self.data['hour'] >= 0) & (self.data['hour'] < 6)
        
        self.data.loc[night_mask, 'is_suspicious'] = True
        self.data.loc[night_mask, 'suspicion_score'] += 15
        self.data.loc[night_mask, 'suspicion_reasons'] += 'Late night transaction; '
        
        # Flag weekend transactions for certain types
        weekend_mask = (self.data['day'] % 7 >= 5)
        high_amount_mask = self.data['amount'] > self.data['amount'].quantile(0.90)
        
        weekend_high_mask = weekend_mask & high_amount_mask
        
        self.data.loc[weekend_high_mask, 'suspicion_score'] += 10
        self.data.loc[weekend_high_mask, 'suspicion_reasons'] += 'Weekend high-value transaction; '
    
    def _flag_velocity_anomalies(self):
        sorted_data = self.data.sort_values(['nameOrig', 'step'])
        sorted_data['time_since_last'] = sorted_data.groupby('nameOrig')['step'].diff()
        
        # Flag very rapid transactions (within 1 hour)
        rapid_mask = sorted_data['time_since_last'] <= 1
        rapid_indices = sorted_data[rapid_mask].index
        
        self.data.loc[rapid_indices, 'is_suspicious'] = True
        self.data.loc[rapid_indices, 'suspicion_score'] += 20
        self.data.loc[rapid_indices, 'suspicion_reasons'] += 'Rapid successive transaction; '
        
        # Calculate number of transactions in short window
        sorted_data['recent_tx_count'] = sorted_data.groupby('nameOrig')['step'].transform(
            lambda x: x.rolling(window=5, min_periods=1).count()
        )
        
        # Flag burst activity (5+ transactions in short period)
        burst_mask = sorted_data['recent_tx_count'] >= 5
        burst_indices = sorted_data[burst_mask].index
        
        self.data.loc[burst_indices, 'suspicion_score'] += 15
        self.data.loc[burst_indices, 'suspicion_reasons'] += 'Burst activity detected; '
    
    def _flag_structuring_patterns(self):
        threshold_amounts = [10000, 5000, 3000]
        
        for threshold in threshold_amounts:
            # Find transactions within 10% below threshold
            near_threshold_mask = (
                (self.data['amount'] >= threshold * 0.85) & 
                (self.data['amount'] < threshold * 0.99)
            )
            
            # Count such transactions per customer
            structuring_counts = self.data[near_threshold_mask].groupby('nameOrig').size()
            
            # Flag customers with multiple near-threshold transactions
            suspicious_customers = structuring_counts[structuring_counts >= 3].index
            structuring_mask = self.data['nameOrig'].isin(suspicious_customers) & near_threshold_mask
            
            self.data.loc[structuring_mask, 'is_suspicious'] = True
            self.data.loc[structuring_mask, 'suspicion_score'] += 25
            self.data.loc[structuring_mask, 'suspicion_reasons'] += f'Potential structuring near ${threshold:,}; '
    
    def _flag_high_risk_customer_transactions(self):
        # Flag transactions from Critical and High risk customers
        high_risk_mask = self.data['risk_band'].isin(['High', 'Critical'])
        
        self.data.loc[high_risk_mask, 'is_suspicious'] = True
        self.data.loc[high_risk_mask, 'suspicion_score'] += self.data.loc[high_risk_mask, 'risk_score_normalized'] * 0.3
        self.data.loc[high_risk_mask, 'suspicion_reasons'] += 'High-risk customer; '
        
        # Extra flag for critical customers with large amounts
        critical_mask = (self.data['risk_band'] == 'Critical') & (self.data['amount'] > self.data['amount'].median())
        
        self.data.loc[critical_mask, 'suspicion_score'] += 30
        self.data.loc[critical_mask, 'suspicion_reasons'] += 'Critical risk customer large transaction; '
    
    def get_flagged_transactions(self):
        if self.flagged_transactions is None:
            raise ValueError("Transactions have not been flagged yet. Call flag_suspicious_transactions() first.")
        return self.flagged_transactions
    
    def get_flagging_summary(self):
        if self.flagged_transactions is None:
            return "No transactions flagged yet."
        
        # Count reasons
        reason_counts = {}
        for reasons in self.flagged_transactions['suspicion_reasons']:
            for reason in reasons.split('; '):
                if reason.strip():
                    reason_counts[reason] = reason_counts.get(reason, 0) + 1
        
        reason_summary = "\n".join([f"  • {reason}: {count:,}" for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True)])
        
        summary = f"""
        Suspicious Transaction Summary:
        - Total transactions analyzed: {len(self.data):,}
        - Flagged as suspicious: {len(self.flagged_transactions):,} ({len(self.flagged_transactions)/len(self.data)*100:.2f}%)

        Suspicion Reasons Distribution:
        {reason_summary}

        Top 5 Most Suspicious Transactions:
        {self.flagged_transactions.nlargest(5, 'suspicion_score')[['nameOrig', 'amount', 'type', 'suspicion_score', 'risk_band']].to_string()}

        Flagged Transactions by Type:
        {self.flagged_transactions['type'].value_counts().to_string()}
        """
        return summary.strip()
    
    def get_customer_flagged_summary(self):
        customer_summary = self.flagged_transactions.groupby('nameOrig').agg({
            'amount': ['count', 'sum', 'mean'],
            'suspicion_score': 'mean',
            'risk_band': 'first'
        }).round(2)
        
        customer_summary.columns = ['flagged_count', 'total_flagged_amount', 'avg_flagged_amount', 'avg_suspicion_score', 'risk_band']
        customer_summary = customer_summary.sort_values('flagged_count', ascending=False)
        
        return customer_summary