import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time

# --- CONFIG ---
st.set_page_config(page_title="GOD COMMAND v52", page_icon="👑", layout="wide")

# --- DATABASE SETUP ---
def init_db():
    conn = sqlite3.connect('v52_core.db', check_same_thread=False)
    cur = conn.cursor()
    cur.execute('''CREATE TABLE IF NOT EXISTS users 
                   (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                    role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                    is_working INTEGER DEFAULT 0, last_act TEXT, xp INTEGER DEFAULT 0)''')
    cur.execute('CREATE TABLE IF NOT EXISTS vault (total_tax REAL DEFAULT 0)')
    cur.execute('CREATE TABLE IF NOT EXISTS config (tax REAL DEFAULT 15, reg_open INTEGER DEFAULT 1)')
    if not cur.execute('SELECT * FROM vault').fetchone(): cur.execute('INSERT INTO vault VALUES (0)')
    if not cur.execute('SELECT * FROM config').fetchone(): cur.execute('INSERT INTO config VALUES (15, 1)')
    conn.commit()
    return conn

conn = init_db()
cur = conn.cursor()

# --- STYLES ---
st.markdown("""<style>
    .stApp { background: #000; color: #0f0; }
    .stMetric { background: #050505; border: 1px solid #0f0; border-radius: 5px; padding: 10px; }
    .stButton>button { border: 1px solid #0f0; color: #0f0; background: transparent; width: 100%; }
    .stButton>button:hover { background: #0f0; color: #000; box-shadow: 0 0 15px #0f0; }
    input { background-color: #111 !important; color: #0f0 !important; border: 1px solid #0f0 !important; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД В СИСТЕМУ ---
if not st.session_state.auth:
    st.title("🔐 TERMINAL ACCESS")
    
    col1, col2 = st.columns(2)
    with col1:
        u = st.text_input("IDENTIFIER").strip()
        p = st.text_input("PASSWORD", type='password').strip()
        if st.button("UPLINK"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[1] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":res[0]})
                    st.rerun()
                else: st.error("ACCESS DENIED / BANNED")
    
    with col2:
        reg_status = cur.execute("SELECT reg_open FROM config").fetchone()[0]
        if reg_status:
            st.info("РЕГИСТРАЦИЯ ОТКРЫТА")
            nu = st.text_input("NEW LOGIN").strip()
            np = st.text_input("NEW PASS").strip()
            if st.button("CREATE UNIT"):
                if nu and np:
                    try:
                        cur.execute('INSERT INTO users(username,password,last_act,xp) VALUES (?,?,?,0)',(nu,np,"-"))
                        conn.commit(); st.success("SUCCESS")
                    except: st.error("ID TAKEN")
        else:
            st.warning("РЕГИСТРАЦИЯ ЗАКРЫТА АДМИНИСТРАТОРОМ")

# --- ГЛАВНЫЙ ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    cur.execute("UPDATE users SET last_act=? WHERE username=?", (datetime.now().strftime("%H:%M:%S"), user))
    conn.commit()

    st.sidebar.title(f"📍 {user}")
    if st.sidebar.button("EXIT"):
        cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
        conn.commit(); st.session_state.auth = False; st.rerun()

    # --- ИНТЕРФЕЙС ВОРКЕРА ---
    if role != "admin":
        st.title(f"🛠 WORKER UNIT: {user}")
        bal, xp = cur.execute("SELECT balance, xp FROM users WHERE username=?",(user,)).fetchone()
        
        c1, c2 = st.columns(2)
        c1.metric("💰 CREDITS", f"{round(bal, 2)} ₽")
        c2.metric("🧬 EXPERIENCE", f"{xp} XP")

        if 'work' not in st.session_state: st.session_state.work = False
        
        if not st.session_state.work:
            if st.button("▶ START HARVESTING", type="primary"):
                st.session_state.start = datetime.now()
                st.session_state.work = True
                cur.execute("UPDATE users SET is_working=1 WHERE username=?", (user,))
                conn.commit(); st.rerun()
        else:
            diff = datetime.now() - st.session_state.start
            st.warning(f"⛏ MINING ACTIVE: {str(diff).split('.')[0]}")
            tax_rate = cur.execute("SELECT tax FROM config").fetchone()[0]
            
            pay = 2.0 
            tax_val = pay * (tax_rate/100)
            cur.execute("UPDATE users SET balance = balance + ?, xp = xp + 1 WHERE username=?", (pay - tax_val, user))
            cur.execute("UPDATE vault SET total_tax = total_tax + ?", (tax_val,))
            conn.commit()
            
            if st.button("⏹ STOP"):
                st.session_state.work = False
                cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
                conn.commit(); st.rerun()
            time.sleep(1); st.rerun()

    # --- ИНТЕРФЕЙС АДМИНА ---
    else:
        st.title("👑 GOD COMMAND CENTER")
        v_bal = cur.execute("SELECT total_tax FROM vault").fetchone()[0]
        tax_now, reg_now = cur.execute("SELECT tax, reg_open FROM config").fetchone()
        
        m1, m2, m3 = st.columns(3)
        m1.metric("🏦 MY VAULT", f"{round(v_bal, 2)} ₽")
        m2.metric("📉 TAX RATE", f"{tax_now}%")
        m3.metric("🚪 REG STATUS", "OPEN" if reg_now else "CLOSED")

        tab1, tab2 = st.tabs(["👥 UNITS", "⚙️ SYSTEM SETTINGS"])
        
        with tab1:
            workers = cur.execute("SELECT username, balance, is_working, status, last_act FROM users WHERE role='worker'").fetchall()
            for wn, wb, is_w, ws, last in workers:
                with st.expander(f"{'🟢' if is_w else '⚪'} {wn} | {round(wb, 1)} ₽"):
                    st.write(f"Last active: {last} | Status: {ws}")
                    c_a, c_b, c_c = st.columns(3)
                    if c_a.button("💀 BAN", key=f"ban_{wn}"):
                        cur.execute("UPDATE users SET status='banned', is_working=0 WHERE username=?", (wn,))
                        conn.commit(); st.rerun()
                    if c_b.button("💸 PAYOUT (0)", key=f"p_{wn}"):
                        cur.execute("UPDATE users SET balance=0 WHERE username=?", (wn,))
                        conn.commit(); st.rerun()
                    if c_c.button("➕ BONUS 500", key=f"g_{wn}"):
                        cur.execute("UPDATE users SET balance=balance+500 WHERE username=?", (wn,))
                        conn.commit(); st.rerun()
        
        with tab2:
            new_tax = st.slider("SET TAX %", 0, 100, int(tax_now))
            new_reg = st.checkbox("ALLOW NEW REGISTRATIONS", value=bool(reg_now))
            if st.button("SAVE CONFIG"):
                cur.execute("UPDATE config SET tax=?, reg_open=?", (new_tax, int(new_reg)))
                conn.commit(); st.success("SYSTEM UPDATED")

        time.sleep(2); st.rerun()
