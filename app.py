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
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }
    .stSelectbox div[data-baseweb="select"] { background-color: #ffffff !important; border-radius: 10px; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; }
    .stPlotlyChart { background-color: white !important; border-radius: 20px; padding: 15px; }
    div.stButton > button { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; color: white !important; border: 1px solid #facc15 !important; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(250, 191, 36, 0.3); border-radius: 16px; padding: 25px; margin-bottom: 20px; }
</style>
""", unsafe_allow_html=True)

# --- 4. DATA GEOJSON ---
@st.cache_data
def load_geojson():
    try:
        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
        return requests.get(url).json()
    except: return None
geojson = load_geojson()
col_y = "Y (TREE COVER LOSS- Ha)"

# --- 5. NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Dashboard"): set_page("Dashboard"); st.rerun()
    if c2.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    if c3.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()
else:
    if st.button("⬅️ KEMBALI KE PORTAL"): set_page("Portal"); st.rerun()
    st.markdown("---")

    if st.session_state.page == "Dashboard":
        st.header("📊 Dashboard Deskriptif Spasial")
        st.markdown("<div style='background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px;'>Keterangan: <span style='color: #ef4444;'>●</span> Merah: Tinggi | <span style='color: #eab308;'>●</span> Kuning: Sedang | <span style='color: #22c55e;'>●</span> Hijau: Rendah</div>", unsafe_allow_html=True)
        # (Dashboard content...)

    elif st.session_state.page == "Prediksi":
        st.header("📈 Prediksi & Update Data Aktual")
        
        # Fitur Input Data (Menambahkan tahun ke dataset tanpa merusak layout)
        with st.expander("📥 Tambah Data Aktual Tahunan"):
            up = st.file_uploader("Upload CSV Data:", type="csv")
            if up and st.button("Proses & Update Model"):
                new_df = pd.read_csv(up)
                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                st.rerun()

        df = st.session_state.df
        prov = st.selectbox("Pilih Wilayah:", sorted(df['PROVINSI'].unique()))
        
        # Tabel & Grafik
        cl, cr = st.columns([1, 1.2])
        with cl:
            st.subheader("📄 Tabel Estimasi")
            # Logic: menampilkan tahun 2026-2028 (atau setelah tahun terakhir di data)
            last_yr = df['TAHUN'].max()
            years = [last_yr+1, last_yr+2, last_yr+3]
            data_tabel = []
            for p in sorted(df['PROVINSI'].unique()):
                val = df[df['PROVINSI']==p].iloc[-1][col_y]
                for y in years:
                    data_tabel.append({"Provinsi": p, "Tahun": y, "Loss (Ha)": round(val * (1.03**(y-last_yr)), 2)})
            st.dataframe(pd.DataFrame(data_tabel).head(15), use_container_width=True, hide_index=True)

        with cr:
            st.subheader("📊 Tren Kehilangan Tutupan Pohon")
            hist = df[df['PROVINSI'] == prov].copy()
            hist['Status'] = 'Aktual'
            fig = px.line(hist, x='TAHUN', y=col_y, markers=True, color_discrete_sequence=['#22c55e'])
            st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.page == "Penelitian":
        st.header("📖 Info Penelitian")
        # (Info Penelitian content...)
