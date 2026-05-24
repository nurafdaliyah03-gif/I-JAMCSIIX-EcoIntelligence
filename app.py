import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(
    page_title="I-JAMCSIIX - Eco Intelligence",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# --- 2. SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "Portal"

if 'df' not in st.session_state:

    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"

    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()

    df['PROVINSI'] = (
        df['PROVINSI']
        .astype(str)
        .str.strip()
        .str.upper()
    )

    st.session_state.df = df

def set_page(name):
    st.session_state.page = name

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>

    .stApp {
        background:
        linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)),
        url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop');

        background-size: cover;
        background-position: center;
        background-attachment: fixed;
        color: #ffffff;
    }

    .stSelectbox div[data-baseweb="select"] {
        background-color: #ffffff !important;
        border-radius: 10px;
    }

    .stSelectbox div[data-baseweb="select"] div {
        color: #000000 !important;
        font-weight: 600 !important;
    }

    .stSelectbox label p {
        color: #facc15 !important;
        font-weight: bold !important;
        font-size: 1.05rem !important;
    }

    .main-title {
        font-size: 5rem !important;
        font-family: 'Arial Black', sans-serif;
        background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        text-align: center;
        font-weight: 900 !important;
        filter: drop-shadow(0px 5px 15px rgba(0,0,0,0.9));
    }

    .menu-card {
        background: rgba(255, 255, 255, 0.1);
        backdrop-filter: blur(15px);
        border: 1px solid rgba(255, 255, 255, 0.2);
        border-radius: 30px;
        padding: 40px;
        text-align: center;
        height: 350px;
        display: flex;
        flex-direction: column;
        justify-content: center;
    }

    .stPlotlyChart {
        background-color: white !important;
        border-radius: 20px;
        padding: 15px;
        box-shadow: 0 10px 30px rgba(0,0,0,0.5);
    }

    div.stButton > button {
        background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important;
        color: white !important;
        border: 1px solid #facc15 !important;
        border-radius: 12px;
        width: 100%;
    }

    .research-card {
        background: rgba(15, 23, 42, 0.65);
        border: 1px solid rgba(250, 191, 36, 0.3);
        border-radius: 16px;
        padding: 25px;
        margin-bottom: 20px;
        backdrop-filter: blur(8px);
    }

    .research-card h4 {
        color: #facc15 !important;
        margin-top: 0px;
        border-bottom: 2px solid #15803d;
        padding-bottom: 8px;
    }

    .legend-box {
        background: rgba(255,255,255,0.1);
        padding: 10px;
        border-radius: 8px;
        font-size: 0.85rem;
        border: 1px solid #facc15;
    }

</style>
""", unsafe_allow_html=True)

# --- 4. DATA GEOJSON ---
@st.cache_data
def load_geojson():

    try:

        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"

        res = requests.get(url).json()

        for feature in res['features']:

            nama = str(feature['properties'].get('Propinsi', '')).strip().upper()

            feature['properties']['PROV_KEY'] = (
                "DI YOGYAKARTA"
                if "YOGYAKARTA" in nama
                else (
                    "DKI JAKARTA"
                    if "JAKARTA" in nama
                    else nama
                )
            )

        return res

    except:
        return None

geojson = load_geojson()

col_y = "Y (TREE COVER LOSS- Ha)"

cols_x = {
    "X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)",
    "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"
}

# --- 5. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":

    st.markdown(
        "<br><br><h1 class='main-title'>🌳 ForestGuard</h1>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown(
            "<div class='menu-card'><h1>🛰️</h1><h3>Dashboard Spasial</h3></div>",
            unsafe_allow_html=True
        )

        if st.button("Buka Dashboard"):
            set_page("Dashboard")
            st.rerun()

    with c2:

        st.markdown(
            "<div class='menu-card'><h1>🧪</h1><h3>Prediksi MERF</h3></div>",
            unsafe_allow_html=True
        )

        if st.button("Mulai Prediksi"):
            set_page("Prediksi")
            st.rerun()

    with c3:

        st.markdown(
            "<div class='menu-card'><h1>📖</h1><h3>Info Penelitian</h3></div>",
            unsafe_allow_html=True
        )

        if st.button("Lihat Penelitian"):
            set_page("Penelitian")
            st.rerun()

else:

    if st.button("⬅️ KEMBALI KE PORTAL"):
        set_page("Portal")
        st.rerun()

    st.markdown("---")

    # =========================
    # HALAMAN PREDIKSI
    # =========================
    elif st.session_state.page == "Prediksi":

        st.markdown(
            "<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: ESTIMASI RISIKO DEFORESTASI & MONITORING JANGKA PENDEK</h3>",
            unsafe_allow_html=True
        )

        with st.expander("📥 TAMBAH DATA AKTUAL (UPDATE TAHUNAN)"):

            uploaded_file = st.file_uploader(
                "Upload CSV Data:",
                type="csv"
            )

            if uploaded_file and st.button("Update Data & Grafik"):

                new_df = pd.read_csv(uploaded_file)

                new_df.columns = new_df.columns.str.strip()

                if 'PROVINSI' in new_df.columns:
                    new_df['PROVINSI'] = (
                        new_df['PROVINSI']
                        .astype(str)
                        .str.strip()
                        .str.upper()
                    )

                st.session_state.df = pd.concat(
                    [st.session_state.df, new_df],
                    ignore_index=True
                )

                st.success("✅ Data berhasil diperbarui!")

                st.rerun()

        df = st.session_state.df

        last_yr = df['TAHUN'].max()

        prov_target = st.selectbox(
            "Pilih Wilayah untuk Grafik Tren:",
            sorted(df['PROVINSI'].unique())
        )

        st.markdown("---")

        cl, cr = st.columns([1, 1.3])

        # =========================
        # TABEL ESTIMASI
        # =========================
        with cl:

            st.markdown(
                f"<h4 style='color: #facc15;'>📄 TABEL ESTIMASI ({last_yr+1} - {last_yr+3})</h4>",
                unsafe_allow_html=True
            )

            national_preds = []

            for p in sorted(df['PROVINSI'].unique()):

                prov_df = df[df['PROVINSI'] == p].sort_values('TAHUN')

                last_val = prov_df.iloc[-1][col_y]

                for i in range(1, 4):

                    pred_val = round(last_val * (1.03 ** i), 2)

                    national_preds.append({
                        "Provinsi": p,
                        "Tahun": last_yr + i,
                        "Estimasi Loss (Ha)": pred_val
                    })

            df_preds = pd.DataFrame(national_preds)

            st.dataframe(
                df_preds,
                use_container_width=True,
                hide_index=True,
                height=500
            )

        # =========================
        # GRAFIK TREN
        # =========================
        with cr:

            st.markdown(
                "<h4 style='color: #facc15;'>📊 TREN KEHILANGAN TUTUPAN POHON</h4>",
                unsafe_allow_html=True
            )

            hist = (
                df[df['PROVINSI'] == prov_target]
                .sort_values('TAHUN')
                .copy()
            )

            hist['Status'] = 'Data Aktual'

            future_years = [last_yr + 1, last_yr + 2, last_yr + 3]

            future_values = [
                hist[col_y].iloc[-1] * (1.03 ** i)
                for i in range(1, 4)
            ]

            future = pd.DataFrame({
                'TAHUN': future_years,
                col_y: future_values,
                'Status': 'Prediksi'
            })

            last_actual = hist.iloc[[-1]].copy()

            last_actual['Status'] = 'Prediksi'

            df_plot = pd.concat([
                hist[['TAHUN', col_y, 'Status']],
                last_actual[['TAHUN', col_y, 'Status']],
                future
            ])

            fig_pred = px.line(
                df_plot,
                x='TAHUN',
                y=col_y,
                color='Status',
                markers=True,
                color_discrete_map={
                    'Data Aktual': '#22c55e',
                    'Prediksi': '#ef4444'
                }
            )

            fig_pred.update_layout(
                height=500,
                paper_bgcolor='white',
                plot_bgcolor='white',
                xaxis_title='Tahun',
                yaxis_title='Y (TREE COVER LOSS - Ha)',
                legend_title='Keterangan'
            )

            st.plotly_chart(
                fig_pred,
                use_container_width=True
            )
