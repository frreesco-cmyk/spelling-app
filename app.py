import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- КОНФИГ СТРАНИЦЫ ---
st.set_page_config(page_title="ELITE SYSTEM v36", page_icon="⚡", layout="wide")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('elite_v36.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# --- КРАСИВЫЙ ДИЗАЙН ---
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    div[data-testid="stMetricValue"] { color: #00ffcc; font-size: 32px; }
    .stButton>button { border-radius: 10px; height: 3em; background-color: #262730; border: 1px solid #444; transition: 0.3s; }
    .stButton>button:hover { border-color: #00ffcc; color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД / РЕГИСТРАЦИЯ ---
if not st.session_state.auth:
    st.title("⚡ ELITE SYSTEM LOGIN")
    tab_in, tab_reg = st.tabs(["🔐 ВХОД", "📝 РЕГИСТРАЦИЯ"])
    
    with tab_in:
        u = st.text_input("Логин", key="login_u").strip()
        p = st.text_input("Пароль", type='password', key="login_p").strip()
        if st.button("🚀 ВОЙТИ В СИСТЕМУ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error
