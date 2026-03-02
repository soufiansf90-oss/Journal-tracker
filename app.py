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
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Lexend:wght@300;500&display=swap');
    
    .stApp { background: #050508; color: #eef2f6; font-family: 'Lexend', sans-serif; }
    
    .welcome-text { 
        font-family: 'Rajdhani'; color: #00d4ff; font-size: 1.6rem; text-align: center; 
        font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 10px rgba(0,212,255,0.4); 
    }
    
    [data-testid="stSidebar"] { background-color: #0a0a12; border-right: 1px solid #bc13fe33; }
    
    .account-card { 
        background: linear-gradient(145deg, rgba(188, 19, 254, 0.1), rgba(0, 0, 0, 0.5));
        border: 1px solid #bc13fe55; border-radius: 12px; padding: 15px; 
        text-align: center; margin-bottom: 20px;
    }

    /* Journal States */
    .journal-win { border-left: 5px solid #00ffcc; background: rgba(0, 255, 204, 0.05); padding:15px; border-radius:12px; margin-bottom:15px; }
    .journal-loss { border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); padding:15px; border-radius:12px; margin-bottom:15px; }
    .journal-be { border-left: 5px solid #ffcc00; background: rgba(255, 204, 0, 0.05); padding:15px; border-radius:12px; margin-bottom:15px; }

    .perf-card { background: #0f111a; border: 1px solid #1e293b; padding: 20px; border-radius: 12px; text-align: center; }
    .perf-card h4 { font-family: 'Rajdhani'; color: #bc13fe; font-size: 1.8rem; margin:0; }
    </style>
    """, unsafe_allow_html=True)

# --- 2. MULTI-ACCOUNT SYSTEM ---
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani; color:#bc13fe; font-size:1.5rem; font-weight:700; text-align:center; padding-bottom:15px;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    existing_accounts = [f.replace('tracker_', '').replace('.db', '') for f in os.listdir() if f.startswith('tracker_') and f.endswith('.db')]
    if not existing_accounts: existing_accounts = ["Main_Fund"]

    selected_acc_name = st.selectbox("📂 SWITCH / OPEN ACCOUNT", options=list(set(existing_accounts + ["+ Create New Account"])))
    
    if selected_acc_name == "+ Create New Account":
        acc_name = st.text_input("New Name", "New_Account").strip().replace(" ", "_")
    else:
        acc_name = selected_acc_name

    init_amount = st.number_input("💰 INITIAL DEPOSIT ($)", value=1000.0)

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

# --- 4. NAVIGATION ---
with st.sidebar:
    st.markdown(f'<div class="account-card"><div style="font-family:Rajdhani; color:#bc13fe; font-size:0.7rem;">{acc_name.upper()}</div><div style="font-size:1.8rem; font-weight:700;">${current_bal:,.2f}</div></div>', unsafe_allow_html=True)
    choice = st.radio("NAVIGATION", ["TERMINAL", "CALENDAR", "PERFORMANCE", "JOURNAL", "ARCHIVE"])

st.markdown('<div class="welcome-text">SYSTEM ONLINE. ANALYZING SHADOW PERFORMANCE.</div>', unsafe_allow_html=True)

# --- 5. TERMINAL ---
if choice == "TERMINAL":
    c1, c2 = st.columns([1, 2])
    with c1:
        with st.form("log_form"):
            st.markdown("<h4 style='font-family:Rajdhani;'>ENTRY LOG</h4>", unsafe_allow_html=True)
            d = st.date_input("Trade Date", datetime.now())
            p = st.text_input("Asset/Pair", "NAS100").upper()
            o = st.selectbox("Outcome", ["WIN", "LOSS", "BE"])
            pnl = st.number_input("PnL ($)", value=0.0)
            rr = st.number_input("Risk:Reward", value=0.0)
            st_name = st.text_input("Setup").upper()
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
            fig = px.line(df_s, x='date', y='curve', title="EQUITY CURVE")
            fig.update_traces(line_color='#bc13fe')
            fig.update_layout(template="plotly_dark", paper_bgcolor='rgba(0,0,0,0)', font_family="Rajdhani")
            st.plotly_chart(fig, use_container_width=True)

# --- 6. CALENDAR (As Requested) ---
elif choice == "CALENDAR":
    if not df.empty:
        df['date_dt'] = pd.to_datetime(df['date'])
        first_day = df['date_dt'].min().replace(day=1)
        month_name = first_day.strftime('%B %Y')
        _, last_day_num = calendar.monthrange(first_day.year, first_day.month)
        
        st.markdown(f"<h2 style='text-align:center; color:#00d4ff; font-family:Rajdhani;'>{month_name.upper()}</h2>", unsafe_allow_html=True)
        
        weekdays = ["MON", "TUE", "WED", "THU", "FRI", "SAT", "SUN"]
        header_cols = st.columns(7)
        for i, wd in enumerate(weekdays):
            header_cols[i].markdown(f"<div style='text-align:center; color:#00ffcc; font-size:0.8rem; font-family:Rajdhani; border-bottom:1px solid #333;'>{wd}</div>", unsafe_allow_html=True)
        
        start_padding = first_day.weekday() 
        total_slots = start_padding + last_day_num
        
        for row in range(0, total_slots, 7):
            cols = st.columns(7)
            for i in range(7):
                day_idx = row + i
                with cols[i]:
                    if start_padding <= day_idx < total_slots:
                        day_num = day_idx - start_padding + 1
                        current_date = first_day.replace(day=day_num)
                        trades_today = df[df['date_dt'].dt.date == current_date.date()]
                        daily_pnl = trades_today['pnl'].sum()
                        num_trades = len(trades_today)
                        
                        bg, border, txt = "rgba(255,255,255,0.02)", "rgba(255,255,255,0.05)", "#444"
                        pnl_str = ""
                        if num_trades > 0:
                            if daily_pnl > 0: bg, border, txt = "rgba(0,255,204,0.1)", "#00ffcc", "#00ffcc"; pnl_str = f"+${daily_pnl:,.0f}"
                            elif daily_pnl < 0: bg, border, txt = "rgba(255,75,75,0.1)", "#ff4b4b", "#ff4b4b"; pnl_str = f"-${abs(daily_pnl):,.0f}"
                            else: bg, border, txt = "rgba(255,204,0,0.1)", "#ffcc00", "#ffcc00"; pnl_str = "$0"

                        st.markdown(f'<div style="background:{bg}; border:1px solid {border}; border-radius:8px; padding:8px; height:90px; text-align:center; margin-bottom:5px;"><div style="font-size:0.7rem; color:#888;">{day_num}</div><div style="color:{txt}; font-weight:bold; font-size:0.9rem; margin-top:5px;">{pnl_str}</div><div style="font-size:0.5rem; color:#00d4ff; margin-top:3px; font-family:Rajdhani;">{f"{num_trades} T" if num_trades > 0 else ""}</div></div>', unsafe_allow_html=True)
        
        st.markdown("---")
        available_days = sorted(df['date_dt'].dt.day.unique())
        selected_day = st.selectbox("Select a day to review trades:", available_days)
        if selected_day:
            day_data = df[df['date_dt'].dt.day == selected_day]
            st.dataframe(day_data[['date', 'pair', 'outcome', 'pnl', 'rr', 'setup']], use_container_width=True)
    else: st.warning("No data found.")

# --- 7. PERFORMANCE ---
elif choice == "PERFORMANCE":
    if not df.empty:
        wins = len(df[df['pnl'] > 0])
        wr = (wins / len(df)) * 100
        avg_rr = df['rr'].mean()
        
        # Consistency
        cv = df['pnl'].std() / abs(df['pnl'].mean()) if abs(df['pnl'].mean()) != 0 else 1
        consistency = max(0, min(100, 100 - (cv * 10)))

        c1, c2 = st.columns([1, 1.5])
        with c1:
            fig_g = go.Figure(go.Indicator(mode="gauge+number", value=wr, number={'suffix': "%", 'font':{'family':'Rajdhani'}}, gauge={'bar':{'color':"#00ffcc"}}))
            fig_g.update_layout(height=300, paper_bgcolor='rgba(0,0,0,0)')
            st.plotly_chart(fig_g, use_container_width=True)
        with c2:
            r1 = st.columns(2)
            r1[0].markdown(f'<div class="perf-card"><h4>{consistency:.0f}%</h4><p>Consistency</p></div>', unsafe_allow_html=True)
            r1[1].markdown(f'<div class="perf-card"><h4>{avg_rr:.2f}</h4><p>Avg RR</p></div>', unsafe_allow_html=True)
            st.markdown(f'<div style="text-align:center; margin-top:20px;"><h1 style="color:{"#00ffcc" if df["pnl"].sum()>=0 else "#ff4b4b"}; font-family:Rajdhani;">${df["pnl"].sum():,.2f}</h1><p>TOTAL NET PROFIT</p></div>', unsafe_allow_html=True)

# --- 8. JOURNAL (Colored) ---
elif choice == "JOURNAL":
    if not df.empty:
        for _, row in df.sort_values('id', ascending=False).iterrows():
            # تحديد اللون بناءً على النتيجة
            if row['outcome'] == "WIN": j_class = "journal-win"
            elif row['outcome'] == "LOSS": j_class = "journal-loss"
            else: j_class = "journal-be"
            
            st.markdown(f'<div class="{j_class}">', unsafe_allow_html=True)
            with st.expander(f"● {row['date']} | {row['pair']} | P&L: ${row['pnl']:,.2f}"):
                col_text, col_img = st.columns([1, 1.5])
                with col_text:
                    st.write(f"**Setup:** {row['setup']}")
                    st.write(f"**RR:** {row['rr']}")
                    st.info(f"Comment: {row['comment']}")
                with col_img:
                    if row['image']: st.image(base64.b64decode(row['image']), use_container_width=True)
            st.markdown('</div>', unsafe_allow_html=True)

# --- 9. ARCHIVE ---
elif choice == "ARCHIVE":
    if not df.empty:
        df['month'] = pd.to_datetime(df['date']).dt.strftime('%B %Y')
        for m in df['month'].unique():
            with st.expander(f"📁 {m}"):
                st.dataframe(df[df['month'] == m][['date', 'pair', 'outcome', 'pnl', 'setup']], use_container_width=True)
