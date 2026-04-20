import streamlit as st
from db import soru_ekle, ders_id_getir, konu_ekle

def soru_yonetimi():
    st.header("📝 Soru Girişi")
    with st.form("soru_formu"):
        ders = st.selectbox("Ders", ["Matematik", "Türkçe", "Tarih", "Coğrafya", "Anayasa", "Vatandaşlık"])
        konu = st.text_input("Konu")
        yil = st.number_input("Yıl", min_value=2000, max_value=2025, step=1)
        soru_metni = st.text_area("Soru Metni")
        
        col1, col2 = st.columns(2)
        with col1:
            sik_a = st.text_input("A Şıkkı")
            sik_c = st.text_input("C Şıkkı")
            sik_e = st.text_input("E Şıkkı (opsiyonel)")
        with col2:
            sik_b = st.text_input("B Şıkkı")
            sik_d = st.text_input("D Şıkkı")
        
        siklar = {"A": sik_a, "B": sik_b, "C": sik_c, "D": sik_d}
        if sik_e:
            siklar["E"] = sik_e
        
        dogru_sik = st.selectbox("Doğru Şık", list(siklar.keys()))
        formül = st.text_area("LaTeX Formül (örnek: $2^2$)", "")
        harita_verisi = st.text_area("Harita verisi (Coğrafya için)", "")
        
        submitted = st.form_submit_button("Soruyu Kaydet")
        if submitted:
            if soru_ekle(ders, konu, yil, soru_metni, siklar, dogru_sik, formül, harita_verisi):
                st.success("Soru eklendi!")
            else:
                st.error("Hata oluştu.")
