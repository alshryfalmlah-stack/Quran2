# Quran.py
import streamlit as st
import pandas as pd
import datetime
import calendar
from io import BytesIO
from supabase import create_client, Client
import os

# استيراد مكتبات توليد الـ PDF ومعالجة النصوص العربية
import arabic_reshaper
from bidi.algorithm import get_display
from reportlab.lib.pagesizes import letter, landscape
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

# تسجيل خط أميري في المشروع لتجنب ظهور المربعات السوداء
try:
    pdfmetrics.registerFont(TTFont('ArabicFont', 'Amiri-Regular.ttf'))
    pdfmetrics.registerFont(TTFont('ArabicFont-Bold', 'Amiri-Bold.ttf'))
    FONT_NAME = 'ArabicFont'
    FONT_BOLD = 'ArabicFont-Bold'
except:
    FONT_NAME = 'Helvetica'
    FONT_BOLD = 'Helvetica-Bold'

# إعداد الصفحة مع دعم الأجهزة الذكية
st.set_page_config(
    page_title="منظومة مراكز تحفيظ القرآن الكريم - سلوق (قسم الطالبات)",
    page_icon="🌸",
    layout="wide"
)

# تخصيص التصميم المحدث بألوان بنفسجية هادئة ومريحة للعين (Muted Lavender Theme)
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Cairo:wght@400;600;700;900&display=swap');

    html, body, [class*="css"] {
        font-family: 'Cairo', sans-serif !important;
        direction: rtl;
        text-align: right;
        background-color: #F7F5FA;
    }

    .main-header-container {
        background: linear-gradient(135deg, #6B5B95 0%, #8370B9 50%, #9683EC 100%);
        padding: 24px 20px;
        border-radius: 16px;
        color: white;
        text-align: center;
        margin-bottom: 20px;
        box-shadow: 0 10px 25px -5px rgba(150, 131, 236, 0.25);
    }
    .main-title {
        font-size: 26px;
        font-weight: 900;
        margin-bottom: 4px;
        color: #ffffff;
    }
    .sub-title-main {
        font-size: 18px;
        font-weight: 700;
        margin-bottom: 6px;
        color: #F0EDF9;
    }
    .sub-title {
        font-size: 13px;
        color: #E2DCF7;
        margin-bottom: 0px;
    }

    .user-top-bar {
        background: white;
        border: 1px solid #DDD6F3;
        padding: 12px 18px;
        border-radius: 12px;
        color: #4A3E6D;
        font-size: 13px;
        font-weight: 600;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        box-shadow: 0 4px 6px -1px rgba(150, 131, 236, 0.05);
    }
    
    .teacher-banner {
        background: linear-gradient(135deg, #F3F0FA 0%, #EAE5F7 100%);
        border: 1px solid #DDD6F3;
        padding: 14px 18px;
        border-radius: 12px;
        color: #5C4B89;
        font-size: 14px;
        font-weight: 700;
        margin-bottom: 16px;
        display: flex;
        justify-content: space-between;
        align-items: center;
        flex-wrap: wrap;
        gap: 10px;
        box-shadow: 0 4px 6px -1px rgba(150, 131, 236, 0.05);
    }

    .section-header {
        text-align: right;
        color: #4A3E6D;
        font-weight: 700;
        font-size: 16px;
        margin-top: 12px;
        margin-bottom: 12px;
        border-right: 4px solid #9683EC;
        padding-right: 10px;
        background-color: #EAE5F7;
        padding-top: 6px;
        padding-bottom: 6px;
        border-radius: 0 8px 8px 0;
    }

    .login-container {
        direction: rtl;
        text-align: right;
    }

    .stTextInput label, .stSelectbox label, .stNumberInput label {
        direction: rtl;
        text-align: right;
        display: block;
        font-weight: 600;
        color: #4A3E6D;
        font-size: 13px;
    }
    
    .stButton button {
        width: 100%;
        background: linear-gradient(135deg, #9683EC 0%, #8370B9 100%);
        color: white;
        font-weight: 700;
        border-radius: 10px;
        border: none;
        padding: 10px 18px;
        font-size: 14px;
        transition: all 0.3s ease;
        box-shadow: 0 4px 12px rgba(150, 131, 236, 0.25);
    }
    .stButton button:hover {
        background: linear-gradient(135deg, #8370B9 0%, #6B5B95 100%);
        box-shadow: 0 6px 16px rgba(131, 112, 185, 0.35);
        transform: translateY(-1px);
    }

    .stDataFrame, table, th, td {
        direction: rtl !important;
        text-align: right !important;
    }

    .stTabs [data-baseweb="tab-list"] {
        gap: 6px;
        background-color: #EAE5F7;
        padding: 6px;
        border-radius: 12px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 40px;
        background-color: white;
        border-radius: 8px;
        font-weight: 600;
        color: #4A3E6D;
        font-size: 13px;
        padding: 0 14px;
    }
    .stTabs [aria-selected="true"] {
        background-color: #9683EC !important;
        color: white !important;
        box-shadow: 0 2px 8px rgba(150, 131, 236, 0.3);
    }
    </style>
""", unsafe_allow_html=True)

st.markdown("""
    <div class="main-header-container">
        <div class="main-title">مكتب الأوقاف والشؤون الإسلامية - سلوق</div>
        <div class="sub-title-main">منظومة مراكز تحفيظ القرآن الكريم (قسم الطالبات)</div>
        <div class="sub-title">نظام إدارة الطالبات، المتابعة الشهرية، والإحصائيات الشاملة للمراكز</div>
    </div>
""", unsafe_allow_html=True)

# الاتصال بـ Supabase باستخدام الأسرار (Secrets)
@st.cache_resource
def init_supabase() -> Client:
    try:
        url = st.secrets["supabase"]["url"]
        key = st.secrets["supabase"]["key"]
        return create_client(url, key)
    except:
        return None

supabase = init_supabase()

quran_surahs = [
    "الفاتحة", "البقرة", "آل عمران", "النساء", "المائدة", "الأنعام", "الأعراف", "الأنفال", "التوبة", "يونس",
    "هود", "يوسف", "الرعد", "إبراهيم", "الحجر", "النحل", "الإسراء", "الكهف", "مريم", "طه",
    "الأنبياء", "الحج", "المؤمنون", "النور", "الفرقان", "الشعراء", "النمل", "القصص", "العنكبوت", "الروم",
    "لقمان", "السجدة", "الأحزاب", "سبأ", "فاطر", "يس", "الصافات", "ص", "الزمر", "غافر",
    "فصلت", "الشورى", "الزخرف", "الدخان", "الجاثية", "الأحقاف", "محمد", "الفتح", "الحجرات", "ق",
    "الذاريات", "الطور", "النجم", "القمر", "الرحمن", "الواقعة", "الحديد", "المجادلة", "الحشر", "الممتحنة",
    "الصف", "الجُمُعَة", "المنافقون", "التغابن", "الطلاق", "التحريم", "الملك", "القلم", "الحاقة", "المعارج",
    "نوح", "الجن", "المزمل", "المدثر", "القيامة", "الإنسان", "المرسلات", "النبأ", "النازعات", "عبس",
    "التكوير", "الانفطار", "المطففين", "الانشقاق", "البروج", "الطارق", "الأعلى", "الغاشية", "الفجر", "البلد",
    "الشمس", "الليل", "الضحى", "الشرح", "التين", "العلق", "القدر", "البينة", "الزلزلة", "العاديات",
    "القارعة", "التكاثر", "العصر", "الهمزة", "الفيل", "قريش", "الماعون", "الكوثَر", "الكافرون", "النصر",
    "المسد", "الإخلاص", "الفلق", "الناس"
]

def sort_students_by_memorization(df):
    if df.empty:
        return df
    surah_order = {surah: idx for idx, surah in enumerate(quran_surahs)}
    df = df.copy()
    df['memo_rank'] = df['memorization'].map(surah_order).fillna(len(quran_surahs))
    df = df.sort_values(by=['memo_rank', 'name'], ascending=[True, True]).drop(columns=['memo_rank'])
    return df

def load_users():
    if supabase is not None:
        try:
            response = supabase.table("users").select("*").execute()
            if response.data and len(response.data) > 0:
                df = pd.DataFrame(response.data)
                for col in ['assigned_supervisor', 'assigned_follower']:
                    if col not in df.columns:
                        df[col] = ""
                return df
        except:
            pass
            
    if os.path.exists("users_rows.csv"):
        try:
            df_csv = pd.read_csv("users_rows.csv")
            if not df_csv.empty:
                for col in ['assigned_supervisor', 'assigned_follower']:
                    if col not in df_csv.columns:
                        df_csv[col] = ""
                return df_csv
        except:
            pass
            
    default_users = {
        'username': ['123'],
        'password': ['123'],
        'role': ['إدارة المكتب'],
        'name': ['123'],
        'center': [''],
        'assigned_supervisor': [''],
        'assigned_follower': ['']
    }
    return pd.DataFrame(default_users)

def load_students():
    if supabase is not None:
        try:
            response = supabase.table("students").select("*").execute()
            if response.data:
                return pd.DataFrame(response.data)
        except:
            pass
    return pd.DataFrame(columns=['student_id', 'name', 'birth_year', 'center', 'teacher', 'memorization', 'status', 'last_update'])

def update_student_in_db(student_id, name, birth_year, memorization, status):
    today_str = str(datetime.date.today())
    if supabase is not None:
        try:
            supabase.table("students").update({
                "name": name,
                "birth_year": birth_year,
                "memorization": memorization,
                "status": status,
                "last_update": today_str
            }).eq("student_id", student_id).execute()
        except:
            pass

def delete_student_from_db(student_id):
    if supabase is not None:
        try:
            supabase.table("students").delete().eq("student_id", student_id).execute()
        except:
            pass

def add_student_to_db(name, birth_year, center, teacher, memorization):
    today_str = str(datetime.date.today())
    if supabase is not None:
        try:
            supabase.table("students").insert({
                "name": name,
                "birth_year": birth_year,
                "center": center,
                "teacher": teacher,
                "memorization": memorization,
                "status": "منتظمة",
                "last_update": today_str
            }).execute()
        except:
            pass

def add_user_to_db(username, password, role, name, center):
    if supabase is not None:
        try:
            supabase.table("users").upsert({
                "username": username,
                "password": password,
                "role": role,
                "name": name,
                "center": center,
                "assigned_supervisor": "",
                "assigned_follower": ""
            }, on_conflict="username").execute()
            return True
        except Exception as e:
            print("Error adding user:", e)
            return False
    return False

def update_teacher_permissions(username, supervisor_name, follower_name):
    if supabase is not None:
        try:
            supabase.table("users").update({
                "assigned_supervisor": supervisor_name,
                "assigned_follower": follower_name
            }).eq("username", username).execute()
            return True
        except Exception as e:
            print("Error updating permissions:", e)
            return False
    return False

def delete_user_from_db(username):
    if supabase is not None:
        try:
            supabase.table("users").delete().eq("username", username).execute()
        except:
            pass

def update_password_in_db(username, new_password):
    if supabase is not None:
        try:
            supabase.table("users").update({"password": new_password}).eq("username", username).execute()
        except:
            pass

def get_arabic_day_name(date_obj):
    days_map = {
        'Sunday': 'الأحد', 'Monday': 'الإثنين', 'Tuesday': 'الثلاثاء',
        'Wednesday': 'الأربعاء', 'Thursday': 'الخميس', 'Friday': 'الجمعة', 'Saturday': 'السبت'
    }
    return days_map.get(date_obj.strftime('%A'), date_obj.strftime('%A'))

def get_month_days_list(year, month):
    num_days = calendar.monthrange(year, month)[1]
    days_list = []
    for day in range(1, num_days + 1):
        d_obj = datetime.date(year, month, day)
        d_str = d_obj.strftime('%Y-%m-%d')
        day_name = get_arabic_day_name(d_obj)
        is_weekend = (day_name in ['الخميس', 'الجمعة'])
        days_list.append({
            'date': d_str,
            'day_num': day,
            'day_name': day_name,
            'is_weekend': is_weekend
        })
    return days_list

def fix_arabic(text):
    try:
        reshaped = arabic_reshaper.reshape(str(text))
        return get_display(reshaped)
    except:
        return str(text)

def generate_teachers_summary_pdf(teachers_summary_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ArabicTitle', parent=styles['Heading1'], fontName=FONT_BOLD, fontSize=20,
        leading=26, textColor=colors.HexColor('#6B5B95'), alignment=1, spaceAfter=6
    )
    sub_style = ParagraphStyle(
        'ArabicSub', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11,
        leading=15, textColor=colors.HexColor('#8370B9'), alignment=1, spaceAfter=10
    )
    
    story.append(Paragraph(fix_arabic("مكتب الأوقاف والشؤون الإسلامية - سلوق (قسم الطالبات)"), title_style))
    story.append(Paragraph(fix_arabic("كشف المحفظات ومراكز التحفيظ وإجمالي الطالبات المنتظمات"), sub_style))
    story.append(Spacer(1, 10))
    
    table_headers = [fix_arabic("اسم المحفظة"), fix_arabic("مركز التحفيظ / المسجد"), fix_arabic("عدد الطالبات المنتظمات"), fix_arabic("م")]
    pdf_table_data = [table_headers]
    
    idx = 1
    for _, row in teachers_summary_df.iterrows():
        pdf_table_data.append([
            fix_arabic(row.get('name', '')),
            fix_arabic(row.get('center', '')),
            str(row.get('regular_count', '')),
            str(idx)
        ])
        idx += 1
        
    col_widths = [160, 180, 100, 40]
    
    t = Table(pdf_table_data, colWidths=col_widths, hAlign='CENTER')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#9683EC')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFFFFF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDD6F3')),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('TOPPADDING', (0,1), (-1,-1), 5),
    ]))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_students_list_pdf(teacher_name, center_name, students_df, report_title="كشف الطالبات المنتظمات بالحلقة"):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=20, bottomMargin=20)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ArabicTitle', parent=styles['Heading1'], fontName=FONT_BOLD, fontSize=20,
        leading=26, textColor=colors.HexColor('#6B5B95'), alignment=1, spaceAfter=6
    )
    sub_style = ParagraphStyle(
        'ArabicSub', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11,
        leading=15, textColor=colors.HexColor('#8370B9'), alignment=1, spaceAfter=10
    )
    
    story.append(Paragraph(fix_arabic("مكتب الأوقاف والشؤون الإسلامية - سلوق (قسم الطالبات)"), title_style))
    story.append(Paragraph(fix_arabic(report_title), sub_style))
    story.append(Paragraph(fix_arabic(f"المحفظة: {teacher_name}  |  المركز: {center_name}"), sub_style))
    story.append(Spacer(1, 10))
    
    table_headers = [fix_arabic("آخر تحديث"), fix_arabic("الحالة"), fix_arabic("آخر سورة محفوظة"), fix_arabic("سنة الميلاد"), fix_arabic("اسم الطالبة"), fix_arabic("م")]
    pdf_table_data = [table_headers]
    
    idx = 1
    for _, row in students_df.iterrows():
        pdf_table_data.append([
            str(row.get('last_update', '')),
            fix_arabic(row.get('status', '')),
            fix_arabic(row.get('memorization', '')),
            str(row.get('birth_year', '')),
            fix_arabic(row.get('name', '')),
            str(idx)
        ])
        idx += 1
        
    col_widths = [75, 55, 110, 65, 160, 35]
    
    t = Table(pdf_table_data, colWidths=col_widths, hAlign='CENTER')
    t.setStyle(TableStyle([
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#9683EC')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,0), 9),
        ('BOTTOMPADDING', (0,0), (-1,0), 6),
        ('TOPPADDING', (0,0), (-1,0), 6),
        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFFFFF')),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDD6F3')),
        ('FONTSIZE', (0,1), (-1,-1), 9),
        ('BOTTOMPADDING', (0,1), (-1,-1), 5),
        ('TOPPADDING', (0,1), (-1,-1), 5),
    ]))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

def generate_teacher_attendance_pdf(teacher_name, center_name, month_name, year_val, att_df):
    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter, rightMargin=20, leftMargin=20, topMargin=15, bottomMargin=15)
    story = []
    
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'ArabicTitle', parent=styles['Heading1'], fontName=FONT_BOLD, fontSize=20,
        leading=26, textColor=colors.HexColor('#6B5B95'), alignment=1, spaceAfter=6
    )
    sub_style = ParagraphStyle(
        'ArabicSub', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11,
        leading=15, textColor=colors.HexColor('#8370B9'), alignment=1, spaceAfter=8
    )
    
    story.append(Paragraph(fix_arabic("مكتب الأوقاف والشؤون الإسلامية - سلوق (قسم الطالبات)"), title_style))
    story.append(Paragraph(fix_arabic(f"سجل حضور وانصراف المحفظة (شهر: {month_name} {year_val})"), sub_style))
    story.append(Paragraph(fix_arabic(f"المحفظة: {teacher_name}  |  المركز: {center_name}"), sub_style))
    story.append(Spacer(1, 4))
    
    table_headers = [fix_arabic("الإنصراف"), fix_arabic("الحضور"), fix_arabic("الحالة"), fix_arabic("اليوم"), fix_arabic("التاريخ")]
    pdf_table_data = [table_headers]
    
    row_styles = [
        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#9683EC')),
        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
        ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
        ('FONTSIZE', (0,0), (-1,0), 8),
        ('BOTTOMPADDING', (0,0), (-1,0), 3),
        ('TOPPADDING', (0,0), (-1,0), 3),
        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDD6F3')),
        ('FONTSIZE', (0,1), (-1,-1), 8),
        ('BOTTOMPADDING', (0,1), (-1,-1), 2.5),
        ('TOPPADDING', (0,1), (-1,-1), 2.5),
    ]
    
    for idx, (_, row) in enumerate(att_df.iterrows(), start=1):
        pdf_table_data.append([
            fix_arabic(row.get('check_out', '')),
            fix_arabic(row.get('check_in', '')),
            fix_arabic(row.get('status', '')),
            fix_arabic(row.get('day_name', '')),
            str(row.get('date', ''))
        ])
        
        status_val = str(row.get('status', ''))
        if "عطلة" in status_val:
            row_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#EAE5F7')))
        elif "إجازة" in status_val:
            row_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#FEF3C7')))
        elif "غياب" in status_val:
            row_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#FEE2E2')))
        else:
            row_styles.append(('BACKGROUND', (0, idx), (-1, idx), colors.HexColor('#FFFFFF')))
        
    col_widths = [100, 100, 100, 100, 114]
    
    t = Table(pdf_table_data, colWidths=col_widths, hAlign='CENTER')
    t.setStyle(TableStyle(row_styles))
    
    story.append(t)
    doc.build(story)
    buffer.seek(0)
    return buffer

if 'logged_in' not in st.session_state:
    st.session_state['logged_in'] = False
    st.session_state['current_username'] = None
    st.session_state['current_user'] = None
    st.session_state['role'] = None
    st.session_state['center'] = None

if not st.session_state['logged_in']:
    col1, col2, col3 = st.columns([0.15, 0.7, 0.15])
    with col2:
        st.markdown('<div class="login-container">', unsafe_allow_html=True)
        with st.container(border=True):
            st.markdown("### 🔐 تسجيل الدخول للمنظومة", unsafe_allow_html=True)
            with st.form("login_form"):
                username_input = st.text_input("اسم المستخدمة أو رقم الهاتف")
                password_input = st.text_input("كلمة المرور", type="password")
                submit_login = st.form_submit_button("تسجيل الدخول", use_container_width=True)
                
                if submit_login:
                    users_df = load_users()
                    if not users_df.empty:
                        user_clean = str(username_input).strip()
                        pass_clean = str(password_input).strip()
                        
                        matched_user = users_df[
                            (
                                (users_df['username'].astype(str).str.strip() == user_clean) | 
                                (users_df['name'].astype(str).str.strip() == user_clean)
                            ) & 
                            (users_df['password'].astype(str).str.strip() == pass_clean)
                        ]
                        
                        if not matched_user.empty:
                            st.session_state['logged_in'] = True
                            st.session_state['current_username'] = str(matched_user.iloc[0]['username']).strip()
                            st.session_state['current_user'] = str(matched_user.iloc[0]['name']).strip()
                            st.session_state['role'] = str(matched_user.iloc[0]['role']).strip()
                            center_val = matched_user.iloc[0].get('center', '')
                            st.session_state['center'] = str(center_val).strip() if pd.notna(center_val) else ""
                            st.success("تم تسجيل الدخول بنجاح!")
                            st.rerun()
                        else:
                            st.error("اسم المستخدمة (أو رقم الهاتف) أو كلمة المرور غير صحيحة.")
                    else:
                        st.error("لا توجد بيانات مستخدمين متاحة.")
        st.markdown('</div>', unsafe_allow_html=True)
else:
    col_info, col_btn = st.columns([3, 1])
    with col_info:
        st.markdown(f"""
            <div class="user-top-bar">
                <span>👤 <b>المستخدمة:</b> {st.session_state['current_user']}</span>
                <span>🛡️ <b>الصلاحية:</b> {st.session_state['role']}</span>
            </div>
        """, unsafe_allow_html=True)
    with col_btn:
        if st.button("خروج", use_container_width=True):
            st.session_state['logged_in'] = False
            st.session_state['current_username'] = None
            st.session_state['current_user'] = None
            st.session_state['role'] = None
            st.session_state['center'] = None
            st.rerun()
    
    # واجهة مدير/مديرة المكتب (الإدارة العامة)
    if st.session_state['role'] == "إدارة المكتب":
        st.markdown(f"""
            <div class="teacher-banner">
                <span>📊 <b>لوحة تحكم إدارة المكتب</b></span>
                <span>🕌 <b>النطاق:</b> إدارة النظام، المستخدمات، استخراج التقارير، والإحصائيات الشاملة</span>
            </div>
        """, unsafe_allow_html=True)
        
        st.markdown("<br>", unsafe_allow_html=True)
        
        admin_tab1, admin_tab2, admin_tab3, admin_tab4, admin_tab5, admin_tab6, admin_tab7 = st.tabs([
            "📈 الإحصائيات الشاملة",
            "📄 تقارير المحفظة",
            "👩‍🏫 المحفظات",
            "🔗 تعيين الموجهات والمتابعات",
            "➕ إضافة مستخدمة",
            "👥 إدارة المستخدمات",
            "🔑 تغيير كلمة السر"
        ])
        
        months_names = {
            1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
            7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
        }
        
        users_df = load_users()
        teachers_list_df = users_df[users_df['role'].isin(['محفظة', 'محفظ'])]
        students_df = load_students()

        with admin_tab1:
            st.markdown('<div class="section-header">الإحصائيات الشاملة لجميع المراكز والبحث بنطاق السور</div>', unsafe_allow_html=True)
            
            if not students_df.empty:
                regular_students_count = len(students_df[students_df['status'].isin(['منتظمة', 'منتظم'])])
                khatim_count = len(students_df[students_df['status'].isin(['خاتمة', 'خاتم'])])
                inactive_count = len(students_df[students_df['status'].isin(['منقطعة', 'منقولة', 'منقطع', 'منقول'])])
            else:
                regular_students_count = khatim_count = inactive_count = 0
            
            c1, c2, c3 = st.columns(3)
            with c1:
                st.metric("الطالبات المنتظمات", regular_students_count)
            with c2:
                st.metric("الطالبات الخاتمات", khatim_count)
            with c3:
                st.metric("المنقطعات / المنقولات", inactive_count)
                
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<p style="font-weight: bold; color: #4A3E6D; font-size: 15px;">🔍 البحث والتصفية حسب نطاق سورة الحفظ (لجميع المراكز)</p>', unsafe_allow_html=True)
            
            col_s1, col_s2 = st.columns(2)
            with col_s1:
                start_surah_default = "البقرة" if "البقرة" in quran_surahs else quran_surahs[0]
                start_surah = st.selectbox("من سورة (البداية)", options=quran_surahs, index=quran_surahs.index(start_surah_default), key="stat_start_surah")
            with col_s2:
                end_surah_default = "مريم" if "مريم" in quran_surahs else quran_surahs[-1]
                end_surah = st.selectbox("إلى سورة (النهاية)", options=quran_surahs, index=quran_surahs.index(end_surah_default), key="stat_end_surah")
            
            start_idx = quran_surahs.index(start_surah)
            end_idx = quran_surahs.index(end_surah)
            
            min_idx = min(start_idx, end_idx)
            max_idx = max(start_idx, end_idx)
            allowed_surahs = quran_surahs[min_idx:max_idx+1]
            
            if not students_df.empty:
                filtered_by_range = students_df[
                    (students_df['memorization'].isin(allowed_surahs)) & 
                    (students_df['status'].isin(['منتظمة', 'منتظم']))
                ].copy()
                filtered_by_range = sort_students_by_memorization(filtered_by_range)
            else:
                filtered_by_range = pd.DataFrame()
            
            st.markdown(f"**عدد الطالبات المنتظمات الواقعات في هذا النطاق ({start_surah} إلى {end_surah}):** {len(filtered_by_range)} طالبة")
            
            if not filtered_by_range.empty:
                display_range_df = filtered_by_range[['name', 'center', 'teacher', 'memorization', 'status', 'birth_year']].rename(columns={
                    'name': 'اسم الطالبة',
                    'center': 'المركز / المسجد',
                    'teacher': 'المحفظة',
                    'memorization': 'آخر سورة محفوظة',
                    'status': 'الحالة',
                    'birth_year': 'سنة الميلاد'
                })
                st.dataframe(display_range_df, use_container_width=True, hide_index=True)
            else:
                st.info("لا توجد سجلات طالبات منتظمات تطابق هذا النطاق من السور.")

        with admin_tab2:
            st.markdown('<div class="section-header">استخراج وتحميل تقارير الـ PDF للمحفظة</div>', unsafe_allow_html=True)
            
            if teachers_list_df.empty:
                st.warning("لا يوجد محفظات مسجلات في النظام حالياً.")
            else:
                teacher_options = dict(zip(teachers_list_df['name'], teachers_list_df['username']))
                selected_teacher_name = st.selectbox("اختر المحفظة المطلوبة", options=list(teacher_options.keys()), key="admin_sel_teacher_inside_tab")
                selected_teacher_username = teacher_options[selected_teacher_name]
                
                t_row_info = teachers_list_df[teachers_list_df['username'] == selected_teacher_username].iloc[0]
                selected_teacher_center = t_row_info.get('center', '')
                
                st.info(f"🕌 المحفظة: **{selected_teacher_name}** | المركز: **{selected_teacher_center}**")
                
                if not students_df.empty:
                    t_students = students_df[students_df['teacher'] == selected_teacher_name]
                    t_reg_count = len(t_students[t_students['status'].isin(['منتظمة', 'منتظم'])])
                    t_khatim_count = len(t_students[t_students['status'].isin(['خاتمة', 'خاتم'])])
                    t_inactive_count = len(t_students[t_students['status'].isin(['منقطعة', 'منقولة', 'منقطع', 'منقول'])])
                else:
                    t_reg_count = t_khatim_count = t_inactive_count = 0

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<h5 style="text-align: right;">📊 إحصائية المحفظة:</h5>', unsafe_allow_html=True)
                sc2, sc3, sc4 = st.columns(3)
                with sc2:
                    st.metric("المنتظمات", t_reg_count)
                with sc3:
                    st.metric("الخاتمات", t_khatim_count)
                with sc4:
                    st.metric("المنقطعات / المنقولات", t_inactive_count)
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                report_options = [
                    "كشف الطالبات المنتظمات بالحلقة",
                    "سجل حضور وانصراف المحفظة الشهري",
                    "كشف الطالبات الخاتمات لكتاب الله",
                    "كشف الطالبات المنقطعات والمنتقلات"
                ]
                sub_pdf_choice = st.selectbox(
                    "اختر نوع التقرير المطلوب",
                    options=report_options,
                    index=0,
                    key="admin_pdf_type_select"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                
                if "سجل حضور وانصراف المحفظة" in sub_pdf_choice:
                    col_y1, col_m1 = st.columns(2)
                    with col_y1:
                        adm_t_year = st.selectbox("السنة", [2026, 2027, 2025], index=0, key="adm_t_yr")
                    with col_m1:
                        adm_t_month = st.selectbox("الشهر", options=list(months_names.keys()), format_func=lambda x: months_names[x], index=datetime.date.today().month - 1, key="adm_t_mo")
                    
                    month_days_full = get_month_days_list(adm_t_year, adm_t_month)
                    start_d = month_days_full[0]['date']
                    end_d = month_days_full[-1]['date']
                    
                    t_records_db = {}
                    if supabase is not None:
                        try:
                            res = supabase.table("teacher_attendance").select("date, status, check_in, check_out").eq("username", selected_teacher_username).gte("date", start_d).lte("date", end_d).execute()
                            t_records_db = {row['date']: {"status": row['status'], "check_in": row['check_in'], "check_out": row['check_out']} for row in res.data}
                        except:
                            pass
                    
                    full_rows = []
                    for d_info in month_days_full:
                        d_s = d_info['date']
                        d_n = d_info['day_name']
                        is_w = d_info['is_weekend']
                        if d_s in t_records_db:
                            st_v = t_records_db[d_s]["status"]
                            ci_v = t_records_db[d_s]["check_in"] if t_records_db[d_s]["check_in"] else ""
                            co_v = t_records_db[d_s]["check_out"] if t_records_db[d_s]["check_out"] else ""
                        else:
                            st_v = "عطلة" if is_w else "حضور"
                            ci_v = ""
                            co_v = ""
                        full_rows.append({"status": st_v, "check_out": co_v, "check_in": ci_v, "date": d_s, "day_name": d_n})
                    
                    adm_t_month_df = pd.DataFrame(full_rows)
                    adm_t_pdf_buffer = generate_teacher_attendance_pdf(
                        selected_teacher_name, 
                        selected_teacher_center, 
                        months_names[adm_t_month], 
                        adm_t_year, 
                        adm_t_month_df
                    )
                    st.download_button(
                        label=f"📥 تحميل سجل حضور المحفظة ({selected_teacher_name}) PDF",
                        data=adm_t_pdf_buffer,
                        file_name=f"teacher_attendance_{selected_teacher_name}_{months_names[adm_t_month]}_{adm_t_year}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                elif "الطالبات المنتظمات" in sub_pdf_choice:
                    if not students_df.empty:
                        adm_reg_df = students_df[(students_df['teacher'] == selected_teacher_name) & (students_df['status'].isin(['منتظمة', 'منتظم']))]
                        adm_reg_df = sort_students_by_memorization(adm_reg_df)
                        if not adm_reg_df.empty:
                            adm_reg_pdf = generate_students_list_pdf(selected_teacher_name, selected_teacher_center, adm_reg_df, "كشف الطالبات المنتظمات بالحلقة")
                            st.download_button(
                                label="📥 تحميل كشف المنتظمات (PDF)",
                                data=adm_reg_pdf,
                                file_name=f"regular_students_{selected_teacher_name}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("لا توجد سجلات طالبات منتظمات لهذه الحلقة.")
                    else:
                        st.info("لا توجد بيانات طالبات في النظام.")
                
                elif "الطالبات الخاتمات" in sub_pdf_choice:
                    if not students_df.empty:
                        adm_khatim_df = students_df[(students_df['teacher'] == selected_teacher_name) & (students_df['status'].isin(['خاتمة', 'خاتم']))]
                        adm_khatim_df = sort_students_by_memorization(adm_khatim_df)
                        if not adm_khatim_df.empty:
                            adm_k_pdf = generate_students_list_pdf(selected_teacher_name, selected_teacher_center, adm_khatim_df, "كشف الطالبات الخاتمات لكتاب الله")
                            st.download_button(
                                label="📥 تحميل كشف الخاتمات (PDF)",
                                data=adm_k_pdf,
                                file_name=f"khatim_students_{selected_teacher_name}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("لا توجد سجلات طالبات خاتمات لهذه الحلقة.")
                    else:
                        st.info("لا توجد بيانات طالبات في النظام.")
                
                elif "المنقطعات والمنتقلات" in sub_pdf_choice:
                    if not students_df.empty:
                        adm_drop_df = students_df[(students_df['teacher'] == selected_teacher_name) & (students_df['status'].isin(["منقطعة", "منقولة", "منقطع", "منقول"]))]
                        adm_drop_df = sort_students_by_memorization(adm_drop_df)
                        if not adm_drop_df.empty:
                            adm_d_pdf = generate_students_list_pdf(selected_teacher_name, selected_teacher_center, adm_drop_df, "كشف الطالبات المنقطعات والمنتقلات")
                            st.download_button(
                                label="📥 تحميل كشف المنقطعات (PDF)",
                                data=adm_d_pdf,
                                file_name=f"inactive_students_{selected_teacher_name}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("لا توجد سجلات طالبات منقطعات أو منتقلات لهذه الحلقة.")
                    else:
                        st.info("لا توجد بيانات طالبات في النظام.")

        with admin_tab3:
            st.markdown('<div class="section-header">قائمة المحفظات مرتبة حسب عدد الطالبات المنتظمات، مركز التحفيظ، واسم المحفظة</div>', unsafe_allow_html=True)
            with st.container(border=True):
                if not teachers_list_df.empty:
                    teachers_summary_list = []
                    for _, t_row in teachers_list_df.iterrows():
                        t_name = str(t_row.get('name', '')).strip()
                        t_center = str(t_row.get('center', '')).strip()
                        t_phone = str(t_row.get('username', '')).strip()
                        
                        if not students_df.empty:
                            reg_count = len(students_df[(students_df['teacher'] == t_name) & (students_df['status'].isin(['منتظمة', 'منتظم']))])
                        else:
                            reg_count = 0
                            
                        teachers_summary_list.append({
                            'name': t_name,
                            'center': t_center,
                            'phone': t_phone,
                            'regular_count': reg_count
                        })
                    
                    df_teachers_summary = pd.DataFrame(teachers_summary_list)
                    df_teachers_summary = df_teachers_summary.sort_values(
                        by=['regular_count', 'center', 'name'], 
                        ascending=[False, True, True]
                    )
                    
                    df_teachers_display = df_teachers_summary.rename(columns={
                        'regular_count': 'عدد الطالبات المنتظمات',
                        'center': 'مركز التحفيظ / المسجد',
                        'name': 'اسم المحفظة'
                    })[['عدد الطالبات المنتظمات', 'مركز التحفيظ / المسجد', 'اسم المحفظة']]
                    
                    st.dataframe(df_teachers_display, use_container_width=True, hide_index=True)
                    
                    st.markdown("<br>", unsafe_allow_html=True)
                    teachers_pdf_buffer = generate_teachers_summary_pdf(df_teachers_summary)
                    st.download_button(
                        label="📥 تحميل كشف المحفظات والطالبات المنتظمات (PDF)",
                        data=teachers_pdf_buffer,
                        file_name="teachers_summary_report.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                else:
                    st.info("لا يوجد محفظات مسجلات في النظام حالياً.")

        with admin_tab4:
            st.markdown('<div class="section-header">تعيين الموجهات والمتابعات للمحفظات</div>', unsafe_allow_html=True)
            st.markdown('<p style="color: #4B5563; font-size: 12px;">اختر اسم المحفظة لتظهر لك خانة الموجهة والمتابعة الخاصة بها، ثم اضغط على زر الحفظ.</p>', unsafe_allow_html=True)
            
            with st.container(border=True):
                if teachers_list_df.empty:
                    st.warning("لا يوجد محفظات مسجلات في النظام.")
                else:
                    supervisors_list = users_df[users_df['role'].isin(['الموجهة', 'الموجه'])]['name'].tolist()
                    followers_list = users_df[users_df['role'].isin(['المتابعة', 'المتابع'])]['name'].tolist()
                    
                    teacher_names_options = teachers_list_df['name'].tolist()
                    selected_assign_teacher_name = st.selectbox(
                        "اختر اسم المحفظة",
                        options=teacher_names_options,
                        key="admin_select_teacher_for_assignment"
                    )
                    
                    if selected_assign_teacher_name:
                        t_row = teachers_list_df[teachers_list_df['name'] == selected_assign_teacher_name].iloc[0]
                        t_username = str(t_row['username'])
                        t_center = str(t_row.get('center', ''))
                        curr_sup = str(t_row.get('assigned_supervisor', ''))
                        curr_fol = str(t_row.get('assigned_follower', ''))
                        
                        exp_assign_key = f"assign_exp_{t_username}"
                        is_assign_expanded = st.session_state.get(exp_assign_key, True)
                        
                        with st.expander(f"👩‍🏫 {selected_assign_teacher_name} - المركز: ({t_center if t_center else 'بدون مركز'})", expanded=is_assign_expanded):
                            sup_idx = supervisors_list.index(curr_sup) if curr_sup in supervisors_list else 0
                            fol_idx = followers_list.index(curr_fol) if curr_fol in followers_list else 0
                            
                            col_s, col_f = st.columns(2)
                            with col_s:
                                chosen_sup = st.selectbox(
                                    "خانة الموجهة", 
                                    options=[""] + supervisors_list, 
                                    index=(supervisors_list.index(curr_sup) + 1) if curr_sup in supervisors_list else 0, 
                                    key=f"sup_assign_{t_username}"
                                )
                            with col_f:
                                chosen_fol = st.selectbox(
                                    "خانة المتابعة", 
                                    options=[""] + followers_list, 
                                    index=(followers_list.index(curr_fol) + 1) if curr_fol in followers_list else 0, 
                                    key=f"fol_assign_{t_username}"
                                )
                            
                            st.markdown("<br>", unsafe_allow_html=True)
                            if st.button(f"حفظ التعيينات للمحفظة: {selected_assign_teacher_name}", key=f"save_assign_btn_{t_username}"):
                                update_teacher_permissions(t_username, chosen_sup, chosen_fol)
                                st.success(f"✅ تم حفظ تعيينات الموجهة والمتابعة للمحفظة ({selected_assign_teacher_name}) بنجاح!")
                                st.rerun()

        with admin_tab5:
            st.markdown('<div class="section-header">إضافة مستخدمة جديدة وإعطاؤها كلمة السر المبدئية</div>', unsafe_allow_html=True)
            with st.container(border=True):
                with st.form("admin_add_user_form", clear_on_submit=True):
                    new_u_username = st.text_input("رقم الهاتف")
                    new_u_pass = st.text_input("كلمة المرور المبدئية", type="password")
                    new_u_name = st.text_input("الاسم الرباعي أو اللقب")
                    new_u_role = st.selectbox("الصلاحية", options=["محفظة", "الموجهة", "المتابعة", "إدارة المكتب"])
                    new_u_center = st.text_input("اسم مركز التحفيظ أو المسجد (اختياري)")
                    
                    submit_user = st.form_submit_button("حفظ وإنشاء المستخدمة الجديدة", use_container_width=True)
                    if submit_user:
                        if new_u_username.strip() and new_u_pass.strip() and new_u_name.strip():
                            success = add_user_to_db(new_u_username.strip(), new_u_pass.strip(), new_u_role, new_u_name.strip(), new_u_center.strip())
                            if success:
                                st.success(f"✅ تم إنشاء حساب المستخدمة ({new_u_name}) برقم الهاتف وصلاحية ({new_u_role}) بنجاح!")
                                st.rerun()
                            else:
                                st.error("❌ حدث خطأ أثناء الحفظ في قاعدة البيانات.")
                        else:
                            st.warning("الرجاء ملء الحقول الأساسية (رقم الهاتف، كلمة المرور، والاسم).")

        with admin_tab6:
            st.markdown('<div class="section-header">إدارة المستخدمات وصلاحياتهن</div>', unsafe_allow_html=True)
            with st.container(border=True):
                current_users_df = load_users()
                
                display_cols = ['username', 'password', 'role', 'name', 'center']
                if 'assigned_supervisor' in current_users_df.columns:
                    display_cols.append('assigned_supervisor')
                if 'assigned_follower' in current_users_df.columns:
                    display_cols.append('assigned_follower')

                display_users_df = current_users_df[display_cols].rename(columns={
                    'username': 'رقم الهاتف',
                    'password': 'كلمة المرور',
                    'role': 'الصلاحية',
                    'name': 'الاسم',
                    'center': 'المركز / المسجد',
                    'assigned_supervisor': 'الموجهة المعتمدة',
                    'assigned_follower': 'المتابعة المعتمدة'
                })
                
                st.dataframe(display_users_df, use_container_width=True, hide_index=True)
                
                st.markdown('<p style="text-align: right; font-weight: bold; font-size: 15px; color: #4A3E6D; margin-top: 15px; margin-bottom: 10px;">حذف مستخدمة من النظام</p>', unsafe_allow_html=True)
                
                current_logged_username = str(st.session_state.get('current_username', '')).strip()
                removable_users = current_users_df[current_users_df['username'].astype(str).str.strip() != current_logged_username]['username'].tolist()

                if removable_users:
                    user_to_delete = st.selectbox(
                        "اختر رقم هاتف المستخدمة للحذف",
                        options=removable_users,
                        index=None,
                        placeholder="اختر مستخدمة لحذفها...",
                        key="admin_del_usr_box"
                    )
                    
                    if st.button("حذف المستخدمة المختارة"):
                        if user_to_delete is None:
                            st.warning("⚠️ يرجى اختيار مستخدمة من القائمة المنسدلة أولاً.")
                        else:
                            target_user_row = current_users_df[current_users_df['username'].astype(str).str.strip() == str(user_to_delete).strip()]
                            if not target_user_row.empty:
                                delete_user_from_db(user_to_delete)
                                st.success(f"تم حذف المستخدمة برقم الهاتف ({user_to_delete}) بنجاح!")
                                st.rerun()
                else:
                    st.info("لا توجد حسابات أخرى يمكن حذفها.")

        with admin_tab7:
            st.markdown('<div class="section-header">تغيير كلمة المرور الخاصة بحسابك (إدارة المكتب)</div>', unsafe_allow_html=True)
            with st.container(border=True):
                with st.form("admin_change_pass_form"):
                    old_pass = st.text_input("كلمة المرور الحالية", type="password")
                    new_pass = st.text_input("كلمة المرور الجديدة", type="password")
                    confirm_pass = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
                    submit_pass = st.form_submit_button("تحديث كلمة المرور", use_container_width=True)
                    
                    if submit_pass:
                        curr_uname = st.session_state['current_username']
                        users_df = load_users()
                        user_row = users_df[users_df['username'].astype(str) == str(curr_uname)]
                        if not user_row.empty:
                            pass_val = str(user_row.iloc[0]['password'])
                            if pass_val == old_pass:
                                if new_pass.strip() and new_pass == confirm_pass:
                                    update_password_in_db(curr_uname, new_pass.strip())
                                    st.success("✅ تم تغيير كلمة المرور بنجاح!")
                                else:
                                    st.error("❌ كلمة المرور الجديدة غير متطابقة أو فارغة.")
                            else:
                                st.error("❌ كلمة المرور الحالية غير صحيحة.")

    elif st.session_state['role'] in ["الموجهة", "المتابعة", "الموجه", "المتابع"]:
        role_title = st.session_state['role']
        st.markdown(f"""
            <div class="teacher-banner">
                <span>📋 <b>لوحة تقارير {role_title}</b></span>
                <span>🔍 <b>الصلاحية:</b> متابعة الحلقات واستخراج تقارير PDF للمحفظات المخصصات لكِ</span>
            </div>
        """, unsafe_allow_html=True)
        
        users_df = load_users()
        current_logged_name = st.session_state['current_user']
        students_df = load_students()
        
        sup_main_tab1, sup_main_tab2, sup_main_tab3 = st.tabs([
            "📋 المحفظات التابعات وعدد الطالبات",
            "📄 تقارير المحفظة والطالبات (PDF)",
            "🔑 تغيير كلمة المرور"
        ])
        
        with sup_main_tab1:
            st.markdown(f'<div class="section-header">قائمة المحفظات، مراكز التحفيظ، وإجمالي عدد الطالبات المنتظمات التابعات لـ ({role_title}: {current_logged_name})</div>', unsafe_allow_html=True)
            
            if role_title in ["الموجهة", "الموجه"]:
                assigned_teachers_df = users_df[(users_df['role'].isin(['محفظة', 'محفظ'])) & (users_df['assigned_supervisor'] == current_logged_name)]
            else:
                assigned_teachers_df = users_df[(users_df['role'].isin(['محفظة', 'محفظ'])) & (users_df['assigned_follower'] == current_logged_name)]
                
            if not assigned_teachers_df.empty:
                summary_data = []
                for _, t_row in assigned_teachers_df.iterrows():
                    t_name = str(t_row.get('name', '')).strip()
                    t_center = str(t_row.get('center', '')).strip()
                    
                    if not students_df.empty:
                        reg_count = len(students_df[(students_df['teacher'] == t_name) & (students_df['status'].isin(['منتظمة', 'منتظم']))])
                    else:
                        reg_count = 0
                        
                    summary_data.append({
                        'اسم المحفظة': t_name,
                        'مركز التحفيظ / المسجد': t_center,
                        'عدد الطالبات المنتظمات': reg_count
                    })
                
                df_assigned_summary = pd.DataFrame(summary_data)
                st.dataframe(df_assigned_summary, use_container_width=True, hide_index=True)
            else:
                st.info(f"لا توجد حلقات محفظات مخصصة لحسابك ({role_title}) حالياً.")

        with sup_main_tab2:
            if role_title in ["الموجهة", "الموجه"]:
                allowed_teachers_df = users_df[(users_df['role'].isin(['محفظة', 'محفظ'])) & (users_df['assigned_supervisor'] == current_logged_name)]
            else:
                allowed_teachers_df = users_df[(users_df['role'].isin(['محفظة', 'محفظ'])) & (users_df['assigned_follower'] == current_logged_name)]
                
            if allowed_teachers_df.empty:
                st.warning(f"⚠️ لا توجد حلقات محفظات مخصصة لحسابك ({role_title}) حالياً لرؤية تقاريرها.")
            else:
                teacher_options = dict(zip(allowed_teachers_df['name'], allowed_teachers_df['username']))
                selected_teacher_name = st.selectbox("اختر المحفظة المطلوبة", options=list(teacher_options.keys()), key="sup_sel_teacher_inside_tab")
                selected_teacher_username = teacher_options[selected_teacher_name]
                
                t_row_info = allowed_teachers_df[allowed_teachers_df['username'] == selected_teacher_username].iloc[0]
                selected_teacher_center = t_row_info.get('center', '')
                
                st.info(f"🕌 المحفظة: **{selected_teacher_name}** | المركز: **{selected_teacher_center}**")
                
                if not students_df.empty:
                    t_students = students_df[students_df['teacher'] == selected_teacher_name]
                    t_reg_count = len(t_students[t_students['status'].isin(['منتظمة', 'منتظم'])])
                    t_khatim_count = len(t_students[t_students['status'].isin(['خاتمة', 'خاتم'])])
                    t_inactive_count = len(t_students[t_students['status'].isin(['منقطعة', 'منقولة', 'منقطع', 'منقول'])])
                else:
                    t_reg_count = t_khatim_count = t_inactive_count = 0

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<h5 style="text-align: right;">📊 إحصائية المحفظة:</h5>', unsafe_allow_html=True)
                sc2, sc3, sc4 = st.columns(3)
                with sc2:
                    st.metric("المنتظمات", t_reg_count)
                with sc3:
                    st.metric("الخاتمات", t_khatim_count)
                with sc4:
                    st.metric("المنقطعات / المنقولات", t_inactive_count)
                
                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown('<div class="section-header">استخراج وتحميل تقارير الـ PDF للمحفظة</div>', unsafe_allow_html=True)
                
                sup_report_options = [
                    "كشف الطالبات المنتظمات بالحلقة",
                    "سجل حضور وانصراف المحفظة الشهري",
                    "كشف الطالبات الخاتمات لكتاب الله",
                    "كشف الطالبات المنقطعات والمنتقلات"
                ]
                sub_sup_pdf_choice = st.selectbox(
                    "اختر نوع التقرير المطلوب",
                    options=sup_report_options,
                    index=0,
                    key="sup_pdf_type_select"
                )
                
                st.markdown("<br>", unsafe_allow_html=True)
                months_names = {
                    1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
                    7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
                }
                
                if "سجل حضور وانصراف المحفظة" in sub_sup_pdf_choice:
                    col_y1, col_m1 = st.columns(2)
                    with col_y1:
                        sup_t_year = st.selectbox("السنة", [2026, 2027, 2025], index=0, key="sup_t_yr")
                    with col_m1:
                        sup_t_month = st.selectbox("الشهر", options=list(months_names.keys()), format_func=lambda x: months_names[x], index=datetime.date.today().month - 1, key="sup_t_mo")
                    
                    month_days_full = get_month_days_list(sup_t_year, sup_t_month)
                    start_d = month_days_full[0]['date']
                    end_d = month_days_full[-1]['date']
                    
                    t_records_db = {}
                    if supabase is not None:
                        try:
                            res = supabase.table("teacher_attendance").select("date, status, check_in, check_out").eq("username", selected_teacher_username).gte("date", start_d).lte("date", end_d).execute()
                            t_records_db = {row['date']: {"status": row['status'], "check_in": row['check_in'], "check_out": row['check_out']} for row in res.data}
                        except:
                            pass
                    
                    full_rows = []
                    for d_info in month_days_full:
                        d_s = d_info['date']
                        d_n = d_info['day_name']
                        is_w = d_info['is_weekend']
                        if d_s in t_records_db:
                            st_v = t_records_db[d_s]["status"]
                            ci_v = t_records_db[d_s]["check_in"] if t_records_db[d_s]["check_in"] else ""
                            co_v = t_records_db[d_s]["check_out"] if t_records_db[d_s]["check_out"] else ""
                        else:
                            st_v = "عطلة" if is_w else "حضور"
                            ci_v = ""
                            co_v = ""
                        full_rows.append({"status": st_v, "check_out": co_v, "check_in": ci_v, "date": d_s, "day_name": d_n})
                    
                    sup_t_month_df = pd.DataFrame(full_rows)
                    sup_t_pdf_buffer = generate_teacher_attendance_pdf(
                        selected_teacher_name, 
                        selected_teacher_center, 
                        months_names[sup_t_month], 
                        sup_t_year, 
                        sup_t_month_df
                    )
                    st.download_button(
                        label=f"📥 تحميل سجل حضور المحفظة ({selected_teacher_name}) PDF",
                        data=sup_t_pdf_buffer,
                        file_name=f"teacher_attendance_{selected_teacher_name}_{months_names[sup_t_month]}_{sup_t_year}.pdf",
                        mime="application/pdf",
                        use_container_width=True
                    )
                
                elif "الطالبات المنتظمات" in sub_sup_pdf_choice:
                    if not students_df.empty:
                        sup_reg_df = students_df[(students_df['teacher'] == selected_teacher_name) & (students_df['status'].isin(['منتظمة', 'منتظم']))]
                        sup_reg_df = sort_students_by_memorization(sup_reg_df)
                        if not sup_reg_df.empty:
                            sup_reg_pdf = generate_students_list_pdf(selected_teacher_name, selected_teacher_center, sup_reg_df, "كشف الطالبات المنتظمات بالحلقة")
                            st.download_button(
                                label="📥 تحميل كشف المنتظمات (PDF)",
                                data=sup_reg_pdf,
                                file_name=f"regular_students_{selected_teacher_name}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("لا توجد سجلات طالبات منتظمات.")
                    else:
                        st.info("لا توجد بيانات طالبات في النظام.")
                
                elif "الطالبات الخاتمات" in sub_sup_pdf_choice:
                    if not students_df.empty:
                        sup_khatim_df = students_df[(students_df['teacher'] == selected_teacher_name) & (students_df['status'].isin(['خاتمة', 'خاتم']))]
                        sup_khatim_df = sort_students_by_memorization(sup_khatim_df)
                        if not sup_khatim_df.empty:
                            sup_k_pdf = generate_students_list_pdf(selected_teacher_name, selected_teacher_center, sup_khatim_df, "كشف الطالبات الخاتمات لكتاب الله")
                            st.download_button(
                                label="📥 تحميل كشف الخاتمات (PDF)",
                                data=sup_k_pdf,
                                file_name=f"khatim_students_{selected_teacher_name}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("لا توجد سجلات طالبات خاتمات.")
                    else:
                        st.info("لا توجد بيانات طالبات في النظام.")
                
                elif "المنقطعات والمنتقلات" in sub_sup_pdf_choice:
                    if not students_df.empty:
                        sup_drop_df = students_df[(students_df['teacher'] == selected_teacher_name) & (students_df['status'].isin(["منقطعة", "منقولة", "منقطع", "منقول"]))]
                        sup_drop_df = sort_students_by_memorization(sup_drop_df)
                        if not sup_drop_df.empty:
                            sup_d_pdf = generate_students_list_pdf(selected_teacher_name, selected_teacher_center, sup_drop_df, "كشف الطالبات المنقطعات والمنتقلات")
                            st.download_button(
                                label="📥 تحميل كشف المنقطعات (PDF)",
                                data=sup_d_pdf,
                                file_name=f"inactive_students_{selected_teacher_name}.pdf",
                                mime="application/pdf",
                                use_container_width=True
                            )
                        else:
                            st.info("لا توجد سجلات طالبات منقطعات أو منتقلات.")
                    else:
                        st.info("لا توجد بيانات طالبات في النظام.")

        with sup_main_tab3:
            st.markdown('<div class="section-header">تغيير كلمة المرور الخاصة بحسابك</div>', unsafe_allow_html=True)
            with st.container(border=True):
                with st.form("sup_change_pass_form"):
                    old_pass = st.text_input("كلمة المرور الحالية", type="password")
                    new_pass = st.text_input("كلمة المرور الجديدة", type="password")
                    confirm_pass = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
                    submit_pass = st.form_submit_button("تحديث كلمة المرور", use_container_width=True)
                    
                    if submit_pass:
                        curr_uname = st.session_state['current_username']
                        users_df = load_users()
                        user_row = users_df[users_df['username'].astype(str) == str(curr_uname)]
                        if not user_row.empty:
                            pass_val = str(user_row.iloc[0]['password'])
                            if pass_val == old_pass:
                                if new_pass.strip() and new_pass == confirm_pass:
                                    update_password_in_db(curr_uname, new_pass.strip())
                                    st.success("✅ تم تغيير كلمة المرور بنجاح!")
                                else:
                                    st.error("❌ كلمة المرور الجديدة غير متطابقة أو فارغة.")
                            else:
                                st.error("❌ كلمة المرور الحالية غير صحيحة.")

    elif st.session_state['role'] in ["محفظة", "محفظ"]:
        st.markdown(f"""
            <div class="teacher-banner">
                <span>👩‍🏫 <b>المحفظة:</b> {st.session_state['current_user']}</span>
                <span>🕌 <b>المركز:</b> {st.session_state['center']}</span>
            </div>
        """, unsafe_allow_html=True)
        
        students_df = load_students()
        users_df = load_users()
        teacher_name = st.session_state['current_user']
        username = st.session_state['current_username']
        
        tab1, tab2, tab3, tab4, tab5, tab6, tab7, tab8 = st.tabs([
            "⏳ حضوري",
            "📚 الطالبات", 
            "➕ إضافة طالبة",
            "📉 كشف حضور الطالبات",
            "🌟 الخاتمات", 
            "⚠️ المنقطعات",
            "🛡️ الموجهة والمتابعة",
            "🔑 تغيير كلمة المرور"
        ])

        with tab1:
            st.markdown('<div class="section-header">تسجيل ومتابعة حضور المحفظة اليومي</div>', unsafe_allow_html=True)
            st.markdown('<p style="color: #4B5563; font-size: 12px;">اختر التاريخ لتسجيل أو تعديل حالة الدوام وساعتي الحضور والانصراف بكل سهولة على الهاتف المحمول.</p>', unsafe_allow_html=True)
            
            with st.container(border=True):
                selected_date = st.date_input("التاريخ", value=datetime.date.today(), key="teacher_single_date")
                date_str = selected_date.strftime('%Y-%m-%d')
                day_name_ar = get_arabic_day_name(selected_date)
                
                st.info(f"📅 اليوم: **{day_name_ar}** | التاريخ المختار: **{date_str}**")
                
                existing_record = None
                if supabase is not None:
                    try:
                        res_att = supabase.table("teacher_attendance").select("status, check_in, check_out").eq("username", username).eq("date", date_str).execute()
                        existing_record = res_att.data[0] if res_att.data else None
                    except:
                        pass
                
                if existing_record:
                    def_status = existing_record['status']
                    def_in = existing_record['check_in'] if existing_record['check_in'] else ""
                    def_out = existing_record['check_out'] if existing_record['check_out'] else ""
                else:
                    def_status = "حضور" if day_name_ar not in ['الخميس', 'الجمعة'] else "عطلة"
                    def_in = ""
                    def_out = ""
                
                status_options = ["حضور", "إجازة", "غياب بعذر", "غياب بدون عذر", "عطلة"]
                try:
                    status_idx = status_options.index(def_status)
                except:
                    status_idx = 0
                
                col_st, col_in, col_out = st.columns(3)
                with col_st:
                    chosen_status = st.selectbox("حالة الدوام", options=status_options, index=status_idx, key="single_day_status")
                with col_in:
                    chosen_checkin = st.text_input("ساعة الحضور", value=def_in, placeholder="مثال: 03:00", key="single_day_in")
                with col_out:
                    chosen_checkout = st.text_input("ساعة الانصراف", value=def_out, placeholder="مثال: 06:00", key="single_day_out")
                
                if st.button("💾 حفظ سجل هذا اليوم", use_container_width=True):
                    if supabase is not None:
                        try:
                            res_upsert = supabase.table("teacher_attendance").upsert({
                                "username": username,
                                "date": date_str,
                                "day_name": day_name_ar,
                                "status": chosen_status,
                                "check_in": chosen_checkin,
                                "check_out": chosen_checkout
                            }, on_conflict="username,date").execute()
                            
                            st.success(f"✅ تم حفظ سجل تاريخ {date_str} بنجاح!")
                            st.rerun()
                        except Exception as e:
                            st.error(f"❌ تعذر الحفظ في قاعدة البيانات: {e}")
                    else:
                        st.error("❌ لا يوجد اتصال بقاعدة البيانات.")

            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown('<div class="section-header">تحميل سجل الحضور الشهري للمحفظة (PDF)</div>', unsafe_allow_html=True)
            with st.container(border=True):
                col_py, col_pm = st.columns(2)
                with col_py:
                    t_pdf_year = st.selectbox("السنة", [2026, 2027, 2025], index=0, key="t_pdf_yr")
                with col_pm:
                    months_names = {
                        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
                        7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
                    }
                    t_pdf_month = st.selectbox("الشهر", options=list(months_names.keys()), format_func=lambda x: months_names[x], index=datetime.date.today().month - 1, key="t_pdf_mo")
                
                month_days_full = get_month_days_list(t_pdf_year, t_pdf_month)
                start_d = month_days_full[0]['date']
                end_d = month_days_full[-1]['date']
                
                t_records_db = {}
                if supabase is not None:
                    try:
                        res_monthly = supabase.table("teacher_attendance").select("date, status, check_in, check_out").eq("username", username).gte("date", start_d).lte("date", end_d).execute()
                        t_records_db = {row['date']: {"status": row['status'], "check_in": row['check_in'], "check_out": row['check_out']} for row in res_monthly.data}
                    except:
                        pass
                
                full_rows = []
                for d_info in month_days_full:
                    d_s = d_info['date']
                    d_n = d_info['day_name']
                    is_w = d_info['is_weekend']
                    if d_s in t_records_db:
                        st_v = t_records_db[d_s]["status"]
                        ci_v = t_records_db[d_s]["check_in"] if t_records_db[d_s]["check_in"] else ""
                        co_v = t_records_db[d_s]["check_out"] if t_records_db[d_s]["check_out"] else ""
                    else:
                        st_v = "عطلة" if is_w else "حضور"
                        ci_v = ""
                        co_v = ""
                    full_rows.append({"status": st_v, "check_out": co_v, "check_in": ci_v, "date": d_s, "day_name": d_n})
                
                t_month_df_export = pd.DataFrame(full_rows)
                t_att_pdf_buffer = generate_teacher_attendance_pdf(
                    teacher_name, 
                    st.session_state['center'], 
                    months_names[t_pdf_month], 
                    t_pdf_year, 
                    t_month_df_export
                )
                st.download_button(
                    label="📥 تحميل السجل الشهري للمحفظة (PDF)",
                    data=t_att_pdf_buffer,
                    file_name=f"teacher_attendance_{teacher_name}_{months_names[t_pdf_month]}_{t_pdf_year}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )

        with tab2:
            st.markdown('<div class="section-header">الطالبات المنتظمات بالحلقة (ترتيب تصاعدي من الفاتحة إلى الناس)</div>', unsafe_allow_html=True)
            if not students_df.empty:
                mask = (students_df['teacher'] == teacher_name) & (students_df['status'].isin(["منتظمة", "منتظم"]))
                active_students_df = students_df[mask].copy()
                active_students_df = sort_students_by_memorization(active_students_df)
            else:
                active_students_df = pd.DataFrame()
            
            if not active_students_df.empty:
                search_query = st.text_input("🔍 بحث عن طالبة بالاسم", "", placeholder="اكتب اسم الطالبة للتصفية...")
                if search_query:
                    active_students_df = active_students_df[active_students_df['name'].str.contains(search_query, na=False)]
                
                st.markdown(f"<p style='font-size: 11px; color: #6B7280;'>عدد الطالبات الظاهرات: {len(active_students_df)}</p>", unsafe_allow_html=True)
                
                for _, row in active_students_df.iterrows():
                    s_id = int(row['student_id'])
                    exp_key = f"exp_{s_id}"
                    is_expanded = st.session_state.get(exp_key, False)
                    
                    with st.expander(f"👤 {row['name']}  ({row['memorization']})", expanded=is_expanded):
                        new_name = st.text_input("الاسم الرباعي", value=row['name'], key=f"name_{s_id}")
                        new_yr = st.number_input("سنة الميلاد", value=int(row['birth_year']), key=f"yr_{s_id}")
                        
                        curr_memo = row['memorization']
                        m_idx = quran_surahs.index(curr_memo) if curr_memo in quran_surahs else 0
                        new_memo = st.selectbox(
                            "آخر سورة محفوظة", 
                            options=quran_surahs, 
                            index=m_idx,
                            key=f"memo_{s_id}"
                        )
                        
                        status_choices = ["منتظمة", "منقطعة", "منقولة", "خاتمة", "حذف الطالبة"]
                        new_st = st.selectbox(
                            "الحالة", 
                            options=status_choices, 
                            index=0,
                            key=f"status_{s_id}"
                        )
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"حفظ التعديلات للطالبة: {row['name']}", key=f"save_btn_{s_id}"):
                            if new_st == "حذف الطالبة":
                                delete_student_from_db(s_id)
                                st.success(f"تم حذف الطالبة {row['name']} بنجاح!")
                            else:
                                update_student_in_db(s_id, new_name.strip(), int(new_yr), new_memo, new_st)
                                st.success(f"✅ تم تحديث وتغيير ترتيب الطالبة ({new_name.strip()}) بنجاح وإغلاق القائمة.")
                            st.session_state[exp_key] = False
                            st.rerun()
                
                st.markdown("<br>", unsafe_allow_html=True)
                students_pdf_buffer = generate_students_list_pdf(teacher_name, st.session_state['center'], active_students_df, "كشف الطالبات المنتظمات بالحلقة")
                st.download_button(
                    label="📥 طباعة كشف الطالبات (PDF)",
                    data=students_pdf_buffer,
                    file_name=f"active_students_{teacher_name}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.info("لا توجد طالبات منتظمات حالياً.")

        with tab3:
            st.markdown('<div class="section-header">تسجيل طالبة جديدة بالحلقة</div>', unsafe_allow_html=True)
            with st.container(border=True):
                with st.form("add_student_form", clear_on_submit=True):
                    new_s_name = st.text_input("اسم الطالبة الرباعي")
                    new_s_birth = st.number_input("سنة الميلاد", min_value=1990, max_value=2026, value=2015)
                    new_s_memo = st.selectbox("آخر سورة محفوظة", quran_surahs)
                    add_btn = st.form_submit_button("إضافة الطالبة", use_container_width=True)
                    
                    if add_btn:
                        if new_s_name.strip():
                            add_student_to_db(new_s_name.strip(), int(new_s_birth), st.session_state['center'], teacher_name, new_s_memo)
                            st.success(f"✅ تم إضافة الطالبة ({new_s_name}) بنجاح!")
                            st.rerun()
                        else:
                            st.error("الرجاء إدخال اسم الطالبة.")

        with tab4:
            st.markdown('<div class="section-header">تصدير كشف حضور الطالبات (PDF)</div>', unsafe_allow_html=True)
            st.markdown('<p style="color: #4B5563; font-size: 12px;">تصدير كشف الحضور الشهري للطالبات المنتظمات في ملف PDF عريض (Landscape) مرتبين تصاعدياً حسب سورة الحفظ.</p>', unsafe_allow_html=True)
            
            with st.container(border=True):
                col_py, col_pm = st.columns(2)
                with col_py:
                    pdf_year = st.selectbox("السنة", [2026, 2027, 2025], index=0, key="pdf_year")
                with col_pm:
                    months_names = {
                        1: "يناير", 2: "فبراير", 3: "مارس", 4: "أبريل", 5: "مايو", 6: "يونيو",
                        7: "يوليو", 8: "أغسطس", 9: "سبتمبر", 10: "أكتوبر", 11: "نوفمبر", 12: "ديسمبر"
                    }
                    pdf_month_num = st.selectbox("الشهر", options=list(months_names.keys()), format_func=lambda x: months_names[x], index=datetime.date.today().month - 1, key="pdf_month")
            
            if not students_df.empty:
                active_only_for_pdf = students_df[(students_df['teacher'] == teacher_name) & (students_df['status'].isin(['منتظمة', 'منتظم']))]
                active_only_for_pdf = sort_students_by_memorization(active_only_for_pdf)
            else:
                active_only_for_pdf = pd.DataFrame()
            
            if not active_only_for_pdf.empty:
                def generate_students_monthly_pdf(teacher_name, center_name, month_name, year_val, active_students):
                    buffer = BytesIO()
                    doc = SimpleDocTemplate(buffer, pagesize=landscape(letter), rightMargin=15, leftMargin=15, topMargin=15, bottomMargin=15)
                    story = []
                    
                    styles = getSampleStyleSheet()
                    title_style = ParagraphStyle(
                        'ArabicTitle', parent=styles['Heading1'], fontName=FONT_BOLD, fontSize=20,
                        leading=26, textColor=colors.HexColor('#6B5B95'), alignment=1, spaceAfter=6
                    )
                    sub_style = ParagraphStyle(
                        'ArabicSub', parent=styles['Normal'], fontName=FONT_NAME, fontSize=11,
                        leading=15, textColor=colors.HexColor('#8370B9'), alignment=1, spaceAfter=8
                    )
                    
                    story.append(Paragraph(fix_arabic("مكتب الأوقاف والشؤون الإسلامية - سلوق (قسم الطالبات)"), title_style))
                    story.append(Paragraph(fix_arabic(f"كشف حضور وغياب الطالبات المنتظمات (شهر: {month_name} {year_val})"), sub_style))
                    story.append(Paragraph(fix_arabic(f"المحفظة: {teacher_name}  |  المركز: {center_name}"), sub_style))
                    story.append(Spacer(1, 5))
                    
                    table_headers = [str(i) for i in range(30, 0, -1)] + [fix_arabic("اسم الطالبة"), "م"]
                    pdf_table_data = [table_headers]
                    
                    idx = 1
                    for _, s_row in active_students.iterrows():
                        row_cells = [""] * 30 + [fix_arabic(s_row['name']), str(idx)]
                        pdf_table_data.append(row_cells)
                        idx += 1
                        
                    col_widths = [18] * 30 + [115, 22]
                    
                    t = Table(pdf_table_data, colWidths=col_widths, hAlign='CENTER')
                    t.setStyle(TableStyle([
                        ('BACKGROUND', (0,0), (-1,0), colors.HexColor('#9683EC')),
                        ('TEXTCOLOR', (0,0), (-1,0), colors.whitesmoke),
                        ('ALIGN', (0,0), (-1,-1), 'CENTER'),
                        ('VALIGN', (0,0), (-1,-1), 'MIDDLE'),
                        ('FONTNAME', (0,0), (-1,-1), FONT_NAME),
                        ('FONTSIZE', (0,0), (-1,0), 8),
                        ('BOTTOMPADDING', (0,0), (-1,0), 5),
                        ('TOPPADDING', (0,0), (-1,0), 5),
                        ('BACKGROUND', (0,1), (-1,-1), colors.HexColor('#FFFFFF')),
                        ('GRID', (0,0), (-1,-1), 0.5, colors.HexColor('#DDD6F3')),
                        ('FONTSIZE', (0,1), (-1,-1), 8),
                        ('BOTTOMPADDING', (0,1), (-1,-1), 6),
                        ('TOPPADDING', (0,1), (-1,-1), 6),
                    ]))
                    
                    story.append(t)
                    doc.build(story)
                    buffer.seek(0)
                    return buffer

                pdf_buffer = generate_students_monthly_pdf(
                    teacher_name,
                    st.session_state['center'],
                    months_names[pdf_month_num],
                    pdf_year,
                    active_only_for_pdf
                )
                st.download_button(
                    label="📥 تحميل كشف الحضور الشهري (PDF)",
                    data=pdf_buffer,
                    file_name=f"students_attendance_{teacher_name}_{months_names[pdf_month_num]}_{pdf_year}.pdf",
                    mime="application/pdf",
                    use_container_width=True
                )
            else:
                st.warning("لا توجد طالبات منتظمات لتوليد التقرير.")

        with tab5:
            st.markdown('<div class="section-header">الطالبات الخاتمات لكتاب الله</div>', unsafe_allow_html=True)
            if not students_df.empty:
                mask_khatim = (students_df['teacher'] == teacher_name) & (students_df['status'].isin(["خاتمة", "خاتم"]))
                khatim_students_df = students_df[mask_khatim].copy()
                khatim_students_df = sort_students_by_memorization(khatim_students_df)
            else:
                khatim_students_df = pd.DataFrame()
            
            if not khatim_students_df.empty:
                search_k = st.text_input("🔍 بحث في الخاتمات", "", placeholder="اكتب اسم الطالبة...", key="search_khatim")
                if search_k:
                    khatim_students_df = khatim_students_df[khatim_students_df['name'].str.contains(search_k, na=False)]
                
                for _, row in khatim_students_df.iterrows():
                    s_id = int(row['student_id'])
                    exp_key = f"k_exp_{s_id}"
                    is_expanded = st.session_state.get(exp_key, False)
                    
                    with st.expander(f"👤 {row['name']}  ({row['memorization']})", expanded=is_expanded):
                        new_name = st.text_input("الاسم الرباعي", value=row['name'], key=f"k_name_{s_id}")
                        new_yr = st.number_input("سنة الميلاد", value=int(row['birth_year']), key=f"k_yr_{s_id}")
                        
                        curr_memo = row['memorization']
                        m_idx = quran_surahs.index(curr_memo) if curr_memo in quran_surahs else 0
                        new_memo = st.selectbox(
                            "آخر سورة محفوظة", 
                            options=quran_surahs, 
                            index=m_idx,
                            key=f"k_memo_{s_id}"
                        )
                        
                        status_choices = ["خاتمة", "منتظمة", "منقطعة", "منقولة", "حذف الطالبة"]
                        new_st = st.selectbox(
                            "الحالة", 
                            options=status_choices, 
                            index=0,
                            key=f"k_status_{s_id}"
                        )
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"حفظ التعديلات للطالبة: {row['name']}", key=f"k_save_btn_{s_id}"):
                            if new_st == "حذف الطالبة":
                                delete_student_from_db(s_id)
                                st.success(f"تم حذف الطالبة {row['name']} بنجاح!")
                            else:
                                update_student_in_db(s_id, new_name.strip(), int(new_yr), new_memo, new_st)
                                st.success(f"✅ تم تحديث بيانات الطالبة ({new_name.strip()}) بنجاح.")
                            st.session_state[exp_key] = False
                            st.rerun()
            else:
                st.info("لا توجد طالبات خاتمات مسجلات حالياً.")

        with tab6:
            st.markdown('<div class="section-header">الطالبات المنقطعات والمنتقلات</div>', unsafe_allow_html=True)
            if not students_df.empty:
                mask_inactive = (students_df['teacher'] == teacher_name) & (students_df['status'].isin(["منقطعة", "منقولة", "منقطع", "منقول"]))
                inactive_students_df = students_df[mask_inactive].copy()
                inactive_students_df = sort_students_by_memorization(inactive_students_df)
            else:
                inactive_students_df = pd.DataFrame()
            
            if not inactive_students_df.empty:
                search_inact = st.text_input("🔍 بحث في المنقطعات", "", placeholder="اكتب اسم الطالبة...", key="search_inactive")
                if search_inact:
                    inactive_students_df = inactive_students_df[inactive_students_df['name'].str.contains(search_inact, na=False)]
                
                for _, row in inactive_students_df.iterrows():
                    s_id = int(row['student_id'])
                    exp_key = f"inact_exp_{s_id}"
                    is_expanded = st.session_state.get(exp_key, False)
                    
                    with st.expander(f"👤 {row['name']} - الحالة: {row['status']}", expanded=is_expanded):
                        new_name = st.text_input("الاسم الرباعي", value=row['name'], key=f"inact_name_{s_id}")
                        new_yr = st.number_input("سنة الميلاد", value=int(row['birth_year']), key=f"inact_yr_{s_id}")
                        
                        curr_memo = row['memorization']
                        m_idx = quran_surahs.index(curr_memo) if curr_memo in quran_surahs else 0
                        new_memo = st.selectbox(
                            "آخر سورة محفوظة", 
                            options=quran_surahs, 
                            index=m_idx,
                            key=f"inact_memo_{s_id}"
                        )
                        
                        status_choices = ["منقطعة", "منقولة", "منتظمة", "خاتمة", "حذف الطالبة"]
                        current_status_idx = status_choices.index(row['status']) if row['status'] in status_choices else 0
                        new_st = st.selectbox(
                            "الحالة", 
                            options=status_choices, 
                            index=current_status_idx,
                            key=f"inact_status_{s_id}"
                        )
                        
                        st.markdown("<br>", unsafe_allow_html=True)
                        if st.button(f"حفظ التعديلات للطالبة: {row['name']}", key=f"inact_save_btn_{s_id}"):
                            if new_st == "حذف الطالبة":
                                delete_student_from_db(s_id)
                                st.success(f"تم حذف الطالبة {row['name']} بنجاح!")
                            else:
                                update_student_in_db(s_id, new_name.strip(), int(new_yr), new_memo, new_st)
                                st.success(f"✅ تم تحديث بيانات الطالبة ({new_name.strip()}) بنجاح.")
                            st.session_state[exp_key] = False
                            st.rerun()
            else:
                st.info("لا توجد طالبات منقطعات أو منتقلات مسجلات حالياً.")

        with tab7:
            st.markdown('<div class="section-header">بيانات الموجهة والمتابعة المعتمدة بالحلقة</div>', unsafe_allow_html=True)
            with st.container(border=True):
                user_info = users_df[users_df['username'].astype(str) == str(username)]
                if not user_info.empty:
                    my_supervisor = user_info.iloc[0].get('assigned_supervisor', 'غير محدد')
                    my_follower = user_info.iloc[0].get('assigned_follower', 'غير محدد')
                    
                    st.write(f"👩‍🏫 **الموجهة المعتمدة:** {my_supervisor if my_supervisor else 'غير محدد'}")
                    st.write(f"📋 **المتابعة المعتمدة:** {my_follower if my_follower else 'غير محدد'}")
                else:
                    st.warning("تعذر العثور على بيانات الموجهة والمتابعة.")

        with tab8:
            st.markdown('<div class="section-header">تغيير كلمة المرور الخاصة بحسابك</div>', unsafe_allow_html=True)
            with st.container(border=True):
                with st.form("teacher_change_pass_form"):
                    old_pass = st.text_input("كلمة المرور الحالية", type="password")
                    new_pass = st.text_input("كلمة المرور الجديدة", type="password")
                    confirm_pass = st.text_input("تأكيد كلمة المرور الجديدة", type="password")
                    submit_pass = st.form_submit_button("تحديث كلمة المرور", use_container_width=True)
                    
                    if submit_pass:
                        user_row = users_df[users_df['username'].astype(str) == str(username)]
                        if not user_row.empty:
                            pass_val = str(user_row.iloc[0]['password'])
                            if pass_val == old_pass:
                                if new_pass.strip() and new_pass == confirm_pass:
                                    update_password_in_db(username, new_pass.strip())
                                    st.success("✅ تم تغيير كلمة المرور بنجاح!")
                                else:
                                    st.error("❌ كلمة المرور الجديدة غير متطابقة أو فارغة.")
                            else:
                                st.error("❌ كلمة المرور الحالية غير صحيحة.")
