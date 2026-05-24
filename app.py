import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = "Portal"
if 'df' not in st.session_state: 
    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    st.session_state.df = df

def set_page(name): st.session_state.page = name

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-attachment: fixed; color: #ffffff; }
    .stSelectbox div[data-baseweb="select"] { background-color: #ffffff !important; border-radius: 10px; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; }
    div.stButton > button { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; color: white !important; border: 1px solid #facc15 !important; border-radius: 12px; width: 100%; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(250, 191, 36, 0.3); border-radius: 16px; padding: 25px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 4. DATA ---
col_y = "Y (TREE COVER LOSS- Ha)"

# --- 5. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Buka Dashboard"): set_page("Dashboard"); st.rerun()
    if c2.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    if c3.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()

else:
    if st.button("⬅️ KEMBALI KE PORTAL"): set_page("Portal"); st.rerun()
    
    if st.session_state.page == "Dashboard":
        st.header("📊 Dashboard Deskriptif")
        st.write("Konten Dashboard di sini...")

    elif st.session_state.page == "Prediksi":
        st.markdown("### 🧪 FORESTGUARD: ANALISIS PREDIKSI")
        df = st.session_state.df
        last_yr = df['TAHUN'].max()
        
        # FILTER MANDIRI UNTUK TABEL DAN GRAFIK
        target_prov = st.selectbox("Pilih Provinsi untuk Estimasi & Grafik:", sorted(df['PROVINSI'].unique()))
        
        cl, cr = st.columns(2)
        with cl:
            st.markdown(f"#### 📄 Tabel Estimasi: {target_prov}")
            last_val = df[df['PROVINSI'] == target_prov].iloc[-1][col_y]
            data_est = [{"Tahun": last_yr + i, "Estimasi Loss (Ha)": round(last_val * (1.03 ** i), 2)} for i in range(1, 4)]
            st.dataframe(pd.DataFrame(data_est), use_container_width=True, hide_index=True)

        with cr:
            st.markdown(f"#### 📊 Tren Kehilangan ({target_prov})")
            hist = df[df['PROVINSI'] == target_prov].sort_values('TAHUN')
            fig = px.line(hist, x='TAHUN', y=col_y, markers=True)
            st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.page == "Penelitian":
        st.header("📖 Info Penelitian")
        st.markdown("""
        <div class='research-card'>
            <h4>🤖 Metode MERF</h4>
            <p>Mixed-Effects Random Forest (MERF) memadukan Random Forest dengan model efek acak untuk akurasi prediksi spasial yang lebih baik.</p>
        </div>
        """, unsafe_allow_html=True)
