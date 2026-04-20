import streamlit as st
from db import sorulari_getir, deneme_ekle, net_hesapla, puan_tahmini
import random

def deneme_olustur():
    st.header("🎯 2026 Tahmini Deneme Sınavı")
    if st.button("Yeni Deneme Oluştur"):
        # 120 soruluk rastgele seçim (gerçekte konu ağırlıklarına göre yapılmalı)
        tum_sorular = sorulari_getir()  # tüm sorular
        if len(tum_sorular) < 120:
            st.warning("Yeterli soru yok. Önce soru ekleyin.")
            return
        secilen_sorular = tum_sorular.sample(n=120).to_dict('records')
        st.session_state['deneme_sorulari'] = secilen_sorular
        st.success("Deneme oluşturuldu. Şimdi çözmeye başlayın!")
    
    if 'deneme_sorulari' in st.session_state:
        with st.form("deneme_formu"):
            cevaplar = {}
            for idx, soru in enumerate(st.session_state['deneme_sorulari']):
                st.markdown(f"**{idx+1}. {soru['metin']}**")
                siklar = soru['siklar']
                secim = st.radio("", list(siklar.keys()), format_func=lambda x: f"{x}: {siklar[x]}", key=f"deneme_{idx}")
                cevaplar[soru['id']] = secim
            if st.form_submit_button("Denemeyi Bitir"):
                dogru_say = 0
                for soru_id, kullanici_sik in cevaplar.items():
                    soru = next(s for s in st.session_state['deneme_sorulari'] if s['id'] == soru_id)
                    if kullanici_sik == soru['dogru_sik']:
                        dogru_say += 1
                net = dogru_say - (120 - dogru_say)/4
                puan = puan_tahmini(net)
                deneme_ekle(net, puan)
                st.success(f"Deneme tamamlandı! Net: {net:.2f}, Tahmini Puan: {puan:.1f}")
                del st.session_state['deneme_sorulari']
