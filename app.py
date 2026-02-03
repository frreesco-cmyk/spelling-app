import streamlit as st
import sqlite3
from datetime import datetime

# --- ИНИЦИАЛИЗАЦИЯ ---
st.set_page_config(page_title="GOD MODE v64", page_icon="👁️", layout="wide")

def get_connection():
    # Новая база v64 для чистого старта без ошибок
    return sqlite3.connect('v64_god.db', check_same_thread=False)

conn = get_connection()
cur = conn.cursor()

# Создание базы
cur.execute('''CREATE TABLE IF NOT EXISTS users 
               (username TEXT PRIMARY KEY, password TEXT, balance REAL DEFAULT 0, 
                role TEXT DEFAULT "worker", status TEXT DEFAULT "active", 
                last_act TEXT, message TEXT DEFAULT "Указаний нет")''')
conn.commit()

# --- СТИЛЬ ---
st.markdown("""<style>
    .stApp { background: #000; color: #fff; }
    .stButton>button { border-radius: 0; border: 1px solid #fff; color: #fff; background: transparent; width: 100%; }
    .stButton>button:hover { background: #fff; color: #000; }
    .worker-msg { background: #111; padding: 15px; border-left: 5px solid #fff; margin: 10px 0; }
</style>""", unsafe_allow_html=True)

if 'auth' not in st.session_state: st.session_state.auth = False

# --- ВХОД ---
if not st.session_state.auth:
    st.title("👁️ ТЕРМИНАЛ v64")
    u = st.text_input("ЛОГИН").strip()
    p = st.text_input("ПАРОЛЬ", type='password').strip()
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("ВОЙТИ"):
            if u == "admin" and p == "admin777":
                st.session_state.update({"auth":True, "user":"admin", "role":"admin"})
                st.rerun()
            else:
                res = cur.execute("SELECT status FROM users WHERE username=? AND password=?",(u,p)).fetchone()
                if res:
                    if res[0] != "banned":
                        st.session_state.update({"auth":True, "user":u, "role":"worker"})
                        st.rerun()
                    else: st.error("ДОСТУП ЗАБЛОКИРОВАН")
                else: st.error("ЮНИТ НЕ НАЙДЕН")
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

    # --- ИНТЕРФЕЙС ВОРКЕРА ---
    if role == "worker":
        st.header(f"ЮНИТ: {user}")
        data = cur.execute("SELECT balance, message FROM users WHERE username=?",(user,)).fetchone()
        
        if data:
            st.metric("ВАШ СЧЕТ", f"{round(data[0], 2)} ₽")
            st.markdown(f'<div class="worker-msg"><b>ПРИКАЗ АДМИНИСТРАЦИИ:</b><br>{data[1]}</div>', unsafe_allow_html=True)
        else:
            st.error("Ошибка данных. Свяжитесь с админом.")

    # --- ИНТЕРФЕЙС АДМИНА ---
    else:
        st.title("👑 ПУЛЬТ ВСЕВЛАСТИЯ")
        
        users = cur.execute("SELECT username, balance, status, last_act, message FROM users WHERE role='worker'").fetchall()
        
        for un, ub, us, last, um in users:
            with st.expander(f"👤 {un} | {round(ub, 2)} ₽ | {us}"):
                st.write(f"Последняя активность: {last}")
                
                # Управление балансом
                new_bal = st.number_input("Установить баланс", value=float(ub), key=f"bal_{un}")
                if st.button("ОБНОВИТЬ СУММУ", key=f"btn_bal_{un}"):
                    cur.execute("UPDATE users SET balance=? WHERE username=?", (new_bal, un))
                    conn.commit(); st.rerun()
                
                # Личное сообщение
                new_msg = st.text_area("Написать приказ", value=um, key=f"msg_{un}")
                if st.button("ОТПРАВИТЬ ПРИКАЗ", key=f"btn_msg_{un}"):
                    cur.execute("UPDATE users SET message=? WHERE username=?", (new_msg, un))
                    conn.commit(); st.success("Отправлено")

                c1, c2 = st.columns(2)
                with c1:
                    # Бан/Разбан
                    if us == "active":
                        if st.button("🚫 ЗАБАНИТЬ", key=f"ban_{un}"):
                            cur.execute("UPDATE users SET status='banned' WHERE username=?", (un,))
                            conn.commit(); st.rerun()
                    else:
                        if st.button("🔓 РАЗБАНИТЬ", key=f"un_{un}"):
                            cur.execute("UPDATE users SET status='active' WHERE username=?", (un,))
                            conn.commit(); st.rerun()
                with c2:
                    # Удаление
                    if st.button("🗑️ СТЕРЕТЬ ИЗ БАЗЫ", key
