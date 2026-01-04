"""
RiskScorer class for computing customer risk scores
"""

import pandas as pd
import numpy as np
from scipy import stats

class RiskScorer:

    def __init__(self, features):
        self.features = features.copy()
        self.risk_scores = None
        self.z_scores = None
        
    def compute_risk_scores(self):
        print("\n--- Computing Risk Scores ---")
        
        print("  Calculating z-scores...")
        self._calculate_z_scores()
        
        print("  Computing composite risk scores...")
        self._compute_composite_score()
        
        print("  Classifying risk bands...")
        self._classify_risk_bands()
        
        print(f"\n✓ Computed risk scores for {len(self.risk_scores):,} customers")
        
        return self.risk_scores
    
    def _calculate_z_scores(self):
        z_score_features = [
            'total_amount',
            'avg_amount',
            'max_amount',
            'transaction_count',
            'transactions_per_day',
            'amount_per_day',
            'unique_recipients',
            'night_transaction_ratio',
            'high_value_ratio',
            'max_single_transaction_ratio'
        ]

        # Calculate z-score
        self.z_scores = pd.DataFrame(index=self.features.index)
        for feature in z_score_features:
            if feature in self.features.columns:
                clean_values = self.features[feature].replace([np.inf, -np.inf], np.nan).fillna(0)
                 
                if clean_values.std() > 0:
                    self.z_scores[f'z_{feature}'] = stats.zscore(clean_values)
                else:
                    self.z_scores[f'z_{feature}'] = 0
    
    def _compute_composite_score(self):
        weights = {
            'z_total_amount': 0.15,
            'z_avg_amount': 0.10,
            'z_max_amount': 0.10,
            'z_transaction_count': 0.08,
            'z_transactions_per_day': 0.12,
            'z_amount_per_day': 0.12,
            'z_unique_recipients': 0.08,
            'z_night_transaction_ratio': 0.12,
            'z_high_value_ratio': 0.09,
            'z_max_single_transaction_ratio': 0.04
        }
        
        # Initialize risk scores dataframe and Calculate weighted score
        self.risk_scores = pd.DataFrame(index=self.features.index)
        composite_score = pd.Series(0.0, index=self.features.index)
        
        for feature, weight in weights.items():
            if feature in self.z_scores.columns:
                composite_score += np.abs(self.z_scores[feature]) * weight
        
        self.risk_scores['risk_score'] = composite_score
        
        # Normalize
        min_score = self.risk_scores['risk_score'].min()
        max_score = self.risk_scores['risk_score'].max()
        
        if max_score > min_score:
            self.risk_scores['risk_score_normalized'] = (
                (self.risk_scores['risk_score'] - min_score) / (max_score - min_score) * 100
            )
        else:
            self.risk_scores['risk_score_normalized'] = 50
        
        # Add scores
        for feature, weight in weights.items():
            if feature in self.z_scores.columns:
                self.risk_scores[feature] = self.z_scores[feature]
    
    def _classify_risk_bands(self):
        p75 = self.risk_scores['risk_score_normalized'].quantile(0.75)
        p90 = self.risk_scores['risk_score_normalized'].quantile(0.90)
        p95 = self.risk_scores['risk_score_normalized'].quantile(0.95)
        
        conditions = [
            self.risk_scores['risk_score_normalized'] < p75,
            (self.risk_scores['risk_score_normalized'] >= p75) & (self.risk_scores['risk_score_normalized'] < p90),
            (self.risk_scores['risk_score_normalized'] >= p90) & (self.risk_scores['risk_score_normalized'] < p95),
            self.risk_scores['risk_score_normalized'] >= p95
        ]
        
        choices = ['Low', 'Medium', 'High', 'Critical']
        
        self.risk_scores['risk_band'] = np.select(conditions, choices, default='Low')
        
        key_features = [
            'transaction_count',
            'total_amount',
            'avg_amount',
            'max_amount',
            'transactions_per_day',
            'unique_recipients',
            'night_transaction_ratio',
            'high_value_ratio'
        ]
        
        for feature in key_features:
            if feature in self.features.columns:
                self.risk_scores[feature] = self.features[feature]
    
    def get_risk_scores(self):
        if self.risk_scores is None:
            raise ValueError("Risk scores have not been computed yet. Call compute_risk_scores() first.")
        return self.risk_scores
    
    def get_high_risk_customers(self, min_band='High'):
        if self.risk_scores is None:
            raise ValueError("Risk scores have not been computed yet.")
        
        band_order = {'Low': 0, 'Medium': 1, 'High': 2, 'Critical': 3}
        min_level = band_order.get(min_band, 2)
        
        high_risk = self.risk_scores[
            self.risk_scores['risk_band'].map(band_order) >= min_level
        ].sort_values('risk_score_normalized', ascending=False)
        
        return high_risk
    
    def get_risk_summary(self):
        if self.risk_scores is None:
            return "No risk scores computed yet."
        
        band_counts = self.risk_scores['risk_band'].value_counts()
        
        summary = f"""
        Risk Score Summary:
        - Total customers scored: {len(self.risk_scores):,}

        Risk Band Distribution:
        • Low Risk: {band_counts.get('Low', 0):,} ({band_counts.get('Low', 0)/len(self.risk_scores)*100:.1f}%)
        • Medium Risk: {band_counts.get('Medium', 0):,} ({band_counts.get('Medium', 0)/len(self.risk_scores)*100:.1f}%)
        • High Risk: {band_counts.get('High', 0):,} ({band_counts.get('High', 0)/len(self.risk_scores)*100:.1f}%)
        • Critical Risk: {band_counts.get('Critical', 0):,} ({band_counts.get('Critical', 0)/len(self.risk_scores)*100:.1f}%)

        Risk Score Statistics:
        - Mean: {self.risk_scores['risk_score_normalized'].mean():.2f}
        - Median: {self.risk_scores['risk_score_normalized'].median():.2f}
        - Std Dev: {self.risk_scores['risk_score_normalized'].std():.2f}
        - Min: {self.risk_scores['risk_score_normalized'].min():.2f}
        - Max: {self.risk_scores['risk_score_normalized'].max():.2f}

        Top 5 Riskiest Customers:
        {self.risk_scores.nlargest(5, 'risk_score_normalized')[['risk_score_normalized', 'risk_band', 'transaction_count', 'total_amount']].to_string()}
        """
        return summary.strip()