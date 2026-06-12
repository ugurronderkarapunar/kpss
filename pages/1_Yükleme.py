import streamlit as st
from PIL import Image
import io
from utils.db import add_question, get_all_questions
from utils.ocr import ocr_turkish
from utils.parser import parse_question_text

st.set_page_config(page_title="Soru Yükleme", layout="wide")

st.title("📸 Soru Fotoğrafı Yükleme")

subjects = ["Türkçe", "Tarih", "Matematik", "Coğrafya", "Vatandaşlık"]
years = list(range(2015, 2026))

col1, col2 = st.columns(2)
with col1:
    selected_subject = st.selectbox("Ders Seçin", subjects)
with col2:
    selected_year = st.selectbox("Yıl Seçin", years)

uploaded_files = st.file_uploader(
    f"**{selected_subject} {selected_year}** için soru fotoğraflarını seçin (png, jpg)",
    type=["png", "jpg", "jpeg"],
    accept_multiple_files=True
)

if uploaded_files:
    if st.button("📥 Yükle ve OCR İşle", type="primary"):
        progress = st.progress(0, text="OCR işleniyor...")
        total = len(uploaded_files)
        for idx, file in enumerate(uploaded_files):
            # Fotoğrafı oku
            image_bytes = file.read()
            # OCR uygula
            raw_text = ocr_turkish(image_bytes)
            # Ayrıştır
            parsed = parse_question_text(raw_text)
            # Veritabanına ekle
            add_question(
                subject=selected_subject,
                year=selected_year,
                image_bytes=image_bytes,
                raw_text=raw_text,
                parsed=parsed
            )
            progress.progress((idx + 1) / total)
        st.success(f"{total} soru başarıyla yüklendi. İnceleme sayfasında düzenleyebilirsiniz.")
