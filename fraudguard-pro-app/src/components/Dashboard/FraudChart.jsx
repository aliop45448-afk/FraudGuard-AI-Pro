import React, { useState, useEffect } from 'react';
import './FraudChart.css';

/**
 * FraudChart Component
 * 
 * Displays fraud detection trends over time using a line chart
 */
const FraudChart = ({ timeRange }) => {
  const [chartData, setChartData] = useState([]);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    // Generate mock chart data based on time range
    const generateChartData = () => {
      const points = timeRange === '1h' ? 12 : timeRange === '24h' ? 24 : 7;
      const data = [];

      for (let i = 0; i < points; i++) {
        data.push({
          time: `${i}:00`,
          fraudRate: Math.random() * 10 + 2,
          transactionCount: Math.floor(Math.random() * 500 + 100),
        });
      }

      return data;
    };

    setLoading(true);
    setTimeout(() => {
      setChartData(generateChartData());
      setLoading(false);
    }, 500);
  }, [timeRange]);

  if (loading) {
    return <div className="chart-loading">جاري تحميل البيانات...</div>;
  }

  const maxFraudRate = Math.max(...chartData.map(d => d.fraudRate));

  return (
    <div className="fraud-chart">
      <div className="chart-area">
        {chartData.map((point, index) => (
          <div key={index} className="chart-point">
            <div className="point-bar">
              <div 
                className="point-fill"
                style={{
                  height: `${(point.fraudRate / maxFraudRate) * 100}%`,
                }}
              ></div>
            </div>
            <span className="point-label">{point.time}</span>
          </div>
        ))}
      </div>
      <div className="chart-legend">
        <div className="legend-item">
          <span className="legend-color" style={{ backgroundColor: '#ef4444' }}></span>
          <span>معدل الاحتيال</span>
        </div>
      </div>
    </div>
  );
};

export default FraudChart;
