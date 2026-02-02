import streamlit as st
import sqlite3
from datetime import datetime
import time

# --- БАЗА ДАННЫХ ---
conn = sqlite3.connect('final_fix_v16.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users 
                  (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                   role TEXT DEFAULT "worker", status TEXT DEFAULT "active", user_state TEXT DEFAULT "Offline")''')
cursor.execute('CREATE TABLE IF NOT EXISTS logs (user TEXT, duration TEXT, date TEXT, money_gain REAL)')
conn.commit()

st.title("⚡ SPELLING CONTROL v16")

# --- ИНИЦИАЛИЗАЦИЯ ПЕРЕМЕННЫХ (FIX ОШИБКИ) ---
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False
if 'user' not in st.session_state:
    st.session_state.user = ""
if 'role' not in st.session_state:
    st.session_state.role = "worker"

# --- ЛОГИКА ВХОДА ---
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("МЕНЮ", ["ВХОД", "РЕГИСТРАЦИЯ"])
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    
    if menu == "РЕГИСТРАЦИЯ" and st.button("СОЗДАТЬ"):
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (u, p))
            conn.commit()
            st.success("Аккаунт создан! Переходи во вход.")
        except: st.error("Ошибка или ник занят")

    if menu == "ВХОД" and st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.logged_in = True
            st.session_state.user = "ADMIN"
            st.session_state.role = "admin"
            st.rerun()
        else:
            res = cursor.execute("SELECT role, status FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res:
                if res[1] == "banned":
                    st.error("ТЫ ЗАБАНЕН")
                else:
                    st.session_state.logged_in = True
                    st.session_state.user = u
                    st.session_state.role = res[0]
                    st.rerun()
            else: st.error("Неверный логин")

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
else:
    user = st.session_state.user
    role = st.session_state.role
    
    st.sidebar.write(f"Вы вошли как: **{user}**")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.logged_in = False
        st.rerun()

    # 1. СТАТУСЫ
    st.subheader("🟢 СТАТУС")
    c1, c2, c3 = st.columns(3)
    if c1.button("В СЕТИ"): cursor.execute("UPDATE users SET user_state='Online' WHERE username=?", (user,)); conn.commit(); st.toast("Статус обновлен")
    if c2.button("АФК"): cursor.execute("UPDATE users SET user_state='AFK' WHERE username=?", (user,)); conn.commit();
