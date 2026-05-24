import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="ForestGuard - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA LOADING (OTOMATIS) ---
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

    # --- DASHBOARD ---
    if st.session_state.page == "Dashboard":
        st.header("📊 Dashboard Deskriptif Spasial")
        col_f1, col_f2 = st.columns(2)
        sel_thn = col_f1.selectbox("Pilih Tahun:", sorted(df['TAHUN'].unique(), reverse=True))
        sel_prov = col_f2.selectbox("Fokus Wilayah:", ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist()))
        
        # Penjelasan Skala di ATAS peta
        st.markdown("""
        <div style='background: rgba(255,255,255,0.1); padding: 10px; border-radius: 10px; font-size: 0.85rem; margin-bottom: 10px;'>
            <b>Keterangan Skala Tree Cover Loss:</b> <span style='color: #ef4444;'>●</span> Merah: Tinggi | <span style='color: #eab308;'>●</span> Kuning: Sedang | <span style='color: #22c55e;'>●</span> Hijau: Rendah
        </div>
        """, unsafe_allow_html=True)

        if geojson:
            data_peta = df[df['TAHUN'] == sel_thn]
            if sel_prov != "Semua Provinsi": data_peta = data_peta[data_peta['PROVINSI'] == sel_prov]
            fig = px.choropleth(data_peta, geojson=geojson, locations="PROVINSI", featureidkey="properties.PROV_KEY", color=col_y, color_continuous_scale="RdYlGn_r")
            fig.update_geos(fitbounds="locations" if sel_prov != "Semua Provinsi" else False, visible=False)
            fig.update_layout(height=450, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='white')
            st.plotly_chart(fig, use_container_width=True)

    # --- PREDISKI (REVISI LOGIKA INPUT 2025 & TAHUN 2028) ---
    elif st.session_state.page == "Prediksi":
        if 'input_2025' not in st.session_state: st.session_state.input_2025 = None
        
        st.markdown("<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: ESTIMASI RISIKO DEFORESTASI & MONITORING JANGKA PENDEK</h3>", unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            prov_target = st.selectbox("Pilih Wilayah untuk Grafik Tren:", sorted(df['PROVINSI'].unique()))
        with col_f2:
            with st.expander("📥 TAMBAH DATA AKTUAL (2025)"):
                val_2025 = st.number_input(f"Masukkan Tree Cover Loss 2025 ({prov_target}):", min_value=0.0)
                if st.button("Simpan Data"):
                    st.session_state.input_2025 = val_2025
                    st.rerun()

        st.markdown("---")
        
        hist = df[df['PROVINSI'] == prov_target].sort_values('TAHUN').copy()
        if st.session_state.input_2025:
            new_row = {'TAHUN': 2025, col_y: st.session_state.input_2025, 'PROVINSI': prov_target}
            hist = pd.concat([hist, pd.DataFrame([new_row])], ignore_index=True)

        cl, cr = st.columns([1, 1.3])
        with cl:
            st.markdown("<h4 style='color: #facc15;'>📄 TABEL ESTIMASI (2026 - 2028)</h4>", unsafe_allow_html=True)
            all_provinces = sorted(df['PROVINSI'].unique())
            national_preds = []
            for p in all_provinces:
                last_val = hist[hist['PROVINSI']==p][col_y].iloc[-1] if p == prov_target else df[df['PROVINSI'] == p][col_y].iloc[-1]
                for thn in [2026, 2027, 2028]:
                    pred_val = last_val * (1.03 ** (thn - 2025))
                    national_preds.append({"Provinsi": p, "Tahun": thn, "Estimasi Loss (Ha)": round(pred_val, 2)})
            st.dataframe(pd.DataFrame(national_preds).head(12), use_container_width=True, hide_index=True)

        with cr:
            st.markdown(f"<h4 style='color: #facc15;'>📊 TREN {prov_target}</h4>", unsafe_allow_html=True)
            last_val_prov = hist[col_y].iloc[-1]
            future_years = [2026, 2027, 2028]
            future_vals = [last_val_prov * (1.03 ** (th - 2025)) for th in future_years]
            
            df_hist = hist.copy()
            df_hist['Status'] = 'Data Aktual (s.d 2025)'
            df_future = pd.DataFrame({'TAHUN': future_years, col_y: future_vals, 'Status': 'Hasil Prediksi (2026-2028)'})
            df_plot = pd.concat([df_hist, df_future])
            
            fig_pred = px.line(df_plot, x='TAHUN', y=col_y, color='Status', markers=True,
                               color_discrete_map={'Data Aktual (s.d 2025)': '#22c55e', 'Hasil Prediksi (2026-2028)': '#ef4444'})
            fig_pred.update_layout(paper_bgcolor='white', plot_bgcolor='white')
            st.plotly_chart(fig_pred, use_container_width=True)

    # --- PENELITIAN ---
    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#facc15; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
        # (Bagian penelitian tetap sama seperti sebelumnya)
