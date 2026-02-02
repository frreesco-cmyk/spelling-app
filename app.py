import streamlit as st
import sqlite3

# База данных
conn = sqlite3.connect('team_v13.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0)')
conn.commit()

st.title("⚡ SPELLING CONTROL")

if 'logged_in' not in st.session_state:
    st.session_state.logged_in = False

if st.session_state.logged_in == False:
    menu = st.sidebar.selectbox("МЕНЮ", ["ВХОД", "РЕГИСТРАЦИЯ"])
    
    if menu == "РЕГИСТРАЦИЯ":
        st.subheader("📝 Регистрация")
        new_u = st.text_input("Логин")
        new_p = st.text_input("Пароль", type='password')
        if st.button("СОЗДАТЬ"):
            try:
                cursor.execute('INSERT INTO users(username, password) VALUES (?,?)', (new_u, new_p))
                conn.commit()
                st.success("Готово! Теперь входи.")
            except:
                st.error("Ник занят")
                
    if menu == "ВХОД":
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

else:
    st.sidebar.write(f"Вы вошли как: **{st.session_state.user}**")
    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.logged_in = False
        st.rerun()

    if st.session_state.user == "ADMIN":
        st.header("👑 АДМИН-ПАНЕЛЬ")
        workers = cursor.execute('SELECT username, balance FROM users').fetchall()
        for w in workers:
            st.write(f"👤 {w[0]} | Баланс: {w[1]} руб.")
    else:
