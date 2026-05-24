import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="ForestGuard", layout="wide", initial_sidebar_state="collapsed")

# 2. KONFIGURASI DATA (PASTIKAN LINK INI SESUAI DENGAN FILE DI GITHUB)
URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-Ecolintelligence/main/data_jamsicx.csv"

# 3. MEMUAT DATA DENGAN PEMBERSIHAN NAMA KOLOM
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL_DATA)
        # Menghapus spasi di awal/akhir nama kolom agar kode tidak error
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        st.error(f"Error memuat data: {e}")
        return None

df = load_data()

# CSS CUSTOM
st.markdown("""
<style>
    .main-title { text-align: center; color: #166534; font-size: 3rem; font-weight: bold; }
    .menu-card { background: #f0fdf4; padding: 20px; border-radius: 15px; text-align: center; border: 1px solid #bbf7d0; }
</style>
""", unsafe_allow_html=True)

# 4. LOGIKA APLIKASI
st.markdown("<h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)

if df is not None:
    # Mengambil nama kolom yang sudah bersih
    kolom_x1 = [c for c in df.columns if c.startswith('X1')][0]
    kolom_y = [c for c in df.columns if c.startswith('X2')][0] # Contoh mengambil kolom X2 sebagai Y untuk testing
    
    c1, c2 = st.columns(2)
    with c1:
        st.markdown("<div class='menu-card'><h3>📊 Dashboard</h3></div>", unsafe_allow_html=True)
        if st.button("Buka Dashboard"):
            st.write("Data berhasil dimuat! Menampilkan visualisasi...")
            fig = px.scatter(df, x=kolom_x1, y=kolom_y, color="PROVINSI", title="Analisis Data")
            st.plotly_chart(fig, use_container_width=True)
            
    with c2:
        st.markdown("<div class='menu-card'><h3>🧪 Prediksi</h3></div>", unsafe_allow_html=True)
        if st.button("Mulai Prediksi"):
            st.write("Fitur Prediksi siap digunakan.")
else:
    st.error("Data belum terbaca. Periksa koneksi ke GitHub.")
