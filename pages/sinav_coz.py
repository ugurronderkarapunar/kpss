import streamlit as st
from db import sorulari_getir, cevap_kaydet

def sinav_coz():
    st.header("✍️ Sınav Çöz")
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
            for idx, soru in enumerate(st.session_state['cozulen_sorular']):
                st.markdown(f"**{soru['metin']}**")
                if soru.get('formül'):
                    st.latex(soru['formül'])
                siklar = soru['siklar']
                secim = st.radio(f"Şıklar (Soru {idx+1})", list(siklar.keys()), format_func=lambda x: f"{x}: {siklar[x]}", key=f"soru_{idx}")
                cevaplar[soru['id']] = secim
            
            if st.form_submit_button("Cevapları Kaydet"):
                for soru_id, kullanici_sik in cevaplar.items():
                    soru = next(s for s in st.session_state['cozulen_sorular'] if s['id'] == soru_id)
                    dogru_mu = (kullanici_sik == soru['dogru_sik'])
                    cevap_kaydet(soru_id, kullanici_sik, dogru_mu)
                st.success("Cevaplar kaydedildi!")
