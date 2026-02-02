import streamlit as st
import sqlite3
from datetime import datetime
import time

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('ultra_system_v17.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Offline")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

st.set_page_config(page_title="SPELLING SYSTEM v17", layout="wide")

# --- ИНИЦИАЛИЗАЦИЯ (ЧТОБЫ НЕ БЫЛО ОШИБОК) ---
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'user' not in st.session_state: st.session_state.user = ""
if 'role' not in st.session_state: st.session_state.role = "worker"
if 'active' not in st.session_state: st.session_state.active = False

# --- ВХОД / РЕГИСТРАЦИЯ ---
if not st.session_state.logged_in:
    st.title("⚡ ВХОД В СИСТЕМУ")
    tab1, tab2 = st.tabs(["ВХОД", "РЕГИСТРАЦИЯ"])
    with tab1:
        u = st.text_input("Логин", key="l_u")
        p = st.text_input("Пароль", type='password', key="l_p")
        if st.button("ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"logged_in": True, "user": "ADMIN", "role": "admin"})
                st.rerun()
            else:
                res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"logged_in": True, "user": u, "role": res[0]})
                    st.rerun()
                elif res and res[1] == "banned": st.error("ВЫ ЗАБАНЕНЫ")
                else: st.error("НЕВЕРНЫЕ ДАННЫЕ")
    with tab2:
        nu = st.text_input("Новый логин")
        np = st.text_input("Новый пароль")
        if st.button("СОЗДАТЬ АККАУНТ"):
            try:
                cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (nu, np))
                conn.commit()
                st.success("Готово! Входи.")
            except: st.error("Ник занят")

# --- ОСНОВНОЙ ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👾 {user}")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.logged_in = False
        st.rerun()

    # БЛОК 1: ТАЙМЕР И СТАТУС (ВИДЯТ ВСЕ)
    col1, col2 = st.columns([1, 1])
    with col1:
