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
    .stSelectbox div[data-baseweb="select"] div { color: #000000 !important; font-weight: 600 !important; }
    .stSelectbox label p { color: #facc15 !important; font-weight: bold !important; font-size: 1.05rem !important; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; filter: drop-shadow(0px 5px 15px rgba(0,0,0,0.9)); }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; display: flex; flex-direction: column; justify-content: center; }
    .stPlotlyChart { background-color: white !important; border-radius: 20px; padding: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    div.stButton > button { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; color: white !important; border: 1px solid #facc15 !important; border-radius: 12px; width: 100%; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(250, 191, 36, 0.3); border-radius: 16px; padding: 25px; margin-bottom: 20px; backdrop-filter: blur(8px); }
    .research-card h4 { color: #facc15 !important; margin-top: 0px; border-bottom: 2px solid #15803d; padding-bottom: 8px; }
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

# --- 5. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        if st.button("Buka Dashboard"): set_page("Dashboard"); st.rerun()
    with c2:
        if st.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    with c3:
        if st.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()

else:
    if st.button("⬅️ KEMBALI KE PORTAL"): set_page("Portal"); st.rerun()
    st.markdown("---")

    if st.session_state.page == "Dashboard":
        st.header("📊 Dashboard")
        # Logika Dashboard
        
    elif st.session_state.page == "Prediksi":
        st.header("🧪 Prediksi MERF")
        # Logika Prediksi

    elif st.session_state.page == "Penelitian":
        st.header("📖 Info Penelitian")
        
        # --- BAGIAN PENELITIAN LENGKAP ---
        st.markdown("### 📋 Definisi Operasional Variabel")
        v_col1, v_col2 = st.columns(2)
        with v_col1:
            st.markdown("""<div class='research-card'><h4>Variabel Independen (X)</h4><p>X1: Luas Penutupan Lahan (Ribu Ha), X2: Luas Karhutla (Ha), X3: Luas Perkebunan (Ribu Ha)</p></div>""", unsafe_allow_html=True)
        with v_col2:
            st.markdown("""<div class='research-card'><h4>Variabel Lainnya</h4><p>X4: Kepadatan Penduduk (Jiwa/km²), X5: Populasi Ternak (Ekor), X6: PDRB Pertambangan (%)</p></div>""", unsafe_allow_html=True)

        st.markdown("""
        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding: 25px; border-radius: 15px; border: 1px solid #ef4444;'>
            <h4 style='color: #fca5a5;'>⚠️ Keterbatasan Model (Limitations)</h4>
            <ul>
                <li><b>Ketergantungan Data Historis:</b> Model hanya membaca tren masa lalu.</li>
                <li><b>Optimal Jangka Pendek:</b> Akurasi menurun untuk prediksi jangka panjang.</li>
                <li><b>Efek Wilayah Baru:</b> Provinsi pemekaran mungkin memiliki error lebih tinggi.</li>
                <li><b>Resolusi Spasial Makro:</b> Belum mencakup konflik lahan mikro.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
