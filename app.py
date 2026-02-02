import streamlit as st
import sqlite3

# База данных
def get_db():
    conn = sqlite3.connect('team_v9.db', check_same_thread=False)
    return conn

conn = get_db()
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, role TEXT DEFAULT "worker")''')
conn.commit()

st.title("⚡ SPELLING SYSTEM V9")

# Самое важное - меню без лишних вкладок для стабильности
menu = ["ВХОД", "РЕГИСТРАЦИЯ"]
choice = st.radio("ВЫБЕРИ ДЕЙСТВИЕ:", menu, horizontal=True)

if choice == "ВХОД":
    st.subheader("🔑 АВТОРИЗАЦИЯ")
    u = st.text_input("Логин", key="login_u")
    p = st.text_input("Пароль", type="password", key="login_p")
    if st.button("ВОЙТИ"):
        # Проверка админа (вшит в код для надежности)
        if u == "admin" and p == "admin777":
            st.success("ПРИВЕТ, ГЛАВНЫЙ!")
            st.session_state.user = "admin"
            st.rerun()
        else:
            res = cursor.execute("SELECT * FROM users WHERE username=? AND password=?", (u, p)).fetchone()
            if res:
                st.success(f"ВОРКЕР {u} В СЕТИ!")
                st.session_state.user = u
                st.rerun()
            else:
                st.error("НЕВЕРНЫЕ ДАННЫЕ")

elif choice == "РЕГИСТРАЦИЯ":
    st.subheader("📝 СОЗДАНИЕ АККАУНТА")
    nu = st.text_input("Придумай логин", key="reg_u")
    np = st.text_input("Придумай пароль", key="reg_p")
    if st.button("ЗАРЕГИСТРИРОВАТЬСЯ"):
        try:
            cursor.execute("INSERT INTO users (username, password) VALUES (?,?)", (nu, np))
            conn.commit()
            st.success("АККАУНТ СОЗДАН! ТЕПЕРЬ ПЕРЕХОДИ ВО ВКЛАДКУ 'ВХОД'")
        except:
            st.error("ЭТОТ НИК УЖЕ ЗАНЯТ")
