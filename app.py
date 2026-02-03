import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# Настройки
st.set_page_config(page_title="ELITE CONTROL v29", page_icon="⚡", layout="wide")

# База
conn = sqlite3.connect('control_v29.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("🔐 АВТОРИЗАЦИЯ")
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    c1, c2 = st.columns(2)
    if c1.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res:
                if res[1] == "banned": st.error("🚫 ТЫ ЗАБАНЕН")
                else:
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
            else: st.error("❌ Неверные данные")
    if c2.button("РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit()
            st.success("✅ Аккаунт создан")
        except: st.warning("⚠️ Логин занят")

# --- ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👤 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    # СЕКЦИЯ БАЛАНСА
    st.header(f"Профиль: {user}")
    if role != "admin":
        r = cursor.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()
        st.metric("Твой баланс", f"{r[0] if r else 0} ₽")

    st.divider()

    # ТАЙМЕР
    if 'work' not in st.session_state: st.session_state.work = False
    if not st.session_state.work:
        if st.button("▶ НАЧАТЬ ВОРК", type="primary"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        diff = datetime.now() - st.session_state.start
        time_str = str(diff).split('.')[0]
        st.error(f"⏱ ТЫ В РАБОТЕ: {time_str}")
        if st.button("⏹ ЗАКОНЧИТЬ"):
            m = max(1, int(diff.total_seconds()/60))
            cash = m * 100
            if role != "admin":
                cursor.execute("UPDATE users SET balance=balance+? WHERE username=?",(cash,
