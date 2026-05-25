# =========================================================
# FORESTGUARD - FULL MERGED VERSION
# Dashboard + Penelitian (Syntax Pertama)
# Prediksi MERF (Syntax Kedua)
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
    page_title="I-JAMCSIIX - Eco Intelligence",
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
# CSS PREMIUM
# =========================================================

st.markdown("""
<style>

.stApp {
    background:
    linear-gradient(rgba(0,0,0,0.35), rgba(0,0,0,0.35)),
    url('https://raw.githubusercontent.com/tanti1i/jamsicx-apps/main/404268504069646243.jpg.jpeg');

    background-size: cover;
    background-position: center top;
    background-attachment: fixed;
    background-repeat: no-repeat;

    color: white;
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
    height: 340px;
    text-align: center;
    backdrop-filter: blur(18px);
    border: 1px solid rgba(255,255,255,0.1);

    display:flex;
    flex-direction:column;
    justify-content:center;
}

.stPlotlyChart {
    background: rgba(15,35,20,0.45);
    backdrop-filter: blur(12px);
    border-radius: 20px;
    padding: 15px;
    border: 1px solid rgba(250,204,21,0.15);
}

[data-testid="stMetricValue"] {
    color: #fde047 !important;
    font-weight: 800;
}

[data-testid="stMetricLabel"] {
    color: white !important;
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
    border: 1px solid rgba(250,204,21,0.15);
}

.stSelectbox div[data-baseweb="select"] {
    background-color: white !important;
    border-radius: 10px;
}

.stSelectbox div[data-baseweb="select"] div {
    color: black !important;
    font-weight: 600;
}

.stSelectbox label p {
    color: #facc15 !important;
    font-weight: bold;
}

[data-testid="stFileUploader"] label p {
    color: #facc15 !important;
    font-weight: bold;
}

[data-testid="stFileUploader"] button {
    background-color: #15803d !important;
    color: white !important;
    border: 1px solid #facc15 !important;
}

h1,h2,h3,h4,h5,h6,p,label,span,li,div {
    color: #f8fafc;
}

div.stButton > button {
    background: linear-gradient(135deg,#15803d,#166534) !important;
    color: white !important;
    border-radius: 12px;
    border: 1px solid #fde047 !important;
    width: 100%;
    font-weight: bold;
}

</style>
""", unsafe_allow_html=True)

# =========================================================
# DEFINISI KOLOM
# =========================================================

col_y = "Y (TREE COVER LOSS- Ha)"

cols_x = {
    "X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)",
    "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"
}

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

    df['TAHUN'] = df['TAHUN'].astype(int)

    for col in [col_y] + list(cols_x.values()):

        if col in df.columns:

            df[col] = pd.to_numeric(
                df[col]
                .astype(str)
                .str.replace(',', '')
                .str.strip(),
                errors='coerce'
            )

    return df

if st.session_state.df is None:
    st.session_state.df = load_internal_data()

# =========================================================
# GEOJSON
# =========================================================

@st.cache_data

def load_geojson():

    try:

        url = "https://raw.githubusercontent.com/superpikar/indonesia-geojson/master/indonesia-province-simple.json"

        res = requests.get(url).json()

        for feature in res['features']:

            nama = str(feature['properties'].get('Propinsi', '')).strip().upper()

            if "ACEH" in nama:
                key = "ACEH"
            elif "BANTEN" in nama:
                key = "BANTEN"
            elif "JAKARTA" in nama:
                key = "DKI JAKARTA"
            elif "YOGYAKARTA" in nama:
                key = "DI YOGYAKARTA"
            elif "BANGKA" in nama:
                key = "BANGKA BELITUNG"
            elif "KEPULAUAN RIAU" in nama:
                key = "KEPULAUAN RIAU"
            else:
                key = nama

            feature['properties']['PROV_KEY'] = key

        return res

    except:
        return None

geojson = load_geojson()

# =========================================================
# PREPARE DATA MERF
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

        if col is not None and col in data.columns:

            data[f'{key}_ma3'] = (
                data
                .groupby('PROVINSI')[col]
                .transform(
                    lambda x:
                    x.rolling(3, min_periods=1).mean()
                )
            )

    data = data.dropna(subset=['Y_lag1']).copy()

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
# TRAIN MODEL MERF
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
# FORECAST
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

        current_year = int(latest['TAHUN'])

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

                ma3 = np.mean(x_hist[key][-3:])

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

            cluster_future = pd.Series([provinsi])

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

    st.markdown("<br>", unsafe_allow_html=True)

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
# HALAMAN LAIN
# =========================================================

else:

    if st.button("⬅️ KEMBALI KE PORTAL"):
        set_page("Portal")
        st.rerun()

    st.markdown("---")

    # =====================================================
    # DASHBOARD
    # =====================================================

    if st.session_state.page == "Dashboard":

        df = st.session_state.df

        st.markdown("""
        <h2 style='color:#facc15;'>
        📊 Dashboard Deskriptif Spasial
        </h2>
        """, unsafe_allow_html=True)

        tahun = st.selectbox(
            "📅 Pilih Tahun",
            sorted(df['TAHUN'].unique(), reverse=True)
        )

        df_tahun = df[df['TAHUN'] == tahun]

        fig_map = px.choropleth(
            df_tahun,
            geojson=geojson,
            locations="PROVINSI",
            featureidkey="properties.PROV_KEY",
            color=col_y,
            color_continuous_scale="YlOrRd",
            hover_name="PROVINSI"
        )

        fig_map.update_geos(
            visible=False,
            fitbounds="locations"
        )

        fig_map.update_layout(
            paper_bgcolor='rgba(15,35,20,0.65)',
            plot_bgcolor='rgba(15,35,20,0.65)',
            font=dict(color='white'),
            height=600
        )

        st.plotly_chart(
            fig_map,
            use_container_width=True
        )

        top10 = (
            df_tahun
            .nlargest(10, col_y)
        )

        fig_bar = px.bar(
            top10,
            x=col_y,
            y='PROVINSI',
            orientation='h',
            color=col_y,
            color_continuous_scale="YlOrRd"
        )

        fig_bar.update_layout(
            paper_bgcolor='rgba(15,35,20,0.65)',
            plot_bgcolor='rgba(15,35,20,0.65)',
            font=dict(color='white'),
            height=450
        )

        st.plotly_chart(
            fig_bar,
            use_container_width=True
        )

    # =====================================================
    # PREDIKSI MERF
    # =====================================================

    elif st.session_state.page == "Prediksi":

        df = st.session_state.df

        st.markdown("""
        <h1 style='color:#facc15; font-weight:800;'>
        🌍 Prediksi Risiko Deforestasi MERF
        </h1>
        """, unsafe_allow_html=True)

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

            new_df['PROVINSI'] = (
                new_df['PROVINSI']
                .astype(str)
                .str.upper()
                .str.strip()
            )

            for col in [col_y] + list(cols_x.values()):

                if col in new_df.columns:

                    new_df[col] = pd.to_numeric(
                        new_df[col],
                        errors='coerce'
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
            "🧠 Menjalankan model MERF..."
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

        with s1:
            st.metric(
                "📅 Tahun Aktual Terakhir",
                latest_year
            )

        with s2:
            st.metric(
                "🌲 Loss Aktual Terakhir",
                f"{latest_value:,.2f}"
            )

        with s3:
            st.metric(
                "📊 Rata-rata Loss",
                f"{avg_loss:,.2f}"
            )

        st.markdown("---")

        pred_awal = pred_prov['PREDIKSI'].iloc[0]
        pred_akhir = pred_prov['PREDIKSI'].iloc[-1]

        change_percent = (
            (
                pred_akhir - pred_awal
            ) / pred_awal
        ) * 100

        trend_text = (
            "↑ Naik"
            if pred_akhir > pred_awal
            else "↓ Turun"
        )

        if pred_akhir < 5000:
            risk_status = "Rendah 🟢"
        elif pred_akhir < 15000:
            risk_status = "Sedang 🟡"
        else:
            risk_status = "Tinggi 🔴"

        cl, cr = st.columns([1,1.5])

        with cl:

            st.markdown("""
            <h3 style='color:#facc15;'>
            📄 Hasil Prediksi
            </h3>
            """, unsafe_allow_html=True)

            st.dataframe(
                pred_prov,
                use_container_width=True,
                hide_index=True
            )

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

            st.markdown("""
            <h3 style='color:#facc15;'>
            📋 Monitoring Risiko
            </h3>
            """, unsafe_allow_html=True)

            st.table(monitor_df)

        with cr:

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
                paper_bgcolor='rgba(15,35,20,0.65)',
                plot_bgcolor='rgba(25,50,30,0.55)',
                font=dict(color='#cbd5e1'),
                height=550
            )

            st.plotly_chart(
                fig_pred,
                use_container_width=True
            )

    # =====================================================
    # PENELITIAN
    # =====================================================

    elif st.session_state.page == "Penelitian":

        st.markdown("""
        <h1 style='color:#facc15; text-align:center;'>
        📖 Info Penelitian
        </h1>
        """, unsafe_allow_html=True)

        c1, c2 = st.columns(2)

        with c1:

            st.markdown("""
            <div class='research-card'>
            <h3>🎯 Tujuan Penelitian</h3>

            <p>
            Penelitian ini bertujuan membangun sistem
            prediksi deforestasi berbasis Mixed Effects
            Random Forest (MERF) untuk menganalisis
            pola spasial dan temporal deforestasi Indonesia.
            </p>

            <p>
            Sistem ForestGuard dirancang untuk membantu
            visualisasi data spasial serta prediksi
            risiko deforestasi antar provinsi.
            </p>

            </div>
            """, unsafe_allow_html=True)

        with c2:

            st.markdown("""
            <div class='research-card'>

            <h3>🤖 Metode MERF</h3>

            <p>
            MERF menggabungkan kemampuan Random Forest
            dalam memodelkan hubungan non-linear dengan
            efek acak dari Linear Mixed Model untuk
            menangani data longitudinal antar provinsi.
            </p>

            <p style='text-align:center;
            font-size:1.4rem;
            color:#fde047;'>

            yᵢ = f(Xᵢ) + Zᵢbᵢ + εᵢ

            </p>

            </div>
            """, unsafe_allow_html=True)

# =========================================================
# END
# =========================================================
