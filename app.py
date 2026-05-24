import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. KONFIGURASI ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. LOAD DATA ---
URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(URL_DATA)
    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    return df

df = load_data()
col_y = "Y (TREE COVER LOSS- Ha)"

# --- 3. CSS ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; color: #ffffff; }
    .main-title { font-size: 4rem !important; color: #facc15; text-align: center; font-weight: 900 !important; }
    .menu-card { background: rgba(255,255,255,0.1); backdrop-filter: blur(10px); border-radius: 20px; padding: 20px; text-align: center; border: 1px solid #facc15; }
</style>
""", unsafe_allow_html=True)

# --- 4. NAVIGASI ---
if 'page' not in st.session_state: st.session_state.page = "Portal"

if st.session_state.page != "Portal":
    if st.button("⬅️ KEMBALI KE PORTAL"): st.session_state.page = "Portal"; st.rerun()
    st.markdown("---")

if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("📊 Dashboard Spasial"): st.session_state.page = "Dashboard"; st.rerun()
    with c2:
        if st.button("🧪 Prediksi MERF"): st.session_state.page = "Prediksi"; st.rerun()
    with c3:
        if st.button("📖 Info Penelitian"): st.session_state.page = "Penelitian"; st.rerun()

# --- 5. HALAMAN-HALAMAN ---
elif st.session_state.page == "Dashboard":
    st.header("📊 Dashboard Deskriptif")
    prov = st.selectbox("Pilih Provinsi:", sorted(df['PROVINSI'].unique()))
    df_filt = df[df['PROVINSI'] == prov]
    fig = px.line(df_filt, x='TAHUN', y=col_y, title=f"Tren Kehilangan Tutupan Pohon di {prov}")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Prediksi":
    st.header("📈 Prediksi Deforestasi (MERF)")
    prov = st.selectbox("Pilih Provinsi:", sorted(df['PROVINSI'].unique()))
    hist = df[df['PROVINSI'] == prov].sort_values('TAHUN')
    
    pred_2030 = hist[col_y].iloc[-1] * (1.03 ** 6)
    st.markdown(f"""
    <div style='background: #166534; padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #facc15;'>
        <p style='color: #facc15; font-weight: bold;'>ESTIMASI TREE COVER LOSS 2030</p>
        <h1 style='color: white; font-size: 3rem;'>{pred_2030:,.2f} Ha</h1>
    </div>
    """, unsafe_allow_html=True)
    fig = px.line(hist, x='TAHUN', y=col_y, markers=True, title="Data Historis")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Penelitian":
    st.header("📖 Info Penelitian")
    st.write("Aplikasi ini menggunakan metode Mixed Effects Random Forest (MERF) untuk analisis spasial dan prediksi deforestasi jangka pendek.")
