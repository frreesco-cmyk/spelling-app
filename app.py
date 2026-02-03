import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- НАСТРОЙКИ ---
st.set_page_config(page_title="SPELLING CONTROL PRO", page_icon="📈", layout="wide")

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('final_v32.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# --- СТИЛЬ ---
st.markdown("""<style>
    .stMetric { background-color: #1e212b; padding: 15px; border-radius: 10px; border: 1px solid #3e4451; }
    .stButton>button { border-radius: 8px; height: 3.5em; font-weight: bold; width: 100%; }
    .work-box { padding: 20px; border-radius: 15px; background-color: #161b22; border: 1px solid #30363d; text-align: center; }
    </style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("🛡️ ВХОД В СИСТЕМУ")
    col1, col2 = st.columns(2)
    with col1:
        u = st.text_input("Логин").strip()
        p = st.text_input("Пароль", type='password').strip()
        if st.button("🚀 ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error("❌ ОШИБКА ИЛИ БАН")
    with col2:
        st.info("Регистрация новых воркеров")
        if st.button("📝 СОЗДАТЬ АККАУНТ"):
            try:
                cur.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
                conn.commit(); st.success("✅ ГОТОВО! ЖМИ ВОЙТИ")
            except: st.error("⚠️ ЛОГИН ЗАНЯТ")

# --- ГЛАВНЫЙ ЭКРАН ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👾 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    st.header(f"👋 Привет, {user}!")
    
    # Виджеты баланса
    c1, c2 = st.columns(2)
    with c1:
        if role == "admin": st.metric("Статус", "👑 ГЛАВНЫЙ")
        else:
            row = cur.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()
            st.metric("Твой баланс", f"{row[0] if row else 0} ₽")
    
    st.divider()

    # РАБОЧИЙ ТАЙМЕР
    st.subheader("⌛ УПРАВЛЕНИЕ СМЕНОЙ")
    if 'work' not in st.session_state: st.session_state.work = False
