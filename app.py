import streamlit as st
import pandas as pd
import plotly.express as px
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="ForestGuard - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. DATA LOADING & STATE ---
if 'df_main' not in st.session_state:
    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    st.session_state.df_main = df

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }
    .main-title { font-size: 3.5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; }
    div.stButton > button { background: #15803d !important; color: white !important; border-radius: 10px; }
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
else:
    if st.button("⬅️ KEMBALI"): set_page("Portal"); st.rerun()
    
    if st.session_state.page == "Prediksi":
        st.header("📈 Prediksi & Update Data Aktual")
        
        # FITUR UPLOAD DATA
        with st.expander("📥 UPLOAD DATA AKTUAL TAHUNAN (CSV)"):
            uploaded_file = st.file_uploader("Upload file CSV data tahunan:", type="csv")
            if uploaded_file:
                new_data = pd.read_csv(uploaded_file)
                if st.button("Proses & Update Model"):
                    # Logika: Menggabungkan data baru ke dataset utama
                    st.session_state.df_main = pd.concat([st.session_state.df_main, new_data], ignore_index=True)
                    st.success("Data berhasil diintegrasikan!")
        
        # ANALISIS & VISUALISASI
        df = st.session_state.df_main
        prov = st.selectbox("Pilih Provinsi:", sorted(df['PROVINSI'].unique()))
        
        hist = df[df['PROVINSI'] == prov].sort_values('TAHUN')
        last_yr = hist['TAHUN'].max()
        last_val = hist.iloc[-1]['Y (TREE COVER LOSS- Ha)']
        
        # TABEL ESTIMASI (Otomatis: Mengambil 3 tahun setelah tahun terakhir di data)
        st.subheader(f"📄 Tabel Estimasi Nasional ({last_yr+1} - {last_yr+3})")
        future_years = [last_yr+1, last_yr+2, last_yr+3]
        preds = []
        for p in df['PROVINSI'].unique():
            val = df[df['PROVINSI']==p].iloc[-1]['Y (TREE COVER LOSS- Ha)']
            for y in future_years:
                preds.append({"Provinsi": p, "Tahun": y, "Estimasi Loss (Ha)": round(val * (1.03**(y-last_yr)), 2)})
        st.dataframe(pd.DataFrame(preds).head(10), use_container_width=True)

        # GRAFIK (Warna Hijau = Data Historis, Merah = Prediksi)
        st.subheader(f"📊 Tren {prov}")
        future_data = pd.DataFrame({'TAHUN': future_years, 'Y (TREE COVER LOSS- Ha)': [last_val * (1.03**(y-last_yr)) for y in future_years], 'Status': 'Prediksi'})
        hist['Status'] = 'Aktual'
        df_plot = pd.concat([hist[['TAHUN', 'Y (TREE COVER LOSS- Ha)', 'Status']], future_data])
        
        fig = px.line(df_plot, x='TAHUN', y='Y (TREE COVER LOSS- Ha)', color='Status', markers=True, 
                      color_discrete_map={'Aktual': '#22c55e', 'Prediksi': '#ef4444'})
        st.plotly_chart(fig, use_container_width=True)
