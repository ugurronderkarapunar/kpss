import streamlit as st

st.set_page_config(page_title="KPSS Soru Analiz", layout="wide")

st.title("📚 KPSS Çıkmış Soru Benzerlik Analizi")
st.markdown("""
Bu uygulama ile 2015‑2025 arası KPSS sorularını yükleyebilir,  
OCR metinlerini düzeltebilir, sorular arasındaki benzerlikleri  
ve yanlış cevapların başka yıllarda doğru cevaba dönüşme durumlarını inceleyebilirsin.
""")
st.info("👉 Sol kenar çubuğundaki sayfalara geçiş yaparak işlemlere başlayabilirsin.")
