import React, { useState, useEffect } from 'react';
import axios from 'axios';
import { Bar, Line, Doughnut } from 'react-chartjs-2';

const API_BASE_URL = 'https://5000-ieddf2kb511tbc1z3de4d-07ec8a8d.manus-asia.computer/api';

const Dashboard = () => {
  const [data, setData] = useState(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchDashboardData();
  }, []);

  const fetchDashboardData = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/dashboard`);
      setData(response.data);
      setLoading(false);
    } catch (err) {
      setError('فشل في جلب بيانات لوحة التحكم. تأكد من تشغيل الـ API.');
      setLoading(false);
    }
  };

  if (loading) return <div className="text-center text-xl p-10">جاري تحميل البيانات...</div>;
  if (error) return <div className="text-center text-xl p-10 text-fraud-red">{error}</div>;

  const { today, trend, type_distribution, high_risk_transactions, system_health } = data;

  // Chart Data
  const trendChartData = {
    labels: trend.map(item => item.date),
    datasets: [
      {
        label: 'إجمالي المعاملات',
        data: trend.map(item => item.total),
        borderColor: '#4A90E2',
        backgroundColor: 'rgba(74, 144, 226, 0.5)',
        yAxisID: 'y',
      },
      {
        label: 'احتيال مكتشف',
        data: trend.map(item => item.fraud),
        borderColor: '#E74C3C',
        backgroundColor: 'rgba(231, 76, 60, 0.5)',
        yAxisID: 'y1',
      },
    ],
  };

  const typeDistributionData = {
    labels: type_distribution.map(item => item.type),
    datasets: [
      {
        label: 'عدد المعاملات',
        data: type_distribution.map(item => item.count),
        backgroundColor: ['#4A90E2', '#A569BD', '#2ECC71', '#F39C12', '#3498DB'],
        hoverOffset: 4,
      },
    ],
  };

  const trendChartOptions = {
    responsive: true,
    interaction: {
      mode: 'index',
      intersect: false,
    },
    stacked: false,
    plugins: {
      title: {
        display: true,
        text: 'اتجاه المعاملات والاحتيال (آخر 7 أيام)',
        font: { family: 'Cairo', size: 16 }
      },
    },
    scales: {
      y: {
        type: 'linear',
        display: true,
        position: 'left',
        title: { display: true, text: 'إجمالي المعاملات', font: { family: 'Cairo' } }
      },
      y1: {
        type: 'linear',
        display: true,
        position: 'right',
        grid: { drawOnChartArea: false },
        title: { display: true, text: 'احتيال مكتشف', font: { family: 'Cairo' } }
      },
      x: {
        ticks: { font: { family: 'Cairo' } }
      }
    },
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">لوحة التحكم الرئيسية</h1>

      {/* Summary Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
        <Card title="إجمالي المعاملات اليوم" value={today.total_transactions} icon="📈" color="primary-blue" />
        <Card title="احتيال مكتشف اليوم" value={today.fraud_detected} icon="🚨" color="fraud-red" />
        <Card title="إجمالي المبلغ اليوم" value={`${today.total_amount.toLocaleString()} ر.س`} icon="💰" color="safe-green" />
        <Card title="صحة النظام" value={system_health.status === 'operational' ? 'يعمل' : 'مشكلة'} icon="✅" color={system_health.status === 'operational' ? 'safe-green' : 'fraud-red'} />
      </div>

      {/* Charts Section */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6 mb-8">
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-lg">
          <Line options={trendChartOptions} data={trendChartData} />
        </div>
        <div className="bg-white p-6 rounded-lg shadow-lg">
          <h3 className="text-xl font-semibold mb-4 text-gray-700">توزيع أنواع المعاملات</h3>
          <Doughnut data={typeDistributionData} options={{ responsive: true, plugins: { legend: { position: 'right', labels: { font: { family: 'Cairo' } } } } }} />
        </div>
      </div>

      {/* High Risk Transactions Table */}
      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h3 className="text-xl font-semibold mb-4 text-gray-700">أعلى المعاملات خطورة (آخر 10)</h3>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-gray-200">
            <thead className="bg-gray-50">
              <tr>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">رقم المعاملة</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">المبلغ (ر.س)</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">نقاط المخاطر</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">مستوى المخاطر</th>
                <th className="px-6 py-3 text-xs font-medium text-gray-500 uppercase tracking-wider">التاريخ</th>
              </tr>
            </thead>
            <tbody className="bg-white divide-y divide-gray-200">
              {high_risk_transactions.map((tx) => (
                <tr key={tx.transaction_id}>
                  <td className="px-6 py-4 whitespace-nowrap text-sm font-medium text-primary-blue">{tx.transaction_id}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{tx.amount.toLocaleString()}</td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{tx.risk_score}</td>
                  <td className={`px-6 py-4 whitespace-nowrap text-sm font-semibold ${tx.risk_level === 'عالي' ? 'text-fraud-red' : 'text-warning-orange'}`}>
                    {tx.risk_level}
                  </td>
                  <td className="px-6 py-4 whitespace-nowrap text-sm text-gray-500">{new Date(tx.timestamp).toLocaleString('ar-SA')}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

const Card = ({ title, value, icon, color }) => (
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

export default Dashboard;
