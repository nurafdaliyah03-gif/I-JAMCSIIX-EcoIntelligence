import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import requests
import numpy as np
import warnings
warnings.filterwarnings('ignore')

# --- 1. KONFIGURASI HALAMAN ---
st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")

# --- 2. SESSION STATE ---
if 'page' not in st.session_state: st.session_state.page = "Portal"
if 'merf_model' not in st.session_state: st.session_state.merf_model = None
if 'merf_trained' not in st.session_state: st.session_state.merf_trained = False
if 'merf_results' not in st.session_state: st.session_state.merf_results = None

if 'df' not in st.session_state:
    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"
    df = pd.read_csv(url)
    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    st.session_state.df = df

def set_page(name): st.session_state.page = name

# --- 3. CSS CUSTOM ---
st.markdown("""
<style>
    .stApp { background: linear-gradient(rgba(0, 0, 0, 0.7), rgba(0, 0, 0, 0.7)), url('https://images.unsplash.com/photo-1441974231531-c6227db76b6e?q=80&w=2000&auto=format&fit=crop'); background-size: cover; background-position: center; background-attachment: fixed; color: #ffffff; }
    .stSelectbox div[data-baseweb="select"] { background-color: #ffffff !important; border-radius: 10px; }
    .stSelectbox div[data-baseweb="select"] div { color: #000000 !important; font-weight: 600 !important; }
    .stSelectbox label p { color: #facc15 !important; font-weight: bold !important; font-size: 1.05rem !important; }
    .main-title { font-size: 5rem !important; font-family: 'Arial Black', sans-serif; background: linear-gradient(to bottom, #facc15 0%, #fbbf24 100%); -webkit-background-clip: text; -webkit-text-fill-color: transparent; text-align: center; font-weight: 900 !important; filter: drop-shadow(0px 5px 15px rgba(0,0,0,0.9)); }
    .menu-card { background: rgba(255, 255, 255, 0.1); backdrop-filter: blur(15px); border: 1px solid rgba(255, 255, 255, 0.2); border-radius: 30px; padding: 40px; text-align: center; height: 350px; display: flex; flex-direction: column; justify-content: center; }
    .stPlotlyChart { background-color: white !important; border-radius: 20px; padding: 15px; box-shadow: 0 10px 30px rgba(0,0,0,0.5); }
    [data-testid="stMetricValue"] { color: #ffffff !important; font-weight: 800 !important; font-size: 1.8rem !important; }
    [data-testid="stMetricLabel"] { color: #facc15 !important; font-weight: bold !important; font-size: 0.9rem !important; }
    div.stButton > button { background: linear-gradient(135deg, #15803d 0%, #166534 100%) !important; color: white !important; border: 1px solid #facc15 !important; border-radius: 12px; width: 100%; }
    .research-card { background: rgba(15, 23, 42, 0.65); border: 1px solid rgba(250, 191, 36, 0.3); border-radius: 16px; padding: 25px; margin-bottom: 20px; backdrop-filter: blur(8px); }
    .research-card h4 { color: #facc15 !important; margin-top: 0px; border-bottom: 2px solid #15803d; padding-bottom: 8px; }
    .legend-box { background: rgba(255,255,255,0.1); padding: 10px; border-radius: 8px; font-size: 0.85rem; border: 1px solid #facc15; }
    .metric-card { background: rgba(15, 23, 42, 0.75); border: 1px solid rgba(250, 204, 21, 0.4); border-radius: 16px; padding: 18px; text-align: center; backdrop-filter: blur(8px); }
    .metric-card .val { font-size: 1.8rem; font-weight: 900; color: #facc15; }
    .metric-card .lbl { font-size: 0.8rem; color: #d1d5db; margin-top: 4px; }
    .info-box { background: rgba(21, 128, 61, 0.2); border: 1px solid #15803d; border-radius: 12px; padding: 14px 18px; margin-bottom: 12px; font-size: 0.9rem; }
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
            feature['properties']['PROV_KEY'] = "DI YOGYAKARTA" if "YOGYAKARTA" in nama else ("DKI JAKARTA" if "JAKARTA" in nama else nama)
        return res
    except: return None

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

# Nama pendek kolom X di CSV
x_short = ["X1", "X2", "X3", "X4", "X5", "X6"]
feature_labels = {
    "Y_lag1_log":  "Y lag-1 (Tree Cover Loss)",
    "X1_lag1_log": "X1 lag-1 (Penutupan Lahan)",
    "X2_lag1_log": "X2 lag-1 (Kebakaran Hutan)",
    "X3_lag1_log": "X3 lag-1 (Tanaman Perkebunan)",
    "X4_lag1_log": "X4 lag-1 (Kepadatan Penduduk)",
    "X5_lag1_log": "X5 lag-1 (Populasi Ternak)",
    "X6_lag1_log": "X6 lag-1 (PDRB Pertambangan)",
}

# =========================================================
# MERF ENGINE (replika logika R: lag, log, EM random effects)
# =========================================================
def prepare_merf_data(df_raw):
    """Buat lag features + log transform persis seperti script R."""
    df = df_raw.copy()
    # Pastikan kolom X1..X6 ada (ambil dari nama pendek)
    y_col_raw = col_y
    df = df.rename(columns={y_col_raw: "Y"})
    for k, v in cols_x.items():
        if v in df.columns:
            df = df.rename(columns={v: k})

    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()
    df['TAHUN']    = pd.to_numeric(df['TAHUN'], errors='coerce')
    df = df.sort_values(['PROVINSI', 'TAHUN']).reset_index(drop=True)

    # Lag per provinsi
    for col in ['Y'] + x_short:
        if col in df.columns:
            df[f'{col}_lag1'] = df.groupby('PROVINSI')[col].shift(1)

    df = df.dropna(subset=['Y_lag1']).reset_index(drop=True)

    # Log transform
    df['Y_log'] = np.log1p(df['Y'])
    for col in ['Y'] + x_short:
        lag_col = f'{col}_lag1'
        if lag_col in df.columns:
            df[f'{col}_lag1_log'] = np.log1p(df[lag_col])

    return df

def train_merf(df_prepared, train_years=(None, 2021), test_years=(2022, None),
               ntree=500, mtry=3, max_iter=100, random_state=123):
    """
    MERF: Mixed Effects Random Forest
    Implementasi EM algorithm:
      y_ij = f(X_ij) + Z_ij * b_i + e_ij
    dimana b_i ~ N(0, D), e_ij ~ N(0, sigma^2)
    """
    from sklearn.ensemble import RandomForestRegressor

    feature_cols = ["Y_lag1_log"] + [f"X{i}_lag1_log" for i in range(1, 7)]
    # Pastikan semua feature ada
    feature_cols = [c for c in feature_cols if c in df_prepared.columns]

    train = df_prepared[df_prepared['TAHUN'] <= train_years[1]].copy() if train_years[1] else df_prepared.copy()
    test  = df_prepared[df_prepared['TAHUN'] > test_years[0]].copy()  if test_years[0] else pd.DataFrame()

    prov_levels = sorted(train['PROVINSI'].unique())
    prov_map    = {p: i for i, p in enumerate(prov_levels)}

    X_tr = train[feature_cols].values
    y_tr = train['Y_log'].values
    grp_tr = train['PROVINSI'].map(prov_map).values

    n_groups = len(prov_levels)

    # Inisialisasi random effects b_i = 0
    b = np.zeros(n_groups)

    # Inisialisasi RF
    max_features = max(1, min(mtry, X_tr.shape[1]))
    rf = RandomForestRegressor(
        n_estimators=ntree,
        max_features=max_features,
        random_state=random_state,
        n_jobs=-1
    )

    sigma2_e = 1.0
    sigma2_b = 1.0
    converged = False

    for iteration in range(max_iter):
        b_old = b.copy()

        # E-step: adjusted target = y - Z*b  (Z=1, random intercept)
        y_adj = y_tr - b[grp_tr]

        # M-step fixed effects: fit RF on adjusted target
        rf.fit(X_tr, y_adj)
        f_hat = rf.predict(X_tr)

        # Update residuals
        residuals = y_tr - f_hat

        # Update random effects via BLUP
        # b_i = (sigma2_b / (sigma2_b + sigma2_e/n_i)) * mean_residual_i
        new_b = np.zeros(n_groups)
        for g in range(n_groups):
            mask = grp_tr == g
            if mask.sum() == 0:
                continue
            n_i = mask.sum()
            mean_res_i = residuals[mask].mean()
            shrinkage   = sigma2_b / (sigma2_b + sigma2_e / n_i)
            new_b[g]    = shrinkage * mean_res_i

        # Update variance components
        sigma2_e = np.mean((residuals - new_b[grp_tr]) ** 2)
        sigma2_b = max(np.mean(new_b ** 2), 1e-6)
        b = new_b

        # Konvergensi
        delta = np.max(np.abs(b - b_old))
        if delta < 1e-4:
            converged = True
            break

    # Prediksi train (dengan random effects)
    pred_tr_log = rf.predict(X_tr) + b[grp_tr]
    mse_train   = np.mean((y_tr - pred_tr_log) ** 2)

    # Prediksi test
    pred_te_log = None
    results_test = pd.DataFrame()
    if not test.empty:
        X_te  = test[feature_cols].values
        grp_te = test['PROVINSI'].map(prov_map).fillna(-1).astype(int).values

        b_test = np.array([b[g] if g >= 0 else 0.0 for g in grp_te])
        pred_te_log = rf.predict(X_te) + b_test

        # Bias correction (sama seperti R: expm1(pred + mse/2))
        pred_te_asli = np.expm1(pred_te_log + mse_train / 2)
        pred_tr_asli = np.expm1(pred_tr_log + mse_train / 2)

        results_test = test[['PROVINSI', 'TAHUN', 'Y'] + feature_cols].copy()
        results_test['Y_Prediksi'] = pred_te_asli.round(2)
        results_test['Error_Pct']  = (np.abs(test['Y'].values - pred_te_asli) / np.clip(test['Y'].values, 1, None) * 100).round(2)
    else:
        pred_tr_asli = np.expm1(pred_tr_log + mse_train / 2)

    # Feature importance
    imp = pd.DataFrame({
        'Fitur': feature_labels.get(c, c) for c in feature_cols
    }, index=[0]).T.reset_index()
    imp_vals = rf.feature_importances_
    feat_imp = pd.DataFrame({
        'Fitur': [feature_labels.get(c, c) for c in feature_cols],
        'Importance': imp_vals
    }).sort_values('Importance', ascending=False)

    # Evaluasi
    def eval_metrics(actual, predicted):
        rmse = np.sqrt(np.mean((actual - predicted)**2))
        mae  = np.mean(np.abs(actual - predicted))
        mape = np.mean(np.abs((actual - predicted) / np.clip(actual, 1, None))) * 100
        ss_res = np.sum((actual - predicted)**2)
        ss_tot = np.sum((actual - np.mean(actual))**2)
        r2   = 1 - ss_res / ss_tot if ss_tot > 0 else float('nan')
        return {'RMSE': rmse, 'MAE': mae, 'MAPE': mape, 'R2': r2}

    metrics_train = eval_metrics(train['Y'].values, pred_tr_asli)
    metrics_test  = eval_metrics(test['Y'].values, results_test['Y_Prediksi'].values) if not test.empty else {}

    return {
        'rf': rf,
        'b': b,
        'prov_map': prov_map,
        'prov_levels': prov_levels,
        'mse_train': mse_train,
        'sigma2_e': sigma2_e,
        'sigma2_b': sigma2_b,
        'feature_cols': feature_cols,
        'converged': converged,
        'iterations': iteration + 1,
        'results_test': results_test,
        'feat_imp': feat_imp,
        'metrics_train': metrics_train,
        'metrics_test': metrics_test,
        'train_data': train,
        'test_data': test,
        'pred_tr_asli': pred_tr_asli,
    }

def merf_predict_future(model_result, df_prepared, prov_name, n_years=3):
    """Prediksi masa depan menggunakan model MERF yang sudah di-train."""
    rf       = model_result['rf']
    b        = model_result['b']
    prov_map = model_result['prov_map']
    mse_tr   = model_result['mse_train']
    feat_cols= model_result['feature_cols']

    grp_idx  = prov_map.get(prov_name, -1)
    b_i      = b[grp_idx] if grp_idx >= 0 else 0.0

    prov_df  = df_prepared[df_prepared['PROVINSI'] == prov_name].sort_values('TAHUN')
    last_row = prov_df.iloc[-1]
    last_yr  = int(last_row['TAHUN'])

    preds = []
    current_row = last_row.copy()

    for i in range(1, n_years + 1):
        # Bangun feature vector (lag dari tahun sebelumnya)
        feat_vec = []
        for c in feat_cols:
            # c adalah e.g. "Y_lag1_log" -> ambil dari current_row["Y_log"] dst
            if c == "Y_lag1_log":
                val = np.log1p(current_row['Y']) if 'Y' in current_row.index else current_row.get('Y_lag1_log', 0)
            else:
                base = c.replace('_lag1_log', '')
                if base in current_row.index:
                    val = np.log1p(current_row[base])
                else:
                    val = current_row.get(c, 0)
            feat_vec.append(val)

        x_arr = np.array(feat_vec).reshape(1, -1)
        pred_log = rf.predict(x_arr)[0] + b_i
        pred_asli = np.expm1(pred_log + mse_tr / 2)

        preds.append({'Tahun': last_yr + i, 'Estimasi Loss (Ha)': round(pred_asli, 2), 'Status': 'Prediksi MERF'})

        # Update current_row untuk lag berikutnya
        current_row = current_row.copy()
        current_row['Y'] = pred_asli

    return pd.DataFrame(preds)

# --- 5. LOGIKA NAVIGASI ---
if st.session_state.page == "Portal":
    st.markdown("<br><br><h1 class='main-title'>🌳 ForestGuard</h1>", unsafe_allow_html=True)
    c1, c2, c3 = st.columns(3)
    with c1:
        st.markdown("<div class='menu-card'><h1>🛰️</h1><h3>Dashboard Spasial</h3></div>", unsafe_allow_html=True)
        if st.button("Buka Dashboard"): set_page("Dashboard"); st.rerun()
    with c2:
        st.markdown("<div class='menu-card'><h1>🧪</h1><h3>Prediksi MERF</h3></div>", unsafe_allow_html=True)
        if st.button("Mulai Prediksi"): set_page("Prediksi"); st.rerun()
    with c3:
        st.markdown("<div class='menu-card'><h1>📖</h1><h3>Info Penelitian</h3></div>", unsafe_allow_html=True)
        if st.button("Lihat Penelitian"): set_page("Penelitian"); st.rerun()

else:
    if st.button("⬅️ KEMBALI KE PORTAL"): set_page("Portal"); st.rerun()
    st.markdown("---")

    # ==================== DASHBOARD ====================
    if st.session_state.page == "Dashboard":
        df = st.session_state.df
        st.header("📊 Dashboard Deskriptif Spasial")
        st.markdown("<div class='legend-box'><b>Legenda Tingkat Kehilangan Tutupan Pohon:</b> 🟢 Rendah (Hijau) ➔ 🟡 Sedang (Kuning) ➔ 🔴 Tinggi (Merah)</div>", unsafe_allow_html=True)
        col_f1, col_f2 = st.columns(2)
        sel_thn  = col_f1.selectbox("Pilih Tahun:", sorted(df['TAHUN'].unique(), reverse=True))
        sel_prov = col_f2.selectbox("Fokus Wilayah (Zoom Provinsi):", ["Semua Provinsi"] + sorted(df['PROVINSI'].unique().tolist()))
        df_filt_year = df[df['TAHUN'] == sel_thn]
        cl, cr = st.columns([1.1, 0.9])
        with cl:
            if geojson:
                data_peta = df_filt_year if sel_prov == "Semua Provinsi" else df_filt_year[df_filt_year['PROVINSI'] == sel_prov]
                fig = px.choropleth(data_peta, geojson=geojson, locations="PROVINSI", featureidkey="properties.PROV_KEY", color=col_y, color_continuous_scale="RdYlGn_r")
                fig.update_geos(fitbounds="locations" if sel_prov != "Semua Provinsi" else False, visible=False)
                fig.update_layout(height=450, margin={"r":0,"t":0,"l":0,"b":0}, paper_bgcolor='white')
                st.plotly_chart(fig, use_container_width=True)
        with cr:
            var_x = st.selectbox("Analisis Korelasi X:", list(cols_x.keys()))
            fig2  = px.scatter(df_filt_year, x=cols_x[var_x], y=col_y, color=col_y, color_continuous_scale="RdYlGn_r", trendline="ols")
            fig2.update_layout(paper_bgcolor='white')
            st.plotly_chart(fig2, use_container_width=True)

    # ==================== PREDIKSI MERF ====================
    elif st.session_state.page == "Prediksi":
        st.markdown("<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: PREDIKSI DEFORESTASI — MODEL MERF</h3>", unsafe_allow_html=True)

        df_raw = st.session_state.df

        # Upload data baru
        with st.expander("📥 TAMBAH DATA AKTUAL (UPDATE TAHUNAN)"):
            uploaded_file = st.file_uploader("Upload CSV Data:", type="csv")
            if uploaded_file and st.button("Update Data & Reset Model"):
                new_df = pd.read_csv(uploaded_file)
                new_df.columns = new_df.columns.str.strip()
                new_df['PROVINSI'] = new_df['PROVINSI'].astype(str).str.strip().str.upper()
                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)
                st.session_state.merf_trained = False
                st.session_state.merf_model   = None
                st.rerun()

        # ---- PANEL TRAINING ----
        st.markdown("### ⚙️ Konfigurasi & Training Model MERF")
        with st.expander("🔧 Parameter Model", expanded=not st.session_state.merf_trained):
            pc1, pc2, pc3 = st.columns(3)
            ntree      = pc1.slider("Jumlah Pohon (ntree)", 100, 1000, 500, 50)
            mtry       = pc2.slider("Fitur per Split (mtry)", 1, 7, 3)
            max_iter   = pc3.slider("Maks Iterasi EM", 10, 200, 100, 10)
            train_end  = pc1.number_input("Tahun Akhir Training", min_value=2010, max_value=2030, value=2021)
            test_start = pc2.number_input("Tahun Awal Testing",   min_value=2010, max_value=2030, value=2022)
            n_future   = pc3.slider("Tahun Prediksi ke Depan", 1, 5, 3)

        col_train, col_status = st.columns([1, 2])
        with col_train:
            if st.button("🚀 Latih Model MERF", use_container_width=True):
                with st.spinner("Mempersiapkan data & melatih model MERF... ⏳"):
                    try:
                        df_prep = prepare_merf_data(df_raw)
                        result  = train_merf(
                            df_prep,
                            train_years=(None, train_end),
                            test_years=(test_start - 1, None),
                            ntree=ntree, mtry=mtry, max_iter=max_iter
                        )
                        st.session_state.merf_model   = result
                        st.session_state.merf_trained  = True
                        st.session_state.df_prepared   = df_prep
                        st.success(f"✅ Model selesai dilatih! ({result['iterations']} iterasi, {'konvergen' if result['converged'] else 'maks iterasi tercapai'})")
                    except Exception as e:
                        st.error(f"❌ Error saat training: {e}")

        with col_status:
            if st.session_state.merf_trained:
                r = st.session_state.merf_model
                mt = r['metrics_train']
                st.markdown(f"""
                <div class='info-box'>
                ✅ <b>Status:</b> Model MERF aktif &nbsp;|&nbsp;
                🌲 <b>Pohon:</b> {ntree} &nbsp;|&nbsp;
                🔁 <b>Iterasi:</b> {r['iterations']} &nbsp;|&nbsp;
                σ²ₑ: <b>{r['sigma2_e']:.4f}</b> &nbsp;|&nbsp;
                σ²ᵦ: <b>{r['sigma2_b']:.4f}</b>
                </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("<div class='info-box'>⚠️ Model belum dilatih. Klik <b>Latih Model MERF</b> untuk memulai.</div>", unsafe_allow_html=True)

        st.markdown("---")

        if st.session_state.merf_trained:
            result   = st.session_state.merf_model
            df_prep  = st.session_state.df_prepared

            # ---- METRIK EVALUASI ----
            st.markdown("### 📈 Evaluasi Model")
            mt = result['metrics_train']
            mx = result['metrics_test']

            mc1, mc2, mc3, mc4, mc5, mc6, mc7, mc8 = st.columns(8)
            cols_m = [mc1, mc2, mc3, mc4, mc5, mc6, mc7, mc8]
            pairs = [
                ("RMSE\nTrain",  f"{mt['RMSE']:,.1f}"),
                ("MAE\nTrain",   f"{mt['MAE']:,.1f}"),
                ("MAPE\nTrain",  f"{mt['MAPE']:.2f}%"),
                ("R²\nTrain",    f"{mt['R2']:.4f}"),
                ("RMSE\nTest",   f"{mx.get('RMSE',0):,.1f}"),
                ("MAE\nTest",    f"{mx.get('MAE',0):,.1f}"),
                ("MAPE\nTest",   f"{mx.get('MAPE',0):.2f}%"),
                ("R²\nTest",     f"{mx.get('R2',0):.4f}"),
            ]
            for col, (lbl, val) in zip(cols_m, pairs):
                col.markdown(f"<div class='metric-card'><div class='val'>{val}</div><div class='lbl'>{lbl}</div></div>", unsafe_allow_html=True)

            st.markdown("---")

            # ---- TABS ----
            tab1, tab2, tab3 = st.tabs(["📊 Tren & Prediksi", "📋 Aktual vs Prediksi (Test)", "🌟 Feature Importance"])

            # TAB 1: Tren & Prediksi masa depan
            with tab1:
                prov_list = sorted(df_prep['PROVINSI'].unique().tolist())
                prov_sel  = st.selectbox("Pilih Provinsi:", prov_list, key="prov_tab1")

                hist_prov = df_prep[df_prep['PROVINSI'] == prov_sel].sort_values('TAHUN')
                hist_plot = hist_prov[['TAHUN', 'Y']].copy()
                hist_plot.columns = ['TAHUN', col_y]
                hist_plot['Status'] = 'Data Aktual'

                # Prediksi masa depan dengan MERF
                try:
                    fut_df = merf_predict_future(result, df_prep, prov_sel, n_years=n_future)
                    fut_plot = pd.DataFrame({
                        'TAHUN': fut_df['Tahun'],
                        col_y: fut_df['Estimasi Loss (Ha)'],
                        'Status': 'Prediksi MERF'
                    })
                    # Bridge point
                    bridge = hist_plot.iloc[[-1]].copy()
                    bridge['Status'] = 'Prediksi MERF'
                    df_plot = pd.concat([hist_plot, bridge, fut_plot], ignore_index=True)
                except Exception as e:
                    df_plot = hist_plot
                    st.warning(f"Prediksi masa depan error: {e}")

                fig_pred = px.line(df_plot, x='TAHUN', y=col_y, color='Status', markers=True,
                                   color_discrete_map={'Data Aktual': '#22c55e', 'Prediksi MERF': '#ef4444'},
                                   title=f"Tren Kehilangan Tutupan Pohon — {prov_sel}")
                fig_pred.update_layout(paper_bgcolor='white', plot_bgcolor='white',
                                       font_color='black', legend_title_text='')
                st.plotly_chart(fig_pred, use_container_width=True)

                # Tabel estimasi
                if 'fut_df' in dir():
                    st.markdown(f"<h4 style='color:#facc15;'>📄 Estimasi {n_future} Tahun ke Depan — {prov_sel}</h4>", unsafe_allow_html=True)
                    st.dataframe(fut_df[['Tahun', 'Estimasi Loss (Ha)']].style.format({'Estimasi Loss (Ha)': '{:,.2f}'}), use_container_width=True, hide_index=True)

            # TAB 2: Aktual vs Prediksi pada data test
            with tab2:
                res_test = result['results_test']
                if res_test.empty:
                    st.info("Tidak ada data test (semua data dipakai training).")
                else:
                    # Filter provinsi
                    prov_test = st.selectbox("Filter Provinsi:", ["Semua"] + sorted(res_test['PROVINSI'].unique().tolist()), key="prov_tab2")
                    df_show   = res_test if prov_test == "Semua" else res_test[res_test['PROVINSI'] == prov_test]

                    # Scatter aktual vs prediksi
                    fig_scatter = go.Figure()
                    fig_scatter.add_trace(go.Scatter(
                        x=df_show['Y'], y=df_show['Y_Prediksi'],
                        mode='markers', marker=dict(color='#15803d', size=8, opacity=0.8),
                        name='Prediksi vs Aktual'
                    ))
                    min_v = min(df_show['Y'].min(), df_show['Y_Prediksi'].min())
                    max_v = max(df_show['Y'].max(), df_show['Y_Prediksi'].max())
                    fig_scatter.add_trace(go.Scatter(x=[min_v, max_v], y=[min_v, max_v],
                                                     mode='lines', line=dict(color='red', dash='dash'), name='Garis Ideal'))
                    fig_scatter.update_layout(
                        title="Aktual vs Prediksi (Data Test)",
                        xaxis_title="Nilai Aktual (Ha)", yaxis_title="Nilai Prediksi (Ha)",
                        paper_bgcolor='white', plot_bgcolor='white', font_color='black'
                    )
                    st.plotly_chart(fig_scatter, use_container_width=True)

                    # Tabel hasil
                    st.markdown("<h4 style='color:#facc15;'>📋 Tabel Perbandingan Aktual vs Prediksi</h4>", unsafe_allow_html=True)
                    tbl = df_show[['PROVINSI', 'TAHUN', 'Y', 'Y_Prediksi', 'Error_Pct']].copy()
                    tbl.columns = ['Provinsi', 'Tahun', 'Y Aktual (Ha)', 'Y Prediksi (Ha)', 'Error (%)']
                    st.dataframe(
                        tbl.style.format({'Y Aktual (Ha)': '{:,.2f}', 'Y Prediksi (Ha)': '{:,.2f}', 'Error (%)': '{:.2f}%'}),
                        use_container_width=True, hide_index=True
                    )

            # TAB 3: Feature Importance
            with tab3:
                feat_imp = result['feat_imp']
                fig_imp  = px.bar(
                    feat_imp.sort_values('Importance'),
                    x='Importance', y='Fitur', orientation='h',
                    title='Feature Importance — Model MERF (Random Forest)',
                    color='Importance', color_continuous_scale='Greens'
                )
                fig_imp.update_layout(paper_bgcolor='white', plot_bgcolor='white',
                                      font_color='black', showlegend=False,
                                      yaxis_title='', xaxis_title='Importance (Mean Decrease Impurity)')
                st.plotly_chart(fig_imp, use_container_width=True)

                st.markdown("<h4 style='color:#facc15;'>📋 Tabel Feature Importance</h4>", unsafe_allow_html=True)
                st.dataframe(feat_imp.style.format({'Importance': '{:.4f}'}), use_container_width=True, hide_index=True)

        else:
            st.markdown("""
            <div style='text-align:center; padding: 60px; opacity:0.6;'>
                <h2>🌲</h2>
                <p>Latih model MERF terlebih dahulu menggunakan tombol di atas.</p>
            </div>
            """, unsafe_allow_html=True)

    # ==================== PENELITIAN ====================
    elif st.session_state.page == "Penelitian":
        st.markdown("<h2 style='text-align:center; color:#facc15; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)
        rc1, rc2 = st.columns(2)
        with rc1:
            st.markdown("<div class='research-card'><h4>🎯 Tujuan Penelitian</h4><ul><li>Menerapkan model hibrida MERF.</li><li>Membangun web interaktif ForestGuard.</li></ul></div>", unsafe_allow_html=True)
        with rc2:
            st.markdown("""
            <div class='research-card'><h4>🤖 Metode MERF</h4>
            <p>Paduan <b>Random Forest</b> (fixed effects) dan <b>Mixed Effects</b> (random intercept per provinsi) via algoritma EM.</p>
            <ul>
                <li>Fixed effects: f(X) dimodelkan oleh Random Forest</li>
                <li>Random effects: intercept per provinsi (b_i ~ N(0, σ²ᵦ))</li>
                <li>Lag-1 + log-transform pada semua variabel</li>
                <li>Bias correction: expm1(ŷ_log + MSE/2)</li>
            </ul>
            </div>
            """, unsafe_allow_html=True)

        st.markdown("### 📋 Definisi Operasional Variabel")
        var_data = {
            'Kode':   ['Y',  'X1', 'X2', 'X3', 'X4', 'X5', 'X6'],
            'Nama':   [
                'Tree Cover Loss', 'Luas Penutupan Lahan',
                'Luas Kebakaran Hutan & Lahan', 'Total Luas Tanaman Perkebunan',
                'Kepadatan Penduduk', 'Total Populasi Ternak', 'PDRB Pertambangan & Penggalian'
            ],
            'Satuan': ['Ha', 'Ribu Ha', 'Ha', 'Ribu Ha', 'Jiwa/km²', 'Ekor', 'Persen']
        }
        st.dataframe(pd.DataFrame(var_data), use_container_width=True, hide_index=True)

        st.markdown("""
        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding: 25px; border-radius: 15px; border: 1px solid #ef4444; margin-top: 10px;'>
            <h5 style='margin: 0 0 15px 0; color: #fca5a5; font-weight: bold;'>⚠️ Keterbatasan Model (Limitations)</h5>
            <ul style='margin: 0; padding-left: 20px; font-size: 0.9rem; color: #ffeeee; line-height: 1.6;'>
                <li><b>Ketergantungan Data Historis:</b> Hanya berdasarkan tren masa lalu.</li>
                <li><b>Optimal Jangka Pendek:</b> Akurasi tertinggi untuk prediksi jangka pendek.</li>
                <li><b>Efek Wilayah Baru:</b> Mengabaikan efek acak pada wilayah pemekaran baru.</li>
                <li><b>Cakupan Variabel:</b> Menggunakan data agregat provinsi, belum mencakup faktor mikro.</li>
                <li><b>Resolusi Spasial:</b> Tidak memperhitungkan faktor eksternal mendadak.</li>
                <li><b>Implementasi Python:</b> Replika logika MERF dari LongituRF (R); hasil dapat sedikit berbeda.</li>
            </ul>
        </div>
        """, unsafe_allow_html=True)
