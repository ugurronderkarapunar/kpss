import streamlit as st
import pandas as pd
from db import soru_ekle, sorulari_getir, get_connection

def soru_yonetimi():
    st.header("📝 Soru Girişi")
    with st.form("soru_formu"):
        ders = st.selectbox("Ders", ["Matematik", "Türkçe", "Tarih", "Coğrafya", "Anayasa", "Vatandaşlık"])
        konu = st.text_input("Konu")
        yil = st.number_input("Yıl", min_value=2000, max_value=2025, step=1)
        soru_metni = st.text_area("Soru Metni (LaTeX destekler: $2^2$)")
        
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
        formül = st.text_area("LaTeX Formül (sadece matematik ifade)", "")
        harita_verisi = st.text_area("Harita verisi (Coğrafya için)", "")
        
        submitted = st.form_submit_button("Soruyu Kaydet")
        if submitted:
            if soru_ekle(ders, konu, yil, soru_metni, siklar, dogru_sik, formül, harita_verisi):
                st.success("Soru eklendi!")
            else:
                st.error("Hata oluştu.")
    
    st.divider()
    st.subheader("📋 Kayıtlı Sorularım")
    
    # Filtreler
    col1, col2 = st.columns(2)
    with col1:
        ders_filtre = st.selectbox("Ders filtresi", ["Tümü"] + ["Matematik", "Türkçe", "Tarih", "Coğrafya", "Anayasa", "Vatandaşlık"])
    with col2:
        yil_filtre = st.multiselect("Yıl filtresi", [2022,2023,2024,2025], default=[])
    
    sorular_df = sorulari_getir()
    if not sorular_df.empty:
        if ders_filtre != "Tümü":
            sorular_df = sorular_df[sorular_df['ders'] == ders_filtre]
        if yil_filtre:
            sorular_df = sorular_df[sorular_df['yil'].isin(yil_filtre)]
        
        # Gösterim için sadeleştirilmiş tablo
        gosterim_df = sorular_df[['id', 'ders', 'konu', 'yil', 'metin']].copy()
        gosterim_df['metin'] = gosterim_df['metin'].str[:50] + "..."
        st.dataframe(gosterim_df, use_container_width=True)
        
        # Silme işlemi
        silinecek_id = st.number_input("Silmek istediğiniz soru ID'si", min_value=0, step=1)
        if st.button("Soru Sil"):
            conn = get_connection()
            conn.execute("DELETE FROM sorular WHERE id = ?", (silinecek_id,))
            conn.commit()
            conn.close()
            st.success(f"{silinecek_id} ID'li soru silindi.")
            st.rerun()
    else:
        st.info("Henüz hiç soru eklenmemiş.")
