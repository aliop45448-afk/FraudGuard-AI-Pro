"""
محرك التعلم الآلي المتقدم لكشف الاحتيال المالي
Advanced Machine Learning Engine for Fraud Detection
"""

import numpy as np
import pandas as pd
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier, IsolationForest
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.model_selection import train_test_split
import joblib
import json
from datetime import datetime
import random


class AdvancedFraudDetectionEngine:
    """محرك متقدم لكشف الاحتيال باستخدام نماذج ML متعددة"""
    
    def __init__(self):
        self.random_forest = None
        self.gradient_boosting = None
        self.isolation_forest = None
        self.scaler = StandardScaler()
        self.label_encoders = {}
        self.is_trained = False
        
        # تدريب النماذج بشكل تلقائي
        self._initialize_models()
    
    def _initialize_models(self):
        """تهيئة وتدريب النماذج الأولية"""
        # توليد بيانات تدريبية اصطناعية
        training_data = self._generate_synthetic_training_data(5000)
        self._train_models(training_data)
    
    def _generate_synthetic_training_data(self, n_samples=5000):
        """توليد بيانات تدريبية اصطناعية"""
        np.random.seed(42)
        data = []
        
        for i in range(n_samples):
            # توليد معاملات عادية (70%)
            if i < n_samples * 0.7:
                transaction = {
                    'amount': np.random.uniform(10, 5000),
                    'balance': np.random.uniform(5000, 100000),
                    'age': np.random.randint(25, 65),
                    'transaction_type': np.random.choice(['شراء', 'تحويل_محلي', 'دفع_فواتير']),
                    'payment_method': np.random.choice(['بطاقة_ائتمان', 'بطاقة_خصم', 'تحويل_بنكي']),
                    'hour': np.random.randint(8, 22),
                    'day_of_week': np.random.randint(0, 7),
                    'location_risk': np.random.uniform(0, 0.3),
                    'device_trust': np.random.uniform(0.7, 1.0),
                    'is_fraud': 0
                }
            # توليد معاملات احتيالية (30%)
            else:
                transaction = {
                    'amount': np.random.uniform(5000, 100000),
                    'balance': np.random.uniform(100, 10000),
                    'age': np.random.randint(18, 75),
                    'transaction_type': np.random.choice(['تحويل_دولي', 'سحب_نقدي', 'شراء']),
                    'payment_method': np.random.choice(['نقد', 'محفظة_رقمية']),
                    'hour': np.random.choice(list(range(0, 6)) + list(range(23, 24))),
                    'day_of_week': np.random.randint(0, 7),
                    'location_risk': np.random.uniform(0.6, 1.0),
                    'device_trust': np.random.uniform(0, 0.4),
                    'is_fraud': 1
                }
            
            data.append(transaction)
        
        return pd.DataFrame(data)
    
    def _prepare_features(self, df, fit=False):
        """تحضير الميزات للنماذج"""
        # نسخ البيانات
        df_processed = df.copy()
        
        # حساب ميزات مشتقة
        df_processed['amount_to_balance_ratio'] = df_processed['amount'] / (df_processed['balance'] + 1)
        df_processed['is_high_amount'] = (df_processed['amount'] > 10000).astype(int)
        df_processed['is_night_transaction'] = ((df_processed['hour'] < 6) | (df_processed['hour'] > 22)).astype(int)
        df_processed['is_weekend'] = (df_processed['day_of_week'] >= 5).astype(int)
        
        # ترميز المتغيرات الفئوية
        categorical_features = ['transaction_type', 'payment_method']
        
        for feature in categorical_features:
            if fit:
                self.label_encoders[feature] = LabelEncoder()
                df_processed[feature + '_encoded'] = self.label_encoders[feature].fit_transform(df_processed[feature])
            else:
                if feature in self.label_encoders:
                    # معالجة القيم غير المعروفة
                    df_processed[feature + '_encoded'] = df_processed[feature].apply(
                        lambda x: self.label_encoders[feature].transform([x])[0] 
                        if x in self.label_encoders[feature].classes_ 
                        else -1
                    )
                else:
                    df_processed[feature + '_encoded'] = 0
        
        # اختيار الميزات النهائية
        feature_columns = [
            'amount', 'balance', 'age', 'hour', 'day_of_week',
            'location_risk', 'device_trust', 'amount_to_balance_ratio',
            'is_high_amount', 'is_night_transaction', 'is_weekend',
            'transaction_type_encoded', 'payment_method_encoded'
        ]
        
        X = df_processed[feature_columns]
        
        # تطبيع البيانات
        if fit:
            X_scaled = self.scaler.fit_transform(X)
        else:
            X_scaled = self.scaler.transform(X)
        
        return X_scaled, feature_columns
    
    def _train_models(self, training_data):
        """تدريب جميع النماذج"""
        # فصل الميزات والهدف
        X, feature_columns = self._prepare_features(training_data, fit=True)
        y = training_data['is_fraud'].values
        
        # تقسيم البيانات
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42, stratify=y
        )
        
        # تدريب Random Forest
        self.random_forest = RandomForestClassifier(
            n_estimators=100,
            max_depth=10,
            random_state=42,
            n_jobs=-1
        )
        self.random_forest.fit(X_train, y_train)
        
        # تدريب Gradient Boosting
        self.gradient_boosting = GradientBoostingClassifier(
            n_estimators=100,
            max_depth=5,
            learning_rate=0.1,
            random_state=42
        )
        self.gradient_boosting.fit(X_train, y_train)
        
        # تدريب Isolation Forest (للكشف عن الشذوذ)
        self.isolation_forest = IsolationForest(
            contamination=0.3,
            random_state=42,
            n_jobs=-1
        )
        self.isolation_forest.fit(X_train)
        
        self.is_trained = True
        
        # حساب دقة النماذج
        rf_score = self.random_forest.score(X_test, y_test)
        gb_score = self.gradient_boosting.score(X_test, y_test)
        
        print(f"✅ تم تدريب النماذج بنجاح")
        print(f"   Random Forest Accuracy: {rf_score:.4f}")
        print(f"   Gradient Boosting Accuracy: {gb_score:.4f}")
    
    def predict_fraud(self, transaction_data):
        """التنبؤ باحتمالية الاحتيال لمعاملة واحدة"""
        if not self.is_trained:
            raise Exception("النماذج غير مدربة بعد")
        
        # تحويل البيانات إلى DataFrame
        df = pd.DataFrame([transaction_data])
        
        # تحضير الميزات
        X, _ = self._prepare_features(df, fit=False)
        
        # التنبؤ باستخدام Random Forest
        rf_proba = self.random_forest.predict_proba(X)[0][1]
        rf_prediction = self.random_forest.predict(X)[0]
        
        # التنبؤ باستخدام Gradient Boosting
        gb_proba = self.gradient_boosting.predict_proba(X)[0][1]
        gb_prediction = self.gradient_boosting.predict(X)[0]
        
        # التنبؤ باستخدام Isolation Forest
        iso_prediction = self.isolation_forest.predict(X)[0]
        iso_score = self.isolation_forest.score_samples(X)[0]
        
        # دمج النتائج (Ensemble)
        ensemble_proba = (rf_proba * 0.4 + gb_proba * 0.4 + (1 if iso_prediction == -1 else 0) * 0.2)
        ensemble_prediction = 1 if ensemble_proba > 0.5 else 0
        
        # حساب نقاط المخاطر (0-100)
        risk_score = min(100, int(ensemble_proba * 100))
        
        # تحديد مستوى المخاطر
        if risk_score < 30:
            risk_level = "منخفض"
            risk_color = "green"
        elif risk_score < 70:
            risk_level = "متوسط"
            risk_color = "orange"
        else:
            risk_level = "عالي"
            risk_color = "red"
        
        # تحليل عوامل المخاطر
        risk_factors = self._analyze_risk_factors(transaction_data, X)
        
        return {
            'is_fraud': bool(ensemble_prediction),
            'fraud_probability': round(ensemble_proba * 100, 2),
            'risk_score': risk_score,
            'risk_level': risk_level,
            'risk_color': risk_color,
            'risk_factors': risk_factors,
            'model_predictions': {
                'random_forest': {
                    'prediction': bool(rf_prediction),
                    'probability': round(rf_proba * 100, 2)
                },
                'gradient_boosting': {
                    'prediction': bool(gb_prediction),
                    'probability': round(gb_proba * 100, 2)
                },
                'isolation_forest': {
                    'is_anomaly': bool(iso_prediction == -1),
                    'anomaly_score': round(float(iso_score), 4)
                }
            },
            'confidence': round((max(rf_proba, 1-rf_proba) + max(gb_proba, 1-gb_proba)) / 2 * 100, 2)
        }
    
    def _analyze_risk_factors(self, transaction_data, X):
        """تحليل عوامل المخاطر"""
        factors = []
        
        amount = transaction_data.get('amount', 0)
        balance = transaction_data.get('balance', 0)
        age = transaction_data.get('age', 0)
        hour = transaction_data.get('hour', 12)
        location_risk = transaction_data.get('location_risk', 0)
        device_trust = transaction_data.get('device_trust', 1)
        
        # تحليل المبلغ
        if balance > 0:
            ratio = amount / balance
            if ratio > 1.5:
                factors.append({
                    'factor': 'نسبة المبلغ إلى الرصيد',
                    'severity': 'عالي',
                    'description': f'المبلغ ({amount:.2f}) يتجاوز الرصيد ({balance:.2f}) بشكل كبير'
                })
            elif ratio > 0.7:
                factors.append({
                    'factor': 'نسبة المبلغ إلى الرصيد',
                    'severity': 'متوسط',
                    'description': f'المبلغ ({amount:.2f}) كبير نسبياً مقارنة بالرصيد ({balance:.2f})'
                })
        
        # تحليل الوقت
        if hour < 6 or hour > 22:
            factors.append({
                'factor': 'توقيت المعاملة',
                'severity': 'متوسط',
                'description': f'معاملة في وقت غير معتاد (الساعة {hour}:00)'
            })
        
        # تحليل الموقع
        if location_risk > 0.6:
            factors.append({
                'factor': 'الموقع الجغرافي',
                'severity': 'عالي',
                'description': 'موقع جغرافي عالي المخاطر'
            })
        elif location_risk > 0.4:
            factors.append({
                'factor': 'الموقع الجغرافي',
                'severity': 'متوسط',
                'description': 'موقع جغرافي متوسط المخاطر'
            })
        
        # تحليل الجهاز
        if device_trust < 0.4:
            factors.append({
                'factor': 'ثقة الجهاز',
                'severity': 'عالي',
                'description': 'جهاز غير موثوق أو مشبوه'
            })
        elif device_trust < 0.6:
            factors.append({
                'factor': 'ثقة الجهاز',
                'severity': 'متوسط',
                'description': 'جهاز ذو ثقة منخفضة'
            })
        
        # تحليل المبلغ الكبير
        if amount > 50000:
            factors.append({
                'factor': 'قيمة المعاملة',
                'severity': 'متوسط',
                'description': f'مبلغ كبير جداً ({amount:.2f} ريال)'
            })
        
        return factors
    
    def get_feature_importance(self):
        """الحصول على أهمية الميزات"""
        if not self.is_trained or self.random_forest is None:
            return {}
        
        feature_names = [
            'المبلغ', 'الرصيد', 'العمر', 'الساعة', 'يوم الأسبوع',
            'مخاطر الموقع', 'ثقة الجهاز', 'نسبة المبلغ/الرصيد',
            'مبلغ كبير', 'معاملة ليلية', 'نهاية الأسبوع',
            'نوع المعاملة', 'طريقة الدفع'
        ]
        
        importances = self.random_forest.feature_importances_
        
        feature_importance = {}
        for name, importance in zip(feature_names, importances):
            feature_importance[name] = round(float(importance), 4)
        
        # ترتيب حسب الأهمية
        sorted_features = dict(sorted(feature_importance.items(), key=lambda x: x[1], reverse=True))
        
        return sorted_features
    
    def save_models(self, path='models/'):
        """حفظ النماذج المدربة"""
        import os
        os.makedirs(path, exist_ok=True)
        
        joblib.dump(self.random_forest, f'{path}random_forest.pkl')
        joblib.dump(self.gradient_boosting, f'{path}gradient_boosting.pkl')
        joblib.dump(self.isolation_forest, f'{path}isolation_forest.pkl')
        joblib.dump(self.scaler, f'{path}scaler.pkl')
        joblib.dump(self.label_encoders, f'{path}label_encoders.pkl')
        
        print(f"✅ تم حفظ النماذج في {path}")
    
    def load_models(self, path='models/'):
        """تحميل النماذج المحفوظة"""
        import os
        
        if not os.path.exists(path):
            print("⚠️ مسار النماذج غير موجود، سيتم التدريب من جديد")
            return False
        
        try:
            self.random_forest = joblib.load(f'{path}random_forest.pkl')
            self.gradient_boosting = joblib.load(f'{path}gradient_boosting.pkl')
            self.isolation_forest = joblib.load(f'{path}isolation_forest.pkl')
            self.scaler = joblib.load(f'{path}scaler.pkl')
            self.label_encoders = joblib.load(f'{path}label_encoders.pkl')
            self.is_trained = True
            
            print(f"✅ تم تحميل النماذج من {path}")
            return True
        except Exception as e:
            print(f"❌ فشل تحميل النماذج: {e}")
            return False


# اختبار المحرك
if __name__ == "__main__":
    print("🚀 تهيئة محرك الكشف عن الاحتيال المتقدم...")
    engine = AdvancedFraudDetectionEngine()
    
    # اختبار معاملة عادية
    normal_transaction = {
        'amount': 500,
        'balance': 25000,
        'age': 35,
        'transaction_type': 'شراء',
        'payment_method': 'بطاقة_ائتمان',
        'hour': 14,
        'day_of_week': 2,
        'location_risk': 0.1,
        'device_trust': 0.9
    }
    
    print("\n📊 اختبار معاملة عادية:")
    result = engine.predict_fraud(normal_transaction)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # اختبار معاملة مشبوهة
    suspicious_transaction = {
        'amount': 75000,
        'balance': 5000,
        'age': 22,
        'transaction_type': 'تحويل_دولي',
        'payment_method': 'نقد',
        'hour': 3,
        'day_of_week': 6,
        'location_risk': 0.9,
        'device_trust': 0.2
    }
    
    print("\n🚨 اختبار معاملة مشبوهة:")
    result = engine.predict_fraud(suspicious_transaction)
    print(json.dumps(result, ensure_ascii=False, indent=2))
    
    # عرض أهمية الميزات
    print("\n📈 أهمية الميزات:")
    feature_importance = engine.get_feature_importance()
    for feature, importance in list(feature_importance.items())[:5]:
        print(f"   {feature}: {importance:.4f}")
