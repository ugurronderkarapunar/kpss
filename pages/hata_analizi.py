import streamlit as st
import pandas as pd
from db import kullanici_istatistikleri, get_connection

def hata_analizi():
    st.header("📉 Hata Analizlerim")
    df_istatistik = kullanici_istatistikleri()
    if not df_istatistik.empty:
        st.dataframe(df_istatistik)
        # Hata tipi dağılım grafiği
        st.bar_chart(df_istatistik.set_index('hata_tipi')['hata_tipi_sayisi'])
    else:
        st.info("Henüz hiç sınav çözülmemiş.")
    
    st.subheader("Hata Notlarım")
    conn = get_connection()
    df_notlar = pd.read_sql_query('''
        SELECT s.metin, kc.hata_notu, kc.hata_tipi 
        FROM kullanici_cevaplari kc
        JOIN sorular s ON kc.soru_id = s.id
        WHERE kc.dogru_mu = 0 AND kc.hata_notu IS NOT NULL AND kc.hata_notu != ''
    ''', conn)
    conn.close()
    if not df_notlar.empty:
        for idx, row in df_notlar.iterrows():
            st.markdown(f"**Soru:** {row['metin'][:100]}...  \n**Hata Notu:** {row['hata_notu']}  \n**Tip:** {row['hata_tipi']}")
            st.divider()
    else:
        st.write("Henüz hata notu eklenmemiş.")
