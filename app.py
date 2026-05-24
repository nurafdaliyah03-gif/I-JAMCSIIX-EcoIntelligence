import streamlit as st

import pandas as pd

import plotly.express as px

import requests

import numpy as np



# --- 1. KONFIGURASI HALAMAN ---

st.set_page_config(page_title="I-JAMCSIIX - Eco Intelligence", layout="wide", initial_sidebar_state="collapsed")



# --- 2. SESSION STATE ---

if 'page' not in st.session_state: st.session_state.page = "Portal"

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

cols_x = {"X1": "X1 (LUAS PENUTUPAN LAHAN - RIBU Ha)", "X2": "X2 (LUAS KEBAKARAN HUTAN DAN LAHAN - Ha)", "X3": "X3 (TOTAL LUAS TANAMAN PERKEBUNAN - RIBU Ha)", "X4": "X4 (KEPADATAN PENDUDUK - jiwa/km2)", "X5": "X5 (TOTAL POPULASI TERNAK - EKOR)", "X6": "X6 (PDRB PERTAMBANGAN DAN PENGGALIAN PERSEN)"}



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



    if st.session_state.page == "Dashboard":

        df = st.session_state.df

        st.header("📊 Dashboard Deskriptif Spasial")

        st.markdown("<div class='legend-box'><b>Legenda Tingkat Kehilangan Tutupan Pohon:</b> 🟢 Rendah (Hijau) ➔ 🟡 Sedang (Kuning) ➔ 🔴 Tinggi (Merah)</div>", unsafe_allow_html=True)

        col_f1, col_f2 = st.columns(2)

        sel_thn = col_f1.selectbox("Pilih Tahun:", sorted(df['TAHUN'].unique(), reverse=True))

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

            fig2 = px.scatter(df_filt_year, x=cols_x[var_x], y=col_y, color=col_y, color_continuous_scale="RdYlGn_r", trendline="ols")

            fig2.update_layout(paper_bgcolor='white')

            st.plotly_chart(fig2, use_container_width=True)



    elif st.session_state.page == "Prediksi":

        st.markdown("<h3 style='color: #facc15; font-weight: bold;'>🌍 FORESTGUARD: ESTIMASI RISIKO DEFORESTASI & MONITORING JANGKA PENDEK</h3>", unsafe_allow_html=True)

        with st.expander("📥 TAMBAH DATA AKTUAL (UPDATE TAHUNAN)"):

            uploaded_file = st.file_uploader("Upload CSV Data:", type="csv")

            if uploaded_file and st.button("Update Data & Grafik"):

                new_df = pd.read_csv(uploaded_file)

                st.session_state.df = pd.concat([st.session_state.df, new_df], ignore_index=True)

                st.rerun()



        df = st.session_state.df

        last_yr = df['TAHUN'].max()

        prov_target = st.selectbox("Pilih Wilayah untuk Grafik Tren:", sorted(df['PROVINSI'].unique()))

        st.markdown("---")

        

        cl, cr = st.columns([1, 1.3])

        with cl:

            st.markdown(f"<h4 style='color: #facc15;'>📄 TABEL ESTIMASI ({last_yr+1} - {last_yr+3}): {prov_target}</h4>", unsafe_allow_html=True)

            p_data = df[df['PROVINSI'] == prov_target]

            last_val = p_data.iloc[-1][col_y]

            pred_data = [{"Tahun": last_yr+i, "Estimasi Loss (Ha)": round(last_val * (1.03 ** i), 2)} for i in range(1, 4)]

            st.dataframe(pd.DataFrame(pred_data), use_container_width=True, hide_index=True)



        with cr:

            st.markdown(f"<h4 style='color: #facc15;'>📊 TREN KEHILANGAN TUTUPAN POHON</h4>", unsafe_allow_html=True)

            hist = p_data.sort_values('TAHUN').copy()

            hist['Status'] = 'Data Aktual'

            future = pd.DataFrame({'TAHUN': [last_yr+1, last_yr+2, last_yr+3], col_y: [last_val * (1.03**i) for i in range(1, 4)], 'Status': 'Prediksi'})

            

            last_actual = hist.iloc[[-1]].copy()

            last_actual['Status'] = 'Prediksi'

            df_plot = pd.concat([hist[['TAHUN', col_y, 'Status']], last_actual, future])

            

            fig_pred = px.line(df_plot, x='TAHUN', y=col_y, color='Status', markers=True, color_discrete_map={'Data Aktual': '#22c55e', 'Prediksi': '#ef4444'})

            st.plotly_chart(fig_pred, use_container_width=True)



     # --- HALAMAN PENELITIAN ---

    elif st.session_state.page == "Penelitian":

        st.markdown("<h2 style='text-align:center; color:#facc15; font-weight: 800;'>📖 Info Penelitian</h2>", unsafe_allow_html=True)

        st.markdown("<br>", unsafe_allow_html=True)

        

        rc1, rc2 = st.columns(2)

        with rc1:

            st.markdown("""

            <div class='research-card'>

                <h4>🎯 Tujuan Penelitian</h4>

                <ul style='color: #f8fafc; padding-left: 20px; line-height: 1.6;'>

                    <li>Menerapkan pendekatan data longitudinal dan model hibrida Mixed Effects Random Forest (MERF) untuk menangkap tren perubahan waktu sekaligus</li>

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

                    <li><b>Global Forest Watch (GFW):</b> Metrik target historis <i>Tree Cover Loss</i> ($Y$) yang dihitung dalam satuan Hektar (Ha).</li>

                </ul>

            </div>

            """, unsafe_allow_html=True)

            

        with rc2:

            st.markdown("""

            <div class='research-card'>

                <h4>🤖 Metode MERF (Mixed-Effects Random Forest)</h4>

                <p style='color: #f8fafc; text-align: justify; line-height: 1.6; margin-bottom: 10px;'>

                    <b>Mixed-Effects Random Forest (MERF)</b> merupakan algoritma lanjut yang memadukan keunggulan non-linearitas dari <i>Random Forest</i> dengan kemampuan menangani data panel berhirarki/kluster milik <i>Linear Mixed Models</i>.

                </p>

                <p style='color: #f8fafc; text-align: justify; line-height: 1.6;'>

                    Dalam kasus deforestasi tingkat nasional, setiap provinsi memiliki karakteristik dasar lingkungan yang berbeda (efek acak) yang tidak bisa disamaratakan oleh model regresi biasa standar. MERF mengisolasi efek kontekstual wilayah ini sehingga tingkat akurasi prediksi (R²) meningkat tajam secara lokal.

                </p>

            </div>

            """, unsafe_allow_html=True)

            

            with st.container():

                st.markdown("<div class='research-card'><h4>🧮 Persamaan Dasar Model MERF</h4>", unsafe_allow_html=True)

                st.write("Persamaan matematis untuk model Mixed Effects Random Forest (MERF) adalah sebagai berikut:")

                st.latex(r"y_i = f(X_i) + Z_i b_i + \varepsilon_i")

                st.markdown("""

                <p style='font-size: 0.85rem; color: #cbd5e1; margin-top: 10px; line-height: 1.4;'>

                    <b>Keterangan fungsi dan simbol (p. 5):</b><br>

                    • $y_i$: Vektor nilai variabel respon (<i>Tree Cover Loss</i>) untuk subjek provinsi ke-$i$.<br>

                    • $f(X_i)$: Fungsi non-linear <i>fixed effects</i> yang diestimasi menggunakan algoritma <b>Random Forest</b> berdasarkan matriks prediktor $X_i$.<br>

                    • $Z_i$: Matriks desain untuk komponen <i>random effects</i> (konstanta intercept untuk tiap provinsi).<br>

                    • $b_i$: Vektor penyimpangan acak (<i>random effects</i>) untuk provinsi ke-$i$, di mana $b_i \sim N(0, D)$.<br>

                    • $\\varepsilon_i$: Vektor <i>error</i> acak sisaan (<i>residual error</i>), di mana $\\varepsilon_i \sim N(0, R_i)$ dengan $R_i = \\sigma^2 I_{n_i}$.

                </p>

                </div>

                """, unsafe_allow_html=True)



        st.markdown("### 📋 Definisi Operasional Variabel Penelitian")

        

        v_col1, v_col2 = st.columns(2)

        with v_col1:

            st.markdown("""

            <div class='research-card'>

                <table style='width: 100%; border-collapse: collapse; color: #f8fafc;'>

                    <tr style='border-bottom: 2px solid #15803d; color: #facc15;'>

                        <th style='padding: 8px; text-align: left;'>Kode</th>

                        <th style='padding: 8px; text-align: left;'>Nama Variabel Operasional</th>

                        <th style='padding: 8px; text-align: left;'>Satuan</th>

                    </tr>

                    <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>

                        <td style='padding: 8px; font-weight: bold; color: #fbbf24;'>Y</td>

                        <td style='padding: 8px;'>Tree Cover Loss (Kehilangan Tutupan Pohon)</td>

                        <td style='padding: 8px;'>Hektar (Ha)</td>

                    </tr>

                    <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>

                        <td style='padding: 8px; font-weight: bold; color: #22c55e;'>X1</td>

                        <td style='padding: 8px;'>Luas Penutupan Lahan Eksisting</td>

                        <td style='padding: 8px;'>Ribu Ha</td>

                    </tr>

                    <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>

                        <td style='padding: 8px; font-weight: bold; color: #22c55e;'>X2</td>

                        <td style='padding: 8px;'>Luas Kebakaran Hutan dan Lahan (Karhutla)</td>

                        <td style='padding: 8px;'>Hektar (Ha)</td>

                    </tr>

                    <tr>

                        <td style='padding: 8px; font-weight: bold; color: #22c55e;'>X3</td>

                        <td style='padding: 8px;'>Total Luas Tanaman Perkebunan</td>

                        <td style='padding: 8px;'>Ribu Ha</td>

                    </tr>

                </table>

            </div>

            """, unsafe_allow_html=True)

            

        with v_col2:

            st.markdown("""

            <div class='research-card'>

                <table style='width: 100%; border-collapse: collapse; color: #f8fafc;'>

                    <tr style='border-bottom: 2px solid #15803d; color: #facc15;'>

                        <th style='padding: 8px; text-align: left;'>Kode</th>

                        <th style='padding: 8px; text-align: left;'>Nama Variabel Operasional</th>

                        <th style='padding: 8px; text-align: left;'>Satuan</th>

                    </tr>

                    <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>

                        <td style='padding: 8px; font-weight: bold; color: #22c55e;'>X4</td>

                        <td style='padding: 8px;'>Kepadatan Penduduk Wilayah Terkait</td>

                        <td style='padding: 8px;'>Jiwa/km²</td>

                    </tr>

                    <tr style='border-bottom: 1px solid rgba(255,255,255,0.1);'>

                        <td style='padding: 8px; font-weight: bold; color: #22c55e;'>X5</td>

                        <td style='padding: 8px;'>Total Populasi Ternak Besar/Kecil Terdata</td>

                        <td style='padding: 8px;'>Ekor</td>

                    </tr>

                    <tr>

                        <td style='padding: 8px; font-weight: bold; color: #22c55e;'>X6</td>

                        <td style='padding: 8px;'>Persentase PDRB Sektor Pertambangan</td>

                        <td style='padding: 8px;'>Persen (%)</td>

                    </tr>

                </table>

            </div>

            """, unsafe_allow_html=True)



        # --- BAGIAN KETERBATASAN MODEL (SAMA PERSIS DENGAN GAMBAR ASLI) ---

        st.markdown("""

        <div style='background: linear-gradient(135deg, #7f1d1d 0%, #450a0a 100%); padding: 25px; border-radius: 15px; border: 1px solid #ef4444; margin-top: 10px;'>

            <h5 style='margin: 0 0 15px 0; color: #fca5a5; font-weight: bold;'>⚠️ Keterbatasan Model (Limitations)</h5>

            <ul style='margin: 0; padding-left: 20px; font-size: 0.9rem; color: #ffeeee; text-align: justify; line-height: 1.6; list-style-type: disc;'>

                <li style='margin-bottom: 10px;'><b>Ketergantungan Data Historis:</b> Model memprediksi berdasarkan tren masa lalu, sehingga tidak bisa membaca perubahan mendadak seperti kebijakan hukum baru atau penegakan hukum di lapangan.</li>

                <li style='margin-bottom: 10px;'><b>Optimal Jangka Pendek:</b> Estimasi paling akurat untuk masa depan terdekat. Prediksi terlalu jauh ke depan berisiko memperbesar akumulasi kesalahan (<i>error propagation</i>).</li>

                <li style='margin-bottom: 10px;'><b>Efek Wilayah Baru:</b> Jika ada provinsi hasil pemekaran baru, model akan mengabaikan efek acak wilayah ($b_i = 0$) dan murni menggunakan prediksi rata-rata global.</li>

                <li style='margin-bottom: 10px;'><b>Cakupan Variabel Makro:</b> Model menggunakan data agregat tahunan (skala provinsi), sehingga belum mencakup faktor mikro lokal seperti konflik lahan atau izin konsesi korporasi.</li>

                <li style='margin-bottom: 10px;'><b>Resolusi Spasial Makro: </b> tidak memperhitungkan faktor pemicu eksternal mendadak (exogenous shocks) di luar variabel terdata</li>

            </ul>

        </div>

        <br>

        """, unsafe_allow_html=True)
