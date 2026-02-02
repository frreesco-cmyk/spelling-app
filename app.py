import streamlit as st
import sqlite3

# Создаем чистую базу данных
conn = sqlite3.connect('ultra_db_v12.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, status TEXT DEFAULT "active")')
conn.commit()

st.title("⚡ SPELLING SYSTEM PRO")

# Простейшая проверка входа
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if not st.session_state.logged_in:
    choice = st.sidebar.selectbox("МЕНЮ", ["ВХОД", "РЕГИСТРАЦИЯ"])
    
    if choice == "РЕГИСТРАЦИЯ":
        st.subheader("📝 Создать аккаунт")
        u = st.text_input("Придумай логин")
        p = st.text_input("Придумай пароль", type='password')
        if st.button("ЗАРЕГИСТРИРОВАТЬСЯ"):
            try:
                cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (u, p))
                conn.commit()
                st.success("Аккаунт создан! Теперь выбери ВХОД в меню слева.")
            except:
                st.error("Этот ник уже занят!")
    else:
        st.subheader("🔑 Авторизация")
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type='password')
        if st.button("ВОЙТИ"):
