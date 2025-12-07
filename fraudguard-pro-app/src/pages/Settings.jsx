import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://5000-ieddf2kb511tbc1z3de4d-07ec8a8d.manus-asia.computer/api';

const Settings = () => {
  const [demoCount, setDemoCount] = useState(100);
  const [message, setMessage] = useState('');
  const [loading, setLoading] = useState(false);

  const handleGenerateDemoData = async () => {
    setLoading(true);
    setMessage('');
    try {
      const response = await axios.post(`${API_BASE_URL}/generate-demo-data`, { count: demoCount });
      setMessage(`✅ ${response.data.message}`);
    } catch (err) {
      setMessage(`❌ فشل في توليد البيانات: ${err.response?.data?.error || err.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">إعدادات النظام</h1>
      
      <div className="bg-white p-6 rounded-lg shadow-lg mb-8">
        <h2 className="text-xl font-semibold mb-4 text-gray-700 border-b pb-2">إدارة البيانات التجريبية</h2>
        <p className="text-gray-600 mb-4">يمكنك توليد بيانات معاملات اصطناعية لاختبار لوحات التحكم ونماذج الذكاء الاصطناعي.</p>
        
        <div className="flex items-center space-x-4 space-x-reverse">
          <input
            type="number"
            value={demoCount}
            onChange={(e) => setDemoCount(parseInt(e.target.value))}
            min="1"
            className="w-32 p-2 border border-gray-300 rounded-lg focus:ring-primary-blue focus:border-primary-blue"
          />
          <button
            onClick={handleGenerateDemoData}
            className="bg-safe-green text-white p-2 rounded-lg font-semibold hover:bg-green-600 transition-colors duration-200 disabled:bg-gray-400"
            disabled={loading}
          >
            {loading ? 'جاري التوليد...' : `توليد ${demoCount} معاملة`}
          </button>
        </div>
        
        {message && (
          <p className={`mt-4 font-semibold ${message.startsWith('✅') ? 'text-safe-green' : 'text-fraud-red'}`}>
            {message}
          </p>
        )}
      </div>

      <div className="bg-white p-6 rounded-lg shadow-lg">
        <h2 className="text-xl font-semibold mb-4 text-gray-700 border-b pb-2">معلومات النظام</h2>
        <div className="space-y-2 text-gray-600">
          <p><span className="font-semibold ml-2">إصدار الواجهة الأمامية:</span> 2.0.0 Enterprise</p>
          <p><span className="font-semibold ml-2">إصدار الـ API:</span> 2.0.0</p>
          <p><span className="font-semibold ml-2">حالة محرك ML:</span> نشط (3 نماذج)</p>
          <p><span className="font-semibold ml-2">قاعدة البيانات:</span> SQLite (fraudguard.db)</p>
        </div>
      </div>
    </div>
  );
};

export default Settings;
