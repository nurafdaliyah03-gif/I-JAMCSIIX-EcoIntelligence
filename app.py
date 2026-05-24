import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA LOADING (OTOMATIS) ---
if 'df_main' not in st.session_state:
    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    st.session_state.df_main = df

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

# --- 3. CSS CUSTOM (TETAP SAMA) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }
    .stSelectbox div[data-baseweb="select"] { background-color: #ffffff !important; border-radius: 10px; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; }
    .stPlotlyChart { background-color: white !important; border-radius: 20px; padding: 15px; }
    div.stButton > button { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; color: white !important; border: 1px solid #facc15 !important; }
</style>
""", unsafe_allow_html=True)

# --- 4. NAVIGASI ---
if 'page' not in st.session_state: st.session_state.page = "Portal"
def set_page(name): st.session_state.page = name

if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    if c1.button("Dashboard"): set_page("Dashboard"); st.rerun()
    if c2.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    if c3.button("Info Penelitian"): set_page("Penelitian"); st.rerun()
else:
    if st.button("⬅️ KEMBALI KE PORTAL"): set_page("Portal"); st.rerun()
    st.markdown("---")

    # --- DASHBOARD ---
    if st.session_state.page == "Dashboard":
        st.header("📊 Dashboard Deskriptif Spasial")
        st.markdown("<div style='background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px;'>Keterangan: <span style='color: #ef4444;'>●</span> Merah: Tinggi | <span style='color: #eab308;'>●</span> Kuning: Sedang | <span style='color: #22c55e;'>●</span> Hijau: Rendah</div>", unsafe_allow_html=True)
        # (Isi dashboard Anda)

    # --- PREDISKI (TATA LETAK PERCIS GAMBAR) ---
    elif st.session_state.page == "Prediksi":
        st.markdown("<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: ESTIMASI RISIKO DEFORESTASI & MONITORING JANGKA PENDEK</h3>", unsafe_allow_html=True)
        
        # Area Filter & Upload
        c_filter, c_upload = st.columns([2, 1])
        with c_filter:
            prov_target = st.selectbox("Pilih Wilayah untuk Grafik Tren:", sorted(st.session_state.df_main['PROVINSI'].unique()))
        with c_upload:
            uploaded_file = st.file_uploader("📥 TAMBAH DATA (Otomatis)", type="csv")
            if uploaded_file:
                if st.button("Proses Data Baru"):
                    new_data = pd.read_csv(uploaded_file)
                    st.session_state.df_main = pd.concat([st.session_state.df_main, new_data], ignore_index=True)
                    st.rerun()

        # Layout Kiri & Kanan (Tabel & Grafik)
        cl, cr = st.columns([1, 1.5])
        df = st.session_state.df_main
        last_yr = df['TAHUN'].max()
        
        with cl:
            st.markdown("<h4 style='color: #facc15;'>📄 TABEL ESTIMASI (NASIONAL)</h4>", unsafe_allow_html=True)
            # Logika tabel: Menampilkan tahun setelah last_yr
            show_years = [last_yr+1, last_yr+2, last_yr+3]
            results = []
            for p in sorted(df['PROVINSI'].unique()):
                val = df[df['PROVINSI']==p].iloc[-1]['Y (TREE COVER LOSS- Ha)']
                for y in show_years:
                    results.append({"Provinsi": p, "Tahun": y, "Estimasi Loss (Ha)": round(val * (1.03**(y-last_yr)), 2)})
            st.dataframe(pd.DataFrame(results).head(15), use_container_width=True, hide_index=True)

        with cr:
            st.markdown(f"<h4 style='color: #facc15;'>📊 TREN KEHILANGAN TUTUPAN POHON (KONTINU) - {prov_target}</h4>", unsafe_allow_html=True)
            hist = df[df['PROVINSI'] == prov_target].sort_values('TAHUN').copy()
            hist['Status'] = 'Data Aktual'
            # Grafik
            fig = px.line(hist, x='TAHUN', y='Y (TREE COVER LOSS- Ha)', markers=True, color_discrete_sequence=['#22c55e'])
            st.plotly_chart(fig, use_container_width=True)

    # --- PENELITIAN ---
    elif st.session_state.page == "Penelitian":
        st.write("Info Penelitian Anda...")
