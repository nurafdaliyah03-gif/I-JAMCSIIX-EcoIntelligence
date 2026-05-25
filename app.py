if 'df' not in st.session_state: 
    url = "https://raw.githubusercontent.com/nurafdaliyah03-gif/I-JAMCSIIX-EcoIntelligence/refs/heads/main/data_jamsicx.csv"
    
    df = pd.read_csv(url)

    df.columns = df.columns.str.strip()
    df['PROVINSI'] = df['PROVINSI'].astype(str).str.strip().str.upper()

    st.session_state.df = df


# CEK STRUKTUR DATA (SEMENTARA)
st.subheader("Cek Struktur Data")

st.write("5 Baris Awal:")
st.dataframe(st.session_state.df.head())

st.write("Tipe Data:")
st.write(st.session_state.df.dtypes.astype(str))
