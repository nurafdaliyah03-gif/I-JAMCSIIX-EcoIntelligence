# ForestGuard — Full Streamlit Syntax (Konsep MERF Deployment)

```python
import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np
import joblib

from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import (
    mean_absolute_error,
    mean_squared_error,
    r2_score
)

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

    # RAPIIKAN NAMA KOLOM
    df.columns = df.columns.str.strip()
    df.columns = df.columns.str.replace(r"\s+", " ", regex=True)

    # RAPIIKAN PROVINSI
    df['PROVINSI'] = (
        df['PROVINSI']
        .astype(str)
        .str.strip()
        .str.upper()
    )

    st.session_state.df = df


def set_page(name):
    st.session_state.page = name

# =========================================================
# AUTO DETECT KOLOM
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
    linear-gradient(rgba(0,0,0,0.7), rgba(0,0,0,0.7)),
    url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop');

    background-size: cover;
    background-position: center;
    background-attachment: fixed;
    color: white;
}

.main-title {
    font-size: 5rem !important;
    font-family: 'Arial Black', sans-serif;
    background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    text-align: center;
    font-weight: 900 !important;
}

.menu-card {
    background: rgba(255,255,255,0.1);
    backdrop-filter: blur(15px);
    border-radius: 30px;
    padding: 40px;
    text-align: center;
    height: 330px;
    display: flex;
    flex-direction: column;
    justify-content: center;
}

.stPlotlyChart {
    background-color: white !important;
    border-radius: 20px;
    padding: 15px;
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
    border-radius: 16px;
    padding: 25px;
    margin-bottom: 20px;
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

    # =====================================================
    # LAG Y
    # =====================================================

    data['Y_lag1'] = (
        data
        .groupby('PROVINSI')[col_y]
        .shift(1)
    )

    # =====================================================
    # LAG X
    # =====================================================

    for key, col in cols_x.items():

        data[f'{key}_lag1'] = (
            data
            .groupby('PROVINSI')[col]
            .shift(1)
        )

    # =====================================================
    # MOVING AVERAGE 3 TAHUN
    # =====================================================

    for key, col in cols_x.items():

        data[f'{key}_ma3'] = (
            data
            .groupby('PROVINSI')[col]
            .transform(
                lambda x:
                x.rolling(3, min_periods=1).mean()
            )
        )

    data = data.dropna().copy()

    # =====================================================
    # LOG TRANSFORM
    # =====================================================

    data['Y_log'] = np.log1p(data[col_y])

    feature_cols = []

    data['Y_lag1_log'] = np.log1p(data['Y_lag1'])

    feature_cols.append('Y_lag1_log')

    for key in cols_x.keys():

        new_col = f'{key}_ma3_log'

        data[new_col] = np.log1p(
            data[f'{key}_ma3']
        )

        feature_cols.append(new_col)

    return data, feature_cols

# =========================================================
# TRAIN GLOBAL MODEL
# =========================================================

@st.cache_resource

def load_or_train_model(df):

    try:

        model = joblib.load("forestguard_model.pkl")

        data, feature_cols = prepare_data(df)

        metrics = {
            "RMSE": 0,
            "MAE": 0,
            "R2": 0
        }

        return model, feature_cols, metrics

    except:

        data, feature_cols = prepare_data(df)

        train_data = data[data['TAHUN'] <= 2021]
        test_data = data[data['TAHUN'] > 2021]

        X_train = train_data[feature_cols]
        y_train = train_data['Y_log']

        X_test = test_data[feature_cols]
        y_test = test_data['Y_log']

        model = RandomForestRegressor(
            n_estimators=500,
            max_depth=10,
            random_state=42
        )

        model.fit(X_train, y_train)

        # SAVE MODEL
        joblib.dump(model, "forestguard_model.pkl")

        pred_test_log = model.predict(X_test)

        pred_test = np.expm1(pred_test_log)

        actual_test = np.expm1(y_test)

        rmse = np.sqrt(
            mean_squared_error(
                actual_test,
                pred_test
            )
        )

        mae = mean_absolute_error(
            actual_test,
            pred_test
        )

        r2 = r2_score(
            actual_test,
            pred_test
        )

        metrics = {
            "RMSE": rmse,
            "MAE": mae,
            "R2": r2
        }

        return model, feature_cols, metrics

# =========================================================
# GLOBAL FORECASTING
# =========================================================

@st.cache_data

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

            x_hist[key] = (
                prov_data[col]
                .tail(3)
                .tolist()
            )

        # =============================================
        # RECURSIVE FORECASTING
        # =============================================

        for i in range(1, n_years + 1):

            tahun = current_year + i

            future_input = {
                'Y_lag1_log': np.log1p(current_y)
            }

            for key in cols_x.keys():

                ma3 = np.mean(x_hist[key][-3:])

                future_input[
                    f'{key}_ma3_log'
                ] = np.log1p(ma3)

            X_future = pd.DataFrame([
                future_input
            ])

            pred_log = model.predict(X_future)[0]

            pred = np.expm1(pred_log)

            hasil_semua.append({
                "PROVINSI": provinsi,
                "TAHUN": tahun,
                "PREDIKSI": round(pred, 2),
                "STATUS": "Prediksi"
            })

            current_y = pred

            # UPDATE MOVING WINDOW
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

        st.header("📊 Dashboard Deskriptif Spasial")

        col1, col2 = st.columns(2)

        sel_thn = col1.selectbox(
            "Pilih Tahun",
            sorted(df['TAHUN'].unique(), reverse=True)
        )

        sel_prov = col2.selectbox(
            "Fokus Wilayah",
            ["Semua Provinsi"] +
            sorted(df['PROVINSI'].unique())
        )

        df_filt = df[df['TAHUN'] == sel_thn]

        cl, cr = st.columns([1.1, 0.9])

        with cl:

            if geojson:

                data_peta = (
                    df_filt
                    if sel_prov == "Semua Provinsi"
                    else df_filt[
                        df_filt['PROVINSI'] == sel_prov
                    ]
                )

                fig = px.choropleth(
                    data_peta,
                    geojson=geojson,
                    locations="PROVINSI",
                    featureidkey="properties.PROV_KEY",
                    color=col_y,
                    color_continuous_scale="RdYlGn_r"
                )

                fig.update_geos(
                    fitbounds="locations"
                    if sel_prov != "Semua Provinsi"
                    else False,
                    visible=False
                )

                fig.update_layout(
                    paper_bgcolor='white',
                    height=500
                )

                st.plotly_chart(
                    fig,
                    use_container_width=True
                )

        with cr:

            var_x = st.selectbox(
                "Pilih Variabel X",
                list(cols_x.keys())
            )

            fig2 = px.scatter(
                df_filt,
                x=cols_x[var_x],
                y=col_y,
                color=col_y,
                trendline="ols"
            )

            fig2.update_layout(
                paper_bgcolor='white'
            )

            st.plotly_chart(
                fig2,
                use_container_width=True
            )

    # =====================================================
    # PREDIKSI
    # =====================================================

    elif st.session_state.page == "Prediksi":

        st.markdown("""
        <h2 style='color:#facc15;'>
        🌍 PREDIKSI RISIKO DEFORESTASI
        </h2>
        """, unsafe_allow_html=True)

        df = st.session_state.df

        # =================================================
        # UPLOAD DATA BARU
        # =================================================

        with st.expander("📥 Upload Data Aktual Baru"):

            uploaded_file = st.file_uploader(
                "Upload CSV Data Aktual",
                type="csv"
            )

            if uploaded_file:

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

                st.success(
                    "Data berhasil ditambahkan"
                )

                st.session_state.df = pd.concat(
                    [df, new_df],
                    ignore_index=True
                )

                df = st.session_state.df

        # =================================================
        # LOAD MODEL GLOBAL
        # =================================================

        with st.spinner(
            "Menjalankan model global ForestGuard..."
        ):

            model, feature_cols, metrics = (
                load_or_train_model(df)
            )

        # =================================================
        # METRICS
        # =================================================

        st.markdown("### 📌 Evaluasi Model")

        m1, m2, m3 = st.columns(3)

        m1.metric(
            "RMSE",
            f"{metrics['RMSE']:.2f}"
        )

        m2.metric(
            "MAE",
            f"{metrics['MAE']:.2f}"
        )

        m3.metric(
            "R²",
            f"{metrics['R2']:.3f}"
        )

        st.markdown("---")

        # =================================================
        # FORECAST GLOBAL
        # =================================================

        last_year = int(df['TAHUN'].max())

        pred_global = forecast_all_provinces(
            model,
            feature_cols,
            df,
            n_years=3
        )

        # =================================================
        # FILTER VISUAL
        # =================================================

        prov_target = st.selectbox(
            "Pilih Provinsi",
            sorted(df['PROVINSI'].unique())
        )

        pred_prov = pred_global[
            pred_global['PROVINSI'] == prov_target
        ]

        cl, cr = st.columns([1, 1.4])

        with cl:

            st.markdown("""
            <h4 style='color:#facc15;'>
            📄 Tabel Estimasi
            </h4>
            """, unsafe_allow_html=True)

            st.dataframe(
                pred_prov,
                use_container_width=True,
                hide_index=True
            )

        with cr:

            st.markdown("""
            <h4 style='color:#facc15;'>
            📈 Aktual vs Prediksi
            </h4>
            """, unsafe_allow_html=True)

            hist = (
                df[df['PROVINSI'] == prov_target]
                .sort_values('TAHUN')
            )

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

            gabung = pd.concat(
                [aktual, prediksi]
            )

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
                height=500
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
        <h2 style='text-align:center;
        color:#facc15;'>
        📖 Info Penelitian
        </h2>
        """, unsafe_allow_html=True)

        st.markdown("""
        <div class='research-card'>

        <h4>🎯 Tujuan Penelitian</h4>

        <ul>
        <li>Menganalisis kehilangan tutupan pohon.</li>
        <li>Menerapkan model MERF.</li>
        <li>Membangun ForestGuard.</li>
        </ul>

        </div>
        """, unsafe_allow_html=True)

