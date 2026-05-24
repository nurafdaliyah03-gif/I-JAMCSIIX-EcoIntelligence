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

# --- 3. CSS CUSTOM (TETAP SAMA) ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }
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

    # --- HALAMAN PREDISKI (MODEL SESUAI GAMBAR) ---
    if st.session_state.page == "Prediksi":
        # Bagian Atas: Judul & Filter
        st.markdown("<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: ESTIMASI RISIKO DEFORESTASI & MONITORING JANGKA PENDEK</h3>", unsafe_allow_html=True)
        
        col_f1, col_f2 = st.columns([2, 1])
        with col_f1:
            prov_target = st.selectbox("Pilih Wilayah untuk Grafik Tren:", sorted(df['PROVINSI'].unique()))
        with col_f2:
            st.markdown("<br>", unsafe_allow_html=True)
            st.button("📥 TAMBAH DATA (Otomatis)")

        st.markdown("---")
        
        # Bagian Bawah: Dua Kolom
        cl, cr = st.columns([1, 1.3])
        
        with cl:
            st.markdown("<h4 style='color: #facc15;'>📄 TABEL ESTIMASI 3 TAHUN (NASIONAL)</h4>", unsafe_allow_html=True)
            
            # Simulasi Tabel Estimasi Nasional 3 Tahun kedepan
            all_provinces = sorted(df['PROVINSI'].unique())
            national_preds = []
            for p in all_provinces:
                last_val = df[df['PROVINSI'] == p][col_y].iloc[-1]
                for thn in [2025, 2026, 2027]:
                    # Simulasi kenaikan 3% pertahun
                    pred_val = last_val * (1.03 ** (thn - 2024))
                    national_preds.append({"Provinsi": p, "Tahun": thn, "Estimasi Loss (Ha)": round(pred_val, 2)})
            
            df_nat = pd.DataFrame(national_preds).head(15) # Ambil 15 teratas
            st.dataframe(df_nat, use_container_width=True, hide_index=True)
            st.markdown("<p style='font-size:0.7rem; color: #cbd5e1;'>[dst...]</p>", unsafe_allow_html=True)

        with cr:
            st.markdown(f"<h4 style='color: #facc15;'>📊 TREN KEHILANGAN TUTUPAN POHON (KONTINU) - {prov_target}</h4>", unsafe_allow_html=True)
            
            hist = df[df['PROVINSI'] == prov_target].sort_values('TAHUN')
            last_val_prov = hist[col_y].iloc[-1]
            
            # Buat Data Gabungan (Historis + Prediksi)
            future_years = [2025, 2026, 2027]
            future_vals = [last_val_prov * (1.03 ** (th - 2024)) for th in future_years]
            
            df_hist = hist[['TAHUN', col_y]].copy()
            df_hist['Status'] = 'Data Aktual (2015-2024)'
            
            df_future = pd.DataFrame({'TAHUN': future_years, col_y: future_vals, 'Status': 'Hasil Prediksi (2025-2027)'})
            
            # Titik jembatan agar garis menyambung
            bridge = pd.DataFrame({'TAHUN': [2024], col_y: [last_val_prov], 'Status': 'Hasil Prediksi (2025-2027)'})
            
            df_plot = pd.concat([df_hist, bridge, df_future])
            
            fig_pred = px.line(df_plot, x='TAHUN', y=col_y, color='Status', markers=True,
                               color_discrete_map={'Data Aktual (2015-2024)': '#22c55e', 'Hasil Prediksi (2025-2027)': '#ef4444'})
            
            fig_pred.update_layout(
                paper_bgcolor='white', 
                legend=dict(orientation="h", yanchor="bottom", y=-0.3, xanchor="center", x=0.5),
                xaxis=dict(tickmode='linear', dtick=1),
                yaxis=dict(title="Loss (Ha)")
            )
            st.plotly_chart(fig_pred, use_container_width=True)
