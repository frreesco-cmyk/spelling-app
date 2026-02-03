import streamlit as st
import sqlite3

# 1. БАЗА
db = sqlite3.connect('final_v100.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, m TEXT DEFAULT 'НЕТ', t TEXT DEFAULT '00:00')")
db.commit()

# 2. СТИЛЬ
st.markdown("<style>.stApp{background:#000;color:#0f0;}</style>", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# 3. ЛОГИКА
if not st.session_state.auth:
    st.title("📟 ВХОД")
    l, p = st.text_input("ID"), st.text_input("KEY", type="password")
    if st.button("LOG"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
    if st.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("ERR")
else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        st.title("👤 ЮНИТ: " + st.session_state.user)
        ud = db.execute("SELECT b, m, t FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        st.metric("CASH", f"{ud[0]} RUB")
        st.metric("TIMER", ud[2])
        st.warning(f"ПРИКАЗ: {ud[1]}")
    else:
        st.title("👑 АДМИН")
        rows = db.execute("SELECT u, b, m, t FROM users").fetchall()
        for u, b, m, t in rows:
            with st.expander(f"ЮНИТ: {u}"):
                nb = st.number_input("CASH", value=float(b), key="b"+u)
                nt = st.text_input("TIME", value=t, key="t"+u)
                nm = st.text_area("MSG", value=m, key="m"+u)
                if st.button("SAVE", key="s"+u):
                    db.execute("UPDATE users SET b=?, t=?, m=? WHERE u=?", (nb, nt, nm, u))
                    db.commit(); st.rerun()
