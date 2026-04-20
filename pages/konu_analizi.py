import streamlit as st
from db import konu_bazli_cikmissoru_analizi
import plotly.express as px

def konu_analizi():
    st.header("📈 Konu Bazlı Çıkmış Soru Analizi")
    ders = st.selectbox("Ders Seç", ["Matematik", "Türkçe", "Tarih", "Coğrafya", "Anayasa", "Vatandaşlık"])
    yil_aralik = st.slider("Yıl Aralığı", 2022, 2025, (2022, 2025))
    
    df = konu_bazli_cikmissoru_analizi(ders, list(yil_aralik))
    if not df.empty:
        fig = px.bar(df, x='konu', y='soru_sayisi', color='yil', title=f"{ders} - Yıllara Göre Soru Dağılımı")
        st.plotly_chart(fig)
        # Zorlaşma trendi göstergesi (basit)
        st.subheader("Zorlaşma Trendi")
        for konu in df['konu'].unique():
            df_konu = df[df['konu'] == konu]
            if len(df_konu) > 1:
                artis = df_konu['soru_sayisi'].diff().fillna(0).iloc[-1]
                if artis > 0:
                    st.write(f"📈 {konu}: Son yılda soru sayısı {artis} arttı.")
                elif artis < 0:
                    st.write(f"📉 {konu}: Son yılda soru sayısı {abs(artis)} azaldı.")
    else:
        st.info("Bu ders için henüz soru girilmemiş.")
