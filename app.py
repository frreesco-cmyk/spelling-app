import streamlit as st
import sqlite3
import pandas as pd
from datetime import datetime
import time
import random

# --- CONFIG ---
st.set_page_config(page_title="GOD MODE v51", page_icon="🧿", layout="wide")

# --- DATABASE (AUTO-FIX) ---
conn = sqlite3.connect('v51_final.db', check_same_thread=False)
cur = conn.cursor()
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                is_working INTEGER DEFAULT 0, last_act TEXT, xp INTEGER DEFAULT 0, last_bonus TEXT)''')
cur.execute('CREATE TABLE IF NOT EXISTS chat (user TEXT, msg TEXT, time TEXT)')
cur.execute('CREATE TABLE IF NOT EXISTS vault (total_tax REAL DEFAULT 0)')
cur.execute('CREATE TABLE IF NOT EXISTS config (tax REAL DEFAULT 15, news TEXT)')
if not cur.execute('SELECT * FROM vault').fetchone(): cur.execute('INSERT INTO vault VALUES (0)')
if not cur.execute('SELECT * FROM config').fetchone(): cur.execute('INSERT INTO config VALUES (15, "SYSTEM ONLINE")')
conn.commit()

# --- STYLES ---
st.markdown("""<style>
    .stApp { background: #000; color: #0f0; }
    .stMetric { background: #111; border: 1px solid #0f0; border-radius: 10px; }
    .chat-box { background: #111; padding: 10px; border: 1px solid #333; height: 200px; overflow-y: scroll; margin-bottom: 10px; }
    .stButton>button { border: 1px solid #0f0; color: #0f0; background: transparent; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- AUTH ---
if not st.session_state.auth:
    st.title("🧿 THE CORE v51")
    u = st.text_input("ID").strip()
    p = st.text_input("KEY", type='password').strip()
    if st.button("UPLINK"):
        if u == "admin" and p == "admin777":
            st.session_state.update({"auth":True, "user":"ADMIN", "role":"admin"})
            st.rerun()
        else:
            res = cur.execute("SELECT role, status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
            if res and res[1] != "banned":
                st.session_state.update({"auth":True, "user":u, "role":res[0]})
                st.rerun()
            else: st.error("ACCESS DENIED")
    if st.button("NEW SLAVE"):
        try:
            cur.execute('INSERT INTO users(username,password,last_act,xp) VALUES (?,?,?,0)',(u,p,"-"))
            conn.commit(); st.success("READY")
        except: st.error("TAKEN")

else:
    user, role = st.session_state.user, st.session_state.role
    cur.execute("UPDATE users SET last_act=? WHERE username=?", (datetime.now().strftime("%H:%M:%S"), user))
    conn.commit()

    # --- WORKER VIEW ---
    if role != "admin":
        st.title(f"👾 UNIT_{user}")
        # Безопасное получение данных
        data = cur.execute("SELECT balance, xp FROM users WHERE username=?",(user,)).fetchone()
        bal, xp = data if data else (0, 0)
        
        c1, c2 = st.columns(2)
        c1.metric("💰 BALANCE", f"{round(bal, 2)} ₽")
        c2.metric("🧬 XP", xp)

        t1, t2 = st.tabs(["⚒️ MINING", "💬 CHAT"])
        with t1:
            if 'work' not in st.session_state: st.session_state.work = False
            if not st.session_state.work:
                if st.button("START"):
                    st.session_state.start = datetime.now()
                    st.session_state.work = True
                    cur.execute("UPDATE users SET is_working=1 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
            else:
                st.warning("MINING ACTIVE...")
                tax = cur.execute("SELECT tax FROM config").fetchone()[0]
                cur.execute("UPDATE users SET balance = balance + ?, xp = xp + 1 WHERE username=?", (3.0 * (1 - tax/100), user))
                cur.execute("UPDATE vault SET total_tax = total_tax + ?", (3.0 * (tax/100),))
                conn.commit()
                if st.button("STOP"):
                    st.session_state.work = False
                    cur.execute("UPDATE users SET is_working=0 WHERE username=?", (user,))
                    conn.commit(); st.rerun()
                time.sleep(1); st.rerun()
        
        with t2:
            msg = st.text_input("Message to all...")
            if st.button("SEND"):
                cur.execute("INSERT INTO chat VALUES (?,?,?)", (user, msg, datetime.now().strftime("%H:%M")))
                conn.commit(); st.rerun()
            
            chat_data = cur.execute("SELECT * FROM chat ORDER BY rowid DESC LIMIT 10").fetchall()
            for cu, cm, ct in chat_data:
                st.write(f"[{ct}] **{cu}**: {cm}")

    # --- ADMIN VIEW ---
    else:
        st.title("👑 GOD COMMAND")
        v_bal = cur.execute("SELECT total_tax FROM vault").fetchone()[0]
        st.metric("🏦 MY VAULT", f"{round(v_bal, 2)} ₽")
        
        workers = cur.execute("SELECT username, balance, is_working FROM users WHERE role='worker'").fetchall()
        for wn, wb, is_w in workers:
            col1, col2, col3 = st.columns([2, 1, 1])
            col1.write(f"{'🟢' if is_w else '⚪'} **{wn}** | {round(wb, 1)} ₽")
            if col2.button("BAN", key=f"b_{wn}"):
                cur.execute("UPDATE users SET status='banned', is_working=0 WHERE username=?",(wn,))
                conn.commit(); st.rerun()
            if col3.button("RESET", key=f"r_{wn}"):
                cur.execute("UPDATE users SET balance=0 WHERE username=?",(wn,))
                conn.commit(); st.rerun()
        
        time.sleep(2); st.rerun()
