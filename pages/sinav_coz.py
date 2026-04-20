import streamlit as st
import pandas as pd
from db import sorulari_getir, cevap_kaydet
from streamlit_drawable_canvas import st_canvas
import re

def sinav_coz():
    st.header("✍️ Sınav Çöz")
    
    # Çözüm tahtası için canvas boyutu
    canvas_result = st_canvas(
        fill_color="rgba(255, 165, 0, 0.3)",
        stroke_width=2,
        stroke_color="#000000",
        background_color="#FFFFFF",
        width=500,
        height=300,
        drawing_mode="freedraw",
        key="canvas",
    )
    
    if canvas_result.image_data is not None:
        st.image(canvas_result.image_data, caption="Çiziminiz")
    
    yillar = st.multiselect("Yıl(lar)", [2022,2023,2024,2025], default=[2025])
    dersler = st.multiselect("Ders(ler)", ["Matematik","Türkçe","Tarih","Coğrafya","Anayasa","Vatandaşlık"], default=["Matematik","Türkçe"])
    
    if st.button("Soruları Getir"):
        tum_sorular = pd.DataFrame()
        for d in dersler:
            df = sorulari_getir(ders_adi=d, yil_listesi=yillar)
            tum_sorular = pd.concat([tum_sorular, df])
        st.session_state['cozulen_sorular'] = tum_sorular.to_dict('records')
        st.success(f"{len(tum_sorular)} soru yüklendi.")
    
    if 'cozulen_sorular' in st.session_state:
        with st.form("cevap_formu"):
            cevaplar = {}
            cozum_metinleri = {}
            for idx, soru in enumerate(st.session_state['cozulen_sorular']):
                st.markdown(f"**Soru {idx+1}:** {soru['metin']}")
                if soru.get('formül'):
                    st.latex(soru['formül'])
                siklar = soru['siklar']
                secim = st.radio(f"Şıklar", list(siklar.keys()), format_func=lambda x: f"{x}: {siklar[x]}", key=f"soru_{idx}")
                cevaplar[soru['id']] = secim
                
                # Çözüm adımlarını yazma alanı
                cozum = st.text_area(f"Çözüm adımlarını yaz (soru {idx+1})", key=f"cozum_{idx}", height=100)
                cozum_metinleri[soru['id']] = cozum
            
            if st.form_submit_button("Cevapları ve Çözümleri Kaydet"):
                for soru_id, kullanici_sik in cevaplar.items():
                    soru = next(s for s in st.session_state['cozulen_sorular'] if s['id'] == soru_id)
                    dogru_mu = (kullanici_sik == soru['dogru_sik'])
                    
                    # Çözüm analizi (basit kelime eşleştirme)
                    cozum_metni = cozum_metinleri.get(soru_id, "")
                    hata_tipi = ""
                    hata_notu = ""
                    if not dogru_mu and cozum_metni:
                        # Basit analiz: "toplama", "çarpma", "bölme" gibi kelimeleri ara
                        if "topla" in cozum_metni.lower() or "çarp" in cozum_metni.lower():
                            hata_tipi = "islem_hatasi"
                            hata_notu = "İşlem hatası olabilir, adımları kontrol edin."
                        else:
                            hata_tipi = "konu_eksik"
                            hata_notu = "Konu eksikliği olabilir, tekrar çalışın."
                    
                    dogru_notu = ""
                    if dogru_mu and cozum_metni:
                        dogru_notu = "Çözüm adımlarınız doğru görünüyor. Diğer şıklar neden yanlış? " + \
                                     "A şıkkı: ... , B şıkkı: ... şeklinde not alabilirsiniz."
                    
                    cevap_kaydet(soru_id, kullanici_sik, dogru_mu, hata_notu, hata_tipi, dogru_notu)
                st.success("Cevaplar ve çözümler kaydedildi! Hata analizi için 'Hata Analizi' sayfasına gidin.")
