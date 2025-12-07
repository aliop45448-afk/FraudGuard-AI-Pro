import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar } from 'react-chartjs-2';

const API_BASE_URL = 'https://5000-ieddf2kb511tbc1z3de4d-07ec8a8d.manus-asia.computer/api';

const Reports = () => {
  const [stats, setStats] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [period, setPeriod] = useState('today');

  useEffect(() => {
    fetchStatistics(period);
  }, [period]);

  const fetchStatistics = async (selectedPeriod) => {
    setLoading(true);
    setError(null);
    try {
      const response = await axios.get(`${API_BASE_URL}/statistics?period=${selectedPeriod}`);
      setStats(response.data);
      setLoading(false);
    } catch (err) {
      setError('فشل في جلب الإحصائيات. تأكد من تشغيل الـ API.');
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center text-xl p-10">جاري تحميل التقارير...</div>;
  if (error) return <div className="text-center text-xl p-10 text-fraud-red">{error}</div>;

  const { summary, risk_distribution, recent_alerts } = stats;

  // Chart Data for Risk Distribution
  const riskLabels = Object.keys(risk_distribution);
  const riskData = Object.values(risk_distribution);
  const riskChartData = {
    labels: riskLabels,
    datasets: [
      {
        label: 'توزيع المعاملات حسب مستوى المخاطر',
        data: riskData,
        backgroundColor: riskLabels.map(label => {
          if (label === 'عالي') return '#E74C3C';
          if (label === 'متوسط') return '#F39C12';
          if (label === 'منخفض') return '#2ECC71';
          return '#3498DB';
        }),
      },
    ],
  };

  const riskChartOptions = {
    responsive: true,
    plugins: {
      title: {
        display: true,
        text: 'توزيع المخاطر',
        font: { family: 'Cairo', size: 16 }
      },
      legend: {
        labels: { font: { family: 'Cairo' } }
      }
    },
    scales: {
      y: {
        beginAtZero: true,
        title: { display: true, text: 'عدد المعاملات', font: { family: 'Cairo' } }
      },
      x: {
        ticks: { font: { family: 'Cairo' } }
      }
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">التقارير والإحصائيات المتقدمة</h1>
      
      {/* Period Selector */}
      <div className="mb-6 flex space-x-4 space-x-reverse">
        {['today', 'week', 'month', 'all'].map(p => (
          <button
            key={p}
            onClick={() => setPeriod(p)}
            className={`p-2 rounded-lg font-semibold transition-colors ${period === p ? 'bg-primary-blue text-white' : 'bg-gray-200 text-gray-700 hover:bg-gray-300'}`}
          >
            {p === 'today' ? 'اليوم' : p === 'week' ? 'آخر 7 أيام' : p === 'month' ? 'آخر 30 يوم' : 'الكل'}
          </button>
        ))}
      </div>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-6 mb-8">
        <StatCard title="إجمالي المعاملات" value={summary.total_transactions.toLocaleString()} icon="🔢" color="primary-blue" />
        <StatCard title="احتيال مكتشف" value={summary.fraud_detected.toLocaleString()} icon="🚨" color="fraud-red" />
        <StatCard title="معدل الاحتيال" value={`${summary.fraud_rate}%`} icon="📉" color="warning-orange" />
        <StatCard title="الأموال المحمية" value={`${summary.protected_amount.toLocaleString()} ر.س`} icon="🛡️" color="safe-green" />
        <StatCard title="متوسط المخاطر" value={summary.avg_risk_score} icon="⚖️" color="secondary-purple" />
      </div>

      {/* Charts and Details */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-lg">
          <Bar data={riskChartData} options={riskChartOptions} />
        </div>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-gray-700">أهمية الميزات (Random Forest)</h3>
          <FeatureImportance />
        </div>
      </div>

      {/* Recent Alerts */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">أحدث التنبيهات</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">التنبيه</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">المعاملة</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">الخطورة</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">التاريخ</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {recent_alerts.map((alert) => (
                <tr key={alert.id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{alert.message}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-blue">{alert.transaction_id}</td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${alert.severity === 'عالي' ? 'text-fraud-red' : 'text-warning-orange'}`}>
                    {alert.severity}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(alert.timestamp).toLocaleString('ar-SA')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const StatCard = ({ title, value, icon, color }) => (
  <div className={`bg-white p-6 rounded-lg shadow-lg border-b-4 border-${color}`}>
    <div className="flex items-center">
      <div className={`p-3 rounded-full bg-${color} bg-opacity-10 text-${color} ml-4`}>
        <span className="text-2xl">{icon}</span>
      </div>
      <div>
        <p className="text-sm font-medium text-gray-500">{title}</p>
        <p className="text-2xl font-bold text-gray-900 mt-1">{value}</p>
      </div>
    </div>
  </div>
);

const FeatureImportance = () => {
  const [importance, setImportance] = useState(null);
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    const fetchImportance = async () => {
      try {
        const response = await axios.get(`${API_BASE_URL}/feature-importance`);
        setImportance(response.data.top_features);
        setLoading(false);
      } catch (err) {
        console.error('فشل في جلب أهمية الميزات:', err);
        setLoading(false);
      }
    };
    fetchImportance();
  }, []);

  if (loading) return <p className="text-sm text-gray-500">جاري التحميل...</p>;
  if (!importance) return <p className="text-sm text-fraud-red">لا تتوفر بيانات.</p>;

  return (
    <div className="space-y-3">
      {importance.map(([feature, score]) => (
        <div key={feature} className="flex justify-between items-center">
          <span className="text-sm text-gray-700">{feature}</span>
          <div className="w-2/3 bg-gray-200 rounded-full h-2.5">
            <div 
              className="bg-primary-blue h-2.5 rounded-full" 
              style={{ width: `${score * 100}%` }}
            ></div>
          </div>
          <span className="text-xs font-semibold text-gray-600">{Math.round(score * 100)}%</span>
        </div>
      ))}
    </div>
  );
};

export default Reports;
