import streamlit as st
import sqlite3

# 1. СТИЛЬ (ЧЕРНЫЙ И ЗЕЛЕНЫЙ)
st.set_page_config(page_title="SYSTEM", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} input{background:#222!important;color:#0f0!important;}</style>", unsafe_allow_html=True)

# 2. ПОДКЛЮЧЕНИЕ БАЗЫ (НОВОЕ ИМЯ ДЛЯ ЧИСТОГО СТАРТА)
conn = sqlite3.connect('database_v77.db', check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, r TEXT DEFAULT 'w', s TEXT DEFAULT 'a', m TEXT DEFAULT 'НЕТ')")
conn.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not conn.execute("SELECT t FROM news WHERE id=1").fetchone():
    conn.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА ЗАПУЩЕНА')")
conn.commit()

# 3. АВТОРИЗАЦИЯ
if 'auth' not in st.session_state: 
    st.session_state.auth = False

if not st.session_state.auth:
    st.title("📟 ВХОД")
    login = st.text_input("ЛОГИН").strip()
    pas = st.text_input("ПАРОЛЬ", type="password").strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ВОЙТИ"):
            if login == "admin" and pas == "admin777":
                st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
                st.rerun()
            else:
                data = conn.execute("SELECT s, r FROM users WHERE u=? AND p=?", (login, pas)).fetchone()
                if data:
                    if data[0] != 'banned':
                        st.session_state.update({"auth":True, "user":login, "role":"worker"})
                        st.rerun()
                    else: st.error("БАН")
                else: st.error("ОШИБКА")
    with col2:
        if st.button("РЕГИСТРАЦИЯ"):
            if login and pas:
                try:
                    conn.execute("INSERT INTO users (u, p) VALUES (?, ?)", (login, pas))
                    conn.commit()
                    st.success("ГОТОВО")
                except:
                    st.error("ЗАНЯТО")

# 4. РАБОЧИЙ СТОЛ
else:
    u_name = st.session_state.user
    u_role = st.session_state.role
    
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False
        st.rerun()

    if u_role == "worker":
        st.title(f"ЮНИТ: {u_name}")
        gn = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info(f"ОБЩЕЕ: {gn}")
        
        ud = conn.execute("SELECT b, m FROM users WHERE u=?", (u_name,)).fetchone()
        if ud:
            st.metric("БАЛАНС", f"{ud[0]} руб")
            st.warning(f"ПРИКАЗ: {ud[1]}")

    else:
        st.title("👑 АДМИН ПАНЕЛЬ")
        
        # Общая новость
        curr_n = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        new_n = st.text_input("ОБЩЕЕ ОБЪЯВЛЕНИЕ", value=curr_n)
        if st.button("ОБНОВИТЬ НОВОСТЬ"):
            conn.execute("UPDATE news SET t=? WHERE id=1", (new_n,))
            conn.commit()
            st.rerun()

        st.divider()
        
        # Список воркеров
        workers = conn.execute("SELECT u, b, s, m FROM users WHERE r='w'").fetchall()
        if not workers: 
            st.
