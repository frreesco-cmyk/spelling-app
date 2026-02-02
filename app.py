import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('final_v18.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Offline")')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

st.title("⚡ SPELLING SYSTEM v18")

# Инициализация сессии
if 'logged_in' not in st.session_state: st.session_state.logged_in = False
if 'active' not in st.session_state: st.session_state.active = False

# --- ОКНО ВХОДА ---
if not st.session_state.logged_in:
    mode = st.sidebar.radio("МЕНЮ", ["ВХОД", "РЕГИСТРАЦИЯ"])
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    
    if mode == "РЕГИСТРАЦИЯ" and st.button("СОЗДАТЬ АККАУНТ"):
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (u, p))
            conn.commit()
            st.success("Успех! Теперь переключись на ВХОД.")
        except: st.error("Ошибка или ник занят")

    if mode == "ВХОД" and st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"logged_in": True, "user": "ADMIN", "role": "admin"})
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"logged_in": True, "user": u, "role": res[0]})
                st.rerun()
            else: st.error("Ошибка доступа или БАН")

# --- ОСНОВНОЙ КОНТЕНТ (БЕЗ ТАБОВ И КОЛОНОК) ---
else:
    user, role = st.session_state.user, st.session_state.role
    st.sidebar.write(f"Вы вошли как: **{user}**")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.logged_in = False
        st.rerun()

    # СТАТУСЫ
    st.write("### 🟢 ВАШ СТАТУС")
    if st.button("Я В СЕТИ"): cursor.execute("UPDATE users SET user_state='Online' WHERE username=?", (user,)); conn.commit(); st.success("Статус: Online")
    if st.button
