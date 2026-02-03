import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# Настройка страницы
st.set_page_config(page_title="SPELLING ELITE", page_icon="⚡", layout="wide")

# Подключение БД
conn = sqlite3.connect('team_elite_v24.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Off")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# Кастомный стиль
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stButton>button { width: 100%; border-radius: 5px; height: 3em; background-color: #262730; color: white; }
    .stat-box { padding: 20px; border-radius: 10px; background-color: #161b22; border: 1px solid #30363d; text-align: center; }
    .timer-text { font-size: 2.5rem; font-weight: bold; color: #ff4b4b; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ЛОГИКА ВХОДА ---
if not st.session_state.auth:
    st.title("⚡ SPELLING ELITE v24")
    u = st.text_input("👤 Логин")
    p = st.text_input("🔑 Пароль", type='password')
    c1, c2 = st.columns(2)
    if c1.button("🚀 ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True,"user":"ADMIN","role":"admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True,"user":u,"role":res[0]})
                st.rerun()
            else: st.error("❌ Ошибка входа")
    if c2.button("📝 РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit()
            st.success("✅ Готово! Жми Войти")
        except: st.error("⚠️ Ник занят")

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👾 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    # Панель баланса и статуса
    col_a, col_b = st.columns(2)
    with col_a:
        st.markdown('<div
