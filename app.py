import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="ForestGuard Debug", layout="wide")

URL_DATA = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-Ecolintelligence/main/data_jamsicx.csv"

def load_data():
    try:
        # Kita cek apakah link ini bisa diakses oleh server
        response = requests.get(URL_DATA)
        st.write(f"Status Akses ke GitHub: {response.status_code}") # Ini akan memberi tahu kita masalahnya
        
        if response.status_code == 200:
            df = pd.read_csv(URL_DATA)
            df.columns = df.columns.str.strip()
            return df
        else:
            st.error("Gagal terhubung ke file (Status bukan 200).")
            return None
    except Exception as e:
        st.error(f"Error teknis: {e}")
        return None

df = load_data()

if df is not None:
    st.success("✅ Data berhasil dibaca!")
    st.dataframe(df.head())
else:
    st.error("❌ Data tetap tidak terbaca.")
