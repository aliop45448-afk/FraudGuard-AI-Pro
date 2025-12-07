import React, { useState } from 'react';
import axios from 'axios';

const API_BASE_URL = 'https://5000-ieddf2kb511tbc1z3de4d-07ec8a8d.manus-asia.computer/api';

const TransactionAnalysis = () => {
  const [formData, setFormData] = useState({
    transaction_id: '',
    amount: '',
    balance: '',
    location: '',
    device_id: '',
    user_id: '',
    transaction_type: 'شراء',
    merchant_category: 'مطاعم وكافيهات',
    payment_method: 'بطاقة_ائتمان',
    age: '',
  });
  const [analysisResult, setAnalysisResult] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState(null);

  const handleChange = (e) => {
    const { name, value } = e.target;
    setFormData(prev => ({ ...prev, [name]: value }));
  };

  const handleSubmit = async (e) => {
    e.preventDefault();
    setLoading(true);
    setAnalysisResult(null);
    setError(null);

    try {
      const response = await axios.post(`${API_BASE_URL}/analyze`, formData);
      setAnalysisResult(response.data);
    } catch (err) {
      setError('فشل في تحليل المعاملة. تأكد من صحة البيانات وتشغيل الـ API.');
      console.error(err);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (level) => {
    switch (level) {
      case 'عالي': return 'bg-fraud-red text-white';
      case 'متوسط': return 'bg-warning-orange text-white';
      case 'منخفض': return 'bg-safe-green text-white';
      default: return 'bg-gray-400 text-white';
    }
  };

  return (
    <div className="p-4">
      <h1 className="text-3xl font-bold text-gray-800 mb-6">تحليل المعاملات الفوري</h1>
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Form Section */}
        <div className="lg:col-span-1 bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-700 border-b pb-2">إدخال بيانات المعاملة</h2>
          <form onSubmit={handleSubmit} className="space-y-4">
            <InputField label="رقم المعاملة" name="transaction_id" value={formData.transaction_id} onChange={handleChange} placeholder="TXN123456789" required />
            <InputField label="المبلغ (ر.س)" name="amount" type="number" value={formData.amount} onChange={handleChange} placeholder="5000.00" required />
            <InputField label="رصيد الحساب (ر.س)" name="balance" type="number" value={formData.balance} onChange={handleChange} placeholder="25000.00" required />
            <InputField label="الموقع الجغرافي" name="location" value={formData.location} onChange={handleChange} placeholder="الرياض، السعودية" />
            <InputField label="معرف الجهاز" name="device_id" value={formData.device_id} onChange={handleChange} placeholder="DEV123456789" />
            <InputField label="معرف المستخدم" name="user_id" value={formData.user_id} onChange={handleChange} placeholder="USER123456" />
            <InputField label="عمر العميل" name="age" type="number" value={formData.age} onChange={handleChange} placeholder="35" />

            <SelectField label="نوع المعاملة" name="transaction_type" value={formData.transaction_type} onChange={handleChange} options={['شراء', 'سحب_نقدي', 'تحويل_محلي', 'تحويل_دولي', 'دفع_فواتير', 'إيداع']} />
            <SelectField label="فئة التاجر" name="merchant_category" value={formData.merchant_category} onChange={handleChange} options={['مطاعم وكافيهات', 'تسوق ومتاجر', 'وقود ومحطات', 'صحة وطب', 'تعليم وتدريب', 'سفر وسياحة', 'أخرى']} />
            <SelectField label="طريقة الدفع" name="payment_method" value={formData.payment_method} onChange={handleChange} options={['بطاقة_ائتمان', 'بطاقة_خصم', 'تحويل_بنكي', 'محفظة_رقمية', 'نقد']} />

            <button
              type="submit"
              className="w-full bg-primary-blue text-white p-3 rounded-lg font-semibold hover:bg-blue-600 transition-colors duration-200 disabled:bg-gray-400"
              disabled={loading}
            >
              {loading ? 'جاري التحليل...' : '🔍 فحص شامل للمعاملة'}
            </button>
          </form>
        </div>

        {/* Results Section */}
        <div className="lg:col-span-2 bg-white p-6 rounded-lg shadow-lg">
          <h2 className="text-xl font-semibold mb-4 text-gray-700 border-b pb-2">نتائج التحليل</h2>
          {error && <div className="p-4 mb-4 bg-red-100 text-fraud-red rounded-lg">{error}</div>}
          
          {analysisResult ? (
            <div className="space-y-6">
              {/* Summary Card */}
              <div className={`p-6 rounded-lg shadow-md ${getRiskColor(analysisResult.risk_level)}`}>
                <h3 className="text-2xl font-bold mb-2">مستوى المخاطر: {analysisResult.risk_level}</h3>
                <p className="text-lg">نقاط المخاطر: {analysisResult.risk_score} / 100</p>
                <p className="text-lg">احتمالية الاحتيال: {analysisResult.fraud_probability}%</p>
              </div>

              {/* Recommendation */}
              <div className="p-4 bg-gray-100 rounded-lg">
                <h4 className="text-lg font-semibold mb-2 text-gray-700">التوصية:</h4>
                <p className={`text-xl font-bold ${analysisResult.recommendation.color === 'red' ? 'text-fraud-red' : analysisResult.recommendation.color === 'orange' ? 'text-warning-orange' : 'text-safe-green'}`}>
                  {analysisResult.recommendation.message}
                </p>
              </div>

              {/* Risk Factors */}
              <div>
                <h4 className="text-lg font-semibold mb-2 text-gray-700">عوامل المخاطر المكتشفة:</h4>
                {analysisResult.risk_factors.length > 0 ? (
                  <ul className="list-disc list-inside space-y-1">
                    {analysisResult.risk_factors.map((factor, index) => (
                      <li key={index} className={`text-sm ${factor.severity === 'عالي' ? 'text-fraud-red' : 'text-warning-orange'}`}>
                        <span className="font-semibold">{factor.factor} ({factor.severity}):</span> {factor.description}
                      </li>
                    ))}
                  </ul>
                ) : (
                  <p className="text-sm text-safe-green">لم يتم اكتشاف عوامل مخاطر عالية.</p>
                )}
              </div>

              {/* Model Details */}
              <div>
                <h4 className="text-lg font-semibold mb-2 text-gray-700">تفاصيل نماذج الذكاء الاصطناعي:</h4>
                <div className="grid grid-cols-3 gap-4 text-sm">
                  <ModelCard name="Random Forest" proba={analysisResult.model_predictions.random_forest.probability} prediction={analysisResult.model_predictions.random_forest.prediction} />
                  <ModelCard name="Gradient Boosting" proba={analysisResult.model_predictions.gradient_boosting.probability} prediction={analysisResult.model_predictions.gradient_boosting.prediction} />
                  <ModelCard name="Isolation Forest" isAnomaly={analysisResult.model_predictions.isolation_forest.is_anomaly} score={analysisResult.model_predictions.isolation_forest.anomaly_score} />
                </div>
                <p className="mt-2 text-xs text-gray-500">ثقة النظام في القرار: {analysisResult.confidence}%</p>
              </div>
            </div>
          ) : (
            <div className="text-center p-10 text-gray-500">
              <p className="text-lg">أدخل بيانات المعاملة أعلاه واضغط على "فحص شامل للمعاملة" لبدء التحليل.</p>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

const InputField = ({ label, name, value, onChange, placeholder, type = 'text', required = false }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1">{label} {required && '*'}</label>
    <input
      type={type}
      name={name}
      value={value}
      onChange={onChange}
      placeholder={placeholder}
      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-primary-blue focus:border-primary-blue"
      required={required}
    />
  </div>
);

const SelectField = ({ label, name, value, onChange, options }) => (
  <div>
    <label className="block text-sm font-medium text-gray-700 mb-1">{label} *</label>
    <select
      name={name}
      value={value}
      onChange={onChange}
      className="w-full p-2 border border-gray-300 rounded-lg focus:ring-primary-blue focus:border-primary-blue"
      required
    >
      {options.map(option => (
        <option key={option} value={option}>{option.replace(/_/g, ' ')}</option>
      ))}
    </select>
  </div>
);

const ModelCard = ({ name, proba, prediction, isAnomaly, score }) => (
  <div className="p-3 border rounded-lg shadow-sm">
    <p className="font-semibold text-primary-blue">{name}</p>
    {name !== 'Isolation Forest' ? (
      <>
        <p>احتمالية الاحتيال: {proba}%</p>
        <p className={`font-bold ${prediction ? 'text-fraud-red' : 'text-safe-green'}`}>
          {prediction ? 'احتيال' : 'آمن'}
        </p>
      </>
    ) : (
      <>
        <p>درجة الشذوذ: {score}</p>
        <p className={`font-bold ${isAnomaly ? 'text-fraud-red' : 'text-safe-green'}`}>
          {isAnomaly ? 'شاذ (Anomaly)' : 'طبيعي'}
        </p>
      </>
    )}
  </div>
);

export default TransactionAnalysis;
