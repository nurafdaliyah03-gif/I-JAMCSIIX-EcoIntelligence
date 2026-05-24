import streamlit as st
import pandas as pd

# TEMPEL LINK YANG KAMU COPY DARI TOMBOL "RAW" TADI DI SINI
URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"

st.set_page_config(page_title="ForestGuard", layout="wide")
st.title("🌳 ForestGuard")

@st.cache_data
def load_data():
    try:
        # Menghapus spasi yang mungkin tidak sengaja ter-copy
        clean_url = URL_DATA.strip()
        df = pd.read_csv(clean_url)
        df.columns = df.columns.str.strip()
        return df
    except Exception as e:
        return None

df = load_data()

if df is not None:
    st.success("✅ Data berhasil dibaca!")
    st.write(df.head())
else:
    st.error("❌ Data tidak ditemukan. Pastikan URL benar.")
    st.write("Pastikan kamu sudah menekan tombol 'Raw' di GitHub dan meng-copy URL di address bar.")
