import sqlite3
import json
import pandas as pd
from datetime import datetime

def get_connection():
    return sqlite3.connect("kpss.db", check_same_thread=False)

def init_db():
    conn = get_connection()
    cursor = conn.cursor()
    
    # Dersler
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS dersler (
            id INTEGER PRIMARY KEY,
            ad TEXT UNIQUE,
            soru_sayisi INTEGER
        )
    ''')
    
    # Konular
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS konular (
            id INTEGER PRIMARY KEY,
            ders_id INTEGER,
            ad TEXT,
            FOREIGN KEY(ders_id) REFERENCES dersler(id)
        )
    ''')
    
    # Sorular
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sorular (
            id INTEGER PRIMARY KEY,
            ders_id INTEGER,
            konu_id INTEGER,
            yil INTEGER,
            metin TEXT,
            siklar TEXT,      -- JSON: {"A":"...", "B":"...", "C":"...", "D":"...", "E":"..."}
            dogru_sik CHAR(1),
            formül TEXT,
            harita_verisi TEXT,
            FOREIGN KEY(ders_id) REFERENCES dersler(id),
            FOREIGN KEY(konu_id) REFERENCES konular(id)
        )
    ''')
    
    # Kullanıcı cevapları
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS kullanici_cevaplari (
            id INTEGER PRIMARY KEY,
            soru_id INTEGER,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            kullanici_sik CHAR(1),
            dogru_mu BOOLEAN,
            hata_notu TEXT,
            hata_tipi TEXT,
            dogru_notu TEXT,
            FOREIGN KEY(soru_id) REFERENCES sorular(id)
        )
    ''')
    
    # Deneme sınavları
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS denemeler (
            id INTEGER PRIMARY KEY,
            tarih TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            net REAL,
            puan REAL
        )
    ''')
    
    # Tahmini sorular
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS tahmini_sorular (
            id INTEGER PRIMARY KEY,
            soru_metni TEXT,
            siklar TEXT,
            dogru_sik CHAR(1),
            aciklama TEXT,
            olusturma_tarihi TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    # Ön tanımlı dersler
    dersler = [
        ("Matematik", 30),
        ("Türkçe", 30),
        ("Tarih", 27),
        ("Coğrafya", 17),
        ("Anayasa", 10),
        ("Vatandaşlık", 6)
    ]
    cursor.executemany("INSERT OR IGNORE INTO dersler (ad, soru_sayisi) VALUES (?, ?)", dersler)
    
    conn.commit()
    conn.close()

# ---------- Ders ve Konu İşlemleri ----------
def ders_id_getir(ders_adi):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT id FROM dersler WHERE ad = ?", (ders_adi,))
    result = cursor.fetchone()
    conn.close()
    return result[0] if result else None

def konu_ekle(ders_adi, konu_adi):
    ders_id = ders_id_getir(ders_adi)
    if not ders_id:
        return None
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT OR IGNORE INTO konular (ders_id, ad) VALUES (?, ?)", (ders_id, konu_adi))
    conn.commit()
    cursor.execute("SELECT id FROM konular WHERE ders_id = ? AND ad = ?", (ders_id, konu_adi))
    konu_id = cursor.fetchone()[0]
    conn.close()
    return konu_id

# ---------- Soru İşlemleri ----------
def soru_ekle(ders_adi, konu_adi, yil, metin, siklar_dict, dogru_sik, formül="", harita_verisi=""):
    ders_id = ders_id_getir(ders_adi)
    if not ders_id:
        return False
    konu_id = konu_ekle(ders_adi, konu_adi)
    siklar_json = json.dumps(siklar_dict, ensure_ascii=False)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO sorular (ders_id, konu_id, yil, metin, siklar, dogru_sik, formül, harita_verisi)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
    ''', (ders_id, konu_id, yil, metin, siklar_json, dogru_sik, formül, harita_verisi))
    conn.commit()
    conn.close()
    return True

def sorulari_getir(ders_adi=None, yil_listesi=None, konu_adi=None):
    conn = get_connection()
    query = '''
        SELECT s.id, d.ad AS ders, k.ad AS konu, s.yil, s.metin, s.siklar, s.dogru_sik, s.formül, s.harita_verisi
        FROM sorular s
        JOIN dersler d ON s.ders_id = d.id
        JOIN konular k ON s.konu_id = k.id
        WHERE 1=1
    '''
    params = []
    if ders_adi:
        query += " AND d.ad = ?"
        params.append(ders_adi)
    if yil_listesi:
        placeholders = ','.join(['?']*len(yil_listesi))
        query += f" AND s.yil IN ({placeholders})"
        params.extend(yil_listesi)
    if konu_adi:
        query += " AND k.ad = ?"
        params.append(konu_adi)
    df = pd.read_sql_query(query, conn, params=params)
    conn.close()
    # siklar sütununu JSON'dan dict'e çevir
    if not df.empty:
        df['siklar'] = df['siklar'].apply(json.loads)
    return df

# ---------- Cevap Kaydetme ----------
def cevap_kaydet(soru_id, kullanici_sik, dogru_mu, hata_notu="", hata_tipi="", dogru_notu=""):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO kullanici_cevaplari (soru_id, kullanici_sik, dogru_mu, hata_notu, hata_tipi, dogru_notu)
        VALUES (?, ?, ?, ?, ?, ?)
    ''', (soru_id, kullanici_sik, dogru_mu, hata_notu, hata_tipi, dogru_notu))
    conn.commit()
    conn.close()

def kullanici_istatistikleri():
    conn = get_connection()
    query = '''
        SELECT 
            SUM(CASE WHEN dogru_mu = 1 THEN 1 ELSE 0 END) as dogru_sayisi,
            SUM(CASE WHEN dogru_mu = 0 THEN 1 ELSE 0 END) as yanlis_sayisi,
            hata_tipi, COUNT(*) as hata_tipi_sayisi
        FROM kullanici_cevaplari
        GROUP BY hata_tipi
    '''
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

def net_hesapla():
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*) FROM kullanici_cevaplari WHERE dogru_mu = 1")
    dogru = cursor.fetchone()[0]
    cursor.execute("SELECT COUNT(*) FROM kullanici_cevaplari WHERE dogru_mu = 0")
    yanlis = cursor.fetchone()[0]
    conn.close()
    net = dogru - (yanlis / 4)
    return net, dogru, yanlis

def puan_tahmini(net):
    # Örnek formül: taban 60, net 40 üzeri her +1 net +0.8 puan
    return 60 + (net - 40) * 0.8 if net > 40 else 60 + (net - 40) * 0.6

# ---------- Deneme Sınavları ----------
def deneme_ekle(net, puan):
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute("INSERT INTO denemeler (net, puan) VALUES (?, ?)", (net, puan))
    conn.commit()
    conn.close()

def denemeleri_getir():
    conn = get_connection()
    df = pd.read_sql_query("SELECT * FROM denemeler ORDER BY tarih", conn)
    conn.close()
    return df

# ---------- Konu Analizi ----------
def konu_bazli_cikmissoru_analizi(ders_adi, yil_araligi=[2022,2023,2024,2025]):
    conn = get_connection()
    ders_id = ders_id_getir(ders_adi)
    if not ders_id:
        return pd.DataFrame()
    query = '''
        SELECT k.ad AS konu, s.yil, COUNT(*) as soru_sayisi
        FROM sorular s
        JOIN konular k ON s.konu_id = k.id
        WHERE s.ders_id = ? AND s.yil BETWEEN ? AND ?
        GROUP BY k.ad, s.yil
        ORDER BY k.ad, s.yil
    '''
    df = pd.read_sql_query(query, conn, params=(ders_id, yil_araligi[0], yil_araligi[1]))
    conn.close()
    return df

# ---------- Tahmini Soru Üretme (Basit şablon) ----------
def tahmini_soru_uret(konu_adi, zorluk="orta"):
    # Bu fonksiyon örnek amaçlıdır, geliştirilebilir.
    import random
    sablonlar = {
        "Üslü Sayılar": [
            ("2^3 + 2^2 işleminin sonucu kaçtır?", {"A":"8","B":"10","C":"12","D":"14","E":"16"}, "C"),
            ("(3^2)^3 ifadesinin eşiti nedir?", {"A":"3^5","B":"3^6","C":"3^8","D":"9^6","E":"27^2"}, "B")
        ],
        "Noktalama İşaretleri": [
            ("Aşağıdaki cümlelerin hangisinde virgül yanlış kullanılmıştır?", {...}, "A")
        ]
    }
    sorular = sablonlar.get(konu_adi, [])
    if not sorular:
        return None
    secili = random.choice(sorular)
    conn = get_connection()
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO tahmini_sorular (soru_metni, siklar, dogru_sik, aciklama)
        VALUES (?, ?, ?, ?)
    ''', (secili[0], json.dumps(secili[1]), secili[2], f"Bu soru {konu_adi} konusundan türetilmiştir."))
    conn.commit()
    soru_id = cursor.lastrowid
    conn.close()
    return soru_id
