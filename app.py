import streamlit as st
import sqlite3

# 1. СТИЛЬ
st.set_page_config(page_title="GOD_MODE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;padding:5px;background:#111;}</style>", unsafe_allow_html=True)

# 2. БАЗА (Новое имя файла, чтобы точно сбросить ошибки)
conn = sqlite3.connect('v80_final.db', check_same_thread=False)
conn.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, r TEXT DEFAULT 'w', s TEXT DEFAULT 'a', m TEXT DEFAULT 'ЖДИТЕ ПРИКАЗА')")
conn.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not conn.execute("SELECT t FROM news WHERE id=1").fetchone():
    conn.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА ОНЛАЙН')")
conn.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# 3. ВХОД
if not st.session_state.auth:
    st.title("📟 АВТОРИЗАЦИЯ")
    l = st.text_input("ЛОГИН")
    p = st.text_input("ПАРОЛЬ", type="password")
    c1, c2 = st.columns(2)
    if c1.button("ВОЙТИ"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = conn.execute("SELECT s, r FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res and res[0] != 'banned':
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ОТКАЗАНО")
    if c2.button("РЕГИСТРАЦИЯ"):
        try:
            conn.execute("INSERT INTO users (u, p, b) VALUES (?, ?, 0)", (l, p))
            conn.commit(); st.success("ГОТОВО")
        except: st.error("ЗАНЯТО")
else:
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False; st.rerun()
    
    # --- ИНТЕРФЕЙС ВОРКЕРА ---
    if st.session_state.role == "worker":
        st.title(f"ЮНИТ: {st.session_state.user}")
        gn = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info(f"📢 ОБЩЕЕ: {gn}")
        
        d = conn.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        # ПРОВЕРКА НА ОШИБКУ (Фикс TypeError)
        val_b = d[0] if (d and d[0] is not None) else 0
        val_m = d[1] if (d and d[1] is not None) else "НЕТ ПРИКАЗОВ"
        
        st.metric("ВАШ БАЛАНС", f"{val_b} RUB")
        st.warning(f"📩 ПРИКАЗ: {val_m}")

    # --- ИНТЕРФЕЙС АДМИНА ---
    else:
        st.title("👑 АДМИН ПАНЕЛЬ")
        gn = conn.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        new_n = st.text_input("ОБЩЕЕ ОБЪЯВЛЕНИЕ", value=gn)
        if st.button("ОБНОВИТЬ"):
            conn.execute("UPDATE news SET t=? WHERE id=1", (new_n,))
            conn.commit(); st.rerun()
        
        st.divider()
        rows = conn.execute("SELECT u, b, s, m FROM users WHERE r='w'").fetchall()
        for u, b, s, m in rows:
            with st.expander(f"ЮНИТ: {u} | {
