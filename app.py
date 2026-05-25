import streamlit as st
import pandas as pd
import plotly.express as px
import requests
import numpy as np

from merf.merf import MERF

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE ---
if 'page' not in st.session_state:
    st.session_state.page = "Portal"
if 'df' not in st.session_state:
    st.session_state.df = None

def set_page(name):
    st.session_state.page = name

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>
    /* Background Imersif */
    .stApp {
        background: linear-gradient(rgba(0, 0, 0, 0.35), rgba(0, 0, 0, 0.35)), 
                     url('https://raw.githubusercontent.com/tanti1i/jamsicx-apps/main/404268504069646243.jpg.jpeg');
        background-size: cover;
        background-position: center top;
        background-attachment: fixed;
        background-repeat: no-repeat;
        image-rendering: -webkit-optimize-contrast;
        image-rendering: crisp-edges;
        color: #ffffff;
    }

    /* === FIX DROPDOWN (SELECTBOX) === */
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

    /* === FIX FILE UPLOADER === */
    [data-testid="stFileUploader"] label p {
        color: #facc15 !important;
        font-weight: bold !important;
        font-size: 1.1rem !important;
        text-shadow: 1px 1px 3px rgba(0,0,0,0.8);
    }
    [data-testid="stFileUploader"] section div div {
        color: #ffffff !important;
    }
    [data-testid="stFileUploader"] button {
        background-color: #15803d !important;
        color: #ffffff !important;
        border: 1px solid #facc15 !important;
    }

    /* Judul Utama */
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

    /* Glassmorphism Card */
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

    /* === PREMIUM DARK CHART BACKGROUND === */
    .stPlotlyChart { 
        background: rgba(15,35,20,0.45) !important;
        backdrop-filter: blur(12px);
        border: 1px solid rgba(250, 204, 21, 0.18) !important;
        border-radius: 20px; 
        padding: 15px; 
        box-shadow: 0 10px 30px rgba(0,0,0,0.6);
    }

    /* Metrik */
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #facc15 !important; font-weight: bold !important; font-size: 0.9rem !important; }

    /* Tombol Navigasi */
    div.stButton > button {
        background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important;
        color: white !important;
        border: 1px solid #facc15 !important;
        border-radius: 12px;
        width: 100%;
    }

    /* Research Cards */
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

    /* DataTable di halaman prediksi */
    [data-testid="stDataFrame"] {
        background: rgba(15, 35, 20, 0.65) !important;
        border-radius: 16px;
        border: 1px solid rgba(250, 204, 21, 0.18) !important;
        padding: 5px;
    }

    /* Table styling prediksi */
    .stTable {
        background: rgba(15, 35, 20, 0.65) !important;
        border-radius: 16px;
    }
</style>
""", unsafe_allow_html=True)

# --- 4. DEFINISI KOLOM ---
col_y = "Y (TREE COVER LOSS- Ha)"
cols_x = {
    "X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)",
    "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)",
    "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)",
    "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)",
    "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)",
    "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"
}

# --- 5. DATA LOADING ---
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
            elif "BANGKA" in nama or "BELITUNG" in nama:
                key = "BANGKA BELITUNG"
            elif "KEPULAUAN RIAU" in nama or "KEP. RIAU" in nama or "KEPRI" in nama:
                key = "KEPULAUAN RIAU"
            elif "KALIMANTAN UTARA" in nama or "KALTARA" in nama:
                key = "KALIMANTAN UTARA"
            elif "PAPUA BARAT" in nama or "IRIAN JAYA BARAT" in nama:
                key = "PAPUA BARAT"
            elif "PAPUA" in nama or "IRIAN JAYA" in nama:
                key = "PAPUA"
            elif "SULAWESI BARAT" in nama:
                key = "SULAWESI BARAT"
            else:
                key = nama
            feature['properties']['PROV_KEY'] = key
        return res
    except:
        return None

@st.cache_data
def load_internal_data():
    CSV_URL = "https://raw.githubusercontent.com/tanti1i/jamsicx-apps/refs/heads/main/data_jamsicx.csv"
    try:
        df = pd.read_csv(CSV_URL)
        df.columns = df.columns.str.strip()
        if 'PROVINSI' in df.columns:
            df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
        if 'TAHUN' in df.columns:
            df['TAHUN'] = df['TAHUN'].astype(int)
        for col_key, col_name in {**{"Y": col_y}, **cols_x}.items():
            if col_name in df.columns:
                df[col_name] = pd.to_numeric(
                    df[col_name].astype(str).str.replace(',', '').str.strip(),
                    errors='coerce'
                )
        return df
    except Exception as e:
        st.error(f"❌ Gagal memuat data dari GitHub: {e}")
        return None

PROV_BOUNDS = {
    "ACEH":                 (-0.5,  6.5,  94.0,  99.5),
    "SUMATERA UTARA":       ( 0.5,  4.5,  97.5, 100.5),
    "SUMATERA BARAT":       (-3.5,  1.5,  98.5, 101.5),
    "RIAU":                 (-2.0,  2.5,  99.5, 103.0),
    "JAMBI":                (-3.5,  0.0, 101.5, 104.5),
    "SUMATERA SELATAN":     (-5.5, -1.5, 102.5, 106.0),
    "BENGKULU":             (-5.5, -2.0, 100.5, 103.5),
    "LAMPUNG":              (-6.5, -3.5, 104.0, 106.5),
    "BANGKA BELITUNG":      (-4.0, -1.0, 105.5, 108.5),
    "KEPULAUAN RIAU":       ( 0.5,  4.5, 103.5, 109.5),
    "DKI JAKARTA":          (-6.5, -5.8, 106.5, 107.2),
    "JAWA BARAT":           (-8.0, -5.8, 106.0, 109.2),
    "JAWA TENGAH":          (-8.5, -6.0, 108.5, 111.5),
    "DI YOGYAKARTA":        (-8.3, -7.5, 110.0, 110.8),
    "JAWA TIMUR":           (-9.0, -6.5, 110.5, 114.5),
    "BANTEN":               (-7.5, -5.8, 105.5, 107.0),
    "BALI":                 (-9.0, -8.0, 114.4, 115.8),
    "NUSA TENGGARA BARAT":  (-9.5, -7.5, 115.5, 117.5),
    "NUSA TENGGARA TIMUR":  (-11.0,-7.5, 118.0, 125.5),
    "KALIMANTAN BARAT":     (-3.5,  3.0, 107.5, 115.0),
    "KALIMANTAN TENGAH":    (-5.0,  2.0, 110.5, 117.0),
    "KALIMANTAN SELATAN":   (-4.5, -1.0, 114.5, 117.5),
    "KALIMANTAN TIMUR":     (-3.5,  2.5, 113.5, 119.0),
    "KALIMANTAN UTARA":     ( 1.5,  4.5, 114.5, 118.5),
    "SULAWESI UTARA":       ( 0.0,  3.5, 123.0, 127.5),
    "SULAWESI TENGAH":      (-4.0,  2.0, 119.5, 125.0),
    "SULAWESI SELATAN":     (-7.0, -2.5, 119.5, 122.5),
    "SULAWESI TENGGARA":    (-6.0, -2.5, 121.0, 124.5),
    "GORONTALO":            (-1.0,  1.5, 121.5, 124.0),
    "SULAWESI BARAT":       (-3.5, -1.5, 118.5, 120.5),
    "MALUKU":               (-8.5, -2.0, 126.0, 135.0),
    "MALUKU UTARA":         (-1.5,  3.5, 125.5, 130.0),
    "PAPUA BARAT":          (-5.0,  1.5, 130.0, 136.5),
    "PAPUA":                (-9.5, -0.5, 131.0, 141.5),
}

geojson = load_geojson()

if st.session_state.df is None:
    st.session_state.df = load_internal_data()

# --- KONSTANTA WARNA PREMIUM (dipakai bersama) ---
C_BG = 'rgba(15,35,20,0.65)'
C_PLOT = 'rgba(25,50,30,0.55)'
C_TEXT = '#cbd5e1'
C_GOLD = '#facc15'
C_GRID = 'rgba(255,255,255,0.06)'
C_BORDER = 'rgba(250,204,21,0.20)'

CUSTOM_SCALE = [
    [0.00, '#1a7a3a'],
    [0.20, '#4caf50'],
    [0.40, '#d4e157'],
    [0.55, '#ffca28'],
    [0.70, '#ff7043'],
    [0.85, '#e53935'],
    [1.00, '#7b0000'],
]

# =========================================================
# FUNGSI MERF
# =========================================================

@st.cache_data
def prepare_data(df_input):
    data = df_input.copy()
    data = data.sort_values(['PROVINSI', 'TAHUN'])
    data['Y_lag1'] = data.groupby('PROVINSI')[col_y].shift(1)
    for key, col in cols_x.items():
        if col is not None and col in data.columns:
            data[f'{key}_ma3'] = (
                data.groupby('PROVINSI')[col]
                .transform(lambda x: x.rolling(3, min_periods=1).mean())
            )
    data = data.dropna().copy()
    data['Y_log'] = np.log1p(data[col_y])
    data['Y_lag1_log'] = np.log1p(data['Y_lag1'])
    feature_cols = ['Y_lag1_log']
    for key in cols_x.keys():
        col = cols_x[key]
        if col is not None and col in data.columns:
            new_col = f'{key}_ma3_log'
            data[new_col] = np.log1p(data[f'{key}_ma3'])
            feature_cols.append(new_col)
    return data, feature_cols

@st.cache_resource
def load_or_train_model(_df):
    data, feature_cols = prepare_data(_df)
    train_data = data[data['TAHUN'] <= 2021]
    X_train = train_data[feature_cols]
    y_train = train_data['Y_log']
    Z_train = np.ones((len(train_data), 1))
    clusters_train = train_data["PROVINSI"]
    model = MERF()
    model.fit(X_train, Z_train, clusters_train, y_train)
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
        x_hist = {}
        for key, col in cols_x.items():
            if col is not None and col in prov_data.columns:
                x_hist[key] = prov_data[col].tail(3).tolist()
        for i in range(1, n_years + 1):
            tahun = current_year + i
            future_input = {'Y_lag1_log': np.log1p(current_y)}
            for key in x_hist.keys():
                ma3 = np.mean(x_hist[key][-3:])
                future_input[f'{key}_ma3_log'] = np.log1p(ma3)
            X_future = pd.DataFrame([future_input])[feature_cols]
            Z_future = np.ones((1, 1))
            cluster_future = pd.Series([provinsi])
            pred_log = model.predict(X_future, Z_future, cluster_future)[0]
            pred = np.expm1(pred_log)
            hasil_semua.append({
                "PROVINSI": provinsi,
                "TAHUN": tahun,
                "PREDIKSI (Ha)": round(pred, 2),
                "STATUS": "Prediksi"
            })
            current_y = pred
            for key in x_hist.keys():
                x_hist[key].append(np.mean(x_hist[key][-3:]))
    return pd.DataFrame(hasil_semua)

# --- 6. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    st.markdown("<br>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    is_locked = st.session_state.df is None

    with c1:
        st.markdown("<div class='menu-card'><h1>🛰️</h1><h3>Dashboard Spasial</h3></div>", unsafe_allow_html=True)
        if st.button("Buka Dashboard", disabled=is_locked): set_page("Dashboard"); st.rerun()
    with c2:
        st.markdown("<div class='menu-card'><h1>🧪</h1><h3>Prediksi MERF</h3></div>", unsafe_allow_html=True)
        if st.button("Mulai Prediksi", disabled=is_locked): set_page("Prediksi"); st.rerun()
    with c3:
        st.markdown("<div class='menu-card'><h1>📖</h1><h3>Info Penelitian</h3></div>", unsafe_allow_html=True)
        if st.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()

else:
    if st.button("⬅️ KEMBALI KE PORTAL"):
        set_page("Portal"); st.rerun()
    st.markdown("---")

    # =========================================================
    # DASHBOARD
    # =========================================================
    if st.session_state.page == "Dashboard" and st.session_state.df is not None:
        df = st.session_state.df

        st.markdown(
            "<h2 style='color:#facc15; font-weight:800; margin-bottom:4px;'>📊 Dashboard Deskriptif Spasial</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color:#94a3b8; font-size:0.9rem; margin-top:0;'>"
            "Sistem membaca database internal — data aktual deforestasi Indonesia 2015–2024</p>",
            unsafe_allow_html=True
        )

        fc1, fc2, fc3 = st.columns([1, 1.2, 1])
        with fc1:
            list_thn = sorted(df['TAHUN'].unique(), reverse=True)
            sel_thn = st.selectbox("📅 Pilih Tahun:", list_thn)
        with fc2:
            list_prov = ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist())
            sel_prov = st.selectbox("🗺️ Fokus Wilayah (Zoom Provinsi):", list_prov)
        with fc3:
            var_x = st.selectbox("📈 Analisis Korelasi X:", list(cols_x.keys()))

        df_yr = df[df['TAHUN'] == sel_thn].copy()
        g_min = 0
        g_max = 200000

        if geojson:
            fig_map = px.choropleth(
                data_frame=df_yr,
                geojson=geojson,
                locations="PROVINSI",
                featureidkey="properties.PROV_KEY",
                color=col_y,
                color_continuous_scale=CUSTOM_SCALE,
                range_color=[g_min, g_max],
                hover_name="PROVINSI",
                hover_data={col_y: ':,.0f'},
                labels={col_y: "Tree Cover Loss (Ha)"},
            )

            if sel_prov == "Semua Provinsi":
                lat_range = [-11.5, 7.5]
                lon_range = [93.5, 142.5]
                map_title = f"🌳 Tree Cover Loss per Provinsi — {sel_thn}"
            else:
                bounds = PROV_BOUNDS.get(sel_prov, (-11.5, 7.5, 93.5, 142.5))
                lat_pad = (bounds[1] - bounds[0]) * 0.12
                lon_pad = (bounds[3] - bounds[2]) * 0.12
                lat_range = [bounds[0] - lat_pad, bounds[1] + lat_pad]
                lon_range = [bounds[2] - lon_pad, bounds[3] + lon_pad]
                map_title = f"🌳 Tree Cover Loss — {sel_prov}  |  Tahun {sel_thn}"

            fig_map.update_geos(
                lataxis_range=lat_range,
                lonaxis_range=lon_range,
                visible=False,
                bgcolor='rgba(0,0,0,0)',
                showland=True,
                landcolor='rgba(0,0,0,0)',
                showocean=True,
                oceancolor='rgba(0,0,0,0)',
                showlakes=True,
                lakecolor='rgba(0,0,0,0)',
                showcoastlines=True,
                coastlinecolor='rgba(255,255,255,0.15)',
                coastlinewidth=0.5,
                showframe=False,
            )

            if sel_prov != "Semua Provinsi":
                fig_map.update_traces(marker_line_color=C_GOLD, marker_line_width=1.2, selector=dict(type='choropleth'))
            else:
                fig_map.update_traces(marker_line_color='rgba(255,255,255,0.15)', marker_line_width=0.5)

            fig_map.update_layout(
                height=560,
                margin={"r": 80, "t": 50, "l": 0, "b": 0},
                paper_bgcolor='rgba(0,0,0,0)',
                plot_bgcolor='rgba(0,0,0,0)',
                font=dict(color=C_TEXT, family="Arial, sans-serif"),
                title=dict(text=map_title, font=dict(color=C_GOLD, size=15, family="Arial Black"), x=0.01, y=0.98),
                coloraxis_colorbar=dict(
                    title=dict(text="Tree Cover<br>Loss (Ha)", font=dict(color=C_TEXT, size=11)),
                    tickfont=dict(color=C_TEXT, size=9),
                    bgcolor='rgba(7,20,34,0.85)',
                    bordercolor=C_BORDER,
                    borderwidth=1,
                    len=0.80,
                    thickness=22,
                    x=1.03,
                    tickformat=',d',
                ),
            )
            st.plotly_chart(fig_map, use_container_width=True)

        if sel_prov != "Semua Provinsi":
            row_prov = df_yr[df_yr['PROVINSI'] == sel_prov]
            if not row_prov.empty:
                loss_val = row_prov[col_y].values[0]
                rank_val = int(df_yr[col_y].rank(ascending=False).loc[row_prov.index[0]])
                pct_nasional = (loss_val / df_yr[col_y].sum()) * 100

                sp1, m1, m2, m3, sp2 = st.columns([2, 3, 3, 3, 2])
                with m1:
                    st.metric("🌲 Tree Cover Loss", f"{loss_val:,.0f} Ha")
                with m2:
                    st.metric("🏆 Ranking Nasional", f"#{rank_val} / 34")
                with m3:
                    st.metric("📊 % Kontribusi Nasional", f"{pct_nasional:.2f}%")

        col_l, col_r = st.columns([1, 1])

        with col_l:
            x_col_name = cols_x[var_x]

            if sel_prov == "Semua Provinsi":
                df_sc_raw = df_yr.copy()
                hover_col = "PROVINSI"
                sc_title = f"Korelasi {var_x} vs Tree Cover Loss — {sel_thn}"
            else:
                df_sc_raw = df[df['PROVINSI'] == sel_prov].sort_values('TAHUN').copy()
                hover_col = "TAHUN"
                sc_title = f"Korelasi {var_x} vs TCL — {sel_prov} (2015–2024)"

            df_sc = df_sc_raw[[hover_col, x_col_name, col_y]].copy()
            df_sc[x_col_name] = pd.to_numeric(
                df_sc[x_col_name].astype(str).str.replace(',', '').str.strip(), errors='coerce'
            )
            df_sc[col_y] = pd.to_numeric(
                df_sc[col_y].astype(str).str.replace(',', '').str.strip(), errors='coerce'
            )
            df_sc = df_sc.replace([np.inf, -np.inf], np.nan).dropna(subset=[x_col_name, col_y])

            can_trendline = (
                len(df_sc) >= 2
                and df_sc[x_col_name].nunique() > 1
                and df_sc[col_y].nunique() > 1
            )

            if df_sc.empty:
                st.markdown(
                    f"""
                    <div style='background:{C_BG}; border:1px solid {C_BORDER};
                                border-radius:20px; padding:30px; height:370px;
                                display:flex; flex-direction:column; justify-content:center; align-items:center;'>
                        <p style='color:#facc15; font-size:1.1rem; font-weight:700; text-align:center;'>
                            ⚠️ Data {var_x} Tidak Tersedia
                        </p>
                        <p style='color:#94a3b8; font-size:0.9rem; text-align:center;'>
                            Kolom <b>{x_col_name}</b> tidak memiliki data numerik valid untuk filter yang dipilih.
                        </p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
            else:
                try:
                    fig_sc = px.scatter(
                        df_sc, x=x_col_name, y=col_y, color=col_y,
                        trendline="ols" if can_trendline else None,
                        hover_name=hover_col,
                        color_continuous_scale=CUSTOM_SCALE,
                        range_color=[g_min, g_max],
                        title=sc_title,
                        labels={col_y: "TCL (Ha)", x_col_name: var_x},
                    )
                except Exception:
                    fig_sc = px.scatter(
                        df_sc, x=x_col_name, y=col_y, color=col_y,
                        trendline=None,
                        hover_name=hover_col,
                        color_continuous_scale=CUSTOM_SCALE,
                        range_color=[g_min, g_max],
                        title=sc_title + " (trendline tidak tersedia)",
                        labels={col_y: "TCL (Ha)", x_col_name: var_x},
                    )

                fig_sc.update_layout(
                    paper_bgcolor=C_BG, plot_bgcolor=C_PLOT,
                    font=dict(color=C_TEXT, size=11),
                    title=dict(font=dict(color=C_GOLD, size=13), x=0.01),
                    xaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER),
                    yaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER),
                    coloraxis_colorbar=dict(
                        title=dict(text="Loss (Ha)", font=dict(color=C_TEXT, size=10)),
                        tickfont=dict(color=C_TEXT, size=8),
                        bgcolor='rgba(7,20,34,0.85)',
                        bordercolor=C_BORDER, borderwidth=1,
                        len=0.80, thickness=11, tickformat=',d',
                    ),
                    height=370,
                    margin=dict(l=10, r=10, t=50, b=10),
                )
                st.plotly_chart(fig_sc, use_container_width=True)

        with col_r:
            if sel_prov != "Semua Provinsi":
                df_ts = df[df['PROVINSI'] == sel_prov].sort_values('TAHUN')
                fig_r = px.area(
                    df_ts, x='TAHUN', y=col_y,
                    title=f"📉 Tren Deforestasi — {sel_prov}",
                    labels={col_y: "TCL (Ha)", "TAHUN": "Tahun"},
                    color_discrete_sequence=['#22c55e'],
                )
                fig_r.update_traces(line_color='#4ade80', fillcolor='rgba(34,197,94,0.12)')
                fig_r.add_vline(
                    x=sel_thn, line_dash="dot", line_color=C_GOLD, line_width=1.5,
                    annotation_text=f"  {sel_thn}",
                    annotation_font_color=C_GOLD, annotation_font_size=11,
                )
            else:
                top10 = (
                    df_yr.nlargest(10, col_y)[['PROVINSI', col_y]]
                    .sort_values(col_y, ascending=True)
                )
                fig_r = px.bar(
                    top10, x=col_y, y='PROVINSI', orientation='h',
                    title=f"🔴 Top 10 Deforestasi Tertinggi — {sel_thn}",
                    color=col_y,
                    color_continuous_scale=CUSTOM_SCALE,
                    range_color=[top10[col_y].min(), top10[col_y].max()],
                    labels={col_y: "TCL (Ha)", 'PROVINSI': ''},
                )
                fig_r.update_traces(marker_line_width=0)
                fig_r.update_layout(coloraxis_showscale=False)

            fig_r.update_layout(
                paper_bgcolor=C_BG, plot_bgcolor=C_PLOT,
                font=dict(color=C_TEXT, size=11),
                title=dict(font=dict(color=C_GOLD, size=13), x=0.01),
                xaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER, tickformat=',d'),
                yaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER),
                height=370,
                margin=dict(l=10, r=10, t=50, b=10),
            )
            st.plotly_chart(fig_r, use_container_width=True)

    # =========================================================
    # PREDIKSI — MERF LENGKAP + STYLING SESUAI SYNTAX 1
    # =========================================================
    elif st.session_state.page == "Prediksi" and st.session_state.df is not None:
        df = st.session_state.df

        st.markdown(
            "<h2 style='color:#facc15; font-weight:800; margin-bottom:4px;'>🧪 Prediksi Risiko Deforestasi (MERF)</h2>",
            unsafe_allow_html=True
        )
        st.markdown(
            "<p style='color:#94a3b8; font-size:0.9rem; margin-top:0;'>"
            "Model Mixed-Effects Random Forest — Prediksi 3 Tahun ke Depan per Provinsi</p>",
            unsafe_allow_html=True
        )

        # Upload data baru
        st.markdown(
            "<h4 style='color:#facc15; margin-top:10px;'>📥 Upload Data Aktual Baru (Opsional)</h4>",
            unsafe_allow_html=True
        )
        uploaded_file = st.file_uploader("Upload file CSV untuk memperbarui data aktual:", type="csv")

        if uploaded_file is not None:
            new_df = pd.read_csv(uploaded_file)
            new_df.columns = new_df.columns.str.strip().str.replace(r"\s+", " ", regex=True)
            new_df['PROVINSI'] = new_df['PROVINSI'].astype(str).str.upper().str.strip()
            if 'TAHUN' in new_df.columns:
                new_df['TAHUN'] = new_df['TAHUN'].astype(int)
            for col_name in [col_y] + list(cols_x.values()):
                if col_name in new_df.columns:
                    new_df[col_name] = pd.to_numeric(
                        new_df[col_name].astype(str).str.replace(',', '').str.strip(), errors='coerce'
                    )
            tahun_baru = new_df['TAHUN'].unique()
            df = df[~df['TAHUN'].isin(tahun_baru)]
            df = pd.concat([df, new_df], ignore_index=True)
            st.session_state.df = df
            st.success(f"✅ Data aktual tahun {list(tahun_baru)} berhasil diperbarui.")

        # Training model
        with st.spinner("⏳ Menjalankan algoritma MERF... Mohon tunggu sebentar."):
            try:
                model, feature_cols = load_or_train_model(df)
                pred_global = forecast_all_provinces(model, feature_cols, df, n_years=3)
                model_ok = True
            except Exception as e:
                st.error(f"❌ Gagal menjalankan model MERF: {e}")
                model_ok = False

        if model_ok:
            # Pilih provinsi
            prov_target = st.selectbox(
                "📍 Pilih Provinsi untuk Detail Prediksi:",
                sorted(df['PROVINSI'].unique())
            )

            pred_prov = pred_global[pred_global['PROVINSI'] == prov_target].copy()
            hist = df[df['PROVINSI'] == prov_target].sort_values('TAHUN')

            latest_year = int(hist['TAHUN'].max())
            latest_value = float(hist[col_y].iloc[-1])
            avg_loss = float(hist[col_y].mean())

            # Metric Cards
            st.markdown("<br>", unsafe_allow_html=True)
            st.markdown(
                "<h4 style='color:#facc15;'>📊 Ringkasan Wilayah</h4>",
                unsafe_allow_html=True
            )
            s1, s2, s3 = st.columns(3)
            s1.metric("📅 Tahun Aktual Terakhir", str(latest_year))
            s2.metric("🌲 Loss Aktual Terakhir", f"{latest_value:,.2f} Ha")
            s3.metric("📈 Rata-rata Loss Historis", f"{avg_loss:,.2f} Ha")

            st.markdown("---")

            # Kalkulasi monitoring
            pred_awal = float(pred_prov['PREDIKSI (Ha)'].iloc[0])
            pred_akhir = float(pred_prov['PREDIKSI (Ha)'].iloc[-1])
            change_percent = ((pred_akhir - pred_awal) / pred_awal) * 100 if pred_awal != 0 else 0

            trend_text = "↑ Naik" if pred_akhir >= pred_awal else "↓ Turun"

            if pred_akhir < 5000:
                risk_status = "Rendah 🟢"
                risk_color = "#22c55e"
            elif pred_akhir < 15000:
                risk_status = "Sedang 🟡"
                risk_color = "#facc15"
            else:
                risk_status = "Tinggi 🔴"
                risk_color = "#ef4444"

            cl, cr = st.columns([1, 1.5])

            with cl:
                st.markdown(
                    "<h4 style='color:#facc15;'>📄 Hasil Prediksi 3 Tahun</h4>",
                    unsafe_allow_html=True
                )
                st.dataframe(pred_prov, use_container_width=True, hide_index=True)

                st.markdown("<br>", unsafe_allow_html=True)
                st.markdown(
                    "<h4 style='color:#facc15;'>📋 Monitoring Risiko Deforestasi</h4>",
                    unsafe_allow_html=True
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
                        f"{pred_akhir:,.2f} Ha"
                    ]
                })
                st.table(monitor_df)

                # Risk badge
                st.markdown(
                    f"""
                    <div style='background:rgba(15,35,20,0.65); border:2px solid {risk_color};
                                border-radius:16px; padding:20px; text-align:center; margin-top:10px;'>
                        <p style='color:#94a3b8; margin:0; font-size:0.85rem;'>STATUS RISIKO AKHIR PREDIKSI</p>
                        <p style='color:{risk_color}; font-size:2rem; font-weight:900; margin:8px 0;'>{risk_status}</p>
                        <p style='color:#cbd5e1; margin:0; font-size:0.85rem;'>Prediksi: {pred_akhir:,.0f} Ha</p>
                    </div>
                    """,
                    unsafe_allow_html=True
                )

            with cr:
                st.markdown(
                    "<h4 style='color:#facc15;'>📈 Grafik Aktual vs Prediksi</h4>",
                    unsafe_allow_html=True
                )

                aktual_df = pd.DataFrame({
                    'TAHUN': hist['TAHUN'],
                    'LOSS (Ha)': hist[col_y],
                    'Status': 'Aktual'
                })

                # Sambungkan dari titik aktual terakhir ke prediksi
                bridge_df = pd.DataFrame({
                    'TAHUN': [latest_year],
                    'LOSS (Ha)': [latest_value],
                    'Status': ['Prediksi']
                })

                pred_line_df = pd.DataFrame({
                    'TAHUN': pred_prov['TAHUN'],
                    'LOSS (Ha)': pred_prov['PREDIKSI (Ha)'],
                    'Status': 'Prediksi'
                })

                gabung = pd.concat([aktual_df, bridge_df, pred_line_df], ignore_index=True)

                fig_pred = px.line(
                    gabung,
                    x='TAHUN',
                    y='LOSS (Ha)',
                    color='Status',
                    markers=True,
                    color_discrete_map={
                        'Aktual': '#22c55e',
                        'Prediksi': '#ef4444'
                    },
                    title=f"Tren Deforestasi Aktual & Prediksi — {prov_target}",
                    labels={'LOSS (Ha)': 'Tree Cover Loss (Ha)', 'TAHUN': 'Tahun'}
                )

                # Garis pemisah aktual-prediksi
                fig_pred.add_vline(
                    x=latest_year, line_dash="dot",
                    line_color=C_GOLD, line_width=1.5,
                    annotation_text=f"  Batas Prediksi",
                    annotation_font_color=C_GOLD,
                    annotation_font_size=11,
                )

                fig_pred.update_layout(
                    paper_bgcolor=C_BG,
                    plot_bgcolor=C_PLOT,
                    font=dict(color=C_TEXT, size=11),
                    title=dict(font=dict(color=C_GOLD, size=13), x=0.01),
                    xaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER, tickformat='d'),
                    yaxis=dict(gridcolor=C_GRID, zerolinecolor=C_GRID, linecolor=C_BORDER, tickformat=',d'),
                    legend=dict(
                        bgcolor='rgba(15,35,20,0.7)',
                        bordercolor=C_BORDER,
                        borderwidth=1,
                        font=dict(color=C_TEXT)
                    ),
                    height=550,
                    margin=dict(l=10, r=10, t=50, b=10),
                )
                st.plotly_chart(fig_pred, use_container_width=True)

            # Tabel semua provinsi
            st.markdown("---")
            st.markdown(
                "<h4 style='color:#facc15;'>🗺️ Prediksi Seluruh Provinsi (3 Tahun ke Depan)</h4>",
                unsafe_allow_html=True
            )
            pivot_pred = pred_global.pivot_table(
                index='PROVINSI', columns='TAHUN', values='PREDIKSI (Ha)'
            ).reset_index()
            pivot_pred.columns = [str(c) for c in pivot_pred.columns]
            st.dataframe(pivot_pred, use_container_width=True, hide_index=True)

    # =========================================================
    # PENELITIAN
    # =========================================================
    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#facc15; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
        st.markdown("<br>", unsafe_allow_html=True)

        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("""
            <div class='research-card'>
                <h4>🎯 Tujuan Penelitian</h4>
                <ul style='color: #f8fafc; padding-left: 20px; line-height: 1.6;'>
                    <li>Menerapkan pendekatan data longitudinal dan model hibrida Mixed Effects Random Forest (MERF) untuk menangkap tren perubahan waktu sekaligus karakteristik spasial.</li>
                    <li>Membangun aplikasi web interaktif ForestGuard sebagai media visualisasi spasial-temporal (Choropleth Map) dan sistem prediksi risiko deforestasi yang praktis dan mudah dipahami oleh pemangku kebijakan serta masyarakat umum.</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class='research-card'>
                <h4>📊 Sumber Data Penelitian</h4>
                <ul style='color: #f8fafc; padding-left: 20px; line-height: 1.6;'>
                    <li><b>BPS (Badan Pusat Statistik):</b> Data sosio-ekonomi agregat tahunan meliputi kepadatan penduduk sektoral dan persentase kontribusi PDRB lapangan usaha.</li>
                    <li><b>KLHK (Kementerian Lingkungan Hidup dan Kehutanan):</b> Rekapitulasi luasan area kebakaran hutan (Karhutla) serta pemantauan status fungsi kawasan hutan.</li>
                    <li><b>Global Forest Watch (GFW):</b> Metrik target historis <i>Tree Cover Loss</i> (Y) yang dihitung dalam satuan Hektar (Ha).</li>
                </ul>
            </div>
            """, unsafe_allow_html=True)

        with rc2:
            st.markdown("""
            <div class='research-card'>
                <h4>🤖 Metode MERF (Mixed-Effects Random Forest)</h4>
                <p style='color: #f8fafc; text-align: justify; line-height: 1.6; margin-bottom: 10px;'>
                    <b>Mixed-Effects Random Forest (MERF)</b> merupakan algoritma lanjut yang memadukan keunggulan non-linearitas dari <i>Random Forest</i> dengan kemampuan menangani data panel berhirarki milik <i>Linear Mixed Models</i>.
                </p>
                <p style='color: #f8fafc; text-align: justify; line-height: 1.6;'>
                    Setiap provinsi memiliki karakteristik dasar lingkungan yang berbeda (efek acak) yang tidak bisa disamaratakan oleh model regresi biasa standar. MERF mengisolasi efek kontekstual wilayah ini sehingga tingkat akurasi prediksi meningkat tajam secara lokal.
                </p>
            </div>
            """, unsafe_allow_html=True)

            st.markdown("""
            <div class='research-card'>
                <h4>🧮 Persamaan Dasar Model MERF</h4>
                <p style='text-align: center; font-size: 1.4rem; color: #f8fafc; font-style: italic; margin: 16px 0 20px 0; letter-spacing: 0.03em;'>
                    <i>y</i><sub><i>i</i></sub> &nbsp;=&nbsp; <i>f</i>(<b>X</b><sub><i>i</i></sub>) &nbsp;+&nbsp; <b>Z</b><sub><i>i</i></sub><b>b</b><sub><i>i</i></sub> &nbsp;+&nbsp; &#x03B5;<sub><i>i</i></sub>
                </p>
                <table style='width:100%; border-collapse: collapse; font-size: 0.88rem;'>
                    <thead>
                        <tr>
                            <th style='padding: 8px 14px; text-align: center; color: #facc15; width: 20%; font-weight: 700;'>Simbol</th>
                            <th style='padding: 8px 14px; text-align: left; color: #facc15; font-weight: 700;'>Keterangan</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a; font-style: italic;'><i>y</i><sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Vektor nilai variabel respon (<i>Tree Cover Loss</i>) untuk subjek provinsi ke-<i>i</i></td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a; font-style: italic;'><i>f</i>(<b>X</b><sub><i>i</i></sub>)</td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Fungsi non-linear <i>fixed effects</i> yang diestimasi menggunakan algoritma <b>Random Forest</b> berdasarkan matriks prediktor <b>X</b><sub><i>i</i></sub></td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a;'><b>Z</b><sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Matriks desain untuk komponen <i>random effects</i> (konstanta intercept untuk tiap provinsi)</td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a;'><b>b</b><sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Vektor penyimpangan acak (<i>random effects</i>) untuk provinsi ke-<i>i</i>, dimana <b>b</b><sub><i>i</i></sub> &#x223C; <i>N</i>(0, <b>D</b>)</td>
                        </tr>
                        <tr>
                            <td style='padding: 8px 14px; text-align: center; color: #fde68a;'>&#x03B5;<sub><i>i</i></sub></td>
                            <td style='padding: 8px 14px; color: #f8fafc;'>Vektor <i>error</i> acak sisaan (<i>residual error</i>), dimana &#x03B5;<sub><i>i</i></sub> &#x223C; <i>N</i>(0, <b>R</b><sub><i>i</i></sub>) dengan <b>R</b><sub><i>i</i></sub> = &#x03C3;&#xB2;<b>I</b><sub><i>n</i><sub><i>i</i></sub></sub></td>
                        </tr>
                    </tbody>
                </table>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("""
        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding: 25px; border-radius: 15px; border: 1px solid #ef4444; margin-top: 10px;'>
            <h5 style='margin: 0 0 10px 0; color: #fca5a5; font-weight: bold;'>⚠️ Batasan Penelitian & Disclaimer Model</h5>
            <ul style='color: #ffeeee; font-size: 0.9rem; line-height: 1.5;'>
                <li><b>Ketergantungan Data Historis:</b> Model memprediksi berdasarkan tren masa lalu, sehingga tidak bisa membaca perubahan mendadak seperti kebijakan hukum baru atau penegakan hukum di lapangan.</li>
                <li><b>Optimal Jangka Pendek:</b> Estimasi paling akurat untuk masa depan terdekat. Prediksi terlalu jauh ke depan berisiko memperbesar akumulasi kesalahan (error propagation).</li>
                <li><b>Efek Wilayah Baru:</b> Jika ada provinsi hasil pemekaran baru, model akan mengabaikan efek acak wilayah (b_i = 0) dan murni menggunakan prediksi rata-rata global.</li>
                <li><b>Cakupan Variabel Makro:</b> Tidak memperhitungkan faktor pemicu eksternal mendadak (exogenous shocks) di luar variabel terdata.</li>
                <li><b>Resolusi Spasial Makro:</b> Dirancang untuk memetakan estimasi risiko di tingkat provinsi, bukan untuk mendeteksi penebangan pohon secara real-time di tingkat koordinat petak hutan.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
