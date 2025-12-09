import React, { useState, useEffect } from 'react';
import './TransactionTable.css';

/**
 * TransactionTable Component
 * 
 * Displays recent transactions with fraud detection results
 */
const TransactionTable = ({ timeRange }) => {
  const [transactions, setTransactions] = useState([]);
  const [loading, setLoading] = useState(true);
  const [sortBy, setSortBy] = useState('timestamp');
  const [filterRisk, setFilterRisk] = useState('all');

  useEffect(() => {
    // Fetch transactions from API
    const fetchTransactions = async () => {
      try {
        setLoading(true);
        // Mock data for now
        const mockTransactions = generateMockTransactions();
        setTransactions(mockTransactions);
      } catch (error) {
        console.error('Error fetching transactions:', error);
      } finally {
        setLoading(false);
      }
    };

    fetchTransactions();
  }, [timeRange]);

  const generateMockTransactions = () => {
    const merchants = ['Amazon', 'Walmart', 'Target', 'Best Buy', 'Apple Store'];
    const categories = ['Electronics', 'Retail', 'Groceries', 'Restaurants', 'Travel'];
    const locations = ['New York', 'Los Angeles', 'Chicago', 'Houston', 'Phoenix'];

    return Array.from({ length: 10 }, (_, i) => ({
      id: `TXN_${String(i + 1).padStart(5, '0')}`,
      merchant: merchants[Math.floor(Math.random() * merchants.length)],
      category: categories[Math.floor(Math.random() * categories.length)],
      amount: (Math.random() * 5000 + 10).toFixed(2),
      location: locations[Math.floor(Math.random() * locations.length)],
      fraudProbability: Math.random(),
      riskScore: Math.random() * 100,
      isFlagged: Math.random() > 0.7,
      recommendation: ['APPROVE', 'BLOCK', 'REVIEW', 'CHALLENGE'][Math.floor(Math.random() * 4)],
      timestamp: new Date(Date.now() - Math.random() * 24 * 60 * 60 * 1000).toLocaleString('ar-SA'),
    }));
  };

  const getRiskLevel = (score) => {
    if (score >= 80) return { label: 'خطر عالي جداً', class: 'risk-critical' };
    if (score >= 60) return { label: 'خطر عالي', class: 'risk-high' };
    if (score >= 40) return { label: 'خطر متوسط', class: 'risk-medium' };
    if (score >= 20) return { label: 'خطر منخفض', class: 'risk-low' };
    return { label: 'آمن', class: 'risk-safe' };
  };

  const getRecommendationIcon = (recommendation) => {
    const icons = {
      'APPROVE': '✓',
      'BLOCK': '✕',
      'REVIEW': '?',
      'CHALLENGE': '!',
    };
    return icons[recommendation] || '?';
  };

  let filteredTransactions = transactions;
  if (filterRisk !== 'all') {
    filteredTransactions = transactions.filter(t => {
      const risk = getRiskLevel(t.riskScore).class;
      return risk === filterRisk;
    });
  }

  if (loading) {
    return <div className="table-loading">جاري تحميل المعاملات...</div>;
  }

  return (
    <div className="transaction-table-container">
      <div className="table-controls">
        <select 
          value={filterRisk}
          onChange={(e) => setFilterRisk(e.target.value)}
          className="filter-select"
        >
          <option value="all">جميع المعاملات</option>
          <option value="risk-critical">خطر عالي جداً</option>
          <option value="risk-high">خطر عالي</option>
          <option value="risk-medium">خطر متوسط</option>
          <option value="risk-low">خطر منخفض</option>
          <option value="risk-safe">آمن</option>
        </select>
      </div>

      <div className="table-wrapper">
        <table className="transaction-table">
          <thead>
            <tr>
              <th>معرف المعاملة</th>
              <th>التاجر</th>
              <th>الفئة</th>
              <th>المبلغ</th>
              <th>الموقع</th>
              <th>احتمالية الاحتيال</th>
              <th>درجة المخاطر</th>
              <th>التوصية</th>
              <th>الوقت</th>
            </tr>
          </thead>
          <tbody>
            {filteredTransactions.map((txn) => {
              const riskLevel = getRiskLevel(txn.riskScore);
              return (
                <tr key={txn.id} className={txn.isFlagged ? 'row-flagged' : ''}>
                  <td className="txn-id">{txn.id}</td>
                  <td>{txn.merchant}</td>
                  <td>{txn.category}</td>
                  <td className="amount">${txn.amount}</td>
                  <td>{txn.location}</td>
                  <td className="probability">
                    {(txn.fraudProbability * 100).toFixed(2)}%
                  </td>
                  <td>
                    <span className={`risk-badge ${riskLevel.class}`}>
                      {riskLevel.label}
                    </span>
                  </td>
                  <td>
                    <span className={`recommendation-badge rec-${txn.recommendation.toLowerCase()}`}>
                      {getRecommendationIcon(txn.recommendation)} {txn.recommendation}
                    </span>
                  </td>
                  <td className="timestamp">{txn.timestamp}</td>
                </tr>
              );
            })}
          </tbody>
        </table>
      </div>

      <div className="table-footer">
        <p>عدد المعاملات المعروضة: {filteredTransactions.length} من {transactions.length}</p>
      </div>
    </div>
  );
};

export default TransactionTable;
