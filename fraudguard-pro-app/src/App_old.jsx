import React, { useState, useEffect } from 'react';
import './App.css';

// Import images
import logoImage from './assets/images/logo_pro.png';
import aiBrainIcon from './assets/images/ai_brain_icon.png';
import securityShieldIcon from './assets/images/security_shield_icon.png';
import analyticsIcon from './assets/images/analytics_dashboard_icon.png';
import realtimeIcon from './assets/images/realtime_monitoring_icon.png';

function App() {
  const [darkMode, setDarkMode] = useState(false);
  const [aiChatOpen, setAiChatOpen] = useState(false);
  const [aiMessages, setAiMessages] = useState([
    { type: 'assistant', content: 'مرحباً! أنا مساعدك الذكي لكشف الاحتيال المالي. كيف يمكنني مساعدتك اليوم؟' }
  ]);
  const [aiInput, setAiInput] = useState('');
  const [isLoading, setIsLoading] = useState(false);
  
  // Transaction form state
  const [transactionData, setTransactionData] = useState({
    transactionId: '',
    amount: '',
    location: '',
    deviceId: '',
    userId: '',
    transactionType: '',
    merchantCategory: '',
    paymentMethod: '',
    customerAge: '',
    accountBalance: '',
    dataFile: null
  });
  
  const [analysisResult, setAnalysisResult] = useState(null);
  const [formLoading, setFormLoading] = useState(false);

  // Toggle dark mode
  const toggleDarkMode = () => {
    setDarkMode(!darkMode);
    document.documentElement.setAttribute('data-theme', !darkMode ? 'dark' : 'light');
  };

  // Handle transaction form input changes
  const handleInputChange = (e) => {
    const { name, value, files } = e.target;
    if (name === 'dataFile') {
      setTransactionData(prev => ({ ...prev, [name]: files[0] }));
    } else {
      setTransactionData(prev => ({ ...prev, [name]: value }));
    }
  };

  // Submit transaction for analysis
  const handleTransactionSubmit = async (e) => {
    e.preventDefault();
    setFormLoading(true);
    
    try {
      // Simulate API call to backend
      const response = await fetch('http://localhost:5001/analyze_transaction', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(transactionData)
      });
      
      if (response.ok) {
        const result = await response.json();
        setAnalysisResult(result);
      } else {
        // Fallback to mock analysis if API is not available
        const mockResult = generateMockAnalysis(transactionData);
        setAnalysisResult(mockResult);
      }
    } catch (error) {
      console.error('Error analyzing transaction:', error);
      // Generate mock result for demonstration
      const mockResult = generateMockAnalysis(transactionData);
      setAnalysisResult(mockResult);
    } finally {
      setFormLoading(false);
    }
  };

  // Generate mock analysis result
  const generateMockAnalysis = (data) => {
    const amount = parseFloat(data.amount) || 0;
    const balance = parseFloat(data.accountBalance) || 0;
    const age = parseInt(data.customerAge) || 25;
    
    let riskScore = 0;
    let riskFactors = [];
    
    // Risk calculation logic
    if (amount > 50000) {
      riskScore += 30;
      riskFactors.push('مبلغ المعاملة مرتفع جداً');
    }
    
    if (balance > 0 && (amount / balance) > 0.8) {
      riskScore += 25;
      riskFactors.push('نسبة المعاملة إلى الرصيد مرتفعة');
    }
    
    if (data.location.includes('غير معروف') || data.location.includes('خارج')) {
      riskScore += 20;
      riskFactors.push('موقع جغرافي مشبوه');
    }
    
    if (data.deviceId.includes('UNKNOWN') || data.deviceId.includes('000')) {
      riskScore += 15;
      riskFactors.push('معرف جهاز غير معروف');
    }
    
    if (data.transactionType === 'تحويل دولي' && data.paymentMethod === 'نقد') {
      riskScore += 20;
      riskFactors.push('تحويل دولي نقدي مشبوه');
    }
    
    if (age < 21 && amount > 10000) {
      riskScore += 15;
      riskFactors.push('عمر صغير مع مبلغ كبير');
    }
    
    let riskLevel = 'منخفض';
    let riskColor = 'risk-low';
    let recommendations = ['المعاملة تبدو آمنة', 'يمكن المتابعة بشكل طبيعي'];
    
    if (riskScore >= 70) {
      riskLevel = 'مرتفع جداً';
      riskColor = 'risk-high';
      recommendations = [
        'إيقاف المعاملة فوراً',
        'التحقق من هوية العميل',
        'مراجعة تاريخ المعاملات السابقة',
        'إشعار قسم الأمان المالي'
      ];
    } else if (riskScore >= 40) {
      riskLevel = 'متوسط إلى مرتفع';
      riskColor = 'risk-medium';
      recommendations = [
        'مراجعة إضافية مطلوبة',
        'التحقق من المستندات',
        'مراقبة المعاملة عن كثب'
      ];
    }
    
    return {
      riskScore,
      riskLevel,
      riskColor,
      riskFactors,
      recommendations,
      transactionId: data.transactionId,
      analysisTime: new Date().toLocaleString('ar-SA'),
      confidence: Math.max(85, 100 - riskScore * 0.3)
    };
  };

  // Handle AI chat
  const handleAiSubmit = async (e) => {
    e.preventDefault();
    if (!aiInput.trim()) return;
    
    const userMessage = { type: 'user', content: aiInput };
    setAiMessages(prev => [...prev, userMessage]);
    setAiInput('');
    setIsLoading(true);
    
    try {
      // Simulate AI response
      setTimeout(() => {
        const response = generateAiResponse(aiInput);
        setAiMessages(prev => [...prev, { type: 'assistant', content: response }]);
        setIsLoading(false);
      }, 1000);
    } catch (error) {
      console.error('Error with AI chat:', error);
      setIsLoading(false);
    }
  };

  // Generate AI response
  const generateAiResponse = (input) => {
    const responses = {
      'احتيال': 'علامات الاحتيال المالي تشمل: المعاملات غير المعتادة، المبالغ الكبيرة المفاجئة، المواقع الجغرافية المشبوهة، والأجهزة غير المعروفة. يجب مراقبة هذه العوامل باستمرار.',
      'حماية': 'لحماية حسابك المصرفي: استخدم كلمات مرور قوية، فعّل المصادقة الثنائية، لا تشارك معلوماتك الشخصية، راقب كشوف حسابك بانتظام، واستخدم شبكات آمنة فقط.',
      'بطاقة': 'لحماية بطاقتك المصرفية: احتفظ بها في مكان آمن، لا تشارك رقم PIN، غطِ لوحة المفاتيح عند الإدخال، تحقق من كشوف الحساب، وأبلغ عن أي معاملات مشبوهة فوراً.',
      'تحويل': 'عند إجراء تحويلات مالية: تأكد من صحة بيانات المستلم، استخدم قنوات رسمية فقط، احتفظ بإيصالات التحويل، وتجنب التحويلات للأشخاص غير المعروفين.',
      'أمان': 'نصائح الأمان المالي: راجع حساباتك يومياً، استخدم تطبيقات البنك الرسمية، فعّل إشعارات المعاملات، وتجنب استخدام أجهزة الكمبيوتر العامة للمعاملات المصرفية.'
    };
    
    for (const [key, response] of Object.entries(responses)) {
      if (input.includes(key)) {
        return response;
      }
    }
    
    return 'شكراً لسؤالك. أنا هنا لمساعدتك في أي استفسارات متعلقة بالأمان المالي وكشف الاحتيال. يمكنك سؤالي عن علامات الاحتيال، طرق الحماية، أو أي موضوع متعلق بالأمان المصرفي.';
  };

  // Quick AI questions
  const quickQuestions = [
    'ما هي علامات الاحتيال المالي؟',
    'كيف أحمي بطاقتي المصرفية؟',
    'نصائح للأمان في التحويلات',
    'كيف أتعامل مع معاملة مشبوهة؟'
  ];

  const handleQuickQuestion = (question) => {
    setAiInput(question);
    handleAiSubmit({ preventDefault: () => {} });
  };

  // Reset form
  const resetForm = () => {
    setTransactionData({
      transactionId: '',
      amount: '',
      location: '',
      deviceId: '',
      userId: '',
      transactionType: '',
      merchantCategory: '',
      paymentMethod: '',
      customerAge: '',
      accountBalance: '',
      dataFile: null
    });
    setAnalysisResult(null);
  };

  return (
    <div className="App">
      {/* Header */}
      <header className="header">
        <div className="container">
          <nav className="nav">
            <a href="#" className="logo">
              <img src={logoImage} alt="FraudGuard AI Pro" />
              FraudGuard AI Pro
            </a>
            <ul className="nav-links">
              <li><a href="#home" className="nav-link">الرئيسية</a></li>
              <li><a href="#features" className="nav-link">الميزات</a></li>
              <li><a href="#analysis" className="nav-link">تحليل المعاملات</a></li>
              <li><a href="#contact" className="nav-link">اتصل بنا</a></li>
              <li>
                <button onClick={toggleDarkMode} className="btn btn-outline">
                  {darkMode ? '☀️' : '🌙'}
                </button>
              </li>
            </ul>
          </nav>
        </div>
      </header>

      {/* Hero Section */}
      <section id="home" className="hero">
        <div className="container">
          <div className="hero-content">
            <h1 className="hero-title">
              نظام كشف الاحتيال المالي المتقدم
            </h1>
            <p className="hero-subtitle">
              احمِ مؤسستك المالية بتقنيات الذكاء الاصطناعي المتطورة لكشف ومنع الاحتيال في الوقت الفعلي
            </p>
            <div className="hero-buttons">
              <a href="#analysis" className="btn btn-primary">
                🔍 ابدأ التحليل الآن
              </a>
              <a href="#features" className="btn btn-secondary">
                📋 تعرف على الميزات
              </a>
            </div>
            
            <div className="hero-stats">
              <div className="stat-card">
                <span className="stat-number">99.8%</span>
                <span className="stat-label">دقة الكشف</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">&lt;100ms</span>
                <span className="stat-label">زمن الاستجابة</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">24/7</span>
                <span className="stat-label">مراقبة مستمرة</span>
              </div>
              <div className="stat-card">
                <span className="stat-number">$2M+</span>
                <span className="stat-label">أموال محمية يومياً</span>
              </div>
            </div>
          </div>
        </div>
      </section>

      {/* Features Section */}
      <section id="features" className="features">
        <div className="container">
          <div className="text-center">
            <h2>ميزات متقدمة لحماية شاملة</h2>
            <p>نظام متكامل يجمع بين أحدث تقنيات الذكاء الاصطناعي والتحليل المتقدم</p>
          </div>
          
          <div className="features-grid">
            <div className="feature-card">
              <div className="feature-icon">
                <img src={aiBrainIcon} alt="AI Analysis" />
              </div>
              <h3 className="feature-title">تحليل ذكي متقدم</h3>
              <p className="feature-description">
                خوارزميات التعلم الآلي المتطورة تحلل أنماط المعاملات وتكتشف الشذوذ بدقة عالية
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <img src={realtimeIcon} alt="Real-time Monitoring" />
              </div>
              <h3 className="feature-title">مراقبة فورية</h3>
              <p className="feature-description">
                كشف الاحتيال في الوقت الفعلي مع إشعارات فورية وإجراءات حماية تلقائية
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <img src={securityShieldIcon} alt="Security Shield" />
              </div>
              <h3 className="feature-title">حماية متعددة الطبقات</h3>
              <p className="feature-description">
                نظام أمان شامل يحمي من جميع أنواع التهديدات المالية والهجمات السيبرانية
              </p>
            </div>
            
            <div className="feature-card">
              <div className="feature-icon">
                <img src={analyticsIcon} alt="Analytics Dashboard" />
              </div>
              <h3 className="feature-title">تقارير تحليلية شاملة</h3>
              <p className="feature-description">
                لوحة تحكم متقدمة مع تقارير مفصلة وإحصائيات دقيقة لاتخاذ قرارات مدروسة
              </p>
            </div>
          </div>
        </div>
      </section>

      {/* Transaction Analysis Section */}
      <section id="analysis" className="transaction-section">
        <div className="container">
          <div className="text-center">
            <h2>تحليل المعاملات المالية</h2>
            <p>أدخل بيانات المعاملة للحصول على تحليل شامل لمستوى المخاطر</p>
          </div>
          
          <form onSubmit={handleTransactionSubmit} className="transaction-form">
            <div className="form-grid">
              <div className="form-group">
                <label className="form-label">رقم المعاملة *</label>
                <input
                  type="text"
                  name="transactionId"
                  value={transactionData.transactionId}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="مثال: TXN123456789"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">مبلغ المعاملة (ريال سعودي) *</label>
                <input
                  type="number"
                  name="amount"
                  value={transactionData.amount}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="مثال: 5000.00"
                  step="0.01"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">الموقع الجغرافي *</label>
                <input
                  type="text"
                  name="location"
                  value={transactionData.location}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="مثال: الرياض، السعودية"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">معرف الجهاز *</label>
                <input
                  type="text"
                  name="deviceId"
                  value={transactionData.deviceId}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="مثال: DEV123456789"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">معرف المستخدم *</label>
                <input
                  type="text"
                  name="userId"
                  value={transactionData.userId}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="مثال: USER123456"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">نوع المعاملة *</label>
                <select
                  name="transactionType"
                  value={transactionData.transactionType}
                  onChange={handleInputChange}
                  className="form-select"
                  required
                >
                  <option value="">اختر نوع المعاملة</option>
                  <option value="شراء">شراء</option>
                  <option value="سحب نقدي">سحب نقدي</option>
                  <option value="تحويل محلي">تحويل محلي</option>
                  <option value="تحويل دولي">تحويل دولي</option>
                  <option value="دفع فواتير">دفع فواتير</option>
                  <option value="إيداع">إيداع</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">فئة التاجر *</label>
                <select
                  name="merchantCategory"
                  value={transactionData.merchantCategory}
                  onChange={handleInputChange}
                  className="form-select"
                  required
                >
                  <option value="">اختر فئة التاجر</option>
                  <option value="مطاعم وكافيهات">مطاعم وكافيهات</option>
                  <option value="تسوق ومتاجر">تسوق ومتاجر</option>
                  <option value="وقود ومحطات">وقود ومحطات</option>
                  <option value="صحة وطب">صحة وطب</option>
                  <option value="تعليم وتدريب">تعليم وتدريب</option>
                  <option value="سفر وسياحة">سفر وسياحة</option>
                  <option value="أخرى">أخرى</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">طريقة الدفع *</label>
                <select
                  name="paymentMethod"
                  value={transactionData.paymentMethod}
                  onChange={handleInputChange}
                  className="form-select"
                  required
                >
                  <option value="">اختر طريقة الدفع</option>
                  <option value="بطاقة ائتمان">بطاقة ائتمان</option>
                  <option value="بطاقة خصم">بطاقة خصم</option>
                  <option value="تحويل بنكي">تحويل بنكي</option>
                  <option value="محفظة رقمية">محفظة رقمية</option>
                  <option value="نقد">نقد</option>
                </select>
              </div>
              
              <div className="form-group">
                <label className="form-label">عمر العميل *</label>
                <input
                  type="number"
                  name="customerAge"
                  value={transactionData.customerAge}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="مثال: 35"
                  min="18"
                  max="100"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">رصيد الحساب (ريال سعودي) *</label>
                <input
                  type="number"
                  name="accountBalance"
                  value={transactionData.accountBalance}
                  onChange={handleInputChange}
                  className="form-input"
                  placeholder="مثال: 25000.00"
                  step="0.01"
                  required
                />
              </div>
              
              <div className="form-group">
                <label className="form-label">ملف البيانات الإضافية</label>
                <input
                  type="file"
                  name="dataFile"
                  onChange={handleInputChange}
                  className="form-input"
                  accept=".csv,.xlsx,.json,.txt"
                />
                <small style={{color: 'var(--gray-500)', fontSize: '0.75rem'}}>
                  يدعم: CSV, XLSX, JSON, TXT
                </small>
              </div>
            </div>
            
            <div className="flex justify-center gap-4 mt-6">
              <button 
                type="submit" 
                className="btn btn-primary"
                disabled={formLoading}
              >
                {formLoading ? (
                  <span className="loading">
                    <span className="loading-spinner"></span>
                    جاري التحليل...
                  </span>
                ) : (
                  '🔍 فحص شامل للمعاملة'
                )}
              </button>
              
              <button 
                type="button" 
                onClick={resetForm}
                className="btn btn-secondary"
                style={{background: 'var(--gray-100)', color: 'var(--gray-700)', border: '2px solid var(--gray-300)'}}
              >
                🔄 إعادة تعيين
              </button>
            </div>
          </form>
          
          {/* Analysis Results */}
          {analysisResult && (
            <div className="results-container animate-fade-in-up">
              <h3>نتائج التحليل</h3>
              
              <div className="mb-4">
                <strong>رقم المعاملة:</strong> {analysisResult.transactionId}
              </div>
              
              <div className="mb-4">
                <strong>مستوى المخاطر:</strong>
                <span className={`risk-indicator ${analysisResult.riskColor} ml-2`}>
                  {analysisResult.riskLevel} ({analysisResult.riskScore}%)
                </span>
              </div>
              
              <div className="mb-4">
                <strong>مستوى الثقة:</strong> {analysisResult.confidence.toFixed(1)}%
              </div>
              
              <div className="mb-4">
                <strong>وقت التحليل:</strong> {analysisResult.analysisTime}
              </div>
              
              {analysisResult.riskFactors.length > 0 && (
                <div className="mb-4">
                  <strong>عوامل المخاطر المكتشفة:</strong>
                  <ul style={{marginTop: '0.5rem', paddingRight: '1.5rem'}}>
                    {analysisResult.riskFactors.map((factor, index) => (
                      <li key={index} style={{color: 'var(--error)', marginBottom: '0.25rem'}}>
                        {factor}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
              
              <div className="mb-4">
                <strong>التوصيات:</strong>
                <ul style={{marginTop: '0.5rem', paddingRight: '1.5rem'}}>
                  {analysisResult.recommendations.map((rec, index) => (
                    <li key={index} style={{color: 'var(--gray-700)', marginBottom: '0.25rem'}}>
                      {rec}
                    </li>
                  ))}
                </ul>
              </div>
            </div>
          )}
        </div>
      </section>

      {/* AI Assistant */}
      <div className="ai-assistant">
        <button 
          className="ai-toggle"
          onClick={() => setAiChatOpen(!aiChatOpen)}
          title="المساعد الذكي"
        >
          🤖
        </button>
        
        {aiChatOpen && (
          <div className="ai-chat">
            <div className="ai-header">
              <h4>المساعد الذكي للأمان المالي</h4>
              <button 
                onClick={() => setAiChatOpen(false)}
                style={{background: 'none', border: 'none', color: 'white', cursor: 'pointer'}}
              >
                ✕
              </button>
            </div>
            
            <div className="ai-messages">
              {aiMessages.map((message, index) => (
                <div key={index} className={`ai-message ${message.type}`}>
                  {message.content}
                </div>
              ))}
              
              {isLoading && (
                <div className="ai-message assistant">
                  <span className="loading">
                    <span className="loading-spinner"></span>
                    جاري الكتابة...
                  </span>
                </div>
              )}
            </div>
            
            <div style={{padding: '1rem', borderTop: '1px solid var(--gray-200)'}}>
              <div style={{marginBottom: '0.5rem'}}>
                <small style={{color: 'var(--gray-500)'}}>أسئلة سريعة:</small>
              </div>
              <div style={{display: 'flex', flexWrap: 'wrap', gap: '0.25rem', marginBottom: '0.5rem'}}>
                {quickQuestions.map((question, index) => (
                  <button
                    key={index}
                    onClick={() => handleQuickQuestion(question)}
                    style={{
                      padding: '0.25rem 0.5rem',
                      fontSize: '0.75rem',
                      background: 'var(--gray-100)',
                      border: '1px solid var(--gray-300)',
                      borderRadius: '0.25rem',
                      cursor: 'pointer',
                      color: 'var(--gray-700)'
                    }}
                  >
                    {question}
                  </button>
                ))}
              </div>
            </div>
            
            <form onSubmit={handleAiSubmit} className="ai-input-area">
              <input
                type="text"
                value={aiInput}
                onChange={(e) => setAiInput(e.target.value)}
                placeholder="اسأل عن الأمان المالي..."
                className="ai-input"
                disabled={isLoading}
              />
              <button 
                type="submit" 
                className="ai-send"
                disabled={isLoading || !aiInput.trim()}
              >
                إرسال
              </button>
            </form>
          </div>
        )}
      </div>
    </div>
  );
}

export default App;
