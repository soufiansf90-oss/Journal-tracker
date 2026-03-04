# =====================================
# ELITE OPERATOR LAB – FULL FIXED VERSION
# =====================================

import streamlit as st
import pandas as pd
import numpy as np
import sqlite3
from datetime import datetime
import calendar
import plotly.graph_objects as go

# -----------------------------
# PAGE CONFIG
# -----------------------------
st.set_page_config(page_title="ELITE OPERATOR LAB", layout="wide")

# -----------------------------
# DATABASE
# -----------------------------
conn = sqlite3.connect("elite_lab.db", check_same_thread=False)
c = conn.cursor()

c.execute("""CREATE TABLE IF NOT EXISTS accounts (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT, starting_balance REAL, max_daily_loss REAL,
    max_trades INTEGER, min_rr REAL)""")

c.execute("""CREATE TABLE IF NOT EXISTS trades (
    id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER,
    date TEXT, asset TEXT, market_type TEXT, session TEXT, setup TEXT,
    entry REAL, sl REAL, tp REAL, exit REAL, pnl REAL,
    rr_planned REAL, rr_achieved REAL, emotion TEXT, rule_break INTEGER,
    rating TEXT, comment TEXT, screenshot TEXT, position TEXT)""")

c.execute("""CREATE TABLE IF NOT EXISTS breaches (
    id INTEGER PRIMARY KEY AUTOINCREMENT, account_id INTEGER,
    date TEXT, breach_type TEXT, description TEXT)""")

conn.commit()

# -----------------------------
# CSS – Neon Style
# -----------------------------
st.markdown("""
<style>
body {background-color:#0B0C10; color:white;}
div[data-testid="stMetric"] {background: linear-gradient(145deg,#7B2FF7,#FF00FF); padding:20px; border-radius:15px; border:1px solid #7B2FF7; box-shadow:0px 0px 15px #7B2FF7;}
.stButton>button {background-color:#7B2FF7; color:white; border-radius:10px;}
.stSidebar {background-color:#111217; padding:15px; border-radius:15px; box-shadow:0 0 15px #7B2FF7;}
</style>
""", unsafe_allow_html=True)

# -----------------------------
# DYNAMIC BALANCE FUNCTION
# -----------------------------
def get_current_balance(account, trades):
    starting = account["starting_balance"]
    if trades.empty:
        return starting
    else:
        account_trades = trades[trades["account_id"]==account["id"]]
        return starting + account_trades["pnl"].sum()

# -----------------------------
# LOAD ACCOUNTS & TRADES
# -----------------------------
accounts = pd.read_sql("SELECT * FROM accounts", conn)
trades = pd.read_sql("SELECT * FROM trades", conn)
if not trades.empty:
    trades["date"] = pd.to_datetime(trades["date"])

# -----------------------------
# SIDEBAR – Right Slide Panel (FIXED)
# -----------------------------
st.sidebar.markdown("<h2 style='color:#7B2FF7;'>ELITE OPERATOR LAB</h2>", unsafe_allow_html=True)

st.sidebar.subheader("Select Active Account")
active_account_id = None

if not accounts.empty:
    balances = [get_current_balance(acc._asdict(), trades) for acc in accounts.itertuples()]
    # ✅ FIX: access tuple attributes with acc.name
    account_options = [f"{acc.name} | Balance: {round(bal,2)}" for acc, bal in zip(accounts.itertuples(), balances)]
    selected = st.sidebar.selectbox("Active Account", account_options)
    active_account_id = accounts.iloc[account_options.index(selected)]["id"]
    account = accounts[accounts["id"]==active_account_id].iloc[0]
else:
    st.sidebar.info("No accounts yet. Create one below!")

st.sidebar.markdown("---")
st.sidebar.subheader("Create New Account")
name = st.sidebar.text_input("Account Name")
balance_input = st.sidebar.number_input("Starting Balance", value=10000.0, step=100.0)
max_loss = st.sidebar.number_input("Max Daily Loss", value=50.0, step=1.0)
max_trades = st.sidebar.number_input("Max Trades Per Day", value=1, step=1)
min_rr = st.sidebar.number_input("Minimum RR", value=2.0, step=0.1)

create_disabled = True if name.strip() == "" else False
if st.sidebar.button("Create Account", disabled=create_disabled):
    c.execute(
        "INSERT INTO accounts (name,starting_balance,max_daily_loss,max_trades,min_rr) VALUES (?,?,?,?,?)",
        (name, balance_input, max_loss, max_trades, min_rr)
    )
    conn.commit()
    st.experimental_rerun()

# -----------------------------
# SCORING FUNCTION
# -----------------------------
def execution_score(trade, account):
    score = 100
    if trade["rr_achieved"] < account["min_rr"]:
        score -= 20
    if trade["rule_break"]==1:
        score -= 25
    if trade["emotion"] in ["Revenge","FOMO"]:
        score -= 15
    score = max(score,0)
    if score>=90:
        verdict="ELITE"
    elif score>=75:
        verdict="PROFESSIONAL"
    elif score>=60:
        verdict="UNSTABLE"
    else:
        verdict="LIABILITY"
    return score, verdict

# -----------------------------
# ANALYTICS FUNCTIONS
# -----------------------------
def equity_curve(trades):
    trades = trades.sort_values("date")
    trades["cumulative"] = trades["pnl"].cumsum()
    trades["drawdown"] = trades["cumulative"] - trades["cumulative"].cummax()
    return trades

def win_rate(trades):
    if len(trades)==0: return 0
    return round(len(trades[trades["pnl"]>0])/len(trades)*100,2)

def profit_factor(trades):
    wins = trades[trades["pnl"]>0]["pnl"].sum()
    losses = trades[trades["pnl"]<0]["pnl"].sum()
    if losses==0: return 0
    return round(abs(wins/losses),2)

def asset_breakdown(trades):
    df = trades.groupby("asset")["pnl"].agg(["count","sum","mean"])
    df["win_rate"] = trades.groupby("asset").apply(lambda x: (x["pnl"]>0).sum()/len(x)*100)
    df["profit_factor"] = trades.groupby("asset").apply(lambda x: abs(x[x["pnl"]>0]["pnl"].sum()/x[x["pnl"]<0]["pnl"].sum()) if x[x["pnl"]<0]["pnl"].sum()!=0 else 0)
    return df
