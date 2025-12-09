import React from 'react';
import './MetricsCard.css';

/**
 * MetricsCard Component
 * 
 * Displays a single metric with icon, value, and optional subtext
 */
const MetricsCard = ({ title, value, icon, color, subtext }) => {
  return (
    <div className={`metrics-card metrics-card-${color}`}>
      <div className="card-icon">{icon}</div>
      <div className="card-content">
        <h3 className="card-title">{title}</h3>
        <p className="card-value">{value}</p>
        {subtext && <p className="card-subtext">{subtext}</p>}
      </div>
      <div className="card-accent"></div>
    </div>
  );
};

export default MetricsCard;
