import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ForestGuard", layout="wide")

# Link Raw GitHub yang WAJIB AKURAT
URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-Ecolintelligence/main/dataset_final.csv"

def load_data():
    try:
        response = requests.get(URL_DATA)
        if response.status_code == 200:
            df = pd.read_csv(URL_DATA)
            return df
        else:
            return None
    except:
        return None

df = load_data()

st.title("🌳 ForestGuard")

if df is not None:
    st.success("✅ Data berhasil dimuat!")
    st.write("Tombol di bawah sekarang seharusnya sudah bisa diklik:")
    
    # Tombol yang dipaksa aktif
    if st.button("Buka Dashboard"):
        st.write("Dashboard terbuka!")
else:
    st.error("❌ Data tidak ditemukan. Pastikan file 'data_jamsicx.csv' sudah di-upload dengan benar di GitHub.")
    st.write(f"Link yang dicoba: {URL_DATA}")
