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

    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"

    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(r"\s+", " ", regex=True)

    df['PROVINSI'] = (
        df['PROVINSI']
        .astype(str)
        .str.strip()
        .str.upper()
    )

    st.session_state.df = df

# =========================================================
# NAVIGASI
# =========================================================

def set_page(name):
    st.session_state.page = name

# =========================================================
# DETEKSI KOLOM
# =========================================================

all_cols = st.session_state.df.columns.tolist()

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
# CSS
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
    linear-gradient(rgba(0,0,0,0.82), rgba(0,0,0,0.82)),
    url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop');

    background-size: cover;
    background-position: center;
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
    background: rgba(255,255,255,0.97);
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
# GEOJSON
# =========================================================

@st.cache_data
def load_geojson():

    try:

        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"

        res = requests.get(url).json()

        for feature in res['features']:

            nama = str(
                feature['properties'].get('Propinsi', '')
            ).strip().upper()

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
                "PREDIKSI": round(pred, 2),
                "STATUS": "Prediksi"
            })

            current_y = pred

            for key in x_hist.keys():

                x_hist[key].append(ma3)

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
# HALAMAN PREDIKSI
# =========================================================

elif st.session_state.page == "Prediksi":

    st.markdown("""
    <h1 style='color:#fde047;'>
    🌍 PREDIKSI RISIKO DEFORESTASI
    </h1>
    """, unsafe_allow_html=True)

    df = st.session_state.df

    st.markdown("## 📥 Upload Data Aktual Baru")

    uploaded_file = st.file_uploader(
        "Upload file CSV",
        type="csv"
    )

    if uploaded_file is not None:

        new_df = pd.read_csv(uploaded_file)

        new_df.columns = (
            new_df.columns
            .str.strip()
        )

        new_df.columns = (
            new_df.columns
            .str.replace(
                r"\s+",
                " ",
                regex=True
            )
        )

        new_df['PROVINSI'] = (
            new_df['PROVINSI']
            .astype(str)
            .str.upper()
            .str.strip()
        )

        tahun_baru = new_df['TAHUN'].unique()

        df = df[
            ~df['TAHUN'].isin(
                tahun_baru
            )
        ]

        df = pd.concat(
            [df, new_df],
            ignore_index=True
        )

        st.session_state.df = df

        st.success(
            f"✅ Data aktual tahun {tahun_baru[0]} berhasil diperbarui."
        )

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

    # =====================================================
    # RINGKASAN
    # =====================================================

    st.markdown("## 📊 Ringkasan Wilayah")

    s1, s2, s3 = st.columns(3)

    s1.metric(
        "Tahun Aktual Terakhir",
        latest_year
    )

    s2.metric(
        "Loss Aktual Terakhir",
        f"{latest_value:,.2f}"
    )

    s3.metric(
        "Rata-rata Loss",
        f"{avg_loss:,.2f}"
    )

    st.markdown("---")

    # =====================================================
    # MONITORING RISIKO
    # =====================================================

    pred_awal = pred_prov['PREDIKSI'].iloc[0]
    pred_akhir = pred_prov['PREDIKSI'].iloc[-1]

    change_percent = (
        (
            pred_akhir - pred_awal
        ) / pred_awal
    ) * 100

    if pred_akhir > pred_awal:
        trend_text = "↑ Naik"
    else:
        trend_text = "↓ Turun"

    if pred_akhir < 5000:
        risk_status = "Rendah 🟢"
    elif pred_akhir < 15000:
        risk_status = "Sedang 🟡"
    else:
        risk_status = "Tinggi 🔴"

    # =====================================================
    # TABEL DAN GRAFIK
    # =====================================================

    cl, cr = st.columns([1,1.5])

    with cl:

        st.markdown("""
        <h3 style='color:#fde047;'>
        📄 Hasil Prediksi
        </h3>
        """, unsafe_allow_html=True)

        st.dataframe(
            pred_prov,
            use_container_width=True,
            hide_index=True
        )

        st.markdown("""
        <br>
        <h3 style='color:#ffffff;'>
        📋 Monitoring Risiko Deforestasi
        </h3>
        """, unsafe_allow_html=True)

        monitor_df = pd.DataFrame({
            "Indikator": [
                "Tren Prediksi",
                "Status Risiko",
                "Perubahan 3 Tahun",
                "Prediksi Tahun Akhir"
            ],
            "Nilai": [
                trend_text,
                risk_status,
                f"{change_percent:.2f}%",
                f"{pred_akhir:,.2f}"
            ]
        })

        st.table(monitor_df)

    with cr:

        st.markdown("""
        <h3 style='color:#fde047;'>
        📈 Aktual vs Prediksi
        </h3>
        """, unsafe_allow_html=True)

        aktual = pd.DataFrame({
            'TAHUN': hist['TAHUN'],
            'LOSS': hist[col_y],
            'Status': 'Aktual'
        })

        prediksi_awal = pd.DataFrame({
            'TAHUN': [latest_year],
            'LOSS': [latest_value],
            'Status': ['Prediksi']
        })

        prediksi_lanjutan = pd.DataFrame({
            'TAHUN': pred_prov['TAHUN'],
            'LOSS': pred_prov['PREDIKSI'],
            'Status': 'Prediksi'
        })

        prediksi = pd.concat([
            prediksi_awal,
            prediksi_lanjutan
        ])

        gabung = pd.concat([
            aktual,
            prediksi
        ])

        fig_pred = px.line(
            gabung,
            x='TAHUN',
            y='LOSS',
            color='Status',
            markers=True,
            color_discrete_map={
                'Aktual': '#22c55e',
                'Prediksi': '#ef4444'
            }
        )

        fig_pred.update_layout(
            paper_bgcolor='white',
            plot_bgcolor='white',
            height=550
        )

        st.plotly_chart(
            fig_pred,
            use_container_width=True
        )

