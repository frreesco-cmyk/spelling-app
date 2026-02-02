import streamlit as st
import pandas as pd
import sqlite3
from datetime import datetime
import time

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="SPELLING CONTROL v6", layout="wide")

def get_db():
    conn = sqlite3.connect('team_v6_status.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()
# Добавлена колонка user_state (Online/AFK/Offline)
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Offline")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

# --- СТИЛИ ---
st.markdown("""
<style>
    .stApp { background-color: #050505; color: #00ffcc; }
    .stButton>button { border-radius: 5px; font-weight: bold; width: 100%; }
    .online-tag { background: #00ff00; color: black; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
    .afk-tag { background: #ffff00; color: black; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
    .offline-tag { background: #555; color: white; padding: 2px 8px; border-radius: 10px; font-size: 12px; }
    .worker-card { background: #111; padding: 15px; border: 1px solid #333; border-radius: 10px; margin-bottom: 10px; }
</style>
""", unsafe_allow_html=True)

if 'user' not in st.session_state: st.session_state.user = None

# --- ЛОГИКА ВХОДА ---
if st.session_state.user is None:
    st.title("⚡ SPELLING SYSTEM v6")
    t_in, t_reg = st.tabs(["ВХОД", "РЕГИСТРАЦИЯ"])
    with t_in:
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type="password")
        if st.button("ВОЙТИ"):
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res:
                if res[1] == "banned": st.error("БАН")
                else:
                    st.session_state.user, st.session_state.role = u, res[0]
                    cursor.execute("UPDATE users SET user_state='Online' WHERE username=?", (u,))
                    conn.commit()
                    st.rerun()
            elif u == "admin" and p == "admin777":
                st.session_state.user, st.session_state.role = "CHIEF_ADMIN", "admin"
                st.rerun()
    with t_reg:
        nu = st.text_input("Ник")
        np = st.text_input("Пароль")
        if st.button("ЗАРЕГИСТРИРОВАТЬСЯ"):
            try:
                cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (nu, np))
                conn.commit()
                st.success("Готово!")
            except: st.error("Ник занят")

# --- ПАНЕЛЬ УПРАВЛЕНИЯ ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # Сайдбар с кнопкой выхода
    st.sidebar.title(f"👾 {user}")
    if st.sidebar.button("ВЫЙТИ ИЗ СИСТЕМЫ"):
        cursor.execute("UPDATE users SET user_state='Offline' WHERE username=?", (user,))
        conn.commit()
        st.session_state.user = None
        st.rerun()

    # --- ПАНЕЛЬ АДМИНА ---
    if role == "admin":
        st.title("👑 АДМИН-ТЕРМИНАЛ")
        a_tabs
