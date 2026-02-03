import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# 1. СИСТЕМА
st.set_page_config(page_title="ELITE v30", layout="wide")
conn = sqlite3.connect('control_v30.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, dur TEXT, date TEXT, cash REAL)')
conn.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# 2. ВХОД
if not st.session_state.auth:
    st.title("🔐 ВХОД")
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    if st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True, "user":u, "role":res[0]})
                st.rerun()
            else: st.error("Ошибка или БАН")
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username,password) VALUES (?,?)',(u,p))
            conn.commit()
            st.success("ОК")
        except: st.error("Занято")

# 3. ПАНЕЛЬ
else:
    user, role = st.session_state.user, st.session_state.role
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.auth = False
        st.rerun()

    st.header(f"Юзер: {user}")
    if role != "admin":
        r = cursor.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()
        st.metric("Баланс", f"{r[0] if r else 0} ₽")

    # ТАЙМЕР
    if 'work' not in st.session_state: st.session_state.work = False
    if not st.session_state.work:
        if st.button("▶ СТАРТ"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        diff = datetime.now() - st.session_state.start
        t_str = str(diff).split('.')[0]
        st.error(f"⏱ ВОРК: {t_str}")
        if st.button("⏹ СТОП"):
            m = max(1, int(diff.total_seconds()/60))
            pay = m * 100
            if role != "admin":
                cursor.execute("UPDATE users SET balance=balance+? WHERE username=?",(pay,user))
                cursor.execute("INSERT INTO logs VALUES
