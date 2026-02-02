import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# Настройка БД
conn = sqlite3.connect('team_v19.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Offline")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

st.title("⚡ SPELLING CONTROL v19")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ОКНО ВХОДА
if st.session_state.logged_in == False:
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    col_l, col_r = st.columns(2)
    if col_l.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"logged_in": True, "user": "ADMIN", "role": "admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"logged_in": True, "user": u, "role": res[0]})
                st.rerun()
            else:
                st.error("Ошибка или БАН")
    if col_r.button("РЕГИСТРАЦИЯ"):
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (u, p))
            conn.commit()
            st.success("Создано! Жми ВОЙТИ")
        except:
            st.error("Ник занят")

# ИНТЕРФЕЙС (ЕСЛИ ВОШЕЛ)
if st.session_state.logged_in == True:
    user = st.session_state.user
    role = st.session_state.role
    st.sidebar.write(f"Юзер: {user}")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.logged_in = False
        st.rerun()

    # КНОПКИ СТАТУСА
    st.write("### 🟢 СТ
