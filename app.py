import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE & DATA CLEANING ---
if 'page' not in st.session_state: st.session_state.page = "Portal"
if 'df' not in st.session_state: 
    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    
    # Standardisasi Nama Provinsi agar Sinkron dengan GeoJSON
    mapping_prov = {
        "KEPULAUAN RIAU": "KEP. RIAU",
        "DAERAH ISTIMEWA YOGYAKARTA": "DI YOGYAKARTA",
        "DKI JAKARTA": "DKI JAKARTA",
        "BANGKA BELITUNG": "KEP. BANGKA BELITUNG"
    }
    df['PROVINSI'] = df['PROVINSI'].replace(mapping_prov)
    st.session_state.df = df

def set_page(name): st.session_state.page = name

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>
    .stApp { 
        background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); 
        background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; 
    }
    .stSelectbox div[data-baseweb="select"] { background-color: #ffffff !important; border-radius: 10px; }
    .stSelectbox div[data-baseweb="select"] div { color: #000000 !important; font-weight: 600 !important; }
    .stSelectbox label p { color: #facc15 !important; font-weight: bold !important; font-size: 1.05rem !important; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; filter: drop-shadow(0px 5px 15px rgba(0,0,0,0.9)); }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; display: flex; flex-direction: column; justify-content: center; }
    .stPlotlyChart { background-color: white !important; border-radius: 20px; padding: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #facc15 !important; font-weight: bold !important; font-size: 0.9rem !important; }
    div.stButton > button { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; color: white !important; border: 1px solid #facc15 !important; border-radius: 12px; width: 100%; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(250, 191, 36, 0.3); border-radius: 16px; padding: 25px; margin-bottom: 20px; backdrop-filter: blur(8px); }
    .research-card h4 { color: #facc15 !important; margin-top: 0px; border-bottom: 2px solid #15803d; padding-bottom: 8px; }
    .legend-box { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; font-size: 0.85rem; border: 1px solid #facc15; }
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
            if "YOGYAKARTA" in nama: key = "DI YOGYAKARTA"
            elif "JAKARTA" in nama: key = "DKI JAKARTA"
            elif "KEPULAUAN RIAU" in nama: key = "KEP. RIAU"
            elif "BANGKA BELITUNG" in nama: key = "KEP. BANGKA BELITUNG"
            else: key = nama
            feature['properties']['PROV_KEY'] = key
        return res
    except: return None
geojson = load_geojson()

col_y = "Y (TREE COVER LOSS- Ha)"
cols_x = {"X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)", "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)", "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)", "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)", "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)", "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"}

# --- 5. LOGIKA NAVIGASI ---
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

    if st.session_state.page == "Dashboard":
        df = st.session_state.df
        st.header("📊 Dashboard Deskriptif Spasial")
        col_f1, col_f2 = st.columns(2)
        sel_thn = col_f1.selectbox("Pilih Tahun:", sorted(df['TAHUN'].unique(), reverse=True))
        sel_prov = col_f2.selectbox("Fokus Wilayah (Zoom Provinsi):", ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist()))
        df_filt_year = df[df['TAHUN'] == sel_thn]
        cl, cr = st.columns([1.1, 0.9])
        with cl:
            if geojson:
                data_peta = df_filt_year if sel_prov == "Semua Provinsi" else df_filt_year[df_filt_year['PROVINSI'] == sel_prov]
                fig = px.choropleth(data_peta, geojson=geojson, locations="PROVINSI", featureidkey="properties.PROV_KEY", color=col_y, color_continuous_scale="RdYlGn_r")
                fig.update_geos(fitbounds="locations" if sel_prov != "Semua Provinsi" else False, visible=False)
                fig.update_layout(height=450, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
        with cr:
            var_x = st.selectbox("Analisis Korelasi X:", list(cols_x.keys()))
            fig2 = px.scatter(df_filt_year, x=cols_x[var_x], y=col_y, color=col_y, color_continuous_scale="RdYlGn_r", trendline="ols")
            fig2.update_layout(paper_bgcolor='white')
            st.plotly_chart(fig2, use_container_width=True)

    elif st.session_state.page == "Prediksi":
        st.markdown("<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: ESTIMASI RISIKO DEFORESTASI</h3>", unsafe_allow_html=True)
        df = st.session_state.df
        prov_target = st.selectbox("Pilih Wilayah untuk Grafik Tren:", sorted(df['PROVINSI'].unique()))
        last_yr = df['TAHUN'].max()
        p_data = df[df['PROVINSI'] == prov_target]
        last_val = p_data.iloc[-1][col_y]
        
        cl, cr = st.columns([1, 1.3])
        with cl:
            pred_data = [{"Tahun": last_yr+i, "Estimasi Loss (Ha)": round(last_val * (1.03 ** i), 2)} for i in range(1, 4)]
            st.dataframe(pd.DataFrame(pred_data), use_container_width=True, hide_index=True)
        with cr:
            hist = p_data.sort_values('TAHUN').copy()
            future = pd.DataFrame({'TAHUN': [last_yr+1, last_yr+2, last_yr+3], col_y: [last_val * (1.03**i) for i in range(1, 4)], 'Status': 'Prediksi'})
            hist['Status'] = 'Data Aktual'
            fig_pred = px.line(pd.concat([hist[['TAHUN', col_y, 'Status']], future]), x='TAHUN', y=col_y, color='Status', markers=True)
            st.plotly_chart(fig_pred, use_container_width=True)

    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#facc15; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
        st.markdown("<div class='research-card'><h4>🎯 Tujuan Penelitian</h4><p>Menerapkan model hibrida MERF dan membangun visualisasi interaktif untuk memonitor deforestasi.</p></div>", unsafe_allow_html=True)
