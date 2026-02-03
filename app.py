import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- 1. PREMIUM STYLE ---
st.set_page_config(page_title="OFFICE CONTROL", layout="wide")
st.markdown("""
<style>
    .stApp {background: #050505; color: #00ff41; font-family: 'Courier New', Courier, monospace;}
    .stMetric {background: #111; border: 1px solid #00ff41; padding: 15px; border-radius: 5px;}
    .stButton>button {background: #000; color: #00ff41; border: 1px solid #00ff41; font-weight: bold;}
    .stButton>button:hover {background: #00ff41; color: #000; box-shadow: 0 0 10px #00ff41;}
    section[data-testid="stSidebar"] {background-color: #0a0a0a; border-right: 1px solid #00ff41;}
</style>
""", unsafe_allow_html=True)

# --- 2. DATABASE CORE ---
db = sqlite3.connect('premium_office_v1.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'ОЖИДАНИЕ', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS team_chat (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS sys_config (id INTEGER PRIMARY KEY, news TEXT)")
if not db.execute("SELECT news FROM sys_config WHERE id=1").fetchone():
    db.execute("INSERT INTO sys_config (id, news) VALUES (1, 'СИСТЕМА ГОТОВА К РАБОТЕ')")
db.commit()

# --- 3. CORE LOGIC ---
def get_rank_badge(xp):
    if xp < 500: return "🌑 РЕКРУТ", "#808080"
    if xp < 2000: return "⚔️ БОЕЦ", "#00ff41"
    if xp < 5000: return "💎 ЭЛИТА", "#00d4ff"
    return "🔥 ЛЕГЕНДА", "#ff00ff"

if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

# --- 4. AUTHENTICATION ---
if not st.session_state.auth:
    st.title("📟 ACCESS TERMINAL")
    l, p = st.text_input("UNIT_ID"), st.text_input("SECRET_KEY", type="password")
    c1, c2 = st.columns(2)
    if c1.button("LOGIN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth": True, "role": "admin", "user": "admin"})
            st.rerun()
        else:
            res = db.execute("SELECT u, status FROM users WHERE u=? AND p=?", (l, p)).fetchone()
            if res:
                if res[1] == 'active':
                    st.session_state.update({"auth": True, "role": "worker", "user": l})
                    st.rerun()
                else: st.error("ACCESS REVOKED")
            else: st.error("INVALID CREDENTIALS")
    if c2.button("REGISTER"):
        if l and p:
            try:
                db.execute("INSERT INTO users (u, p) VALUES (?, ?)", (l, p))
                db.commit(); st.success("UNIT REGISTERED")
            except: st.error("ID TAKEN")

else:
    if st.sidebar.button("LOGOUT"):
        st.session_state.auth = False; st.rerun()

    # --- WORKER INTERFACE ---
    if st.session_state.role == "worker":
        st.title(f"UNIT: {st.session_state.user}")
        
        # Dashboard
        news = db.execute("SELECT news FROM sys_config WHERE id=1").fetchone()[0]
        st.info(f"📢 СВОДКА: {news}")
        
        ud = db.execute("SELECT b, xp, m FROM users WHERE u=?", (st.session_state.user,)).fetchone()
        badge, color = get_rank_badge(ud[1])
        
        c1, c2, c3 = st.columns(3)
        c1.metric("CASH", f"{ud[0]} RUB")
        c2.metric("XP", ud[1])
        c3.markdown(f"**РАНГ:** <br><span style='color:{color}; font-size:20px;'>{badge}</span>", unsafe_allow_html=True)

        st.divider()
        
        # Live Timer
        st.subheader("⚙️ ВОРК-ТАЙМЕР")
        if not st.session_state.shift:
            if st.button("▶️ ЗАПУСТИТЬ ПРОТОКОЛ"):
                st.session_state.shift = True
                st.session_state.start = time.time()
                st.rerun()
        else:
            el = int(time.time() - st.session_state.start)
            st.error(f"⏳ ПРОЦЕСС ИДЕТ: {el} сек.")
            if st.button("🛑 СТОП"):
                add_xp = max(2, el // 3)
                db.execute("UPDATE users SET xp = xp + ? WHERE u = ?", (add_xp, st.session_state.user))
                db.commit()
                st.session_state.shift = False
                st.success(f"PROFIT: +{add_xp} XP")
                time.sleep(2); st.rerun()
            time.sleep(1); st.rerun()

        st.warning(f"🎯 ЗАДАЧА: {ud[2]}")

        # Top Workers List
        with st.expander("🏆 ДОСКА ЛИДЕРОВ"):
            tops = db.execute("SELECT u, xp FROM users ORDER BY xp DESC LIMIT 5").fetchall()
            for i, (tu, tx) in enumerate(tops):
                st.write(f"{i+1}. {tu} — {tx} XP")

        # Chat
        with st.expander("💬 СВЯЗЬ"):
            msg = st.text_input("Введите сообщение...")
            if st.button("SEND"):
                db.execute("INSERT INTO chat (u, msg, dt) VALUES (?, ?, ?)", (st.session_state.user, msg, datetime.now().strftime("%H:%M")))
                db.commit(); st.rerun()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 5").fetchall():
                st.text(f"[{cd}] {cu}: {cm}")

    # --- ADMIN INTERFACE ---
    else:
        st.title("👑 SUPREME COMMANDER")
        tab1, tab2 = st.tabs(["CONTROL", "MONITORING"])
        
        with tab1:
            # Global News
            gn = st.text_input("NEW GLOBAL ANNOUNCEMENT")
            if st.button("PUSH NEWS"):
                db.execute("UPDATE sys_config SET news=? WHERE id=1", (gn,))
                db.commit(); st.rerun()
            
            st.divider()
            
            # User Management
            for u, b, xp, m, stat, p in db.execute("SELECT u, b, xp, m, status, p FROM users").fetchall():
                with st.expander(f"UNIT: {u} | BAL: {b} | XP: {xp}"):
                    nb = st.number_input("БАЛАНС", value=float(b), key=f"b{u}")
                    nx = st.number_input("XP", value=int(xp), key=f"x{u}")
                    np = st.text_input("PASS", value=str(p), key=f"p{u}")
                    nm = st.text_area("TASK", value=str(m), key=f"m{u}")
                    
                    cc1, cc2 = st.columns(2)
                    if cc1.button("SAVE", key=f"s{u}"):
                        db.execute("UPDATE users SET b=?, xp=?, m=?, p=? WHERE u=?", (nb, nx, nm, np, u))
                        db.commit(); st.rerun()
                    if cc2.button("BAN/UNBAN", key=f"bn{u}"):
                        ns = 'banned' if stat == 'active' else 'active'
                        db.execute("UPDATE users SET status=? WHERE u=?", (ns, u))
                        db.commit(); st.rerun()

        with tab2:
            st.subheader("COMMUNICATIONS")
            adm_m = st.text_input("ADMIN MSG")
            if st.button("PUSH TO ALL"):
                db.execute("INSERT INTO chat (u, msg, dt) VALUES ('ADMIN', ?, ?)", (adm_m, datetime.now().strftime("%H:%M")))
                db.commit(); st.rerun()
            for cu, cm, cd in db.execute("SELECT u, msg, dt FROM chat ORDER BY id DESC LIMIT 20").fetchall():
                st.text(f"[{cd}] {cu}: {cm}")
