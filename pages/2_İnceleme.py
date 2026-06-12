import streamlit as st
import pandas as pd
from utils.db import get_all_questions, update_question, delete_all
from PIL import Image
import io

st.set_page_config(page_title="OCR İnceleme ve Düzeltme", layout="wide")

st.title("🔎 OCR Sonuçlarını İncele")

subjects = ["Tümü", "Türkçe", "Tarih", "Matematik", "Coğrafya", "Vatandaşlık"]
years = ["Tümü"] + list(range(2015, 2026))

col1, col2, col3 = st.columns(3)
with col1:
    filter_subject = st.selectbox("Ders", subjects)
with col2:
    filter_year = st.selectbox("Yıl", years)
with col3:
    st.write("")
    st.write("")
    if st.button("🔄 Listeyi Güncelle"):
        st.rerun()

# Sorgu parametrelerini ayarla
subj = None if filter_subject == "Tümü" else filter_subject
yr = None if filter_year == "Tümü" else int(filter_year)
questions = get_all_questions(subject=subj, year=yr)

if not questions:
    st.warning("Henüz soru yüklenmemiş. Önce yükleme sayfasından soru ekleyin.")
else:
    st.info(f"Toplam {len(questions)} soru listeleniyor.")
    for q in questions:
        with st.expander(f"📌 {q.subject} {q.year} - ID: {q.id}"):
            col_img, col_text = st.columns([1, 2])
            with col_img:
                if q.image:
                    img = Image.open(io.BytesIO(q.image))
                    st.image(img, caption="Yüklenen Fotoğraf", use_column_width=True)
                else:
                    st.text("Fotoğraf yok")
            with col_text:
                # Düzenlenebilir metin alanları
                question_text = st.text_area("Soru Kökü", value=q.question_text or "", height=100)
                opt_a = st.text_area("A)", value=q.option_a or "", height=50)
                opt_b = st.text_area("B)", value=q.option_b or "", height=50)
                opt_c = st.text_area("C)", value=q.option_c or "", height=50)
                opt_d = st.text_area("D)", value=q.option_d or "", height=50)
                opt_e = st.text_area("E)", value=q.option_e or "", height=50)

                # Doğru cevap seçimi
                current_answer = q.correct_answer if q.correct_answer else 'A'
                answer_index = ['A','B','C','D','E'].index(current_answer) if current_answer in ['A','B','C','D','E'] else 0
                correct = st.radio("Doğru Cevap", ['A','B','C','D','E'], index=answer_index, horizontal=True)

                if st.button("💾 Kaydet", key=f"save_{q.id}"):
                    update_question(
                        q.id,
                        question_text=question_text,
                        option_a=opt_a,
                        option_b=opt_b,
                        option_c=opt_c,
                        option_d=opt_d,
                        option_e=opt_e,
                        correct_answer=correct
                    )
                    st.success(f"Soru {q.id} güncellendi.")
                    st.rerun()

    # Tüm verileri silme (opsiyonel)
    st.divider()
    if st.button("⚠️ Tüm Soruları Sil", type="secondary"):
        delete_all()
        st.warning("Tüm sorular silindi. Sayfayı yenileyin.")
        st.rerun()
