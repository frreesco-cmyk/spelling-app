import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# Настройки
st.set_page_config(page_title="CONTROL PRO v28", page_icon="🚫", layout="wide")

# База
conn = sqlite3.connect('control_v28.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# ВХОД
if not st.session_state.auth:
    st.title("🛡️ ВХОД")
    u = st.text_input("Username")
    p = st.text_input("Password", type='password')
    if st.button("🔓 ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res:
                if res[1] == "banned": st.error("🛑 ДОСТУП ЗАКРЫТ (БАН)")
                else:
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
            else: st.error("❌ Ошибка")
    if st.button("📝 РЕГ"):
        try:
            cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit()
            st.success("✅ Создано")
        except: st.warning("⚠️ Занято")

# ИНТЕРФЕЙС
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.title(f"👾 {user}")
    if st.sidebar.button("🚪 ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    # БАЛАНС И ТАЙМЕР
    st.header(f"Профиль: {user}")
    if role != "admin":
        row = cursor.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()
        st.metric("Твой баланс", f"{row[0] if row else 0} ₽")

    st.divider()
    if 'work' not in st.session_state: st.session_state.work = False
    
    if not st.session_state.work:
        if st.button("▶ СТАРТ", type="primary"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
