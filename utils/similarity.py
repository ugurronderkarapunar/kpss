import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np
import re

def build_tfidf_vectorizer(texts):
    """Türkçe stopwords ve karakter tabanlı n-gram eklenmiş TF-IDF."""
    vectorizer = TfidfVectorizer(
        analyzer='word',
        ngram_range=(1, 2),          # kelime ikilileri
        stop_words='english',        # Türkçe stopwords listesi eklenebilir
        lowercase=True
    )
    # Özel Türkçe stopwords (basit bir set)
    turkish_stops = [
        've', 'veya', 'bir', 'bu', 'şu', 'o', 'ile', 'için', 'da', 'de', 'mi', 'mu',
        'ne', 'neden', 'nasıl', 'hangi', 'daha', 'en', 'çok', 'az', 'ama', 'fakat'
    ]
    vectorizer.set_params(stop_words=vectorizer.get_params()['stop_words'] or 'english')
    # sklearn'in stop_words parametresine liste verebiliriz ama burada basit tutuyoruz.
    # Daha iyisi: from nltk.corpus import stopwords (ek kurulum istememek için listeden verdim)
    vectorizer.stop_words = turkish_stops
    return vectorizer

def compute_similarity_matrix(questions):
    """Soru köklerinden TF-IDF matrisi ve kosinüs benzerliği döndürür."""
    texts = [q.question_text if q.question_text else "" for q in questions]
    vectorizer = build_tfidf_vectorizer(texts)
    tfidf = vectorizer.fit_transform(texts)
    sim = cosine_similarity(tfidf)
    return sim

def find_similar_questions(questions, threshold=0.75):
    """Benzerlik eşiğini geçen soru çiftlerini bulur."""
    sim = compute_similarity_matrix(questions)
    pairs = []
    n = len(questions)
    for i in range(n):
        for j in range(i+1, n):
            if sim[i][j] >= threshold:
                pairs.append((i, j, sim[i][j]))
    # Benzerlik skoruna göre sırala
    pairs.sort(key=lambda x: x[2], reverse=True)
    return pairs

def compute_option_similarity(option_texts, correct_texts):
    """
    Tüm yanlış seçenek metinleri ile tüm doğru cevap metinleri arasındaki
    en yüksek benzerlikleri hesaplar.
    option_texts: liste (yanlış seçenek metinleri)
    correct_texts: liste (doğru cevap metinleri)
    Döndürür: (max_sim, matched_opt, matched_correct)
    """
    if not option_texts or not correct_texts:
        return 0, None, None
    vectorizer = build_tfidf_vectorizer(option_texts + correct_texts)
    all_vecs = vectorizer.fit_transform(option_texts + correct_texts)
    n_opt = len(option_texts)
    opt_vecs = all_vecs[:n_opt]
    corr_vecs = all_vecs[n_opt:]
    sim_matrix = cosine_similarity(opt_vecs, corr_vecs)
    max_idx = np.unravel_index(np.argmax(sim_matrix), sim_matrix.shape)
    return sim_matrix[max_idx], option_texts[max_idx[0]], correct_texts[max_idx[1]]
