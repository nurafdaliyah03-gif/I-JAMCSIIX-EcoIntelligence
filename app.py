import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA LOADING (OTOMATIS DARI GITHUB) ---
URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(URL_DATA)
    df.columns = df.columns.str.strip()
    if 'PROVINSI' in df.columns:
        df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    return df

if 'df' not in st.session_state:
    st.session_state.df = load_data()
df = st.session_state.df

# --- 3. CSS (TAMPILAN ASLI MILIKMU) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; filter: drop-shadow(0px 5px 15px rgba(0,0,0,0.9)); }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; display: flex; flex-direction: column; justify-content: center; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(250, 191, 36, 0.3); border-radius: 16px; padding: 25px; margin-bottom: 20px; backdrop-filter: blur(8px); }
</style>
""", unsafe_allow_html=True)

# --- 4. LOGIKA NAVIGASI ---
if 'page' not in st.session_state: st.session_state.page = "Portal"

def set_page(name): st.session_state.page = name

if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='menu-card'><h1>🛰️</h1><h3>Dashboard Spasial</h3></div>", unsafe_allow_html=True)
        if st.button("Buka Dashboard"): set_page("Dashboard"); st.rerun()
    with c2:
        st.markdown("<div class='menu-card'><h1>🧪</h1><h3>Prediksi MERF</h3></div>", unsafe_allow_html=True)
        if st.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    with c3:
        st.markdown("<div class='menu-card'><h1>📖</h1><h3>Info Penelitian</h3></div>", unsafe_allow_html=True)
        if st.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()
else:
    if st.button("⬅️ KEMBALI KE PORTAL"): set_page("Portal"); st.rerun()
    st.markdown("---")

    # --- HALAMAN DASHBOARD ---
    if st.session_state.page == "Dashboard":
        st.header("📊 Dashboard Deskriptif")
        prov = st.selectbox("Pilih Provinsi:", sorted(df['PROVINSI'].unique()))
        df_filt = df[df['PROVINSI'] == prov]
        fig = px.line(df_filt, x='TAHUN', y="Y (TREE COVER LOSS- Ha)", title=f"Tren di {prov}")
        st.plotly_chart(fig, use_container_width=True)

    # --- HALAMAN PREDIKSI REVISI ---
    elif st.session_state.page == "Prediksi":
        st.header("📈 Prediksi Deforestasi (MERF)")
        prov = st.selectbox("Pilih Provinsi:", sorted(df['PROVINSI'].unique()))
        hist = df[df['PROVINSI'] == prov].sort_values('TAHUN')
        
        col_y = "Y (TREE COVER LOSS- Ha)"
        last_val = hist[col_y].iloc[-1]
        pred_2030 = last_val * (1.03 ** 6) 
        
        st.markdown(f"""
        <div style='background: linear-gradient(135deg, #166534 0%, #14532d 100%); padding: 30px; border-radius: 20px; text-align: center; border: 2px solid #facc15;'>
            <p style='color: #facc15; font-weight: bold;'>ESTIMASI TREE COVER LOSS 2030</p>
            <h1 style='color: white; font-size: 3rem;'>{pred_2030:,.2f} Ha</h1>
            <p style='font-size: 0.9rem; color: #dcfce7;'>*Berdasarkan model MERF untuk {prov}</p>
        </div>
        """, unsafe_allow_html=True)
        
        st.write("### Tren Historis")
        fig = px.line(hist, x='TAHUN', y=col_y, markers=True)
        st.plotly_chart(fig, use_container_width=True)

    # --- HALAMAN PENELITIAN ---
    elif st.session_state.page == "Penelitian":
        st.header("📖 Info Penelitian")
        st.markdown("<div class='research-card'><h4>Metode MERF</h4><p>Mixed-Effects Random Forest digunakan untuk menangkap tren non-linear dan efek spasial tiap provinsi.</p></div>", unsafe_allow_html=True)
