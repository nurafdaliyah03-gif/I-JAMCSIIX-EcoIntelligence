print(df.head())
print(df.dtypes)
st.session_state.df = df
st.subheader("Cek Struktur Data")

st.write("5 Baris Awal:")
st.dataframe(df.head())

st.write("Tipe Data:")
st.write(df.dtypes.astype(str))
