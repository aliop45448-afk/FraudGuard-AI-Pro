import React, { useState, useEffect } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://5000-ieddf2kb511tbc1z3de4d-07ec8a8d.manus-asia.computer/api';

const Alerts = () => {
  const [alerts, setAlerts] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    fetchAlerts();
  }, []);

  const fetchAlerts = async () => {
    try {
      const response = await axios.get(`${API_BASE_URL}/alerts`);
      setAlerts(response.data.alerts);
      setLoading(false);
    } catch (err) {
      setError('فشل في جلب التنبيهات. تأكد من تشغيل الـ API.');
      setLoading(false);
    }
  };

  const markAsRead = async (alertId) => {
    try {
      await axios.put(`${API_BASE_URL}/alerts/${alertId}/read`);
      setAlerts(prevAlerts => prevAlerts.map(alert => 
        alert.id === alertId ? { ...alert, is_read: 1 } : alert
      ));
    } catch (err) {
      console.error('فشل في تحديث حالة التنبيه:', err);
    }
  };

  const getSeverityColor = (severity) => {
    switch (severity) {
      case 'عالي': return 'bg-red-100 text-fraud-red border-fraud-red';
      case 'متوسط': return 'bg-yellow-100 text-warning-orange border-warning-orange';
      case 'منخفض': return 'bg-green-100 text-safe-green border-safe-green';
      default: return 'bg-gray-100 text-gray-700 border-gray-400';
    }
  };

  if (loading) return <div className="text-center text-xl p-10">جاري تحميل التنبيهات...</div>;
  if (error) return <div className="text-center text-xl p-10 text-fraud-red">{error}</div>;

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">مركز التنبيهات</h1>
      <div className="flex justify-between items-center mb-4">
        <p className="text-lg text-gray-600">إجمالي التنبيهات: {alerts.length}</p>
        <button 
          onClick={fetchAlerts} 
          className="bg-primary-blue text-white p-2 rounded-lg text-sm hover:bg-blue-600 transition-colors"
        >
          🔄 تحديث
        </button>
      </div>

      <div className="space-y-4">
        {alerts.length > 0 ? (
          alerts.map((alert) => (
            <div 
              key={alert.id} 
              className={`p-4 rounded-lg border-r-4 shadow-md transition-all ${getSeverityColor(alert.severity)} ${alert.is_read ? 'opacity-60' : 'opacity-100'}`}
            >
              <div className="flex justify-between items-start">
                <div>
                  <p className="font-bold text-lg">{alert.alert_type === 'fraud_detected' ? '🚨 كشف احتيال' : alert.alert_type}</p>
                  <p className="text-sm mt-1">{alert.message}</p>
                  <p className="text-xs mt-2 text-gray-500">
                    <span className="font-semibold ml-2">المعاملة:</span> {alert.transaction_id || 'غير محدد'}
                    <span className="font-semibold ml-2 mr-4">التاريخ:</span> {new Date(alert.timestamp).toLocaleString('ar-SA')}
                  </p>
                </div>
                {!alert.is_read && (
                  <button 
                    onClick={() => markAsRead(alert.id)}
                    className="bg-white text-primary-blue border border-primary-blue p-2 rounded-lg text-xs hover:bg-gray-50 transition-colors flex-shrink-0"
                  >
                    ✔ تم القراءة
                  </button>
                )}
              </div>
            </div>
          ))
        ) : (
          <div className="text-center p-10 bg-white rounded-lg shadow-lg text-gray-500">
            <p className="text-xl">لا توجد تنبيهات حالياً. النظام يعمل بأمان.</p>
          </div>
        )}
      </div>
    </div>
  );
};

export default Alerts;
