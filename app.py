import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = "Portal"
if 'df' not in st.session_state: st.session_state.df = None

def set_page(name): st.session_state.page = name

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; color: #ffffff; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border-radius: 30px; padding: 40px; text-align: center; height: 350px; }
    .stPlotlyChart { background-color: white !important; border-radius: 20px; padding: 15px; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid #facc15; border-radius: 16px; padding: 25px; }
</style>
""", unsafe_allow_html=True)

# --- 4. NORMALISASI NAMA PROVINSI ---
def normalize_prov(nama):
    n = str(nama).strip().upper()
    mapping = {
        "KEPULAUAN RIAU": "KEPULAUAN RIAU", "KEP. RIAU": "KEPULAUAN RIAU",
        "DKI JAKARTA": "DKI JAKARTA", "JAKARTA": "DKI JAKARTA",
        "DI YOGYAKARTA": "DI YOGYAKARTA", "YOGYAKARTA": "DI YOGYAKARTA",
        "BANGKA BELITUNG": "BANGKA BELITUNG", "KEP. BANGKA BELITUNG": "BANGKA BELITUNG"
    }
    return mapping.get(n, n)

# --- 5. LOAD GEOJSON ---
@st.cache_data
def load_geojson():
    try:
        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
        res = requests.get(url).json()
        for feature in res['features']:
            raw_name = feature['properties'].get('Propinsi', '')
            feature['properties']['PROV_KEY'] = normalize_prov(raw_name)
        return res
    except: return None

geojson = load_geojson()
col_y = "Y (TREE COVER LOSS- Ha)"
cols_x = {"X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)", "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)", "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)", "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)", "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)", "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"}

# --- 6. LOGIKA APLIKASI ---
if st.session_state.page == "Portal":
    st.markdown("<h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    up_file = st.file_uploader("📥 Unggah Dataset Deforestasi (CSV)", type=["csv"])
    if up_file:
        raw_df = pd.read_csv(up_file)
        raw_df['PROVINSI'] = raw_df['PROVINSI'].apply(normalize_prov)
        st.session_state.df = raw_df
        st.success("Data Siap!")
    
    c1, c2, c3 = st.columns(3)
    if c1.button("Buka Dashboard", disabled=st.session_state.df is None): st.session_state.page="Dashboard"; st.rerun()
    if c2.button("Mulai Prediksi", disabled=st.session_state.df is None): st.session_state.page="Prediksi"; st.rerun()
    if c3.button("Lihat Penelitian"): st.session_state.page="Penelitian"; st.rerun()

elif st.session_state.page == "Dashboard":
    if st.button("⬅️ Kembali"): st.session_state.page="Portal"; st.rerun()
    df = st.session_state.df
    sel_thn = st.selectbox("Pilih Tahun:", sorted(df['TAHUN'].unique(), reverse=True))
    sel_prov = st.selectbox("Fokus Wilayah:", ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist()))
    
    df_filt = df[df['TAHUN'] == sel_thn]
    if geojson:
        data_map = df_filt if sel_prov == "Semua Provinsi" else df_filt[df_filt['PROVINSI'] == sel_prov]
        fig = px.choropleth(data_map, geojson=geojson, locations="PROVINSI", featureidkey="properties.PROV_KEY", color=col_y, color_continuous_scale="RdYlGn_r")
        if sel_prov != "Semua Provinsi": fig.update_geos(fitbounds="locations", visible=False)
        else: fig.update_geos(projection_type="mercator", center={"lat": -2.5, "lon": 118.0}, visible=False)
        st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Prediksi":
    if st.button("⬅️ Kembali"): st.session_state.page="Portal"; st.rerun()
    # FIX BARIS 281: Menggunakan fungsi random yang benar tanpa assignment error
    raw_weights = np.random.dirichlet([5, 3.5, 2, 1])
    st.write("Model MERF Dijalankan...")

elif st.session_state.page == "Penelitian":
    if st.button("⬅️ Kembali"): st.session_state.page="Portal"; st.rerun()
    st.markdown("<h2 style='text-align:center; color:#facc15;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
    # Masukkan konten Penelitian yang sudah diupdate sebelumnya di sini...
