import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- STYLING ---
st.set_page_config(page_title="SYNDICATE PANEL", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:15px;}</style>", unsafe_allow_html=True)

# --- DB INIT ---
db = sqlite3.connect('syndicate_final.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'WAIT', s TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT DEFAULT 'SYSTEM READY')")
db.commit()

# --- RANKING ---
def get_rank(xp):
    if xp < 500: return "RECRUIT", 0.2
    if xp < 2000: return "OPERATIVE", 0.5
    if xp < 5000: return "ELITE", 0.8
    return "LEGEND", 1.0

# --- AUTH ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

if not st.session_state.auth:
    st.title("📟 ACCESS TERMINAL")
    l, p = st.text_input("ID").strip(), st.text_input("PASSWORD", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("ENTER"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        res = db.execute("SELECT u, s FROM users WHERE u=? AND p=?", (l, p)).fetchone()
        if res and res[1] == 'active':
            st.session_state.update({"auth":True, "role":"worker", "user":l})
            st.rerun()
        else: st.error("DENIED")
    if c2.button("JOIN"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
            db.commit(); st.success("REGISTERED")
        except: st.error("TAKEN")
else:
    # --- WORKER ---
    if st.session_state.role == "worker":
        st.title("UNIT: " + str(st.session_state.user))
        news = db.execute("SELECT news FROM config WHERE id=1").fetchone()[0]
        st.info("DISPATCH: " + str(news))
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        rn, pr = get_rank(ud[1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CASH", str(ud[0]))
        c2.metric("XP", str(ud[1]))
        c3.metric("RANK", rn)
        st.progress(pr)

        st.divider()
        if not st.session_state.shift:
            if st.button("▶️ START SHIFT"):
                st.session_state.shift, st.session_state.st = True, time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.st)
            st.error("PROCESS: " + str(el) + "s")
            if st.button("🛑 STOP"):
                db.execute("UPDATE users SET xp=xp+? WHERE u=?", (max(5, el//4), st.session_state.user))
                db.commit(); st.session_state.shift = False
                st.rerun()
            time.sleep(1); st.rerun()

        st.warning("TASK: " + str(ud[2]))
        with st.expander("COMMS"):
            m_in = st.text_input("Message...")
            if st.button("SEND"):
                db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", (st.session_state.user, m_in, datetime.now().strftime("%H:%M")))
                db.commit(); st.rerun()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 5").fetchall():
                st.text("[" + str(cd) + "] " + str(cu) + ": " + str(cm))

    # --- ADMIN ---
    else:
        st.title("👑 SUPREME COMMAND")
        t1, t2 = st.tabs(["UNITS", "SYSTEM"])
        with t1:
            for u, b, x, m, s, p in db.execute("SELECT * FROM users").fetchall():
                with st.expander("USER: " + str(u)):
                    nb = st.number_input("CASH", value=float(b), key="b"+u)
                    nx = st.number_input("XP", value=int(x), key="x"+u)
                    nm = st.text_area("TASK", value=str(m), key="m"+u)
                    np = st.text_input("PASS", value=str(p), key="p"+u)
                    if st.button("SAVE " + str(u)):
                        db.execute("UPDATE users SET b=?, xp=?, m=?, p=? WHERE u=?", (nb, nx, nm, np, u))
                        db.commit(); st.rerun()
                    if st.button("BAN/UNBAN " + str(u)):
                        ns = 'banned' if s == 'active' else 'active'
                        db.execute("UPDATE users SET s=? WHERE u=?", (ns, u))
                        db.commit(); st.rerun()
        with t2:
            nn = st.text_input("BROADCAST NEWS")
            if st.button("SEND"):
                db.execute("UPDATE config SET news=? WHERE id=1", (nn,))
                db.commit(); st.rerun()
            st.divider()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 20").fetchall():
                st.text("[" + str(cd) + "] " + str(cu) + ": " + str(cm))
