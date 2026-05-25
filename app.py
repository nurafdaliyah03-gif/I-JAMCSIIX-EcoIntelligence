import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

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
# NAMA KOLOM
# =========================================================

col_y = "Y (TREE COVER LOSS- Ha)"

cols_x = {
    "X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5": "X5  (TOTAL POPULASI TERNAK - EKOR)",
    "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN) "
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

        data[f'{key}_lag1'] = (
            data
            .groupby('PROVINSI')[col]
            .shift(1)
        )

    data = data.dropna().copy()

    data['Y_log'] = np.log1p(data[col_y])

    feature_cols = []

    data['Y_lag1_log'] = np.log1p(data['Y_lag1'])

    feature_cols.append('Y_lag1_log')

    for key in cols_x.keys():

        new_col = f'{key}_lag1_log'

        data[new_col] = np.log1p(
            data[f'{key}_lag1']
        )

        feature_cols.append(new_col)

    return data, feature_cols

# =========================================================
# TRAIN MODEL
# =========================================================

@st.cache_data
def train_model(df):

    data, feature_cols = prepare_data(df)

    train_data = data[data['TAHUN'] <= 2021]
    test_data = data[data['TAHUN'] > 2021]

    X_train = train_data[feature_cols]
    y_train = train_data['Y_log']

    X_test = test_data[feature_cols]

    model = RandomForestRegressor(
        n_estimators=500,
        max_depth=10,
        random_state=42
    )

    model.fit(X_train, y_train)

    pred_test_log = model.predict(X_test)

    pred_test = np.expm1(pred_test_log)

    rmse = np.sqrt(
        mean_squared_error(
            test_data[col_y],
            pred_test
        )
    )

    mae = mean_absolute_error(
        test_data[col_y],
        pred_test
    )

    r2 = r2_score(
        test_data[col_y],
        pred_test
    )

    metrics = {
        "RMSE": rmse,
        "MAE": mae,
        "R2": r2
    }

    return model, feature_cols, metrics

# =========================================================
# FUTURE PREDICTION
# =========================================================

def predict_future(
    model,
    feature_cols,
    df,
    provinsi,
    n_years=3
):

    data = df.copy()

    prov_data = (
        data[data['PROVINSI'] == provinsi]
        .sort_values('TAHUN')
    )

    latest = prov_data.iloc[-1]

    current_y = latest[col_y]

    current_year = int(latest['TAHUN'])

    x_values = {}

    for key, col in cols_x.items():
        x_values[key] = latest[col]

    results = []

    for i in range(1, n_years + 1):

        tahun = current_year + i

        future_input = {
            'Y_lag1_log': np.log1p(current_y)
        }

        for key in cols_x.keys():

            future_input[f'{key}_lag1_log'] = np.log1p(
                x_values[key]
            )

        X_future = pd.DataFrame([future_input])

        pred_log = model.predict(X_future)[0]

        pred = np.expm1(pred_log)

        results.append({
            "Tahun": tahun,
            "Prediksi Tree Cover Loss (Ha)": round(pred, 2)
        })

        current_y = pred

    return pd.DataFrame(results)

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
        🌍 PREDIKSI MERF TREE COVER LOSS
        </h2>
        """, unsafe_allow_html=True)

        df = st.session_state.df

        with st.spinner("Training Model..."):

            model, feature_cols, metrics = train_model(df)

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

        prov_target = st.selectbox(
            "Pilih Provinsi",
            sorted(df['PROVINSI'].unique())
        )

        future_years = st.slider(
            "Jumlah Tahun Prediksi",
            1,
            5,
            3
        )

        pred_df = predict_future(
            model,
            feature_cols,
            df,
            prov_target,
            future_years
        )

        cl, cr = st.columns([1, 1.4])

        with cl:

            st.markdown("""
            <h4 style='color:#facc15;'>
            📄 Tabel Estimasi
            </h4>
            """, unsafe_allow_html=True)

            st.dataframe(
                pred_df,
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
                'TAHUN': pred_df['Tahun'],
                'LOSS': pred_df[
                    'Prediksi Tree Cover Loss (Ha)'
                ],
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
