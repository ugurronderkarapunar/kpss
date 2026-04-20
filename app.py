import streamlit as st
from db import init_db, get_connection
import pandas as pd
import plotly.express as px
from streamlit_folium import folium_static
import folium

st.set_page_config(page_title="KPSS Takip", layout="wide")
st.title("📚 KPSS Soru ve Hata Takip Programı")

# Veritabanını başlat
init_db()

# Sidebar navigasyon
st.sidebar.title("Menü")
sayfa = st.sidebar.radio("Git", ["Soru Yönetimi", "Sınav Çöz", "Hata Analizi", "İstatistikler", "Deneme Oluştur", "Konu Analizi"])

if sayfa == "Soru Yönetimi":
    st.header("📝 Soru Girişi")
    with st.form("soru_formu"):
        ders = st.selectbox("Ders", ["Matematik", "Türkçe", "Tarih", "Coğrafya", "Anayasa", "Vatandaşlık"])
        konu = st.text_input("Konu (örnek: Üslü Sayılar, Noktalama İşaretleri vb.)")
        yil = st.number_input("Yıl", min_value=2000, max_value=2025, step=1)
        soru_metni = st.text_area("Soru Metni")
        
        # Şıklar
        col1, col2 = st.columns(2)
        with col1:
            sik_a = st.text_input("A Şıkkı")
            sik_c = st.text_input("C Şıkkı")
            sik_e = st.text_input("E Şıkkı (isteğe bağlı)")
        with col2:
            sik_b = st.text_input("B Şıkkı")
            sik_d = st.text_input("D Şıkkı")
        
        sıklar = {"A": sik_a, "B": sik_b, "C": sik_c, "D": sik_d}
        if sik_e:
            sıklar["E"] = sik_e
        
        dogru_sik = st.selectbox("Doğru Şık", list(sıklar.keys()))
        
        # Matematiksel formül (LaTeX)
        formül = st.text_area("Matematiksel Formül (LaTeX formatında, örn: $2^2$)", "")
        
        # Coğrafya haritası (eğer ders Coğrafya ise)
        harita_verisi = None
        if ders == "Coğrafya":
            st.subheader("🗺️ Türkiye Haritası İşaretleme")
            m = folium.Map(location=[39.0, 35.0], zoom_start=6)
            folium.Marker([39.0, 35.0], popup="Örnek nokta").add_to(m)
            folium_static(m)
            harita_verisi = st.text_area("Harita koordinatları (JSON veya 'İç Anadolu' gibi metin)", "")
        
        submitted = st.form_submit_button("Soruyu Kaydet")
        if submitted:
            # Veritabanına ekle (kod tamamlanacak)
            st.success("Soru başarıyla eklendi!")
    
elif sayfa == "Sınav Çöz":
    st.header("✍️ Sınav Çöz")
    # Yıl ve ders filtreleri
    yil_filtre = st.multiselect("Yıl(lar)", [2022,2023,2024,2025], default=[2025])
    ders_filtre = st.multiselect("Ders(ler)", ["Matematik","Türkçe","Tarih","Coğrafya","Anayasa","Vatandaşlık"], default=["Matematik","Türkçe"])
    
    # Soruları getir
    conn = get_connection()
    # ... sorgu yap, soruları listele
    st.info("Burada sorular listelenir, kullanıcı cevaplarını işaretler, doğru/yanlış kaydedilir.")
    # Cevaplama mantığı: Her soru için radio buton, "Cevapları Kaydet" butonu
    
elif sayfa == "Hata Analizi":
    st.header("📉 Hata Analizlerim")
    # Yanlış yapılan soruları getir, konu bazlı grupla
    # Hata tiplerine göre dağılım grafiği
    st.write("Yanlış yapılan sorular ve hata nedenleri:")
    # Örnek veri gösterimi
    data = pd.DataFrame({
        "Konu": ["Üslü Sayılar", "Noktalama", "Kurtuluş Savaşı"],
        "Yanlış Sayısı": [5, 2, 3],
        "Hata Tipi": ["işlem hatası", "konu eksik", "konu eksik"]
    })
    st.bar_chart(data, x="Konu", y="Yanlış Sayısı")
    
    # Kullanıcının hata notlarını göster
    st.subheader("Hata Notlarım")
    # ... veritabanından notları çek
    
elif sayfa == "İstatistikler":
    st.header("📊 Netlerim ve Puan Tahmini")
    # Doğru yanlış sayıları hesapla
    dogru_sayisi = 85
    yanlis_sayisi = 20
    net = dogru_sayisi - yanlis_sayisi/4
    tahmini_puan = 60 + (net - 40) * 0.8  # basit örnek formül
    st.metric("Net", f"{net:.2f}")
    st.metric("Tahmini KPSS Puanı", f"{tahmini_puan:.1f}")
    
    # Zaman içinde net değişimi (deneme sınavlarından)
    # ... grafik
    
elif sayfa == "Deneme Oluştur":
    st.header("🎯 2026 Tahmini Deneme Sınavı")
    st.write("Her 4 ayda bir yapılacak genel deneme. Aşağıdaki butona tıklayarak yeni deneme oluşturun.")
    if st.button("Yeni Deneme Başlat"):
        # Rastgele sorular seç (yanlış yapılan konulardan ağırlıklı)
        # Veritabanından 120 soru seç, kullanıcıya sun
        st.success("Deneme oluşturuldu. Şimdi çözmeye başlayın!")
        # Yönlendirme veya aynı sayfada soruları göster
        
elif sayfa == "Konu Analizi":
    st.header("📈 Konu Bazlı Çıkmış Soru Analizi")
    # Son 3 yılın sorularını analiz et: hangi konudan kaç soru çıkmış, zorlaşma trendi
    st.write("Örnek: Matematik - Üslü Sayılar")
    col1, col2 = st.columns(2)
    with col1:
        st.metric("2025'te Çıkan Soru Sayısı", 3, delta="+1")
    with col2:
        st.metric("Zorluk Seviyesi", "Orta", delta="Arttı")
    # Konular listesi ve yıllara göre çıkma sıklığı grafiği
