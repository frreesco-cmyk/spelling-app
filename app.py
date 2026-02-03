import streamlit as st
import sqlite3
from datetime import datetime

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="DICTATOR v63", page_icon="👤", layout="wide")

def get_connection():
    return sqlite3.connect('v63_dictator.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание базы
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                last_act TEXT)''')
conn.commit()

# --- СТИЛЬ (ЧЕРНЫЙ СПИСОК) ---
st.markdown("""<style>
    .stApp { background: #000; color: #fff; }
    .stButton>button { border-radius: 0; border: 1px solid #fff; color: #fff; background: transparent; width: 100%; }
    .stButton>button:hover { background: #fff; color: #000; }
    input { background-color: #111 !important; color: #fff !important; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("👤 ТЕРМИНАЛ УПРАВЛЕНИЯ")
    u = st.text_input("ЛОГИН").strip()
    p = st.text_input("ПАРОЛЬ", type='password').strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ВХОД"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"АДМИН", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res and res[0] != "banned":
                    st.session_state.update({"auth":True, "user":u, "role":"worker"})
                    st.rerun()
                else: st.error("ДОСТУП ЗАБЛОКИРОВАН")
    with col2:
        if st.button("РЕГИСТРАЦИЯ"):
            try:
                cur.execute('INSERT INTO users(username,password,last_act) VALUES (?,?,?)',(u,p,"-"))
                conn.commit(); st.success("ЮНИТ СОЗДАН")
            except: st.error("ЗАНЯТО")

# --- ИНТЕРФЕЙС ---
else:
    user, role = st.session_state.user, st.session_state.role
    cur.execute("UPDATE users SET last_act=? WHERE username=?", (datetime.now().strftime("%H:%M:%S"), user))
    conn.commit()

    if st.sidebar.button("ВЫЙТИ"):
        st.session_state.auth = False; st.rerun()

    if role == "worker":
        st.header(f"ЮНИТ: {user}")
        bal = cur.execute("SELECT balance FROM users WHERE username=?",(user,)).fetchone()[0]
        st.metric("ВАШ СЧЕТ", f"{round(bal, 2)} ₽")
        st.write("Ожидайте указаний администратора.")

    else:
        st.title("👑 ПАНЕЛЬ ДИКТАТОРА")
        
        st.subheader("СПИСОК ВСЕХ ПОЛЬЗОВАТЕЛЕЙ")
        users = cur.execute("SELECT username, balance, status, last_act FROM users WHERE role='worker'").fetchall()
        
        for un, ub, us, last in users:
            with st.expander(f"{un} | Баланс: {round(ub, 2)} | {us}"):
                st.write(f"Последний вход: {last}")
                c1, c2, c3 = st.columns(3)
                
                # Смена баланса вручную
                new_bal = st.number_input("Изменить баланс", value=float(ub), key=f"bal_{un}")
                if c1.button("ОБНОВИТЬ СУММУ", key=f"upd_{un}"):
                    cur.execute("UPDATE users SET balance=? WHERE username=?", (new_bal, un))
                    conn.commit(); st.rerun()
                
                # Бан/Разбан
                if us == "active":
                    if c2.button("🚫 ЗАБАНИТЬ", key=f"ban_{un}"):
                        cur.execute("UPDATE users SET status='banned' WHERE username=?", (un,))
                        conn.commit(); st.rerun()
                else:
                    if c2.button("🔓 РАЗБАНИТЬ", key=f"un_{un}"):
                        cur.execute("UPDATE users SET status='active' WHERE username=?", (un,))
                        conn.commit(); st.rerun()
                
                # Удаление под корень
                if c3.button("🗑️ УДАЛИТЬ", key=f"del_{un}"):
                    cur.execute("DELETE FROM users WHERE username=?", (un,))
                    conn.commit(); st.rerun()
