import streamlit as st
import sqlite3
import time
from datetime import datetime

# --- 1. СТИЛЬ ПАНЕЛИ ---
st.set_page_config(page_title="SUPREME SYSTEM", layout="wide")
st.markdown("""
<style>
    .stApp {background: #000; color: #00ff41; font-family: 'Courier New', monospace;}
    .stMetric {background: #111; border: 1px solid #00ff41; padding: 15px; border-radius: 5px;}
    .stButton>button {background: #000; color: #00ff41; border: 1px solid #00ff41; width: 100%;}
    .stButton>button:hover {background: #00ff41; color: #000;}
</style>
""", unsafe_allow_html=True)

# --- 2. ИНИЦИАЛИЗАЦИЯ БАЗЫ (БЕЗ ОШИБОК) ---
db = sqlite3.connect('main_core_v5.db', check_same_thread=False)
db.execute("CREATE TABLE IF NOT EXISTS users (u TEXT PRIMARY KEY, p TEXT, b REAL DEFAULT 0, xp INTEGER DEFAULT 0, m TEXT DEFAULT 'НЕТ', status TEXT DEFAULT 'active')")
db.execute("CREATE TABLE IF NOT EXISTS chat_logs (id INTEGER PRIMARY KEY, u TEXT, msg TEXT, dt TEXT)")
db.execute("CREATE TABLE IF NOT EXISTS config (id INTEGER PRIMARY KEY, news TEXT)")
if not db.execute("SELECT news FROM config WHERE id=1").fetchone():
    db.execute("INSERT INTO config (id, news) VALUES (1, 'СИСТЕМА ЗАПУЩЕНА')")
db.commit()

# --- 3. РАНГИ ---
def get_rank_data(xp_val):
    if xp_val < 500: return "🌑 РЕКРУТ", 0.2
    if xp_val < 2000: return "⚔️ БОЕЦ", 0.5
    if xp_val < 5000: return "💎 ЭЛИТА", 0.8
    return "🔥 ЛЕГЕНДА", 1.0

# --- 4. СЕССИЯ ---
if 'auth' not in st.session_state: st.session_state.auth = False
if 'shift' not in st.session_state: st.session_state.shift = False

# --- 5. ЛОГИКА ДОСТУПА ---
if not st.session_state.auth:
    st.title("📟 СИСТЕМА УПРАВЛЕНИЯ")
    l = st.text_input("ID ЮНИТА").strip()
    p = st.text_input("КЛЮЧ", type="password").strip()
    c1, c2 = st.columns(2)
    if c1.button("LOG IN"):
        if l == "admin" and p == "admin777":
            st.session_state.update({"auth": True, "role": "admin", "user": "admin"})
            st.rerun()
        else:
