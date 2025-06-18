import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from fpdf import FPDF
import tempfile
import os

st.set_page_config(page_title="📊 Raporttigeneraattori", layout="centered")
st.title("📊 Raporttigeneraattori")

uploaded_file = st.file_uploader("Lataa Excel- tai CSV-tiedosto", type=["xlsx", "csv"])

if uploaded_file:
    try:
        if uploaded_file.name.endswith(".csv"):
            df = pd.read_csv(uploaded_file)
        else:
            df = pd.read_excel(uploaded_file, engine="openpyxl")
    except Exception as e:
        st.error(f"Tiedoston lukeminen epäonnistui: {e}")
        st.stop()

    st.subheader("📋 Esikatselu datasta")
    st.dataframe(df.head())

    # ✅ Suodatus kategorian mukaan
    if "Kategoria" in df.columns:
        kategoriat = df["Kategoria"].dropna().unique().tolist()
        valitut = st.multiselect("Valitse halutut kategoriat", kategoriat, default=kategoriat)
        df = df[df["Kategoria"].isin(valitut)]

    # 📊 Kaavio: Summa per Kategoria
    if "Kategoria" in df.columns and "Summa" in df.columns:
        st.subheader("📌 Yhteenveto: Summa per Kategoria")
        try:
            grouped = df.groupby("Kategoria")["Summa"].sum().sort_values(ascending=False)

            fig, ax = plt.subplots()
            grouped.plot(kind="bar", ax=ax, color="skyblue")
            ax.set_ylabel("Summa (€)")
            ax.set_title("Summa per Kategoria")
            st.pyplot(fig)
        except Exception as e:
            st.warning(f"Kaavion luonti epäonnistui: {e}")
    else:
        st.warning("Sarakkeet 'Kategoria' ja 'Summa' puuttuvat. Kaaviota ei voi näyttää.")

    # 📈 Tilastot
    st.subheader("📑 Perustilastot")
    try:
        st.write(f"Rivejä yhteensä: {len(df)}")
        st.write(f"Sarakkeita yhteensä: {len(df.columns)}")

        if "Summa" in df.columns:
            st.metric("Summa yhteensä", f"{df['Summa'].sum():,.2f} €")
            st.write(f"Keskimääräinen: {df['Summa'].mean():,.2f} €")
            st.write(f"Mediaani: {df['Summa'].median():,.2f} €")
            st.write(f"Maksimi: {df['Summa'].max():,.2f} €")
    except:
        st.warning("Tilastojen laskeminen epäonnistui.")

    # 💾 CSV-lataus
    st.download_button("📥 Lataa suodatettu data CSV:nä", df.to_csv(index=False), "raportti.csv", "text/csv")

    # 📄 PDF-raportin luonti
    if "grouped" in locals():
        st.subheader("📤 Lataa PDF-raportti")

        # Tallenna kaavio tilapäisesti
        kuva_path = os.path.join(tempfile.gettempdir(), "kaavio.png")
        fig.savefig(kuva_path)

        def luo_pdf(yhteenveto, kuva_path):
            pdf = FPDF()
            pdf.add_page()
            pdf.set_font("Arial", "B", 16)
            pdf.cell(40, 10, "Raportti")
            pdf.ln(20)

            pdf.set_font("Arial", "", 12)
            pdf.multi_cell(0, 10, yhteenveto)
            try:
                pdf.image(kuva_path, x=10, y=80, w=180)
            except:
                pass
            return pdf.output(dest="S").encode("latin-1")

        yhteenveto_teksti = grouped.to_string()
        pdf_bytes = luo_pdf(yhteenveto_teksti, kuva_path)

        st.download_button("📥 Lataa raportti PDF:nä", data=pdf_bytes, file_name="raportti.pdf")

else:
    st.info("Lataa ensin tiedosto aloittaaksesi.")