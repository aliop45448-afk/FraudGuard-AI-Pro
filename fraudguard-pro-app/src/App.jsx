import React from 'react';
import { BrowserRouter as Router, Routes, Route, Link } from 'react-router-dom';
import { Chart as ChartJS, ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement } from 'chart.js';
import Dashboard from './pages/Dashboard';
import TransactionAnalysis from './pages/TransactionAnalysis';
import Alerts from './pages/Alerts';
import Reports from './pages/Reports';
import Settings from './pages/Settings';

ChartJS.register(ArcElement, Tooltip, Legend, CategoryScale, LinearScale, BarElement, Title, PointElement, LineElement);

const Layout = ({ children }) => {
  const navItems = [
    { path: '/', name: 'لوحة التحكم', icon: '📊' },
    { path: '/analyze', name: 'تحليل المعاملات', icon: '🔍' },
    { path: '/alerts', name: 'التنبيهات', icon: '🚨' },
    { path: '/reports', name: 'التقارير', icon: '📋' },
    { path: '/settings', name: 'الإعدادات', icon: '⚙️' },
  ];

  return (
    <div className="flex h-screen bg-gray-50 font-cairo">
      {/* Sidebar */}
      <div className="w-64 bg-white shadow-xl p-4 flex flex-col">
        <div className="text-2xl font-bold text-primary-blue mb-8 border-b pb-4">
          FraudGuard AI Pro
        </div>
        <nav className="flex-grow">
          {navItems.map((item) => (
            <Link
              key={item.path}
              to={item.path}
              className="flex items-center p-3 my-2 text-gray-700 rounded-lg hover:bg-primary-blue hover:text-white transition-colors duration-200"
            >
              <span className="text-xl ml-3">{item.icon}</span>
              <span className="font-medium">{item.name}</span>
            </Link>
          ))}
        </nav>
        <div className="mt-auto pt-4 border-t text-sm text-gray-500">
          <p>الإصدار: 2.0.0 Enterprise</p>
          <p>© 2025 FraudGuard AI</p>
        </div>
      </div>

      {/* Main Content */}
      <main className="flex-1 overflow-y-auto p-8">
        {children}
      </main>
    </div>
  );
};

const App = () => {
  return (
    <Router>
      <Layout>
        <Routes>
          <Route path="/" element={<Dashboard />} />
          <Route path="/analyze" element={<TransactionAnalysis />} />
          <Route path="/alerts" element={<Alerts />} />
          <Route path="/reports" element={<Reports />} />
          <Route path="/settings" element={<Settings />} />
          <Route path="*" element={<h1 className="text-3xl text-fraud-red">404 - الصفحة غير موجودة</h1>} />
        </Routes>
      </Layout>
    </Router>
  );
};

export default App;
