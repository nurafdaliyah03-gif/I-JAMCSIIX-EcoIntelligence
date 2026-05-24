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
    try:
        df = pd.read_csv(url)
        df.columns = df.columns.str.strip()
        df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
        st.session_state.df = df
    except:
        st.error("Gagal memuat data. Periksa koneksi internet.")

def set_page(name): st.session_state.page = name

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }
    .stSelectbox div[data-baseweb="select"] { background-color: #ffffff !important; border-radius: 10px; }
    .stSelectbox div[data-baseweb="select"] div { color: #000000 !important; font-weight: 600 !important; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; display: flex; flex-direction: column; justify-content: center; }
    .stPlotlyChart { background-color: white !important; border-radius: 20px; padding: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    div.stButton > button { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; color: white !important; border: 1px solid #facc15 !important; border-radius: 12px; width: 100%; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(250, 191, 36, 0.3); border-radius: 16px; padding: 25px; margin-bottom: 20px; backdrop-filter: blur(8px); }
    .research-card h4 { color: #facc15 !important; border-bottom: 2px solid #15803d; padding-bottom: 8px; }
</style>
""", unsafe_allow_html=True)

# --- 4. DATA GEOJSON ---
@st.cache_data
def load_geojson():
    try:
        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"
        res = requests.get(url).json()
        for feature in res['features']:
            nama = str(feature['properties'].get('Propinsi', '')).strip().upper()
            feature['properties']['PROV_KEY'] = "DI YOGYAKARTA" if "YOGYAKARTA" in nama else ("DKI JAKARTA" if "JAKARTA" in nama else nama)
        return res
    except: return None
geojson = load_geojson()
col_y = "Y (TREE COVER LOSS- Ha)"
cols_x = {"X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)", "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)", "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)", "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)", "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)", "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"}

# --- 5. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Buka Dashboard"): set_page("Dashboard"); st.rerun()
    if c2.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    if c3.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()
else:
    if st.button("⬅️ KEMBALI KE PORTAL"): set_page("Portal"); st.rerun()
    st.markdown("---")

    if st.session_state.page == "Dashboard":
        df = st.session_state.df
        st.header("📊 Dashboard Deskriptif Spasial")
        sel_thn = st.selectbox("Pilih Tahun:", sorted(df['TAHUN'].unique(), reverse=True))
        df_filt = df[df['TAHUN'] == sel_thn]
        fig = px.choropleth(df_filt, geojson=geojson, locations="PROVINSI", featureidkey="properties.PROV_KEY", color=col_y, color_continuous_scale="RdYlGn_r")
        fig.update_layout(height=450, margin={"r":0,"t":0,"l":0,"b":0})
        st.plotly_chart(fig, use_container_width=True)

    elif st.session_state.page == "Prediksi":
        st.subheader("🌍 Estimasi Risiko Deforestasi")
        df = st.session_state.df
        prov = st.selectbox("Pilih Wilayah:", sorted(df['PROVINSI'].unique()))
        p_data = df[df['PROVINSI'] == prov]
        last_val = p_data.iloc[-1][col_y]
        st.write(f"Estimasi Tren (3 Tahun ke Depan): {round(last_val * 1.03, 2)} Ha")

    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#facc15;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("<div class='research-card'><h4>🎯 Tujuan Penelitian</h4><ul><li>Menerapkan model hibrida MERF.</li><li>Visualisasi spasial ForestGuard.</li></ul></div>", unsafe_allow_html=True)
        with rc2:
            st.markdown("<div class='research-card'><h4>🤖 Metode MERF</h4><p>Menggabungkan Random Forest dan Mixed Effects Model untuk akurasi tinggi.</p></div>", unsafe_allow_html=True)
            st.latex(r"y_i = f(X_i) + Z_i b_i + \varepsilon_i")
        
        st.markdown("### 📋 Definisi Variabel")
        v_col1, v_col2 = st.columns(2)
        v_col1.table(pd.DataFrame({"Kode": ["Y", "X1", "X2"], "Variabel": ["Loss", "Lahan", "Karhutla"]}))
        
        st.markdown("""
        <div style='background: #450a0a; padding: 20px; border-radius: 15px; border: 1px solid #ef4444;'>
            <h5>⚠️ Keterbatasan Model</h5>
            <ul><li>Data historis terbatas.</li><li>Optimal untuk jangka pendek.</li></ul>
        </div>
        """, unsafe_allow_html=True)
