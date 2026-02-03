import streamlit as st
import sqlite3
import time
from datetime import datetime

# 1. ТЕМА
st.set_page_config(page_title="CORE v102", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:10px;}</style>", unsafe_allow_html=True)

# 2. БАЗА
db = sqlite3.connect('core_v102.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'НЕТ', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS logs (id INTEGER PRIMARY KEY, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT)")
if not db.execute("SELECT news FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, news) VALUES (1, 'SYSTEM ONLINE')")
db.commit()

# 3. ЛОГИКА
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False
if 'stime' not in st.session_state: st.session_state.stime = 0

if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l, p = st.text_input("ID").strip(), st.text_input("KEY", type="password").strip()
    if st.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u, status FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res and res[1] != 'banned':
                st.session_state.update({"auth":True, "user":l, "role":"worker"})
                st.rerun()
            else: st.error("ACCESS DENIED")
    if st.button("REG"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("OK")
        except: st.error("TAKEN")
else:
    if st.sidebar.button("EXIT"):
        st.session_state.auth = False; st.rerun()

    if st.session_state.role == "worker":
        # --- ВОРКЕР ---
        st.title("👤 UNIT: " + str(st.session_state.user))
        gn = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info("📢 GLOBAL: " + str(gn))
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        c1, c2, c3 = st.columns(3)
        c1.metric("CASH", str(ud[0]) + " RUB")
        c2.metric("XP", str(ud[1]))
        
        st.divider()
        if not st.session_state.shift:
            if st.button("▶️ START SHIFT"):
                st.session_state.shift = True
                st.session_state.stime = time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.stime)
            st.write("⏳ ON SHIFT: " + str(el) + " sec")
            if st.button("🛑 STOP SHIFT"):
                nxp = el // 10
                db.execute("UPDATE users SET xp=xp+? WHERE u=?", (max(1, nxp), st.session_state.user))
                db.commit()
                st.session_state.shift = False
                st.success("GOT " + str(nxp) + " XP")
                time.sleep(1); st.rerun()
            time.sleep(1); st.rerun()
        
        st.warning("📩 TASK: " + str(ud[2]))

    else:
        # --- АДМИН ---
        st.title("👑 ADMIN")
        nn = st.text_input("SET GLOBAL NEWS")
        if st.button("SEND NEWS"):
            db.execute("UPDATE config SET news=? WHERE id=1", (nn,))
            db.commit(); st.rerun()
        
        rows = db.execute("SELECT u, b, xp, m, status, p FROM users").fetchall()
        for u, b, xp, m, stat, pwd in rows:
            with st.expander("UNIT: " + str(u)):
                nb = st.number_input("CASH", value=float(b), key="b"+u)
                nx = st.number_input("XP", value=int(xp), key="x"+u)
                np = st.text_input("PASS", value=str(pwd), key="p"+u)
                nm = st.text_area("TASK", value=str(m), key="m"+u)
                if st.button("SAVE " + u):
                    db.execute("UPDATE users SET b=?, xp=?, m=?, p=? WHERE u=?", (nb, nx, nm, np, u))
                    db.commit(); st.rerun()
                if st.button("BAN/UNBAN " + u):
                    ns = 'banned' if stat == 'active' else 'active'
                    db.execute("UPDATE users SET status=? WHERE u=?", (ns, u))
                    db.commit(); st.rerun()
