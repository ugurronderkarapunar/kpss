import streamlit as st
import pandas as pd
from utils.db import get_all_questions
from utils.similarity import find_similar_questions, compute_option_similarity

st.set_page_config(page_title="Benzerlik Analizi", layout="wide")

st.title("🔬 Soru Benzerlik Analizi")

if st.button("🔍 Analizi Başlat", type="primary"):
    with st.spinner("Tüm sorular taranıyor..."):
        questions = get_all_questions()
        if len(questions) < 2:
            st.error("Analiz için en az 2 soru gerekli.")
        else:
            # 1. Soru kökü benzerlikleri
            sim_pairs = find_similar_questions(questions, threshold=0.75)
            
            # Sonuçları tabloya dönüştür
            similar_rows = []
            for i, j, score in sim_pairs:
                q1 = questions[i]
                q2 = questions[j]
                similar_rows.append({
                    "Ders": q1.subject,
                    "Yıl 1": q1.year,
                    "Soru 1 (ID)": q1.id,
                    "Soru 1 Metin": q1.question_text[:100] + "...",
                    "Yıl 2": q2.year,
                    "Soru 2 (ID)": q2.id,
                    "Soru 2 Metin": q2.question_text[:100] + "...",
                    "Benzerlik": f"{score:.2f}"
                })
            
            df_sim = pd.DataFrame(similar_rows)
            
            # 2. Yanlış → Doğru cevap analizi (aynı ders için)
            # Verimlilik için aynı ders içinde bakalım
            subjects_set = set(q.subject for q in questions)
            swap_rows = []
            for subj in subjects_set:
                subj_questions = [q for q in questions if q.subject == subj]
                n = len(subj_questions)
                for i in range(n):
                    qi = subj_questions[i]
                    if not qi.correct_answer:
                        continue
                    # Yanlış seçenekleri bul
                    wrong_opts = []
                    for opt in ['A','B','C','D','E']:
                        if opt != qi.correct_answer:
                            text = getattr(qi, f"option_{opt.lower()}", "")
                            if text:
                                wrong_opts.append(text)
                    # Diğer soruların doğru cevap metinleri
                    for j in range(n):
                        if i == j:
                            continue
                        qj = subj_questions[j]
                        if not qj.correct_answer:
                            continue
                        correct_text = getattr(qj, f"option_{qj.correct_answer.lower()}", "")
                        if not correct_text:
                            continue
                        sim, matched_opt, matched_cor = compute_option_similarity(
                            wrong_opts, [correct_text]
                        )
                        if sim > 0.70:   # eşik
                            swap_rows.append({
                                "Ders": subj,
                                "Yıl (Yanlış)": qi.year,
                                "Soru ID (Yanlış)": qi.id,
                                "Yanlış Seçenek": matched_opt[:80],
                                "Yıl (Doğru)": qj.year,
                                "Soru ID (Doğru)": qj.id,
                                "Doğru Cevap": matched_cor[:80],
                                "Benzerlik": f"{sim:.2f}"
                            })
            
            df_swap = pd.DataFrame(swap_rows)
            
            # Görüntüle
            st.subheader("📊 Benzer Soru Çiftleri")
            if df_sim.empty:
                st.info("Eşiğin üzerinde benzer soru bulunamadı.")
            else:
                st.dataframe(df_sim, use_container_width=True)
            
            st.subheader("🔄 Yanlış Cevap Başka Yılda Doğru Cevap Olmuş mu?")
            if df_swap.empty:
                st.info("Bu tür bir dönüşüm tespit edilemedi.")
            else:
                st.dataframe(df_swap, use_container_width=True)
else:
    st.info("Analizi başlatmak için butona tıklayın. Soruların OCR düzeltmeleri tamamlanmış olmalı.")
