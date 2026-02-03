import streamlit as st
import sqlite3

# --- СИСТЕМА ---
st.set_page_config(page_title="GOD_MODE", layout="wide")
st.markdown("<style>.stApp{background:#000;color:#0f0;} .stButton>button{border:1px solid #0f0;color:#0f0;}</style>", unsafe_allow_html=True)

def connect_db():
    c = sqlite3.connect('v74_final.db', check_same_thread=False)
    u = "CREATE TABLE IF NOT EXISTS users (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, role TEXT DEFAULT 'worker', status TEXT DEFAULT 'active', message TEXT DEFAULT 'НЕТ ПРИКАЗОВ')"
    g = "CREATE TABLE IF NOT EXISTS global_cfg (id INTEGER PRIMARY KEY, news TEXT)"
    c.execute(u)
    c.execute(g)
    if not c.execute("SELECT * FROM global_cfg").fetchone():
        c.execute("INSERT INTO global_cfg (id, news) VALUES (1, 'СИСТЕМА ЗАПУЩЕНА')")
    c.commit()
    return c

db = connect_db()

if 'auth' not in st.session_state:
    st.session_state['auth'] = False

# --- ВХОД ---
if not st.session_state['auth']:
    st.title("📟 LOGIN TERMINAL")
    u_in = st.text_input("USER").strip()
    p_in = st.text_input("PASS", type='password').strip()
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("LOGIN"):
            if u_in == "admin" and p_in == "admin777":
                st.session_state.update({"auth":True,"user":"admin","role":"admin"})
                st.rerun()
            else:
                r = db.execute("SELECT status FROM users WHERE username=? AND password=?", (u_in, p_in)).fetchone()
                if r and r[0] != 'banned':
                    st.session_state.update({"auth":True,"user":u_in,"role":"worker"})
                    st.rerun()
                else: st.error("DENIED")
    with c2:
        if st.button("REGISTER"):
            try:
                db.execute("INSERT INTO users (username,password) VALUES (?,?)", (u_in, p_in))
                db.commit()
                st.success("OK")
            except: st.error("ERROR")

# --- ИНТЕРФЕЙС ---
else:
    role = st.session_state['role']
    user = st.session_state['user']
    
    if st.sidebar.button("EXIT"):
        st.session_state['auth'] = False
        st.rerun()

    # --- ВОРКЕР ---
    if role == "worker":
        st.title(f"UNIT: {user}")
        gn = db.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()[0]
        st.info(f"ОБЩЕЕ: {gn}")
        
        ud = db.execute("SELECT balance, message FROM users WHERE username=?", (user,)).fetchone()
        if ud:
            st.metric("CASH", f"{ud[0]} RUB")
            st.warning(f"ORDER: {ud[1]}")

    # --- АДМИН ---
    else:
        st.title("👑 ADMIN CONTROL")
        gn = db.execute("SELECT news FROM global_cfg WHERE id=1").fetchone()[0]
        new_gn = st.text_input("GLOBAL NEWS", value=gn)
        if st.button("UPDATE"):
            db.execute("UPDATE global_cfg SET news=? WHERE id=1", (new_gn,))
            db.commit()
            st.rerun()

        st.divider()
        rows = db.execute("SELECT username, balance, status, message FROM users WHERE role='worker'").fetchall()
        for un, ub, us, um in rows:
            with st.expander(f"USER: {un} | {ub} RUB"):
                nb = st.number_input("Money", value=float(ub), key="b"+un)
                if st.button("SET MONEY", key="btnb"+un):
                    db.execute("UPDATE users SET balance=? WHERE username=?", (nb, un))
                    db.commit()
                    st.rerun()
                
                nm = st.text_area("Order", value=um, key="m"+un)
                if st.button("SET ORDER", key="btnm"+un):
                    db.execute("UPDATE users SET message=? WHERE username=?", (nm, un))
                    db.commit()
                    st.rerun()

                if st.button("BAN/UNBAN", key="s"+un):
                    ns = 'active' if us == 'banned' else 'banned'
                    db.execute("UPDATE users SET status=? WHERE username=?", (ns, un))
                    db.commit()
                    st.rerun()
                    
                if st.button("DELETE", key="d"+un):
                    db.execute("DELETE FROM users WHERE username=?", (un,))
                    db.commit()
                    st.rerun()
