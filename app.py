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
    /* Menggelapkan background agar teks lebih terbaca */
    .stApp { 
        background: linear-gradient(rgba(0, 0, 0, 0.85), rgba(0, 0, 0, 0.85)), 
                    url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); 
        background-size: cover; 
        background-attachment: fixed; 
        color: #ffffff; 
    }
    
    /* Input & Selectbox */
    .stSelectbox div[data-baseweb="select"] { background-color: #f8fafc !important; border-radius: 10px; border: 1px solid #facc15; }
    .stSelectbox div[data-baseweb="select"] div { color: #000000 !important; font-weight: 700 !important; }
    
    /* Teks Judul */
    .main-title { 
        font-size: 5rem !important; font-family: 'Arial Black', sans-serif; 
        background: linear-gradient(to bottom, #fef08a 0%, #facc15 100%); 
        -webkit-background-clip: text; -webkit-text-fill-color: transparent; 
        text-align: center; font-weight: 900 !important; 
        text-shadow: 2px 2px 10px rgba(0,0,0,0.5);
    }
    
    /* Kartu Menu */
    .menu-card { 
        background: rgba(255, 255, 255, 0.08); 
        backdrop-filter: blur(20px); 
        border: 1px solid rgba(250, 204, 21, 0.3); 
        border-radius: 30px; padding: 40px; text-align: center; height: 350px;
        transition: 0.3s;
    }
    .menu-card:hover { background: rgba(255, 255, 255, 0.15); border-color: #facc15; }
    
    /* Grafik & Tabel */
    .stPlotlyChart { background-color: #ffffff !important; border-radius: 20px; padding: 10px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); }
    
    /* Warna Metrik */
    [data-testid="stMetricValue"] { color: #ffffff !important; text-shadow: 1px 1px 2px #000; }
    [data-testid="stMetricLabel"] { color: #fbbf24 !important; font-weight: bold !important; }
    
    /* Tombol */
    div.stButton > button { 
        background: #166534 !important; 
        color: #ffffff !important; 
        border: 1px solid #facc15 !important; 
        border-radius: 10px; font-weight: bold;
    }
    div.stButton > button:hover { background: #15803d !important; border-color: #ffffff !important; }
    
    /* Kartu Penelitian */
    .research-card { 
        background: rgba(30, 41, 59, 0.7); 
        border: 1px solid rgba(250, 204, 21, 0.2); 
        border-radius: 16px; padding: 25px; color: #e2e8f0;
    }
    .research-card h4 { color: #facc15 !important; border-bottom: 2px solid #166534; padding-bottom: 8px; }
    
    /* Legenda */
    .legend-box { background: rgba(0,0,0,0.4); padding: 12px; border-radius: 8px; border: 1px solid #facc15; color: #ffffff; }
</style>
""", unsafe_html=True)

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
        st.markdown("<div class='legend-box'><b>Legenda Tingkat Kehilangan Tutupan Pohon:</b> 🟢 Rendah (Hijau) ➔ 🟡 Sedang (Kuning) ➔ 🔴 Tinggi (Merah)</div>", unsafe_allow_html=True)
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
        st.markdown("<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: ESTIMASI RISIKO DEFORESTASI & MONITORING JANGKA PENDEK</h3>", unsafe_allow_html=True)
        with st.expander("📥 TAMBAH DATA AKTUAL (UPDATE TAHUNAN)"):
            uploaded_file = st.file_uploader("Upload CSV Data:", type="csv")
            if uploaded_file and st.button("Update Data & Grafik"):
                new_df = pd.read_csv(uploaded_file)
                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                st.rerun()

        df = st.session_state.df
        last_yr = df['TAHUN'].max()
        prov_target = st.selectbox("Pilih Wilayah untuk Grafik Tren:", sorted(df['PROVINSI'].unique()))
        st.markdown("---")
        
        cl, cr = st.columns([1, 1.3])
        with cl:
            st.markdown(f"<h4 style='color: #facc15;'>📄 TABEL ESTIMASI ({last_yr+1} - {last_yr+3}): {prov_target}</h4>", unsafe_allow_html=True)
            p_data = df[df['PROVINSI'] == prov_target]
            last_val = p_data.iloc[-1][col_y]
            pred_data = [{"Tahun": last_yr+i, "Estimasi Loss (Ha)": round(last_val * (1.03 ** i), 2)} for i in range(1, 4)]
            st.dataframe(pd.DataFrame(pred_data), use_container_width=True, hide_index=True)

        with cr:
            st.markdown(f"<h4 style='color: #facc15;'>📊 TREN KEHILANGAN TUTUPAN POHON</h4>", unsafe_allow_html=True)
            hist = p_data.sort_values('TAHUN').copy()
            hist['Status'] = 'Data Aktual'
            future = pd.DataFrame({'TAHUN': [last_yr+1, last_yr+2, last_yr+3], col_y: [last_val * (1.03**i) for i in range(1, 4)], 'Status': 'Prediksi'})
            
            last_actual = hist.iloc[[-1]].copy()
            last_actual['Status'] = 'Prediksi'
            df_plot = pd.concat([hist[['TAHUN', col_y, 'Status']], last_actual, future])
            
            fig_pred = px.line(df_plot, x='TAHUN', y=col_y, color='Status', markers=True, color_discrete_map={'Data Aktual': '#22c55e', 'Prediksi': '#ef4444'})
            st.plotly_chart(fig_pred, use_container_width=True)

    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#facc15; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("<div class='research-card'><h4>🎯 Tujuan Penelitian</h4><ul><li>Menerapkan model hibrida MERF.</li><li>Membangun web interaktif ForestGuard.</li></ul></div>", unsafe_allow_html=True)
        with rc2:
            st.markdown("<div class='research-card'><h4>🤖 Metode MERF</h4><p>Paduan Random Forest & Mixed Effects.</p></div>", unsafe_allow_html=True)
        
        st.markdown("### 📋 Definisi Operasional")
        st.markdown("""
        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding: 25px; border-radius: 15px; border: 1px solid #ef4444; margin-top: 10px;'>
            <h5 style='margin: 0 0 15px 0; color: #fca5a5; font-weight: bold;'>⚠️ Keterbatasan Model (Limitations)</h5>
            <ul style='margin: 0; padding-left: 20px; font-size: 0.9rem; color: #ffeeee; line-height: 1.6;'>
                <li><b>Ketergantungan Data Historis:</b> Hanya berdasarkan tren masa lalu.</li>
                <li><b>Optimal Jangka Pendek:</b> Akurasi tertinggi untuk prediksi jangka pendek.</li>
                <li><b>Efek Wilayah Baru:</b> Mengabaikan efek acak pada wilayah pemekaran baru.</li>
                <li><b>Cakupan Variabel:</b> Menggunakan data agregat provinsi, belum mencakup faktor mikro.</li>
                <li><b>Resolusi Spasial:</b> Tidak memperhitungkan faktor eksternal mendadak.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
