import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- НАСТРОЙКИ СИСТЕМЫ ---
st.set_page_config(page_title="ELITE CONTROL v37", page_icon="💎", layout="wide")

# --- ПОДКЛЮЧЕНИЕ БД ---
# Имя базы изменено, чтобы избежать конфликтов со старыми версиями
conn = sqlite3.connect('elite_v37.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cur.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

# --- СТИЛИЗАЦИЯ ---
st.markdown("""
    <style>
    .stMetric { background-color: #1e212b; padding: 15px; border-radius: 10px; border: 1px solid #3e4451; }
    .stButton>button { border-radius: 8px; font-weight: bold; width: 100%; }
    h1, h2, h3 { color: #00ffcc; }
    </style>
    """, unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ОКНО ВХОДА ---
if not st.session_state.auth:
    st.title("🛡️ ВХОД В ELITE SYSTEM")
    t_login, t_reg = st.tabs(["🔑 АВТОРИЗАЦИЯ", "📝 РЕГИСТРАЦИЯ"])
    
    with t_login:
        u = st.text_input("Логин", key="u_in").strip()
        p = st.text_input("Пароль", type='password', key="p_in").strip()
        if st.button("🚀 ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error("❌ ДОСТУП ЗАПРЕЩЕН ИЛИ БАН")
                
    with t_reg:
        ru = st.text_input("Придумай логин").strip()
        rp = st.text_input("Придумай пароль", type='password').strip()
        if st.button("🆕 ЗАРЕГИСТРИРОВАТЬСЯ"):
            if ru and rp:
                try:
                    cur.execute('INSERT INTO users(username,password) VALUES (?,?)',(ru,rp))
                    conn.commit(); st.success("✅ Аккаунт создан! Теперь войди.")
                except: st.error("⚠️ Этот логин уже занят")
            else: st.warning("Заполни все поля")

# --- ГЛАВНЫЙ ЭКРАН ---
else:
    user, role = st.session_state.user, st.session_state.role
    
    # ПРОВЕРКА БАНА (КАЖДУЮ СЕКУНДУ)
    if role != "admin":
        check = cur.execute("SELECT status FROM users WHERE username=?",(user,)).fetchone()
        if not check or check[0] == "banned":
            st.session_state.auth = False
            st.error
