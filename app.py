import streamlit as st
import sqlite3

# Чистая база данных
conn = sqlite3.connect('fix_v10.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0)')
conn.commit()

st.header("⚡ ПАНЕЛЬ УПРАВЛЕНИЯ SPELLING")

# Выбор действия через радио-кнопки (они никогда не исчезают)
choice = st.sidebar.selectbox("МЕНЮ", ["ВХОД", "РЕГИСТРАЦИЯ"])

if choice == "РЕГИСТРАЦИЯ":
    st.subheader("📝 Создать аккаунт")
    new_user = st.text_input("Логин")
    new_pass = st.text_input("Пароль", type='password')
    if st.button("ЗАРЕГИСТРИРОВАТЬСЯ"):
        try:
            cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (new_user, new_pass))
            conn.commit()
            st.success("Аккаунт создан! Теперь переключись на ВХОД.")
        except:
            st.error("Этот логин уже занят.")

elif choice == "ВХОД":
    st.subheader("🔑 Авторизация")
    user = st.text_input("Ваш логин")
    pw = st.text_input("Ваш пароль", type='password')
    
    if st.button("ВОЙТИ"):
        # Вход для тебя (админ)
        if user == "admin" and pw == "admin777":
            st.session_state.logged_in = True
            st.session_state.user = "ГЛАВНЫЙ"
            st.success("ДОСТУП РАЗРЕШЕН")
            st.rerun()
        else:
            # Вход для воркера
            cursor.execute('SELECT * FROM users WHERE username=? AND password=?', (user, pw))
            data = cursor.fetchone()
            if data:
                st.session_state.logged_in = True
                st.session_state.user = user
                st.success(f"Привет, {user}!")
                st.rerun()
            else:
                st.error("Неверный логин или пароль")

# Если вошли — показываем функционал
if 'logged_in' in st.session_state and st.session_state
