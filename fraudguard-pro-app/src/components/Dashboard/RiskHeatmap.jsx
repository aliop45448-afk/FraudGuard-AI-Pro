import React from 'react';
import './RiskHeatmap.css';

/**
 * RiskHeatmap Component
 * 
 * Displays risk score distribution as a heatmap
 */
const RiskHeatmap = ({ metrics }) => {
  const riskBuckets = {
    'خطر عالي جداً (80-100)': 0,
    'خطر عالي (60-79)': 0,
    'خطر متوسط (40-59)': 0,
    'خطر منخفض (20-39)': 0,
    'آمن (0-19)': 0,
  };

  // Mock distribution data
  const distribution = {
    'خطر عالي جداً (80-100)': 15,
    'خطر عالي (60-79)': 25,
    'خطر متوسط (40-59)': 35,
    'خطر منخفض (20-39)': 20,
    'آمن (0-19)': 5,
  };

  const total = Object.values(distribution).reduce((a, b) => a + b, 0);

  return (
    <div className="risk-heatmap">
      {Object.entries(distribution).map(([label, count]) => {
        const percentage = (count / total) * 100;
        const riskLevel = label.split('(')[0].trim();
        
        let colorClass = 'risk-safe';
        if (riskLevel.includes('عالي جداً')) colorClass = 'risk-critical';
        else if (riskLevel.includes('عالي')) colorClass = 'risk-high';
        else if (riskLevel.includes('متوسط')) colorClass = 'risk-medium';
        else if (riskLevel.includes('منخفض')) colorClass = 'risk-low';

        return (
          <div key={label} className="heatmap-row">
            <div className="heatmap-label">{label}</div>
            <div className="heatmap-bar">
              <div 
                className={`heatmap-fill ${colorClass}`}
                style={{ width: `${percentage}%` }}
              ></div>
            </div>
            <div className="heatmap-value">
              {count} ({percentage.toFixed(1)}%)
            </div>
          </div>
        );
      })}
    </div>
  );
};

export default RiskHeatmap;
