import streamlit as st
import sqlite3

# --- ИНТЕРФЕЙС ---
st.set_page_config(page_title="WORK")
st.markdown("<style>.stApp{background:#111;color:#0f0;}</style>", unsafe_allow_html=True)

# --- БАЗА ---
db = sqlite3.connect('classic.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, m TEXT DEFAULT 'НЕТ')")
db.commit()

if 'auth' not in st.session_state:
    st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("ТЕРМИНАЛ")
    l = st.text_input("ID")
    p = st.text_input("KEY", type="password")
    
    if st.button("LOG"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ОШИБКА")
            
    if st.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("ЗАНЯТО")

else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        st.title("UNIT: " + str(st.session_state.user))
        d = db.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        st.metric("CASH", str(d[0]) + " RUB")
        st.info("MSG: " + str(d[1]))
    else:
        st.title("ADMIN")
        rows = db.execute("SELECT u, b, m FROM users").fetchall()
        for u, b, m in rows:
            with st.expander("ЮЗЕР: " + str(u)):
                nb = st.number_input("CASH", value=float(b), key="b"+u)
                nm = st.text_area("MSG", value=str(m), key="m"+u)
                # КОРОТКИЕ СТРОКИ ЧТОБЫ НЕ ОБРЕЗАЛОСЬ:
                if st.button("SAVE", key="s"+u):
                    db.execute("UPDATE users SET b=?, m=? WHERE u=?", (nb, nm, u))
                    db.commit(); st.rerun()
                if st.button("DEL", key="d"+u):
                    db.execute("DELETE FROM users WHERE u=?", (u,))
                    db.commit(); st.rerun()
