import streamlit as st
import sqlite3

# Настройка базы
conn = sqlite3.connect('team_v14.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0)')
conn.commit()

st.title("⚡ SPELLING CONTROL")

# Инициализация входа
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# ОКНО ВХОДА И РЕГИСТРАЦИИ
if not st.session_state.logged_in:
    menu = st.sidebar.selectbox("МЕНЮ", ["ВХОД", "РЕГИСТРАЦИЯ"])
    u = st.text_input("Логин")
    p = st.text_input("Пароль", type='password')
    
    if menu == "РЕГИСТРАЦИЯ" and st.button("СОЗДАТЬ"):
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (u, p))
            conn.commit()
            st.success("Аккаунт создан! Теперь выбери ВХОД.")
        except:
            st.error("Ник занят или ошибка.")

    if menu == "ВХОД" and st.button("ВОЙТИ"):
        if u == "admin" and p == "admin777":
            st.session_state.logged_in = True
            st.session_state.user = "ADMIN"
            st.rerun()
        else:
            cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (u, p))
            if cursor.fetchone():
                st.session_state.logged_in = True
                st.session_state.user = u
                st.rerun()
            else:
                st.error("Неверный логин или пароль.")

# ОКНО ПОСЛЕ ВХОДА (УБРАЛ ВСЕ СЛОЖНЫЕ ОТСТУПЫ)
if st.session_state.logged_in:
    st.sidebar.write(f"Вы вошли как: **{st.session_state.user}**")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.logged_in = False
        st.rerun()

    # ЕСЛИ АДМИН
    if st.session_state.user == "ADMIN":
        st.header("👑 АДМИН-ПАНЕЛЬ")
        workers = cursor.execute('SELECT username, balance FROM users').fetchall()
        for w in workers:
            st.write(f"👤 {w[0]} | Баланс: {w[1]} руб.")

    # ЕСЛИ ВОРКЕР
    if st.session_state.user != "ADMIN":
        st.header("🚀 ПАНЕЛЬ ВОРКЕРА")
        st.write("Таймер скоро будет тут.")
