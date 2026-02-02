import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# База данных
conn = sqlite3.connect('team_v21.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Off")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, cash REAL)')
conn.commit()

st.title("⚡ SYSTEM v21")

if 'auth' not in st.session_state:
    st.session_state.auth = False

# ВХОД
if not st.session_state.auth:
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    if st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth": True, "user": "ADMIN", "role": "admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth": True, "user": u, "role": res[0]})
                st.rerun()
            else: st.error("Ошибка")
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (u, p))
            conn.commit()
            st.success("ОК")
        except: st.error("Занято")

# ИНТЕРФЕЙС
else:
    user, role = st.session_state.user, st.session_state.role
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False
        st.rerun()

    st.write(f"### Юзер: {user}")
    
    # ТАЙМЕР
    if 'work' not in st.session_state: st.session_state.work = False
    if not st.session_state.work:
        if st.button("▶ СТАРТ"):
            st.session_state.start = datetime.now()
            st.session_state.work = True
            st.rerun()
    else:
        dur = datetime.now() - st.session_state
