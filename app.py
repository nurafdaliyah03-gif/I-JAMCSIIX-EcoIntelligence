import streamlit as st
import pandas as pd
import plotly.express as px

# 1. KONFIGURASI HALAMAN
st.set_page_config(page_title="ForestGuard", layout="wide", initial_sidebar_state="collapsed")

# 2. LOAD DATA (PASTIKAN URL SUDAH SESUAI DENGAN LINK 'RAW' KAMU)
URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"

@st.cache_data
def load_data():
    df = pd.read_csv(URL_DATA)
    df.columns = df.columns.str.strip()
    return df

df = load_data()

# CSS CUSTOM
st.markdown("""
<style>
    .main-title { font-size: 3rem; font-weight: bold; color: #166534; text-align: center; }
    .menu-card { background: #f0fdf4; padding: 20px; border-radius: 15px; border: 1px solid #bbf7d0; text-align: center; }
</style>
""", unsafe_allow_html=True)

# 3. SESSION STATE UNTUK NAVIGASI
if 'page' not in st.session_state: st.session_state.page = "Dashboard"

# 4. HALAMAN UTAMA
st.markdown("<h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)

col1, col2, col3 = st.columns(3)
with col1:
    if st.button("📊 Dashboard"): st.session_state.page = "Dashboard"
with col2:
    if st.button("🧪 Prediksi"): st.session_state.page = "Prediksi"
with col3:
    if st.button("📖 Penelitian"): st.session_state.page = "Penelitian"

st.markdown("---")

# 5. LOGIKA HALAMAN
if st.session_state.page == "Dashboard":
    st.subheader("Dashboard Deskriptif")
    prov = st.selectbox("Pilih Provinsi:", df['PROVINSI'].unique())
    df_filt = df[df['PROVINSI'] == prov]
    
    # Visualisasi
    fig = px.line(df_filt, x='TAHUN', y='X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)', title=f"Tren di {prov}")
    st.plotly_chart(fig, use_container_width=True)

elif st.session_state.page == "Prediksi":
    st.subheader("Simulasi Prediksi")
    st.write("Masukkan parameter untuk simulasi deforestasi.")
    # Logika input prediksi
    val = st.slider("Input Variabel X1", 0.0, 5000.0)
    st.write(f"Hasil simulasi berdasarkan variabel {val} adalah ...")

elif st.session_state.page == "Penelitian":
    st.subheader("Info Penelitian")
    st.write("Aplikasi ini menggunakan pendekatan MERF untuk analisis spasial.")
