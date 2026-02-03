import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time
import random

# --- КОНФИГУРАЦИЯ ---
st.set_page_config(page_title="СИНДИКАТ v53", page_icon="🇷🇺", layout="wide")

# --- БАЗА ДАННЫХ ---
def init_db():
    conn = sqlite3.connect('v53_syndicate.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                    role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                    is_working INTEGER DEFAULT 0, last_act TEXT, xp INTEGER DEFAULT 0)''')
    cur.execute('CREATE TABLE IF NOT EXISTS snitch_reports (sender TEXT, target TEXT, reason TEXT, date TEXT)')
    cur.execute('CREATE TABLE IF NOT EXISTS system_config (tax REAL DEFAULT 15, reg_open INTEGER DEFAULT 1, msg TEXT DEFAULT "РАБОТАТЬ!")')
    cur.execute('CREATE TABLE IF NOT EXISTS vault (total_tax REAL DEFAULT 0)')
    if not cur.execute('SELECT * FROM vault').fetchone(): cur.execute('INSERT INTO vault VALUES (0)')
    if not cur.execute('SELECT * FROM system_config').fetchone(): cur.execute('INSERT INTO system_config (tax, reg_open) VALUES (15, 1)')
    conn.commit()
    return conn

conn = init_db()
cur = conn.cursor()

# --- СТИЛИ (КИБЕР-РОССИЯ) ---
st.markdown("""<style>
    .stApp { background: #050505; color: #00ff00; }
    .stMetric { background: #111; border: 1px solid #00ff00; border-radius: 5px; padding: 10px; }
    .stButton>button { border: 1px solid #00ff00; color: #00ff00; background: transparent; width: 100%; transition: 0.3s; }
    .stButton>button:hover { background: #00ff00; color: #000; box-shadow: 0 0 20px #00ff00; }
    .snitch-box { background: rgba(255, 0, 0, 0.1); border: 1px solid red; padding: 10px; margin-bottom: 5px; color: #ff4b4b; }
    input { background-color: #0a0a0a !important; color: #00ff00 !important; border: 1px solid #00ff00 !important; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- СИСТЕМА ВХОДА ---
if not st.session_state.auth:
    st.title("🇷🇺 СИСТЕМА СИНДИКАТ v53")
    
    t1, t2 = st.tabs(["🔐 ВХОД", "📝 РЕГИСТРАЦИЯ"])
    
    with t1:
        u = st.text_input("ЛОГИН").strip()
        p = st.text_input("ПАРОЛЬ", type='password').strip()
        if st.button("ПОДКЛЮЧИТЬСЯ К СЕТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ЦАРЬ", "role":"admin"})
                st.rerun()
            else:
