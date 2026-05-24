import streamlit as st
import pandas as pd
import plotly.express as px
import requests

# Konfigurasi Halaman
st.set_page_config(page_title="ForestGuard", layout="wide")

# Link GitHub (Pastikan link ini sudah benar setelah kamu upload file CSV)
URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-Ecolintelligence/main/data_jamsicx.csv"

# Fungsi Memuat Data
@st.cache_data
def load_data():
    try:
        df = pd.read_csv(URL_DATA)
        df.columns = df.columns.str.strip() # Menghapus spasi di nama kolom
        return df
    except Exception as e:
        st.error(f"Gagal memuat data: {e}")
        return None

df = load_data()

# Tampilan Utama
st.title("🌳 ForestGuard")

if df is not None:
    st.success("Data berhasil dimuat!")
    st.dataframe(df.head()) # Menampilkan 5 baris pertama data
    
    # Contoh visualisasi sederhana
    st.subheader("Grafik Tren Kehilangan Hutan")
    if 'TAHUN' in df.columns and 'Y' in df.columns:
        fig = px.line(df, x='TAHUN', y='Y', color='PROVINSI')
        st.plotly_chart(fig)
else:
    st.warning("Data belum terbaca. Pastikan file CSV sudah ada di GitHub dengan nama yang tepat.")
