import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime
import sqlite3
import calendar
import base64
import os

# --- 1. SETTINGS & ADVANCED VIOLET NEON UI ---
st.set_page_config(page_title="369 SHADOW PRO", layout="wide")

st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Rajdhani:wght@500;700&family=Lexend:wght@300;500&display=swap');
    
    .stApp { background: #050508; color: #eef2f6; font-family: 'Lexend', sans-serif; }
    
    .welcome-text { 
        font-family: 'Rajdhani'; color: #00d4ff; font-size: 1.6rem; text-align: center; 
        font-weight: 700; margin-bottom: 25px; text-shadow: 0 0 10px rgba(0,212,255,0.4); 
    }
    
    [data-testid="stSidebar"] { background-color: #080810; border-right: 2px solid #bc13fe33; }
    
    .equity-box { 
        background: rgba(188, 19, 254, 0.05); border: 1px solid #bc13fe; 
        border-radius: 20px; padding: 15px; text-align: center; margin-bottom: 20px; 
        box-shadow: 0 0 10px rgba(188,19,254,0.2);
    }

    /* UPDATED PREMIUM PERFORMANCE CARDS */
    .perf-card { 
        background: linear-gradient(145deg, rgba(30,30,40,0.9), rgba(10,10,20,0.9));
        border: 1px solid #bc13fe55; 
        padding: 25px; 
        border-radius: 25px; 
        text-align: center; 
        box-shadow: 0 0 20px rgba(188,19,254,0.15);
        transition: 0.3s;
    }
    .perf-card:hover {
        transform: translateY(-4px);
        box-shadow: 0 0 30px rgba(188,19,254,0.4);
    }
    .perf-card h4 { font-family: 'Rajdhani'; color: #bc13fe; font-size: 1.8rem; margin:0; }
    .perf-card p { font-size: 0.8rem; color: #64748b; text-transform: uppercase; margin-top:5px; }
    </style>
""", unsafe_allow_html=True)

# --- 2. MULTI-ACCOUNT SYSTEM ---
with st.sidebar:
    st.markdown('<div style="font-family:Rajdhani; color:#bc13fe; font-size:1.5rem; font-weight:700; text-align:center; padding-bottom:15px;">SHADOW SYSTEM</div>', unsafe_allow_html=True)
    
    existing_accounts = [f.replace('tracker_', '').replace('.db', '') for f in os.listdir() if f.startswith('tracker_') and f.endswith('.db')]
    selected_acc = st.selectbox("📂 ACCOUNT", options=list(set(existing_accounts + ["+ New Account"])))
    
    if selected_acc == "+ New Account":
        acc_name = st.text_input("Account Name", "Main_Tracker").strip().replace(" ", "_")
    else:
        acc_name = selected_acc

    init_amount = st.number_input("💰 INITIAL AMOUNT ($)", value=1000.0)

    db_path = f"tracker_{acc_name.lower()}.db"
    conn = sqlite3.connect(db_path, check_same_thread=False)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS trades 
                 (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, 
                  outcome TEXT, pnl REAL, rr REAL, balance REAL, mindset TEXT, 
                  setup TEXT, comment TEXT, setup_desc TEXT, image TEXT)''')
    conn.commit()

df = pd.read_sql_query("SELECT * FROM trades", conn)
current_bal = init_amount
daily_pnl = 0.0

if not df.empty:
    df['date_dt'] = pd.to_datetime(df['date'])
    current_bal = init_amount + df['pnl'].sum()
    daily_pnl = df[df['date'] == datetime.now().strftime('%Y-%m-%d')]['pnl'].sum()

# --- TERMINAL ---
if not df.empty:
    df_chart = df.sort_values(by='date_dt')
    df_chart['equity_curve'] = init_amount + df_chart['pnl'].cumsum()

    fig = px.line(
        df_chart,
        x='date_dt',
        y='equity_curve',
        title="EQUITY EVOLUTION",
        markers=True
    )

    fig.update_traces(line_color='#bc13fe', line_width=3)

    fig.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="",
        yaxis_title="",
        font_family="Rajdhani",
        hovermode="x unified"
    )

# --- PERFORMANCE ---
if not df.empty:
    wins = df[df['pnl'] > 0]
    losses = df[df['pnl'] < 0]

    wr = (len(wins)/len(df))*100
    avg_rr = df['rr'].mean()
    sum_w = wins['pnl'].sum()
    sum_l = abs(losses['pnl'].sum())

    # FIXED PROFIT FACTOR
    if sum_l == 0 and sum_w > 0:
        tf = float('inf')
    elif sum_l == 0:
        tf = 0
    else:
        tf = sum_w / sum_l

    tf_display = "∞" if tf == float('inf') else f"{tf:.2f}"

    consistency = max(0, min(100, 100 - ((df['pnl'].std() / abs(df['pnl'].mean())) * 10))) if len(df)>2 else 0

    net = df['pnl'].sum()

    # WEEKLY % CHART
    st.markdown("### WEEKLY PERFORMANCE (%)")

    df_week = df.copy()
    df_week['week'] = df_week['date_dt'].dt.to_period('W').astype(str)

    weekly = df_week.groupby('week')['pnl'].sum().reset_index()
    weekly['pct'] = (weekly['pnl'] / init_amount) * 100

    fig_week = px.bar(
        weekly,
        x='week',
        y='pct',
        text=weekly['pct'].round(2).astype(str) + "%"
    )

    fig_week.update_traces(textposition='outside')

    fig_week.update_layout(
        template="plotly_dark",
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        xaxis_title="",
        yaxis_title="%",
        font_family="Rajdhani"
    )

    st.plotly_chart(fig_week, use_container_width=True)
