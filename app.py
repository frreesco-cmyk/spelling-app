import streamlit as st
import sqlite3

# 1. СТИЛЬ (ЧИСТЫЙ НЕОН)
st.set_page_config(page_title="SYSTEM", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# 2. БАЗА (БЕЗ ОШИБОК)
db = sqlite3.connect('v85_final.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, m TEXT DEFAULT 'ЖДИТЕ')")
db.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not db.execute("SELECT t FROM news WHERE id=1").fetchone():
    db.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА ГОТОВА')")
db.commit()

# 3. ЛОГИКА АВТОРИЗАЦИИ
if 'auth' not in st.session_state: st.session_state.auth = False

if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l = st.text_input("ЛОГИН").strip()
    p = st.text_input("ПАРОЛЬ", type="password").strip()
    c1, c2 = st.columns(2)
    
    if c1.button("ВХОД"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ОТКАЗАНО")
            
    if c2.button("РЕГИСТРАЦИЯ"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("ОК")
            except: st.error("ЗАНЯТО")
else:
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False; st.rerun()
    
    if st.session_state.role == "worker":
        # ИНТЕРФЕЙС ВОРКЕРА
        st.title("🤖 ЮНИТ: " + st.session_state.user)
        n = db.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info("📢 ОБЩЕЕ: " + str(n))
        d = db.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        st.metric("ВАШ БАЛАНС", str(d[0]) + " RUB")
        st.warning("📩 ВАШ ПРИКАЗ: " + str(d[1]))
    else:
        # ИНТЕРФЕЙС АДМИНА
        st.title("👑 GOD MODE")
        n = db.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        new_n = st.text_input("ОБЩЕЕ ОБЪЯВЛЕНИЕ", value=n)
        if st.button("ОБНОВИТЬ"):
            db.execute("UPDATE news SET t=? WHERE id=1", (new_n,))
            db.commit(); st.rerun()
        
        st.divider()
        rows = db.execute("SELECT u, b, m FROM users").fetchall()
        for u, b, m in rows
