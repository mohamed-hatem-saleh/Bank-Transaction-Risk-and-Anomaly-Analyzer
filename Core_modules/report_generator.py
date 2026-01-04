"""
ReportGenerator class for generating CSV and text reports
"""
from datetime import datetime
import os

class ReportGenerator:    
    def __init__(self, risk_scores, flagged_transactions, original_data):
        self.risk_scores = risk_scores
        self.flagged_transactions = flagged_transactions
        self.original_data = original_data
        self.output_dir = "reports"
        
        if not os.path.exists(self.output_dir):
            os.makedirs(self.output_dir)
    
    def generate_all_reports(self):
        print("\n--- Generating Reports ---")
        
        print("  Generating flagged transactions report...")
        self._export_flagged_transactions()
        
        print("  Generating customer risk summary...")
        self._export_customer_risk_summary()
        
        print("  Generating text report...")
        self._generate_text_report()
        
        print(f"\n✓ All reports generated successfully in '{self.output_dir}/' directory")
    
    def _export_flagged_transactions(self):
        output_file = os.path.join(self.output_dir, "flagged_transactions.csv")
        
        export_columns = [
            'step', 'type', 'amount', 'nameOrig', 'nameDest',
            'hour', 'day', 'time_period',
            'suspicion_score', 'suspicion_reasons', 'risk_band', 'risk_score_normalized'
        ]
        
        # Filter to columns that exist
        available_columns = [col for col in export_columns if col in self.flagged_transactions.columns]
        
        export_data = self.flagged_transactions[available_columns].copy()
        export_data = export_data.sort_values('suspicion_score', ascending=False)
        
        export_data.to_csv(output_file, index=False)
        print(f"    ✓ Exported {len(export_data)} flagged transactions to {output_file}")
    
    def _export_customer_risk_summary(self):
        output_file = os.path.join(self.output_dir, "customer_risk_summary.csv")
        
        # Prepare comprehensive customer summary
        summary = self.risk_scores.copy()
        summary.index.name = 'customer_id'
        
        # Add transaction counts from flagged transactions
        flagged_counts = self.flagged_transactions.groupby('nameOrig').size()
        summary['flagged_transaction_count'] = flagged_counts
        summary['flagged_transaction_count'] = summary['flagged_transaction_count'].fillna(0).astype(int)
        
        # Sort by risk score
        summary = summary.sort_values('risk_score_normalized', ascending=False)
        
        summary.to_csv(output_file)
        print(f"    ✓ Exported {len(summary)} customer risk profiles to {output_file}")
    
    def _generate_text_report(self):
        """Generate comprehensive text report"""
        output_file = os.path.join(self.output_dir, "report.txt")
        
        with open(output_file, 'w') as f:
            f.write("=" * 80 + "\n")
            f.write("BANK TRANSACTION RISK & ANOMALY ANALYSIS REPORT\n")
            f.write("=" * 80 + "\n")
            f.write(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("=" * 80 + "\n\n")
            
            # Executive Summary
            f.write("EXECUTIVE SUMMARY\n")
            f.write("-" * 80 + "\n")
            f.write(f"Total Transactions Analyzed: {len(self.original_data):,}\n")
            f.write(f"Unique Customers Analyzed: {self.original_data['nameOrig'].nunique():,}\n")
            f.write(f"Total Transaction Volume: ${self.original_data['amount'].sum():,.2f}\n")
            f.write(f"Average Transaction Amount: ${self.original_data['amount'].mean():,.2f}\n")
            f.write(f"\nSuspicious Transactions Detected: {len(self.flagged_transactions):,}\n")
            f.write(f"Percentage of Flagged Transactions: {len(self.flagged_transactions)/len(self.original_data)*100:.2f}%\n")
            f.write(f"Total Flagged Transaction Volume: ${self.flagged_transactions['amount'].sum():,.2f}\n\n")
            
            # Risk Distribution
            f.write("CUSTOMER RISK DISTRIBUTION\n")
            f.write("-" * 80 + "\n")
            risk_counts = self.risk_scores['risk_band'].value_counts()
            for band in ['Low', 'Medium', 'High', 'Critical']:
                count = risk_counts.get(band, 0)
                pct = count / len(self.risk_scores) * 100
                f.write(f"{band:12s}: {count:6,} customers ({pct:5.2f}%)\n")
            f.write("\n")
            
            # Top Risky Customers
            f.write("TOP 20 HIGHEST RISK CUSTOMERS\n")
            f.write("-" * 80 + "\n")
            top_risky = self.risk_scores.nlargest(20, 'risk_score_normalized')
            
            f.write(f"{'Rank':<6}{'Customer ID':<20}{'Risk Score':<12}{'Risk Band':<12}{'Transactions':<15}{'Total Amount':<15}\n")
            f.write("-" * 80 + "\n")
            
            for idx, (customer_id, row) in enumerate(top_risky.iterrows(), 1):
                f.write(f"{idx:<6}{customer_id:<20}{row['risk_score_normalized']:>11.2f} {row['risk_band']:<12}")
                f.write(f"{int(row.get('transaction_count', 0)):<15}${row.get('total_amount', 0):>13,.2f}\n")
            
            f.write("\n")
            
            # Flagging Reasons Analysis
            f.write("SUSPICIOUS TRANSACTION REASON ANALYSIS\n")
            f.write("-" * 80 + "\n")
            
            reason_counts = {}
            for reasons in self.flagged_transactions['suspicion_reasons']:
                for reason in reasons.split('; '):
                    if reason.strip():
                        reason_counts[reason] = reason_counts.get(reason, 0) + 1
            
            for reason, count in sorted(reason_counts.items(), key=lambda x: x[1], reverse=True):
                pct = count / len(self.flagged_transactions) * 100
                f.write(f"{reason:<50}: {count:6,} ({pct:5.2f}%)\n")
            
            f.write("\n")
            
            # Most Suspicious Transactions
            f.write("TOP 10 MOST SUSPICIOUS TRANSACTIONS\n")
            f.write("-" * 80 + "\n")
            top_suspicious = self.flagged_transactions.nlargest(10, 'suspicion_score')
            
            f.write(f"{'Customer':<15}{'Amount':<15}{'Type':<12}{'Suspicion Score':<18}{'Risk Band':<12}\n")
            f.write("-" * 80 + "\n")
            
            for _, row in top_suspicious.iterrows():
                f.write(f"{row['nameOrig']:<15}${row['amount']:>13,.2f} {row['type']:<12}")
                f.write(f"{row['suspicion_score']:>17.2f} {row['risk_band']:<12}\n")
            
            f.write("\n")
            
            # Transaction Type Analysis
            f.write("FLAGGED TRANSACTIONS BY TYPE\n")
            f.write("-" * 80 + "\n")
            type_counts = self.flagged_transactions['type'].value_counts()
            
            for tx_type, count in type_counts.items():
                pct = count / len(self.flagged_transactions) * 100
                total_amt = self.flagged_transactions[self.flagged_transactions['type'] == tx_type]['amount'].sum()
                f.write(f"{tx_type:<15}: {count:6,} transactions ({pct:5.2f}%) - ${total_amt:,.2f}\n")
            
            f.write("\n")
            
            # Methodology
            f.write("METHODOLOGY\n")
            f.write("-" * 80 + "\n")
            f.write("This analysis employed the following techniques:\n\n")
            f.write("1. Feature Engineering:\n")
            f.write("   - Transaction counts and amounts per customer\n")
            f.write("   - Temporal patterns (daily velocity, time-of-day analysis)\n")
            f.write("   - Behavioral metrics (volatility, regularity, diversity)\n")
            f.write("   - Rolling statistics for trend detection\n\n")
            f.write("2. Risk Scoring:\n")
            f.write("   - Z-score normalization for key features\n")
            f.write("   - Weighted composite risk score calculation\n")
            f.write("   - Percentile-based risk band classification\n\n")
            f.write("3. Anomaly Detection:\n")
            f.write("   - Statistical outlier detection (Z-score > 3)\n")
            f.write("   - Timing pattern analysis\n")
            f.write("   - Transaction velocity monitoring\n")
            f.write("   - Structuring pattern detection\n")
            f.write("   - High-risk customer transaction flagging\n\n")
            
            # Recommendations
            f.write("RECOMMENDATIONS\n")
            f.write("-" * 80 + "\n")
            f.write("1. Immediate Review Required:\n")
            critical_customers = len(self.risk_scores[self.risk_scores['risk_band'] == 'Critical'])
            f.write(f"   - {critical_customers} Critical risk customers require immediate investigation\n")
            high_suspicion = len(self.flagged_transactions[self.flagged_transactions['suspicion_score'] > 50])
            f.write(f"   - {high_suspicion} transactions with very high suspicion scores\n\n")
            
            f.write("2. Enhanced Monitoring:\n")
            high_customers = len(self.risk_scores[self.risk_scores['risk_band'] == 'High'])
            f.write(f"   - {high_customers} High risk customers should be placed under enhanced monitoring\n")
            f.write("   - Implement real-time alerts for transactions from flagged customers\n\n")
            
            f.write("3. Process Improvements:\n")
            f.write("   - Review transaction limits for high-risk profiles\n")
            f.write("   - Implement additional verification for late-night transactions\n")
            f.write("   - Monitor for structuring patterns across multiple accounts\n\n")
            
            f.write("=" * 80 + "\n")
            f.write("END OF REPORT\n")
            f.write("=" * 80 + "\n")
        
        print(f"    ✓ Generated comprehensive text report: {output_file}")
    
    def display_summary(self):
        """Display summary in console"""
        print("\n" + "=" * 80)
        print("ANALYSIS SUMMARY")
        print("=" * 80)
        
        print(f"\nDataset Overview:")
        print(f"  • Total Transactions: {len(self.original_data):,}")
        print(f"  • Unique Customers: {self.original_data['nameOrig'].nunique():,}")
        print(f"  • Total Volume: ${self.original_data['amount'].sum():,.2f}")
        
        print(f"\nRisk Assessment:")
        risk_counts = self.risk_scores['risk_band'].value_counts()
        for band in ['Critical', 'High', 'Medium', 'Low']:
            count = risk_counts.get(band, 0)
            pct = count / len(self.risk_scores) * 100
            print(f"  • {band} Risk: {count:,} customers ({pct:.1f}%)")
        
        print(f"\nAnomaly Detection:")
        print(f"  • Flagged Transactions: {len(self.flagged_transactions):,} ({len(self.flagged_transactions)/len(self.original_data)*100:.2f}%)")
        print(f"  • Flagged Volume: ${self.flagged_transactions['amount'].sum():,.2f}")
        
        print(f"\nTop 5 Highest Risk Customers:")
        top_5 = self.risk_scores.nlargest(5, 'risk_score_normalized')
        for idx, (customer_id, row) in enumerate(top_5.iterrows(), 1):
            print(f"  {idx}. {customer_id}: Risk Score {row['risk_score_normalized']:.1f} ({row['risk_band']})")
        
        print("\n" + "=" * 80)