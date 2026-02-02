import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# --- КОНФИГ СТРАНИЦЫ ---
st.set_page_config(page_title="SPELLING SYSTEM PRO", page_icon="📈", layout="wide")

# --- БАЗА ДАННЫХ ---
def get_db():
    conn = sqlite3.connect('team_v3_pro.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, xp INTEGER DEFAULT 0, role TEXT DEFAULT "worker", rank TEXT DEFAULT "Новичок")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, xp_gain INTEGER)')
conn.commit()

# --- АХУЕННЫЙ СТИЛЬ (NEON DARK) ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #e0e0e0; }
    .stButton>button { background: linear-gradient(45deg, #00f2ff, #0066ff); color: white; border: none; font-weight: bold; width: 100%; border-radius: 8px; height: 50px; transition: 0.3s; }
    .stButton>button:hover { box-shadow: 0 0 20px #00f2ff; transform: translateY(-2px); }
    .metric-card { background: #111; padding: 20px; border-radius: 15px; border: 1px solid #222; text-align: center; box-shadow: 0 4px 15px rgba(0,0,0,0.5); }
    .stTabs [data-baseweb="tab-list"] { background-color: transparent; }
    .stTabs [data-baseweb="tab"] { color: #888; font-size: 18px; }
    .stTabs [data-baseweb="tab--active"] { color: #00f2ff !important; font-weight: bold; border-bottom-color: #00f2ff !important; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user = None

# --- ВХОД / РЕГИСТРАЦИЯ ---
if st.session_state.user is None:
    st.markdown("<h1 style='text-align: center; color: #00f2ff; text-shadow: 0 0 15px #00f2ff;'>⚡ SPELLING TEAM SYSTEM</h1>", unsafe_allow_html=True)
