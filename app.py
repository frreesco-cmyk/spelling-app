import streamlit as st
import sqlite3

# Настройка базы
conn = sqlite3.connect('final_v11.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0)')
conn.commit()

st.title("⚡ SPELLING CONTROL")

# Инициализация сессии, чтобы не вылетало ошибок
if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

# Если не залогинен - показываем вход/рег
if not st.session_state.logged_in:
    menu = ["ВХОД", "РЕГИСТРАЦИЯ"]
    choice = st.sidebar.selectbox("МЕНЮ", menu)

    if choice == "РЕГИСТРАЦИЯ":
        st.subheader("📝 Регистрация воркера")
        new_u = st.text_input("Придумай логин")
        new_p = st.text_input("Придумай пароль", type='password')
        if st.button("СОЗДАТЬ АККАУНТ"):
            try:
                cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (new_u, new_p))
                conn.commit()
                st.success("Готово! Переходи во вкладку ВХОД")
            except:
                st.error("Этот логин уже занят")

    else:
        st.subheader("🔑 Авторизация")
        u = st.text_input("Логин")
        p = st.text_input("Пароль", type='password')
        if st.button("ВОЙТИ"):
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
                    st.error("Неверный логин или пароль")

# Если залогинен - показываем контент
else:
    st.
