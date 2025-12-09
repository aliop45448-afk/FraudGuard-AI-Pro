import React from 'react';
import './ModelPerformance.css';

/**
 * ModelPerformance Component
 * 
 * Displays performance metrics for all active fraud detection models
 */
const ModelPerformance = ({ models }) => {
  // Mock model data if not provided
  const mockModels = {
    'rf_v1': {
      average_fraud_probability: 0.45,
      predictions_count: 1250,
      max_probability: 0.98,
      min_probability: 0.02,
    },
    'gb_v1': {
      average_fraud_probability: 0.42,
      predictions_count: 1250,
      max_probability: 0.96,
      min_probability: 0.01,
    },
    'if_v1': {
      average_fraud_probability: 0.48,
      predictions_count: 1250,
      max_probability: 0.99,
      min_probability: 0.03,
    },
  };

  const modelData = Object.keys(models).length > 0 ? models : mockModels;

  const getModelName = (modelId) => {
    const names = {
      'rf_v1': 'Random Forest',
      'gb_v1': 'Gradient Boosting',
      'if_v1': 'Isolation Forest',
      'nn_v1': 'Neural Network',
      'lstm_v1': 'LSTM',
    };
    return names[modelId] || modelId;
  };

  return (
    <div className="model-performance">
      <div className="models-grid">
        {Object.entries(modelData).map(([modelId, metrics]) => (
          <div key={modelId} className="model-card">
            <div className="model-header">
              <h3>{getModelName(modelId)}</h3>
              <span className="model-id">{modelId}</span>
            </div>

            <div className="model-metrics">
              <div className="metric-item">
                <span className="metric-label">متوسط احتمالية الاحتيال</span>
                <span className="metric-value">
                  {(metrics.average_fraud_probability * 100).toFixed(2)}%
                </span>
              </div>

              <div className="metric-item">
                <span className="metric-label">عدد التنبؤات</span>
                <span className="metric-value">
                  {metrics.predictions_count?.toLocaleString() || 'N/A'}
                </span>
              </div>

              <div className="metric-item">
                <span className="metric-label">أقصى احتمالية</span>
                <span className="metric-value">
                  {(metrics.max_probability * 100).toFixed(2)}%
                </span>
              </div>

              <div className="metric-item">
                <span className="metric-label">أدنى احتمالية</span>
                <span className="metric-value">
                  {(metrics.min_probability * 100).toFixed(2)}%
                </span>
              </div>
            </div>

            <div className="model-status">
              <span className="status-badge status-active">✓ نشط</span>
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default ModelPerformance;
