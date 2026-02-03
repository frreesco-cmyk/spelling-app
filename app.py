import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- CORE SETTINGS ---
st.set_page_config(page_title="OFFICE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stMetric{border:1px solid #0f0;background:#111;padding:15px;}</style>", unsafe_allow_html=True)

# --- DB INIT ---
db = sqlite3.connect('synd_v125.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'ЗАДАНИЙ НЕТ', s TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT DEFAULT 'ONLINE')")
db.commit()

# --- RANK ---
def get_rank(xp_val):
    if xp_val < 500: return "РЕКРУТ"
    if xp_val < 2000: return "БОЕЦ"
    return "ЭЛИТА"

# --- SESSION ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

# --- LOGIN ---
if not st.session_state.auth:
    st.title("📟 ТЕРМИНАЛ")
    l_id = st.text_input("ID").strip()
    l_pw = st.text_input("КЛЮЧ", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("ВХОД"):
        if l_id == "admin" and l_pw == "admin777":
            st.session_state.update({"auth":True, "role":"admin", "user":"admin"})
            st.rerun()
        q = "SELECT u, s FROM users WHERE u=? AND p=?"
        res = db.execute(q, (l_id, l_pw)).fetchone()
        if res and res[1] == 'active':
            st.session_state.update({"auth":True, "role":"worker", "user":l_id})
            st.rerun()
        else: st.error("ОТКАЗАНО")
    if c2.button("РЕГИСТРАЦИЯ"):
        try:
            db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l_id, l_pw))
            db.commit(); st.success("OK")
        except: st.error("ЗАНЯТО")

else:
    if st.sidebar.button("ВЫХОД"):
        st.session_state.auth = False; st.rerun()

    # --- WORKER ---
    if st.session_state.role == "worker":
        st.title("ЮНИТ: " + str(st.session_state.user))
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        
        col1, col2 = st.columns(2)
        col1.metric("БАЛАНС", str(ud[0]))
        col2.metric("XP", str(ud[1]))
        st.write("РАНГ: " + get_rank(ud[1]))

        st.divider()
        if not st.session_state.shift:
            if st.button("▶️ НАЧАТЬ"):
                st.session_state.shift, st.session_state.st = True, time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.st)
            st.error("ВРЕМЯ: " + str(el) + " сек.")
            if st.button("🛑 СТОП"):
                db.execute("UPDATE users SET xp=xp+? WHERE u=?", (max(5, el//4), st.session_state.user))
                db.commit(); st.session_state.shift = False
                st.rerun()
            time.sleep(1); st.rerun()

        st.warning("ЗАДАЧА: " + str(ud[2]))
        
        with st.expander("ЧАТ"):
            m_txt = st.text_input("Сообщение")
            if st.button("ОТПРАВИТЬ"):
                db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", (st.session_state.user, m_txt, "now"))
                db.commit(); st.rerun()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 5").fetchall():
                st.text(str(cu) + ": " + str(cm))

    # --- ADMIN ---
    else:
        st.title("👑 АДМИН")
        t1, t2 = st.tabs(["ЮНИТЫ", "ЧАТ"])
        with t1:
            for u, b, x, m, s, p in db.execute("SELECT * FROM users").fetchall():
                with st.expander("UNIT: " + str(u)):
                    nb = st.number_input("CASH", value=float(b), key="b"+u)
                    nx = st.number_input("XP", value=int(x), key="x"+u)
                    nm = st.text_area("TASK", value=str(m), key="m"+u)
                    if st.button("SAVE", key="s"+u):
                        db.execute("UPDATE users SET b=?, xp=?, m=? WHERE u=?", (nb, nx, nm, u))
                        db.commit(); st.rerun()
                    if st.button("BAN", key="bn"+u):
                        ns = 'banned' if s == 'active' else 'active'
                        db.execute("UPDATE users SET s=? WHERE u=?", (ns, u))
                        db.commit(); st.rerun()
        with t2:
            st.subheader("ЛОГИ ЧАТА")
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 15").fetchall():
                st.text(str(cu) + ": " + str(cm))
