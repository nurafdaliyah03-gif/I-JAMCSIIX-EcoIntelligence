import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np
from merf.merf import MERF

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================
st.set_page_config(page_title="ForestGuard", layout="wide", initial_sidebar_state="collapsed")

# =========================================================
# CSS
# =========================================================
st.markdown("""
<style>
.stApp { background: linear-gradient(rgba(0,0,0,0.82), rgba(0,0,0,0.82)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; }
.main-title { font-size: 5rem !important; font-family: 'Arial Black'; background: linear-gradient(to bottom, #fde047 0%, #facc15 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900; }
.menu-card { background: rgba(255,255,255,0.10); border-radius: 28px; padding: 40px; height: 320px; text-align: center; backdrop-filter: blur(18px); border: 1px solid rgba(255,255,255,0.1); }
div.stButton > button { background: linear-gradient(135deg,#15803d,#166534) !important; color: white !important; border-radius: 12px; border: 1px solid #fde047 !important; width: 100%; font-weight: bold; }
h1,h2,h3,h4,h5,h6,p,label,span,li,div { color: #f8fafc !important; }
[data-testid="stMetricValue"] { color: #fde047 !important; font-weight: 800; }
.stPlotlyChart { background: rgba(255,255,255,0.97); border-radius: 20px; padding: 12px; }
[data-testid="stDataFrame"] { background: rgba(255,255,255,0.97); border-radius: 18px; padding: 5px; }
.research-card { background: rgba(15,23,42,0.7); border-radius: 18px; padding: 25px; }
</style>
""", unsafe_allow_html=True)

# =========================================================
# SESSION STATE & DATA LOAD
# =========================================================
if 'page' not in st.session_state: st.session_state.page = "Portal"
if 'df' not in st.session_state:
    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip().str.replace(r"\s+", " ", regex=True)
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    st.session_state.df = df

all_cols = st.session_state.df.columns.tolist()
def cari_kolom(keyword):
    for col in all_cols:
        if keyword.lower() in col.lower(): return col
    return None

col_y = cari_kolom("TREE COVER LOSS")
cols_x = {"X1": cari_kolom("LUAS PENUTUPAN LAHAN"), "X2": cari_kolom("KEBAKARAN HUTAN"), "X3": cari_kolom("TOTAL LUAS TANAMAN"), 
          "X4": cari_kolom("KEPADATAN PENDUDUK"), "X5": cari_kolom("TOTAL POPULASI TERNAK"), "X6": cari_kolom("PDRB PERTAMBANGAN")}

# =========================================================
# FUNGSI PEMROSESAN DATA & MODEL (SESUAI SYNTAX ANDA)
# =========================================================
@st.cache_data
def prepare_data(df):
    data = df.copy().sort_values(['PROVINSI', 'TAHUN'])
    data['Y_lag1'] = data.groupby('PROVINSI')[col_y].shift(1)
    for key, col in cols_x.items():
        if col: data[f'{key}_ma3'] = data.groupby('PROVINSI')[col].transform(lambda x: x.rolling(3, min_periods=1).mean())
    data = data.dropna().copy()
    data['Y_log'] = np.log1p(data[col_y])
    data['Y_lag1_log'] = np.log1p(data['Y_lag1'])
    feature_cols = ['Y_lag1_log']
    for key in cols_x.keys():
        if cols_x[key]:
            new_col = f'{key}_ma3_log'
            data[new_col] = np.log1p(data[f'{key}_ma3'])
            feature_cols.append(new_col)
    return data, feature_cols

@st.cache_resource
def load_or_train_model(df):
    data, feature_cols = prepare_data(df)
    train_data = data[data['TAHUN'] <= 2021]
    model = MERF()
    model.fit(train_data[feature_cols], np.ones((len(train_data), 1)), train_data["PROVINSI"], train_data['Y_log'])
    return model, feature_cols

def forecast_all_provinces(model, feature_cols, df, n_years=3):
    data = df.copy()
    hasil_semua = []
    provinsi_list = sorted(data['PROVINSI'].unique())
    for provinsi in provinsi_list:
        prov_data = data[data['PROVINSI'] == provinsi].sort_values('TAHUN')
        latest = prov_data.iloc[-1]
        current_y = latest[col_y]
        current_year = int(latest['TAHUN'])
        x_hist = {key: prov_data[col].tail(3).tolist() for key, col in cols_x.items() if col is not None}
        for i in range(1, n_years + 1):
            tahun = current_year + i
            future_input = {'Y_lag1_log': np.log1p(current_y)}
            for key in x_hist.keys():
                ma3 = np.mean(x_hist[key][-3:])
                future_input[f'{key}_ma3_log'] = np.log1p(ma3)
            X_future = pd.DataFrame([future_input])[feature_cols]
            pred_log = model.predict(X_future, np.ones((1,1)), pd.Series([provinsi]))[0]
            pred = np.expm1(pred_log)
            hasil_semua.append({"PROVINSI": provinsi, "TAHUN": tahun, "PREDIKSI": round(pred, 2), "STATUS": "Prediksi"})
            current_y = pred
            for key in x_hist.keys(): x_hist[key].append(np.mean(x_hist[key][-3:]))
    return pd.DataFrame(hasil_semua)

# =========================================================
# NAVIGASI DAN HALAMAN
# =========================================================
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='menu-card'><h1>🛰️</h1><h3>Dashboard Spasial</h3></div>", unsafe_allow_html=True)
        if st.button("Buka Dashboard"): st.session_state.page = "Dashboard"; st.rerun()
    with c2:
        st.markdown("<div class='menu-card'><h1>🧪</h1><h3>Prediksi MERF</h3></div>", unsafe_allow_html=True)
        if st.button("Mulai Prediksi"): st.session_state.page = "Prediksi"; st.rerun()
    with c3:
        st.markdown("<div class='menu-card'><h1>📖</h1><h3>Info Penelitian</h3></div>", unsafe_allow_html=True)
        if st.button("Lihat Penelitian"): st.session_state.page = "Penelitian"; st.rerun()

elif st.session_state.page == "Dashboard":
    st.title("🛰️ Dashboard Spasial")
    if st.button("⬅️ Kembali"): st.session_state.page = "Portal"; st.rerun()
    st.write("Konten Dashboard Spasial Anda di sini.")

elif st.session_state.page == "Prediksi":
    if st.button("⬅️ Kembali"): st.session_state.page = "Portal"; st.rerun()
    st.markdown("<h1 style='color:#fde047;'>🌍 PREDIKSI RISIKO DEFORESTASI</h1>", unsafe_allow_html=True)
    # (Di sini masukkan seluruh logika halaman prediksi Anda yang asli)
    df = st.session_state.df
    st.markdown("## 📥 Upload Data Aktual Baru")
    uploaded_file = st.file_uploader("Upload file CSV", type="csv")
    # ... Lanjutkan sisa logika prediksi Anda ...

elif st.session_state.page == "Penelitian":
    st.title("📖 Info Penelitian")
    if st.button("⬅️ Kembali"): st.session_state.page = "Portal"; st.rerun()
    st.markdown("<div class='research-card'>Informasi detail mengenai model dan penelitian ForestGuard...</div>", unsafe_allow_html=True)
