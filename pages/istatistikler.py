import streamlit as st
from db import net_hesapla, puan_tahmini, denemeleri_getir
import plotly.express as px

def istatistikler():
    st.header("📊 Netlerim ve Puan Tahmini")
    net, dogru, yanlis = net_hesapla()
    puan = puan_tahmini(net)
    col1, col2, col3 = st.columns(3)
    col1.metric("Doğru", dogru)
    col2.metric("Yanlış", yanlis)
    col3.metric("Net", f"{net:.2f}")
    st.metric("Tahmini KPSS Puanı", f"{puan:.1f}")
    
    st.subheader("Deneme Sınavları Gelişimi")
    df_deneme = denemeleri_getir()
    if not df_deneme.empty:
        fig = px.line(df_deneme, x='tarih', y='net', title='Netlerin Zamanla Değişimi')
        st.plotly_chart(fig)
    else:
        st.info("Henüz deneme sınavı yapılmamış.")
