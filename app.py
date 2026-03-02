import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import calendar
import base64
import os

# --- 1. SETTINGS & PROFESSIONAL TECH UI ---
st.set_page_config(page_title="SHADOW PRO V5", layout="wide")

st.markdown("""
    <style>
    /* استيراد خطوط احترافية وتقنية */
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Lexend:wght@300;500&display=swap');
    
    .stApp { background: #050508; color: #eef2f6; font-family: 'Lexend', sans-serif; }
    
    /* Welcome Message - NEON BLUE */
    .welcome-text { 
        font-family: 'Rajdhani'; color: #00d4ff; font-size: 1.6rem; text-align: center; 
        font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 10px rgba(0,212,255,0.4); 
        letter-spacing: 1px; 
    }
    
    /* Sidebar Styling */
    [data-testid="stSidebar"] { background-color: #0a0a12; border-right: 1px solid #bc13fe33; }
    
    .account-card { 
        background: linear-gradient(145deg, rgba(188, 19, 254, 0.1), rgba(0, 0, 0, 0.5));
        border: 1px solid #bc13fe55; border-radius: 12px; padding: 15px; 
        text-align: center; margin-bottom: 20px;
    }

    /* Menu Styling */
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
        background: transparent !important;
        border: 1px solid rgba(255, 255, 255, 0.05) !important;
        padding: 10px 15px !important;
        border-radius: 8px !important;
        color: #94a3b8; font-family: 'Rajdhani'; font-size: 0.9rem;
        margin-bottom: 6px; transition: 0.2s;
    }
    
    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label:hover {
        border-color: #bc13feaa !important;
    }

    [data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb="radio"]:has(input:checked) {
        border: 1px solid #bc13fe !important; color: #bc13fe !important; 
        background: rgba(188, 19, 254, 0.05) !important;
    }

    /* Professional Cards */
    .perf-card { 
        background: #0f111a; border: 1px solid #1e293b; 
        padding: 20px; border-radius: 12px; text-align: center;
    }
    .perf-card h4 { font-family: 'Rajdhani'; margin: 0; color: #bc13fe; font-size: 1.8rem; }
    .perf-card p { font-size: 0.75rem; color: #64748b; margin-top: 5px; text-transform: uppercase; }

    /* Inputs */
    div[data-baseweb="select"] > div, div[data-baseweb="input"] > div, div[data-baseweb="textarea"] > div { 
        border-radius: 8px !important; background-color: #0f111a !important; border: 1px solid #1e293b !important;
    }
    </style>
    """, unsafe_allow_html=True)

# --- 2. ADVANCED MULTI-ACCOUNT SYSTEM ---
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani; color:#bc13fe; font-size:1.5rem; font-weight:700; text-align:center; padding-bottom:15px;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    # محرك البحث عن الحسابات (ملفات الـ DB)
    existing_accounts = [f.replace('tracker_', '').replace('.db', '') for f in os.listdir() if f.startswith('tracker_') and f.endswith('.db')]
    
    if not existing_accounts:
        existing_accounts = ["Main_Fund"]

    # إدخال اسم الحساب (كتابة يدوية لإنشاء جديد أو اختيار قديم)
    selected_acc_name = st.selectbox("📂 SWITCH / OPEN ACCOUNT", options=list(set(existing_accounts + ["+ Create New Account"])) )
    
    if selected_acc_name == "+ Create New Account":
        acc_name = st.text_input("Enter New Account Name", "New_Account").strip().replace(" ", "_")
    else:
        acc_name = selected_acc_name

    init_amount = st.number_input("💰 INITIAL DEPOSIT ($)", value=1000.0, step=100.0)

    # اتصال بقاعدة البيانات الخاصة بالحساب المختار
    db_path = f"tracker_{acc_name.lower()}.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, 
                  outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, 
                  setup TEXT, comment TEXT, setup_desc TEXT, image TEXT)''')
    conn.commit()

# --- 3. SHARED DATA LOGIC ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
current_bal = init_amount
if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    current_bal = init_amount + df['pnl'].sum()

# --- 4. SIDEBAR EQUITY DISPLAY ---
with st.sidebar:
    st.markdown(f"""
    <div class="account-card">
        <div style="font-family:Rajdhani; font-size:0.7rem; color:#bc13fe; letter-spacing:2px;">ACTIVE ACCOUNT: {acc_name.upper()}</div>
        <div style="font-family:Rajdhani; font-size:1.8rem; font-weight:700; color:#fff;">${current_bal:,.2f}</div>
        <div style="font-size:0.75rem; color:#64748b;">Equity Status</div>
    </div>
    """, unsafe_allow_html=True)
    
    choice = st.radio("NAVIGATION", ["TERMINAL", "CALENDAR", "PERFORMANCE", "JOURNAL", "ARCHIVE"])

st.markdown('<div class="welcome-text">SYSTEM ONLINE. ANALYZING SHADOW PERFORMANCE.</div>', unsafe_allow_html=True)

# --- 5. SECTIONS ---

if choice == "TERMINAL":
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.form("log_form"):
            st.markdown("<h4 style='font-family:Rajdhani;'>ENTRY LOG</h4>", unsafe_allow_html=True)
            d = st.date_input("Trade Date")
            p = st.text_input("Asset/Pair", "NAS100")
            o = st.selectbox("Outcome", ["WIN", "LOSS", "BE"])
            pnl = st.number_input("PnL ($)", value=0.0)
            rr = st.number_input("Risk:Reward", value=0.0)
            st_name = st.text_input("Setup")
            msg = st.text_area("Notes")
            img = st.file_uploader("Upload Chart", type=['png','jpg'])
            if st.form_submit_button("EXECUTE"):
                img_str = base64.b64encode(img.read()).decode() if img else None
                c.execute("INSERT INTO trades (date, pair, outcome, pnl, rr, balance, setup, comment, image) VALUES (?,?,?,?,?,?,?,?,?)",
                          (str(d), p, o, pnl, rr, current_bal, st_name, msg, img_str))
                conn.commit()
                st.rerun()
    with c2:
        if not df.empty:
            df_s = df.sort_values('date_dt')
            df_s['curve'] = init_amount + df_s['pnl'].cumsum()
            fig = px.line(df_s, x='date', y='curve', title=f"EQUITY CURVE - {acc_name}")
            fig.update_traces(line_color='#bc13fe')
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', plot_bgcolor='rgba(0,0,0,0)', font_family="Rajdhani")
            st.plotly_chart(fig, use_container_width=True)

elif choice == "PERFORMANCE":
    if not df.empty:
        # حسابات الـ Performance للحساب النشط فقط
        wins = len(df[df['pnl'] > 0])
        wr = (wins / len(df)) * 100
        
        # حساب الـ Consistency
        if len(df) > 2:
            std = df['pnl'].std()
            avg = abs(df['pnl'].mean())
            consistency = max(0, min(100, 100 - ((std/avg)*10 if avg !=0 else 0)))
        else: consistency = 0

        col_g, col_s = st.columns([1, 1.5])
        with col_g:
            fig_g = go.Figure(go.Indicator(mode="gauge+number", value=wr, title={'text': "WIN RATE", 'font':{'family':'Rajdhani'}},
                                         number={'suffix': "%", 'font':{'family':'Rajdhani'}},
                                         gauge={'axis':{'range':[0,100]}, 'bar':{'color':"#00ffcc"}}))
            fig_g.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_g, use_container_width=True)
        
        with col_s:
            st.markdown("<br>", unsafe_allow_html=True)
            r1 = st.columns(2)
            r1[0].markdown(f'<div class="perf-card"><h4>{consistency:.0f}%</h4><p>Consistency Score</p></div>', unsafe_allow_html=True)
            r1[1].markdown(f'<div class="perf-card"><h4>{df["rr"].mean():.2f}</h4><p>Average R:R</p></div>', unsafe_allow_html=True)
            
            r2 = st.columns(2)
            r2[0].markdown(f'<div class="perf-card"><h4 style="color:#00ffcc">${df["pnl"].max():,.0f}</h4><p>Best Trade</p></div>', unsafe_allow_html=True)
            r2[1].markdown(f'<div class="perf-card"><h4 style="color:#ff4b4b">${df["pnl"].min():,.0f}</h4><p>Worst Trade</p></div>', unsafe_allow_html=True)

elif choice == "CALENDAR":
    if not df.empty:
        # كود الكالندر كيبقى خدام غير على الـ DF ديال الحساب المفتوح
        st.info(f"Viewing Trading Calendar for: {acc_name}")
        # (نفس منطق الكالندر السابق لكنه يقرأ من الداتابيز الحالية)
        df['date_dt'] = pd.to_datetime(df['date'])
        # ... تكملة كود الكالندر ...

elif choice == "ARCHIVE":
    if not df.empty:
        st.markdown(f"### 📂 {acc_name.upper()} ARCHIVE")
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%B %Y')
        for m in df['month'].unique():
            with st.expander(f"📁 {m}"):
                st.dataframe(df[df['month'] == m][['date', 'pair', 'pnl', 'setup', 'comment']], use_container_width=True)
