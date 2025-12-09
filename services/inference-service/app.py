from flask import Flask, request, jsonify
import json
import datetime
import random
import math

app = Flask(__name__)

# إضافة CORS headers يدوياً
@app.after_request
def after_request(response):
    response.headers.add('Access-Control-Allow-Origin', '*')
    response.headers.add('Access-Control-Allow-Headers', 'Content-Type,Authorization')
    response.headers.add('Access-Control-Allow-Methods', 'GET,PUT,POST,DELETE,OPTIONS')
    return response

# قاعدة بيانات مؤقتة في الذاكرة
transactions_db = []
fraud_patterns = []

class FraudDetectionEngine:
    """محرك كشف الاحتيال المتقدم"""
    
    def __init__(self):
        self.risk_weights = {
            'amount_ratio': 0.25,      # نسبة المبلغ إلى الرصيد
            'transaction_type': 0.20,   # نوع المعاملة
            'location': 0.15,          # الموقع الجغرافي
            'payment_method': 0.15,    # طريقة الدفع
            'age_factor': 0.10,        # عامل العمر
            'device_trust': 0.10,      # ثقة الجهاز
            'time_pattern': 0.05       # نمط الوقت
        }
    
    def calculate_risk_score(self, transaction_data):
        """حساب نقاط المخاطر للمعاملة"""
        risk_score = 0
        risk_factors = []
        
        # 1. تحليل نسبة المبلغ إلى الرصيد
        amount = float(transaction_data.get('amount', 0))
        balance = float(transaction_data.get('balance', 0))
        
        if balance > 0:
            amount_ratio = amount / balance
            if amount_ratio > 2.0:  # المبلغ أكبر من ضعف الرصيد
                risk_score += self.risk_weights['amount_ratio'] * 100
                risk_factors.append("المبلغ أكبر بكثير من رصيد الحساب")
            elif amount_ratio > 1.0:  # المبلغ أكبر من الرصيد
                risk_score += self.risk_weights['amount_ratio'] * 70
                risk_factors.append("المبلغ يتجاوز رصيد الحساب")
            elif amount_ratio > 0.5:  # المبلغ أكبر من نصف الرصيد
                risk_score += self.risk_weights['amount_ratio'] * 30
                risk_factors.append("المبلغ كبير نسبياً مقارنة بالرصيد")
        
        # 2. تحليل نوع المعاملة
        transaction_type = transaction_data.get('transaction_type', '')
        high_risk_types = ['تحويل_دولي', 'سحب_نقدي']
        medium_risk_types = ['تحويل_محلي', 'شراء_أونلاين']
        
        if transaction_type in high_risk_types:
            risk_score += self.risk_weights['transaction_type'] * 80
            risk_factors.append(f"نوع المعاملة عالي المخاطر: {transaction_type}")
        elif transaction_type in medium_risk_types:
            risk_score += self.risk_weights['transaction_type'] * 40
            risk_factors.append(f"نوع المعاملة متوسط المخاطر: {transaction_type}")
        
        # 3. تحليل الموقع الجغرافي
        location = transaction_data.get('location', '').lower()
        suspicious_locations = ['غير معروف', 'خارج البلاد', 'مجهول', 'unknown']
        
        if any(keyword in location for keyword in suspicious_locations):
            risk_score += self.risk_weights['location'] * 90
            risk_factors.append("موقع جغرافي مشبوه أو غير معروف")
        
        # 4. تحليل طريقة الدفع
        payment_method = transaction_data.get('payment_method', '')
        if payment_method == 'نقد' and amount > 10000:
            risk_score += self.risk_weights['payment_method'] * 70
            risk_factors.append("دفع نقدي لمبلغ كبير")
        elif payment_method == 'محفظة_رقمية' and amount > 50000:
            risk_score += self.risk_weights['payment_method'] * 50
            risk_factors.append("محفظة رقمية لمبلغ كبير")
        
        # 5. تحليل عامل العمر
        age = int(transaction_data.get('age', 25))
        if age < 21 and amount > 50000:
            risk_score += self.risk_weights['age_factor'] * 80
            risk_factors.append("عمر صغير لمعاملة بمبلغ كبير")
        elif age > 70 and transaction_type in ['شراء_أونلاين', 'محفظة_رقمية']:
            risk_score += self.risk_weights['age_factor'] * 40
            risk_factors.append("نمط معاملة غير معتاد للفئة العمرية")
        
        # 6. تحليل ثقة الجهاز
        device_id = transaction_data.get('device_id', '')
        suspicious_devices = ['unknown', 'غير معروف', '000', 'suspicious']
        
        if any(keyword in device_id.lower() for keyword in suspicious_devices):
            risk_score += self.risk_weights['device_trust'] * 85
            risk_factors.append("معرف جهاز مشبوه أو غير موثوق")
        
        # 7. تحليل نمط الوقت (محاكاة)
        current_hour = datetime.datetime.now().hour
        if current_hour < 6 or current_hour > 23:  # معاملات في أوقات غير عادية
            risk_score += self.risk_weights['time_pattern'] * 60
            risk_factors.append("معاملة في وقت غير عادي")
        
        return min(risk_score, 100), risk_factors
    
    def get_risk_level(self, risk_score):
        """تحديد مستوى المخاطر بناءً على النقاط"""
        if risk_score >= 80:
            return "خطر عالي جداً", "red"
        elif risk_score >= 60:
            return "خطر عالي", "orange"
        elif risk_score >= 40:
            return "خطر متوسط", "yellow"
        elif risk_score >= 20:
            return "خطر منخفض", "blue"
        else:
            return "آمن", "green"
    
    def generate_recommendations(self, risk_score, risk_factors):
        """توليد توصيات بناءً على مستوى المخاطر"""
        recommendations = []
        
        if risk_score >= 80:
            recommendations.extend([
                "رفض المعاملة فوراً",
                "إجراء تحقق إضافي من هوية العميل",
                "الاتصال بالعميل للتأكد من المعاملة",
                "إبلاغ وحدة مكافحة الاحتيال"
            ])
        elif risk_score >= 60:
            recommendations.extend([
                "تأخير المعاملة لمراجعة إضافية",
                "طلب تأكيد إضافي من العميل",
                "مراجعة تاريخ المعاملات السابقة"
            ])
        elif risk_score >= 40:
            recommendations.extend([
                "مراقبة المعاملة عن كثب",
                "إرسال تنبيه للعميل",
                "توثيق المعاملة للمراجعة اللاحقة"
            ])
        elif risk_score >= 20:
            recommendations.extend([
                "مراقبة عادية",
                "تسجيل المعاملة في السجلات"
            ])
        else:
            recommendations.append("السماح بالمعاملة - لا توجد مخاطر ظاهرة")
        
        return recommendations

# إنشاء محرك كشف الاحتيال
fraud_engine = FraudDetectionEngine()

@app.route('/')
def home():
    """الصفحة الرئيسية للـ API"""
    return jsonify({
        "message": "مرحباً بك في API كشف الاحتيال المالي",
        "version": "1.0.0",
        "endpoints": {
            "/analyze": "تحليل معاملة مالية",
            "/history": "عرض تاريخ المعاملات",
            "/stats": "إحصائيات النظام"
        }
    })

@app.route('/analyze', methods=['POST'])
def analyze_transaction():
    """تحليل معاملة مالية لكشف الاحتيال"""
    try:
        data = request.get_json()
        
        # التحقق من وجود البيانات المطلوبة
        required_fields = ['transaction_id', 'amount', 'location', 'device_id', 
                          'user_id', 'transaction_type', 'merchant_category', 
                          'payment_method', 'age', 'balance']
        
        missing_fields = [field for field in required_fields if not data.get(field)]
        if missing_fields:
            return jsonify({
                "error": "حقول مطلوبة مفقودة",
                "missing_fields": missing_fields
            }), 400
        
        # حساب نقاط المخاطر
        risk_score, risk_factors = fraud_engine.calculate_risk_score(data)
        risk_level, risk_color = fraud_engine.get_risk_level(risk_score)
        recommendations = fraud_engine.generate_recommendations(risk_score, risk_factors)
        
        # إنشاء معرف فريد للتحليل
        analysis_id = f"ANALYSIS_{datetime.datetime.now().strftime('%Y%m%d_%H%M%S')}_{random.randint(1000, 9999)}"
        
        # حفظ المعاملة في قاعدة البيانات المؤقتة
        transaction_record = {
            "analysis_id": analysis_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "transaction_data": data,
            "risk_score": risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": recommendations
        }
        transactions_db.append(transaction_record)
        
        # إعداد النتيجة
        result = {
            "analysis_id": analysis_id,
            "timestamp": datetime.datetime.now().isoformat(),
            "risk_assessment": {
                "risk_score": round(risk_score, 2),
                "risk_level": risk_level,
                "risk_color": risk_color,
                "risk_factors": risk_factors
            },
            "transaction_summary": {
                "transaction_id": data['transaction_id'],
                "amount": f"{float(data['amount']):,.2f} ريال سعودي",
                "balance": f"{float(data['balance']):,.2f} ريال سعودي",
                "ratio": f"{(float(data['amount']) / float(data['balance']) * 100):.1f}%" if float(data['balance']) > 0 else "غير محدد"
            },
            "recommendations": recommendations,
            "detailed_analysis": {
                "amount_analysis": f"المبلغ: {float(data['amount']):,.2f} ريال، الرصيد: {float(data['balance']):,.2f} ريال",
                "location_analysis": f"الموقع: {data['location']}",
                "transaction_type_analysis": f"نوع المعاملة: {data['transaction_type']}",
                "payment_method_analysis": f"طريقة الدفع: {data['payment_method']}",
                "age_analysis": f"عمر العميل: {data['age']} سنة"
            }
        }
        
        return jsonify(result)
        
    except Exception as e:
        return jsonify({
            "error": "خطأ في تحليل المعاملة",
            "details": str(e)
        }), 500

@app.route('/history', methods=['GET'])
def get_transaction_history():
    """عرض تاريخ المعاملات المحللة"""
    try:
        # ترتيب المعاملات حسب التاريخ (الأحدث أولاً)
        sorted_transactions = sorted(transactions_db, 
                                   key=lambda x: x['timestamp'], 
                                   reverse=True)
        
        # تحديد عدد النتائج المطلوبة
        limit = request.args.get('limit', 10, type=int)
        limited_transactions = sorted_transactions[:limit]
        
        return jsonify({
            "total_transactions": len(transactions_db),
            "returned_transactions": len(limited_transactions),
            "transactions": limited_transactions
        })
        
    except Exception as e:
        return jsonify({
            "error": "خطأ في استرجاع التاريخ",
            "details": str(e)
        }), 500

@app.route('/stats', methods=['GET'])
def get_system_stats():
    """عرض إحصائيات النظام"""
    try:
        if not transactions_db:
            return jsonify({
                "message": "لا توجد معاملات محللة بعد",
                "total_transactions": 0
            })
        
        # حساب الإحصائيات
        total_transactions = len(transactions_db)
        high_risk_count = sum(1 for t in transactions_db if t['risk_score'] >= 60)
        medium_risk_count = sum(1 for t in transactions_db if 40 <= t['risk_score'] < 60)
        low_risk_count = sum(1 for t in transactions_db if t['risk_score'] < 40)
        
        avg_risk_score = sum(t['risk_score'] for t in transactions_db) / total_transactions
        
        return jsonify({
            "system_stats": {
                "total_transactions": total_transactions,
                "high_risk_transactions": high_risk_count,
                "medium_risk_transactions": medium_risk_count,
                "low_risk_transactions": low_risk_count,
                "average_risk_score": round(avg_risk_score, 2)
            },
            "risk_distribution": {
                "high_risk_percentage": round((high_risk_count / total_transactions) * 100, 1),
                "medium_risk_percentage": round((medium_risk_count / total_transactions) * 100, 1),
                "low_risk_percentage": round((low_risk_count / total_transactions) * 100, 1)
            },
            "last_updated": datetime.datetime.now().isoformat()
        })
        
    except Exception as e:
        return jsonify({
            "error": "خطأ في حساب الإحصائيات",
            "details": str(e)
        }), 500

if __name__ == '__main__':
    print("🚀 بدء تشغيل API كشف الاحتيال المالي...")
    print("📊 النظام جاهز لتحليل المعاملات المالية")
    app.run(host='0.0.0.0', port=5000, debug=True)
@app.route('/ai-assistant', methods=['POST'])
def ai_assistant():
    """مساعد ذكاء اصطناعي للمعاملات المالية"""
    try:
        data = request.get_json()
        user_message = data.get('message', '').strip()
        
        if not user_message:
            return jsonify({
                "error": "الرجاء إدخال رسالة"
            }), 400
        
        # تحليل نوع السؤال وتوليد الإجابة
        response = generate_ai_response(user_message)
        
        return jsonify({
            "user_message": user_message,
            "ai_response": response,
            "timestamp": datetime.datetime.now().isoformat(),
            "response_type": "financial_advice"
        })
        
    except Exception as e:
        return jsonify({
            "error": "خطأ في المساعد الذكي",
            "details": str(e)
        }), 500

def generate_ai_response(user_message):
    """توليد إجابة ذكية بناءً على رسالة المستخدم"""
    message_lower = user_message.lower()
    
    # قاموس الكلمات المفتاحية والإجابات
    responses = {
        # أسئلة حول الاحتيال
        'احتيال': {
            'keywords': ['احتيال', 'غش', 'نصب', 'خداع', 'مشبوه'],
            'response': """🛡️ **كشف الاحتيال المالي**

الاحتيال المالي هو استخدام وسائل خادعة للحصول على أموال أو معلومات مالية بطريقة غير قانونية.

**علامات الاحتيال الشائعة:**
• معاملات بمبالغ كبيرة غير معتادة
• معاملات من مواقع جغرافية مشبوهة
• استخدام أجهزة غير معروفة أو مشبوهة
• معاملات في أوقات غير عادية
• طلبات معلومات شخصية حساسة

**كيف تحمي نفسك:**
• لا تشارك معلوماتك المصرفية مع أحد
• تحقق من المعاملات بانتظام
• استخدم كلمات مرور قوية
• فعّل التنبيهات المصرفية"""
        },
        
        # أسئلة حول المعاملات
        'معاملة': {
            'keywords': ['معاملة', 'تحويل', 'دفع', 'شراء', 'سحب'],
            'response': """💳 **أنواع المعاملات المالية**

**المعاملات الآمنة:**
• الشراء المحلي من متاجر معروفة
• التحويلات للأصدقاء والعائلة
• السحب من أجهزة الصراف المعتادة

**المعاملات عالية المخاطر:**
• التحويلات الدولية لجهات غير معروفة
• المعاملات النقدية الكبيرة
• الشراء من مواقع غير موثوقة

**نصائح للمعاملات الآمنة:**
• تأكد من صحة بيانات المستقبل
• استخدم طرق دفع آمنة
• احتفظ بإيصالات المعاملات
• راجع كشف الحساب بانتظام"""
        },
        
        # أسئلة حول الأمان
        'أمان': {
            'keywords': ['أمان', 'حماية', 'آمن', 'خصوصية', 'تشفير'],
            'response': """🔒 **الأمان المصرفي**

**حماية الحساب:**
• استخدم المصادقة الثنائية
• غيّر كلمة المرور بانتظام
• لا تستخدم شبكات Wi-Fi عامة للمعاملات
• سجّل خروج من التطبيقات المصرفية

**علامات التحذير:**
• رسائل تطلب معلومات شخصية
• روابط مشبوهة في الرسائل
• مكالمات تدّعي أنها من البنك
• طلبات عاجلة للتحقق من الحساب

**في حالة الاشتباه:**
• اتصل بالبنك فوراً
• غيّر كلمات المرور
• راجع المعاملات الأخيرة
• أبلغ عن النشاط المشبوه"""
        },
        
        # أسئلة حول البطاقات
        'بطاقة': {
            'keywords': ['بطاقة', 'فيزا', 'ماستركارد', 'ائتمان', 'خصم'],
            'response': """💳 **أمان البطاقات المصرفية**

**نصائح الاستخدام الآمن:**
• احتفظ بالبطاقة في مكان آمن
• لا تشارك رقم البطاقة أو CVV
• غطّ لوحة المفاتيح عند إدخال الرقم السري
• تحقق من المعاملات فوراً

**في حالة فقدان البطاقة:**
• أبلغ البنك فوراً لإيقاف البطاقة
• راجع المعاملات الأخيرة
• اطلب بطاقة بديلة
• غيّر الرقم السري

**علامات سوء الاستخدام:**
• معاملات لم تقم بها
• مبالغ غير صحيحة
• معاملات من مواقع لم تزرها
• رسوم غير مبررة"""
        }
    }
    
    # البحث عن الكلمات المفتاحية في الرسالة
    for category, data in responses.items():
        if any(keyword in message_lower for keyword in data['keywords']):
            return data['response']
    
    # إجابات عامة للأسئلة الشائعة
    general_responses = [
        """🤖 **مساعدك المالي الذكي**

أهلاً بك! أنا هنا لمساعدتك في:

**🛡️ أمان المعاملات:**
• كشف الاحتيال والأنشطة المشبوهة
• نصائح الحماية المصرفية
• تقييم مخاطر المعاملات

**💡 استشارات مالية:**
• أفضل ممارسات الدفع الآمن
• كيفية حماية معلوماتك المالية
• التعرف على علامات الاحتيال

**📊 تحليل المعاملات:**
• فحص المعاملات المشبوهة
• تقييم مستوى المخاطر
• توصيات الأمان المخصصة

اسألني عن أي شيء يتعلق بالأمان المالي!""",

        """💼 **خدمات الاستشارة المالية**

يمكنني مساعدتك في:

**🔍 تحليل المخاطر:**
• تقييم أمان المعاملات
• كشف الأنماط المشبوهة
• تحليل سلوك الإنفاق

**🛡️ الحماية والوقاية:**
• نصائح الأمان المصرفي
• حماية البيانات الشخصية
• تجنب عمليات الاحتيال

**📈 التوعية المالية:**
• فهم أنواع المعاملات
• معرفة حقوقك كعميل
• أفضل الممارسات المصرفية

كيف يمكنني مساعدتك اليوم؟"""
    ]
    
    # اختيار إجابة عشوائية من الإجابات العامة
    return random.choice(general_responses)
