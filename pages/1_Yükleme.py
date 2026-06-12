import streamlit as st
from utils.db import add_question, get_all_questions
from utils.ocr import ocr_turkish
from utils.parser import parse_question_text

st.set_page_config(page_title="Soru Yükleme", layout="wide")

st.title("📸 KPSS Soru Yükleme Slotları")
st.markdown("Her ders ve yıl için ayrı yükleme alanı. İlgili slota tıklayıp soruları yükleyin.")

subjects = ["Türkçe", "Tarih", "Matematik", "Coğrafya", "Vatandaşlık"]
years = list(range(2015, 2026))

# Mevcut yükleme sayılarını hesapla
all_questions = get_all_questions()
upload_counts = {}
for q in all_questions:
    key = (q.subject, q.year)
    upload_counts[key] = upload_counts.get(key, 0) + 1

# Izgara: her satır bir ders, her sütun bir yıl
cols_per_year = 6  # Aynı anda 6 yıl gösterelim, alta kaydıralım
year_chunks = [years[i:i+cols_per_year] for i in range(0, len(years), cols_per_year)]

for subject in subjects:
    st.subheader(f"📘 {subject}")
    for chunk in year_chunks:
        cols = st.columns(len(chunk))
        for idx, year in enumerate(chunk):
            with cols[idx]:
                slot_key = f"{subject}_{year}"
                count = upload_counts.get((subject, year), 0)
                # Slot başlığı ve sayaç
                st.markdown(f"**{year}**  \n📂 {count} soru")
                # Her slot için expander içinde yükleme alanı
                with st.expander("➕ Yükle", expanded=False):
                    uploaded_files = st.file_uploader(
                        "Fotoğraf seç (png,jpg)",
                        type=["png", "jpg", "jpeg"],
                        accept_multiple_files=True,
                        key=f"upload_{slot_key}"
                    )
                    if uploaded_files:
                        if st.button(f"📥 {year} yılını kaydet", key=f"btn_{slot_key}"):
                            progress = st.progress(0, text="OCR işleniyor...")
                            total = len(uploaded_files)
                            for i, file in enumerate(uploaded_files):
                                image_bytes = file.read()
                                raw_text = ocr_turkish(image_bytes)
                                parsed = parse_question_text(raw_text)
                                add_question(
                                    subject=subject,
                                    year=year,
                                    image_bytes=image_bytes,
                                    raw_text=raw_text,
                                    parsed=parsed
                                )
                                progress.progress((i + 1) / total)
                            st.success(f"{total} soru eklendi.")
                            st.rerun()
