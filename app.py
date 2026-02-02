import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# База
conn = sqlite3.connect('team_v20.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Off")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, cash REAL)')
conn.commit()

st.title("⚡ CONTROL v20")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ВХОД
if not st.session_state.logged_in:
    u = st.text_input("Login")
    p = st.text_input("Pass", type='password')
    if st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"logged_in": True, "user": "ADMIN", "role": "admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"logged_in": True, "user": u, "role": res[0]})
                st.rerun()
            else: st.error("Ошибка входа")
    if st.button("РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (u, p))
            conn.commit()
            st.success("ОК! Жми войти")
        except: st.error("Ник занят")

# ПАНЕЛЬ
else:
    user, role = st.session_state.user, st.session_state.role
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.logged_in = False
        st.rerun()

    st.write(f"### Юзер: {user}")
    
    # СТАТУС
    if st.button("ОНЛАЙН"):
        cursor.execute("UPDATE users SET user_state='On' WHERE username=?", (user,))
        conn.commit()
    
    # ТАЙМЕР
    if 'active' not in st.session_state: st.session_state.active = False
    if not st.session_state.active:
        if st.button("▶ СТАРТ"):
            st.session_state.start_t = datetime.now()
            st.
