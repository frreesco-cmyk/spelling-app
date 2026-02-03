import streamlit as st
import sqlite3

# 1. ТЕМА
st.set_page_config(page_title="SYSTEM", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# 2. БАЗА
db = sqlite3.connect('v86_work.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, m TEXT DEFAULT 'ЖДИТЕ')")
db.execute("CREATE TABLE IF NOT EXISTS news (id INTEGER PRIMARY KEY, t TEXT)")
if not db.execute("SELECT t FROM news WHERE id=1").fetchone():
    db.execute("INSERT INTO news (id, t) VALUES (1, 'СИСТЕМА ЗАПУЩЕНА')")
db.commit()

if 'auth' not in st.session_state: st.session_state.auth = False

# 3. ВХОД
if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l = st.text_input("ID").strip()
    p = st.text_input("KEY", type="password").strip()
    c1, c2 = st.columns(2)
    
    if c1.button("LOG"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ERR")
            
    if c2.button("REG"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("OK")
            except: st.error("TAKEN")

# 4. ИНТЕРФЕЙС
else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()
    
    if st.session_state.role == "worker":
        st.title("🤖 UNIT: " + str(st.session_state.user))
        n = db.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        st.info("📢 GLOBAL: " + str(n))
        d = db.execute("SELECT b, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        st.metric("CASH", str(d[0]) + " RUB")
        st.warning("ORDER: " + str(d[1]))
    else:
        st.title("👑 ADMIN")
        n = db.execute("SELECT t FROM news WHERE id=1").fetchone()[0]
        new_n = st.text_input("NEWS", value=n)
        if st.button("SET"):
            db.execute("UPDATE news SET t=? WHERE id=1", (new_n,))
            db.commit(); st.rerun()
        
        st.divider()
        rows = db.execute("SELECT u, b, m FROM users").fetchall()
        for u, b, m in rows:
            if u == "admin": continue
            with st.expander("👤 " + str(u) + " | " + str(b) + " RUB"):
                nb = st.number_input("Money", value=float(b), key="b"+u)
                if st.button("SAVE CASH", key="sb"+u):
                    db.execute("UPDATE users SET b=? WHERE u=?", (nb, u))
                    db.commit(); st.rerun()
                nm = st.text_area("Order", value=m, key="m"+u)
                if st.button("SAVE ORDER", key="sm"+u):
                    db.execute("UPDATE users SET m=? WHERE u=?", (nm, u))
                    db.commit(); st.rerun()
                if st.button("DELETE USER", key="dl"+u):
                    db.execute("DELETE FROM users WHERE u=?", (u,))
                    db.commit(); st.rerun()
