import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="SPELLING TOTAL CONTROL v7", layout="wide")

def get_db():
    conn = sqlite3.connect('team_v7_final.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Offline")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

# --- СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ffcc; }
    .stButton>button { border-radius: 5px; font-weight: bold; width: 100%; border: none; }
    .status-btn { height: 40px; margin-bottom: 10px; }
    .online-tag { background: #00ff00; color: black; padding: 3px 10px; border-radius: 10px; font-weight: bold; }
    .afk-tag { background: #ffff00; color: black; padding: 3px 10px; border-radius: 10px; font-weight: bold; }
    .offline-tag { background: #555; color: white; padding: 3px 10px; border-radius: 10px; font-weight: bold; }
    .worker-card { background: #111; padding: 15px; border: 1px solid #222; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user = None

# --- ВХОД / РЕГИСТРАЦИЯ ---
if st.session_state.user is None:
    st.title("⚡ SPELLING SYSTEM v7")
    t1, t2 = st.tabs(["ВХОД", "РЕГИСТРАЦИЯ"])
    with t1:
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ"):
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res:
                if res[1]
