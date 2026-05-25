# =========================================================
# IMPORT
# =========================================================

import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

from merf.merf import MERF

# =========================================================
# KONFIGURASI HALAMAN
# =========================================================

st.set_page_config(
    page_title="ForestGuard",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# =========================================================
# SESSION STATE
# =========================================================

if 'page' not in st.session_state:
    st.session_state.page = "Portal"

if 'df' not in st.session_state:
    st.session_state.df = None

def set_page(name):
    st.session_state.page = name

# =========================================================
# CSS ASLI DARI SYNTAX PERTAMA
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
    linear-gradient(rgba(0,0,0,0.45), rgba(0,0,0,0.45)),
    url('https://raw.githubusercontent.com/tanti1i/jamsicx-apps/main/404268504069646243.jpg.jpeg');

    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
}

.main-title {
    font-size: 5rem !important;
    font-family: 'Arial Black';
    background: linear-gradient(to bottom, #fde047 0%, #facc15 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-weight: 900;
}

.menu-card {
    background: rgba(255,255,255,0.10);
    border-radius: 28px;
    padding: 40px;
    height: 320px;
    text-align: center;
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.1);
}

div.stButton > button {
    background: linear-gradient(135deg,#15803d,#166534) !important;
    color: white !important;
    border-radius: 12px;
    border: 1px solid #fde047 !important;
    width: 100%;
    font-weight: bold;
}

h1,h2,h3,h4,h5,h6,p,label,span,li,div {
    color: #f8fafc !important;
}

[data-testid="stMetricValue"] {
    color: #fde047 !important;
    font-weight: 800;
}

.stPlotlyChart {
    background: rgba(15,35,20,0.45);
    border-radius: 20px;
    padding: 12px;
}

[data-testid="stDataFrame"] {
    background: rgba(255,255,255,0.97);
    border-radius: 18px;
    padding: 5px;
}

.research-card {
    background: rgba(15,23,42,0.7);
    border-radius: 18px;
    padding: 25px;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# LOAD DATA
# =========================================================

@st.cache_data
def load_internal_data():

    CSV_URL = "https://raw.githubusercontent.com/tanti1i/jamsicx-apps/refs/heads/main/data_jamsicx.csv"

    df = pd.read_csv(CSV_URL)

    df.columns = df.columns.str.strip()

    df['PROVINSI'] = (
        df['PROVINSI']
        .astype(str)
        .str.strip()
        .str.upper()
    )

    return df

if st.session_state.df is None:
    st.session_state.df = load_internal_data()

df = st.session_state.df

# =========================================================
# DETEKSI KOLOM
# =========================================================

all_cols = df.columns.tolist()

def cari_kolom(keyword):

    for col in all_cols:

        if keyword.lower() in col.lower():
            return col

    return None

col_y = cari_kolom("TREE COVER LOSS")

cols_x = {
    "X1": cari_kolom("LUAS PENUTUPAN LAHAN"),
    "X2": cari_kolom("KEBAKARAN HUTAN"),
    "X3": cari_kolom("TOTAL LUAS TANAMAN"),
    "X4": cari_kolom("KEPADATAN PENDUDUK"),
    "X5": cari_kolom("TOTAL POPULASI TERNAK"),
    "X6": cari_kolom("PDRB PERTAMBANGAN")
}

# =========================================================
# PREPARE DATA
# =========================================================

@st.cache_data
def prepare_data(df):

    data = df.copy()

    data = data.sort_values(
        ['PROVINSI', 'TAHUN']
    )

    data['Y_lag1'] = (
        data
        .groupby('PROVINSI')[col_y]
        .shift(1)
    )

    for key, col in cols_x.items():

        if col is not None:

            data[f'{key}_ma3'] = (
                data
                .groupby('PROVINSI')[col]
                .transform(
                    lambda x:
                    x.rolling(3, min_periods=1).mean()
                )
            )

    data = data.dropna().copy()

    data['Y_log'] = np.log1p(data[col_y])

    data['Y_lag1_log'] = np.log1p(data['Y_lag1'])

    feature_cols = ['Y_lag1_log']

    for key in cols_x.keys():

        if cols_x[key] is not None:

            new_col = f'{key}_ma3_log'

            data[new_col] = np.log1p(
                data[f'{key}_ma3']
            )

            feature_cols.append(new_col)

    return data, feature_cols

# =========================================================
# TRAIN MODEL
# =========================================================

@st.cache_resource
def load_or_train_model(df):

    data, feature_cols = prepare_data(df)

    train_data = data[data['TAHUN'] <= 2021]

    X_train = train_data[feature_cols]
    y_train = train_data['Y_log']

    Z_train = np.ones((len(train_data), 1))

    clusters_train = train_data["PROVINSI"]

    model = MERF()

    model.fit(
        X_train,
        Z_train,
        clusters_train,
        y_train
    )

    return model, feature_cols

# =========================================================
# FORECASTING
# =========================================================

def forecast_all_provinces(
    model,
    feature_cols,
    df,
    n_years=3
):

    data = df.copy()

    hasil_semua = []

    provinsi_list = sorted(
        data['PROVINSI'].unique()
    )

    for provinsi in provinsi_list:

        prov_data = (
            data[data['PROVINSI'] == provinsi]
            .sort_values('TAHUN')
        )

        latest = prov_data.iloc[-1]

        current_y = latest[col_y]

        current_year = int(
            latest['TAHUN']
        )

        x_hist = {}

        for key, col in cols_x.items():

            if col is not None:

                x_hist[key] = (
                    prov_data[col]
                    .tail(3)
                    .tolist()
                )

        for i in range(1, n_years + 1):

            tahun = current_year + i

            future_input = {
                'Y_lag1_log': np.log1p(current_y)
            }

            for key in x_hist.keys():

                ma3 = np.mean(
                    x_hist[key][-3:]
                )

                future_input[
                    f'{key}_ma3_log'
                ] = np.log1p(ma3)

            X_future = pd.DataFrame([
                future_input
            ])

            X_future = X_future[
                feature_cols
            ]

            Z_future = np.ones((1,1))

            cluster_future = pd.Series(
                [provinsi]
            )

            pred_log = model.predict(
                X_future,
                Z_future,
                cluster_future
            )[0]

            pred = np.expm1(pred_log)

            hasil_semua.append({
                "PROVINSI": provinsi,
                "TAHUN": tahun,
                "PREDIKSI": round(pred, 2)
            })

            current_y = pred

    return pd.DataFrame(hasil_semua)

# =========================================================
# PORTAL
# =========================================================

if st.session_state.page == "Portal":

    st.markdown(
        "<br><br><h1 class='main-title'>🌳 ForestGuard</h1>",
        unsafe_allow_html=True
    )

    c1, c2, c3 = st.columns(3)

    with c1:

        st.markdown("""
        <div class='menu-card'>
        <h1>🛰️</h1>
        <h3>Dashboard Spasial</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Buka Dashboard"):
            set_page("Dashboard")
            st.rerun()

    with c2:

        st.markdown("""
        <div class='menu-card'>
        <h1>🧪</h1>
        <h3>Prediksi MERF</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Mulai Prediksi"):
            set_page("Prediksi")
            st.rerun()

    with c3:

        st.markdown("""
        <div class='menu-card'>
        <h1>📖</h1>
        <h3>Info Penelitian</h3>
        </div>
        """, unsafe_allow_html=True)

        if st.button("Lihat Penelitian"):
            set_page("Penelitian")
            st.rerun()

# =========================================================
# DASHBOARD ASLI
# =========================================================

elif st.session_state.page == "Dashboard":

    st.title("📊 Dashboard Spasial")

    st.info("Bagian dashboard tetap dari syntax pertama")

# =========================================================
# PREDIKSI MERF
# =========================================================

elif st.session_state.page == "Prediksi":

    st.header("📈 Prediksi Deforestasi MERF")

    uploaded_file = st.file_uploader(
        "Upload file CSV",
        type="csv"
    )

    if uploaded_file is not None:

        new_df = pd.read_csv(uploaded_file)

        df = pd.concat(
            [df, new_df],
            ignore_index=True
        )

        st.session_state.df = df

        st.success("✅ Data berhasil diperbarui")

    with st.spinner(
        "Menjalankan model MERF..."
    ):

        model, feature_cols = (
            load_or_train_model(df)
        )

    pred_global = forecast_all_provinces(
        model,
        feature_cols,
        df,
        n_years=3
    )

    prov_target = st.selectbox(
        "📍 Pilih Provinsi",
        sorted(df['PROVINSI'].unique())
    )

    pred_prov = pred_global[
        pred_global['PROVINSI'] == prov_target
    ]

    hist = (
        df[df['PROVINSI'] == prov_target]
        .sort_values('TAHUN')
    )

    latest_year = hist['TAHUN'].max()

    latest_value = hist[col_y].iloc[-1]

    avg_loss = hist[col_y].mean()

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Tahun Aktual",
        latest_year
    )

    s2.metric(
        "Loss Terakhir",
        f"{latest_value:,.2f}"
    )

    s3.metric(
        "Rata-rata",
        f"{avg_loss:,.2f}"
    )

    cl, cr = st.columns([1,1.5])

    with cl:

        st.dataframe(
            pred_prov,
            use_container_width=True,
            hide_index=True
        )

    with cr:

        aktual = pd.DataFrame({
            'TAHUN': hist['TAHUN'],
            'LOSS': hist[col_y],
            'Status': 'Aktual'
        })

        prediksi = pd.DataFrame({
            'TAHUN': pred_prov['TAHUN'],
            'LOSS': pred_prov['PREDIKSI'],
            'Status': 'Prediksi'
        })

        gabung = pd.concat([
            aktual,
            prediksi
        ])

        fig_pred = px.line(
            gabung,
            x='TAHUN',
            y='LOSS',
            color='Status',
            markers=True
        )

        fig_pred.update_layout(
            paper_bgcolor='rgba(15,35,20,0.65)',
            plot_bgcolor='rgba(25,50,30,0.55)',
            font=dict(color='#ffffff'),
            height=550
        )

        st.plotly_chart(
            fig_pred,
            use_container_width=True
        )

# =========================================================
# INFO PENELITIAN ASLI
# =========================================================

elif st.session_state.page == "Penelitian":

    st.markdown("""
    <div class='research-card'>
    <h2>📖 Info Penelitian</h2>
    <p>
    Halaman penelitian tetap dari syntax pertama.
    </p>
    </div>
    """, unsafe_allow_html=True)
