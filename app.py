        import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, date
import sqlite3
import calendar
import base64

# --- SETTINGS ---
st.set_page_config(page_title="369 SHADOW V43", layout="wide")

# --- CSS: NEON SIDEBAR & CARDS ---
st.markdown("""
<style>
@import url('https://fonts.googleapis.com/css2?family=Orbitron:wght@400;700&family=Inter:wght@300;400;600&display=swap');
.stApp { background: #05070a; color: #e6edf3; font-family: 'Inter', sans-serif; }

/* Sidebar Neon Buttons */
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label {
    background: rgba(0, 212, 255, 0.05);
    border: 1px solid rgba(0, 212, 255, 0.2);
    padding: 15px; border-radius: 10px;
    margin-bottom: 10px; transition: 0.3s;
    color: #8b949e; font-family: 'Orbitron';
}
div[data-testid="stSidebar"] .stRadio div[role="radiogroup"] label[data-baseweb='radio']:has(input:checked) {
    background: rgba(0, 212, 255, 0.2) !important;
    border: 1px solid #00d4ff !important;
    box-shadow: 0 0 15px #00d4ff66;
    color: #00ffcc !important;
}

/* Journal Colors */
.win-card { border-left: 5px solid #00ffcc; background: rgba(0, 255, 204, 0.05); padding: 10px; margin-bottom: 5px; border-radius: 5px; }
.loss-card { border-left: 5px solid #ff4b4b; background: rgba(255, 75, 75, 0.05); padding: 10px; margin-bottom: 5px; border-radius: 5px; }
.be-card { border-left: 5px solid #fbbf24; background: rgba(251, 191, 36, 0.05); padding: 10px; margin-bottom: 5px; border-radius: 5px; }

/* Calendar Day Box */
.cal-box { border: 1px solid rgba(255,255,255,0.1); border-radius: 5px; padding: 5px; text-align: center; min-height: 60px; }
</style>
""", unsafe_allow_html=True)

# --- DATABASE ---
conn = sqlite3.connect('shadow_v43_final.db', check_same_thread=False)
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS trades 
             (id INTEGER PRIMARY KEY AUTOINCREMENT, date TEXT, pair TEXT, outcome TEXT, 
              pnl REAL, rr REAL, setup_name TEXT, setup_desc TEXT, mindset_type TEXT, 
              mindset_desc TEXT, month_archive TEXT)''')
conn.commit()

# --- LOAD DATA ---
df = pd.read_sql_query("SELECT * FROM trades", conn)
if not df.empty:
    df['date'] =
