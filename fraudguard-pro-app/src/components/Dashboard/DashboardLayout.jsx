import React, { useState, useEffect } from 'react';
import './DashboardLayout.css';
import MetricsCard from './MetricsCard';
import FraudChart from './FraudChart';
import TransactionTable from './TransactionTable';
import RiskHeatmap from './RiskHeatmap';
import ModelPerformance from './ModelPerformance';

/**
 * Main Dashboard Layout Component
 * 
 * Displays real-time fraud detection metrics, charts, and analytics
 * in an enterprise-grade dashboard interface.
 */
const DashboardLayout = () => {
  const [metrics, setMetrics] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [timeRange, setTimeRange] = useState('24h');
  const [autoRefresh, setAutoRefresh] = useState(true);

  // Fetch dashboard metrics from API
  useEffect(() => {
    const fetchMetrics = async () => {
      try {
        setLoading(true);
        const response = await fetch('/api/v1/dashboards/metrics', {
          headers: {
            'Authorization': `Bearer ${localStorage.getItem('token')}`,
          },
        });

        if (!response.ok) {
          throw new Error('Failed to fetch metrics');
        }

        const data = await response.json();
        setMetrics(data);
        setError(null);
      } catch (err) {
        setError(err.message);
        console.error('Error fetching metrics:', err);
      } finally {
        setLoading(false);
      }
    };

    fetchMetrics();

    // Auto-refresh metrics if enabled
    let interval;
    if (autoRefresh) {
      interval = setInterval(fetchMetrics, 30000); // Refresh every 30 seconds
    }

    return () => {
      if (interval) clearInterval(interval);
    };
  }, [autoRefresh, timeRange]);

  if (loading && !metrics) {
    return (
      <div className="dashboard-loading">
        <div className="spinner"></div>
        <p>جاري تحميل لوحة المعلومات...</p>
      </div>
    );
  }

  if (error) {
    return (
      <div className="dashboard-error">
        <p>خطأ: {error}</p>
        <button onClick={() => window.location.reload()}>إعادة محاولة</button>
      </div>
    );
  }

  const currentMetrics = metrics?.current_snapshot || {};

  return (
    <div className="dashboard-container">
      {/* Header */}
      <div className="dashboard-header">
        <h1>لوحة المعلومات - كشف الاحتيال</h1>
        <div className="header-controls">
          <select 
            value={timeRange} 
            onChange={(e) => setTimeRange(e.target.value)}
            className="time-range-select"
          >
            <option value="1h">آخر ساعة</option>
            <option value="24h">آخر 24 ساعة</option>
            <option value="7d">آخر 7 أيام</option>
            <option value="30d">آخر 30 يوم</option>
          </select>
          
          <label className="auto-refresh-toggle">
            <input 
              type="checkbox" 
              checked={autoRefresh}
              onChange={(e) => setAutoRefresh(e.target.checked)}
            />
            تحديث تلقائي
          </label>

          <button className="refresh-btn" onClick={() => window.location.reload()}>
            🔄 تحديث الآن
          </button>
        </div>
      </div>

      {/* Key Metrics Cards */}
      <div className="metrics-grid">
        <MetricsCard
          title="إجمالي المعاملات"
          value={currentMetrics.total_transactions || 0}
          icon="📊"
          color="blue"
        />
        <MetricsCard
          title="معاملات احتيالية"
          value={currentMetrics.fraudulent_transactions || 0}
          icon="⚠️"
          color="red"
          subtext={`${((currentMetrics.fraud_rate || 0) * 100).toFixed(2)}%`}
        />
        <MetricsCard
          title="معاملات محجوبة"
          value={currentMetrics.blocked_transactions || 0}
          icon="🚫"
          color="orange"
        />
        <MetricsCard
          title="متوسط درجة المخاطر"
          value={currentMetrics.average_risk_score?.toFixed(2) || 0}
          icon="📈"
          color="purple"
        />
      </div>

      {/* Charts Row */}
      <div className="charts-grid">
        <div className="chart-container">
          <h2>معدل الاحتيال بمرور الوقت</h2>
          <FraudChart timeRange={timeRange} />
        </div>

        <div className="chart-container">
          <h2>توزيع درجات المخاطر</h2>
          <RiskHeatmap metrics={metrics} />
        </div>
      </div>

      {/* Model Performance */}
      <div className="section-container">
        <h2>أداء النماذج</h2>
        <ModelPerformance models={metrics?.model_performance || {}} />
      </div>

      {/* Recent Transactions */}
      <div className="section-container">
        <h2>آخر المعاملات</h2>
        <TransactionTable timeRange={timeRange} />
      </div>

      {/* Top Merchants */}
      <div className="top-merchants-container">
        <div className="merchants-card">
          <h2>أكثر التجار احتيالاً</h2>
          <ul className="merchant-list">
            {(metrics?.top_merchants || []).slice(0, 5).map(([merchant, count]) => (
              <li key={merchant}>
                <span className="merchant-name">{merchant}</span>
                <span className="merchant-count">{count}</span>
              </li>
            ))}
          </ul>
        </div>

        <div className="merchants-card">
          <h2>أكثر الفئات احتيالاً</h2>
          <ul className="merchant-list">
            {(metrics?.top_fraud_categories || []).slice(0, 5).map(([category, count]) => (
              <li key={category}>
                <span className="merchant-name">{category}</span>
                <span className="merchant-count">{count}</span>
              </li>
            ))}
          </ul>
        </div>
      </div>

      {/* Geographic Distribution */}
      <div className="section-container">
        <h2>التوزيع الجغرافي للاحتيال</h2>
        <div className="geo-distribution">
          {Object.entries(metrics?.geographic_distribution || {}).map(([location, count]) => (
            <div key={location} className="geo-item">
              <span className="geo-location">{location}</span>
              <div className="geo-bar">
                <div 
                  className="geo-fill" 
                  style={{
                    width: `${(count / Math.max(...Object.values(metrics?.geographic_distribution || {}))) * 100}%`
                  }}
                ></div>
              </div>
              <span className="geo-count">{count}</span>
            </div>
          ))}
        </div>
      </div>

      {/* Footer */}
      <div className="dashboard-footer">
        <p>آخر تحديث: {new Date(currentMetrics.timestamp).toLocaleString('ar-SA')}</p>
        <p>النسخة: 1.0.0 | حالة النظام: ✅ سليم</p>
      </div>
    </div>
  );
};

export default DashboardLayout;
