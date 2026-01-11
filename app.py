import streamlit as st
import sqlite3
import hashlib
from datetime import datetime, timedelta
import os

# --- Veritabanı Kurulumu ---
def init_db():
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            password_hash TEXT NOT NULL,
            subscription_status TEXT DEFAULT 'trialing',
            trial_end TEXT
        )
    """)
    conn.commit()
    conn.close()

init_db()

# --- Yardımcı Fonksiyonlar ---
def hash_password(p): return hashlib.sha256(p.encode()).hexdigest()

def register(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    try:
        c.execute("""
            INSERT INTO users (email, password_hash, trial_end)
            VALUES (?, ?, ?)
        """, (email, hash_password(password), (datetime.now() + timedelta(days=7)).strftime("%Y-%m-%d")))
        conn.commit()
        return True
    except:
        return False
    finally:
        conn.close()

def login(email, password):
    conn = sqlite3.connect("users.db")
    c = conn.cursor()
    c.execute("SELECT * FROM users WHERE email=? AND password_hash=?", (email, hash_password(password)))
    user = c.fetchone()
    conn.close()
    return user

def is_active(user):
    if not user: return False
    status, trial_end = user[3], user[4]
    if status == "active": return True
    if status == "trialing" and trial_end:
        return datetime.strptime(trial_end, "%Y-%m-%d") > datetime.now()
    return False

# --- Streamlit Arayüzü ---
st.set_page_config(page_title="Sentinel Pro - Demo", layout="centered")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user is None:
    st.title("🛡️ Sentinel Pro – Global Trade Intelligence")
    st.subheader("Demo Sürümü – Gerçek Zamanlı Borsa Uyarıları")
    
    tab1, tab2 = st.tabs(["Giriş Yap", "Üye Ol (7 Gün Ücretsiz)"])
    
    with tab1:
        email = st.text_input("Email")
        pwd = st.text_input("Şifre", type="password")
        if st.button("Giriş Yap"):
            user = login(email, pwd)
            if user:
                st.session_state.user = user
                st.rerun()
            else:
                st.error("Hatalı email/şifre")
    
    with tab2:
        email = st.text_input("Email", key="reg_email")
        pwd = st.text_input("Şifre", type="password", key="reg_pwd")
        if st.button("Üye Ol"):
            if register(email, pwd):
                st.success("Kayıt başarılı! Giriş yapabilirsiniz.")
            else:
                st.error("Bu email zaten kayıtlı.")
    
    st.info("💰 Aylık abonelik: **$100**\n\nTüm borsalar, gerçek zamanlı uyarılar, portföy takibi dahil.")

else:
    user = st.session_state.user
    if is_active(user):
        st.sidebar.title("Sentinel Pro")
        st.sidebar.write(f"Merhaba, {user[1]}")
        if st.sidebar.button("Çıkış Yap"):
            st.session_state.user = None
            st.rerun()
        
        st.success("✅ Aboneliğiniz aktif! Tüm özellikler kullanılabilir.")
        st.header("🌍 Küresel Pazar Durumu")
        st.info("Burada NYSE, NASDAQ, BIST, TSE vs. anlık veriler yer alacak.")
        st.subheader("Örnek Uyarılar")
        st.warning("⚠️ THYAO.IS – Tavan yakınında! SATIŞ fırsatı.")
        st.success("🟢 AAPL – Tabandan kalktı! ALIM fırsatı.")
    else:
        st.error("Aboneliğiniz sona erdi. Lütfen ödeme yapın.")
        st.link_button("Abonelik Satın Al ($100/ay)", "https://buy.stripe.com/test_123")
