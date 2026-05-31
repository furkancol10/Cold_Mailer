# SmartReach — AI Destekli Soğuk E-Mail Otomasyon Aracı

Potansiyel müşteri listesini yükle, Google Gemini AI her kişi için kişiselleştirilmiş mail yazsın, Gmail üzerinden otomatik göndersin, açılma ve cevapları takip et.

> **Not:** Bu proje bir bitirme projesi olarak geliştirilmiştir. AI mail üretimi (Gemini API) ve Gmail gönderimi gerçek API anahtarları gerektirdiğinden **entegrasyon testleri yapılamamıştır.** Temel Django akışları (lead yönetimi, kampanya CRUD, kullanıcı girişi) çalışır durumdadır.

---

## Özellikler

- **Google ile giriş** — django-allauth ile OAuth2
- **Lead yönetimi** — CSV yükleme, tek tek ekleme/düzenleme/silme, arama
- **Kampanya yönetimi** — Lead seçimi, AI prompt şablonu, günlük gönderim limiti
- **AI mail üretimi** — Google Gemini 1.5 Flash her lead için kişiselleştirilmiş mail yazar
- **Mail onaylama** — Kullanıcı gönderilmeden önce mailleri tek tek veya toplu onaylar, düzenler
- **Zamanlanmış gönderim** — Celery + Redis ile arka planda, spam koruması için 30–90 sn bekleme
- **Açılma takibi** — Gizli 1×1 tracking pixel ile açılma olayları kaydedilir
- **Abonelikten çıkma** — Her mailin altında otomatik unsubscribe linki
- **Dashboard** — Kampanya ve gönderim istatistikleri

## Tech Stack

| Katman | Teknoloji |
|---|---|
| Backend | Django 5.2 LTS + Django REST Framework |
| Veritabanı | PostgreSQL + psycopg3 |
| AI | Google Gemini 1.5 Flash |
| E-Mail | Gmail API (OAuth2) |
| Zamanlama | Celery + Redis |
| Frontend | Django Templates + HTMX + Tailwind CSS (CDN) |
| Auth | django-allauth (Google OAuth2) |

---

## Kurulum

### 1. Gereksinimler

- Python 3.11+
- PostgreSQL
- Redis

### 2. Projeyi klonla

```bash
git clone https://github.com/kullanici-adi/smartreach.git
cd smartreach
```

### 3. Sanal ortam oluştur ve paketleri yükle

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# macOS / Linux
source venv/bin/activate

pip install -r requirements.txt
```

### 4. Ortam değişkenlerini ayarla

```bash
cp .env.example .env
```

`.env` dosyasını aç ve değerleri doldur:

```env
SECRET_KEY=cok-gizli-bir-anahtar
DEBUG=True
DATABASE_URL=postgres://postgres:sifre@localhost:5432/smartreach_db
GEMINI_API_KEY=AIza...          # aistudio.google.com
GOOGLE_CLIENT_ID=...            # console.cloud.google.com
GOOGLE_CLIENT_SECRET=GOCSPX-...
APP_BASE_URL=http://localhost:8000
```

### 5. Veritabanını oluştur ve migrate et

```bash
# PostgreSQL'de veritabanı oluştur
psql -U postgres -c "CREATE DATABASE smartreach_db;"

python manage.py migrate
```

### 6. Admin kullanıcısı oluştur

```bash
python manage.py createsuperuser
```

### 7. Google OAuth2 ayarla

```bash
python manage.py setup_oauth
```

Bu komut:
- Site'i `localhost:8000` olarak günceller
- Google OAuth2 SocialApp kaydını oluşturur

### 8. Uygulamayı başlat

**Terminal 1 — Django:**
```bash
python manage.py runserver
```

**Terminal 2 — Celery (AI üretimi ve mail gönderimi için):**
```bash
celery -A smartreach worker -l info
```

Tarayıcıda aç: [http://localhost:8000](http://localhost:8000)

---

## API Anahtarları Nereden Alınır?

| Servis | URL | Notlar |
|---|---|---|
| **Gemini API** | [aistudio.google.com](https://aistudio.google.com) | Ücretsiz, günde 1500 istek |
| **Google OAuth2** | [console.cloud.google.com](https://console.cloud.google.com) | Gmail API'yi de aktif et |

### Google Cloud Console adımları:
1. Yeni proje oluştur
2. **APIs & Services → OAuth consent screen** → External
3. **APIs & Services → Credentials → Create OAuth 2.0 Client ID**
   - Authorized redirect URI: `http://localhost:8000/accounts/google/login/callback/`
4. **APIs & Services → Enabled APIs → Gmail API** → Enable

---

## Kullanım Akışı

```
Lead Yükle (CSV)
    ↓
Kampanya Oluştur (lead seç, prompt yaz)
    ↓
"Mailler Üret" → Gemini her lead için mail yazar
    ↓
Mailleri İncele / Düzenle / Onayla
    ↓
"Kampanyayı Başlat" → Celery Gmail ile gönderir
    ↓
Dashboard'dan açılma / cevap oranlarını takip et
```

---

## Proje Yapısı

```
smartreach/          ← Django proje ayarları
accounts/            ← Kullanıcı profili, Google OAuth2 signal
leads/               ← Lead modeli, CSV upload, CRUD
campaigns/           ← Kampanya modeli, AI üretim ve gönderim tetikleyicileri
emails/              ← GeneratedEmail, Celery tasks, Gmail servisi, tracking pixel
templates/           ← Tüm HTML template'leri
```

---

## Önemli Notlar

- **Spam koruması:** Mailler arasında 30–90 saniye rastgele bekleme uygulanır
- **Günlük limit:** Varsayılan 50 mail/gün (kampanya ayarlarından değiştirilebilir)
- **Unsubscribe:** Her mailde zorunlu abonelikten çıkma linki bulunur
- **API anahtarları:** Asla `.env` dışında tutma, Git'e commit etme

---

## Bilinen Kısıtlamalar

- Gemini API ve Gmail API entegrasyonları **gerçek ortamda test edilmemiştir**
- Celery reply detection (gelen cevap takibi) henüz implemente edilmemiştir
- Production deployment için ek güvenlik ayarları gereklidir (`SECURE_SSL_REDIRECT` vb.)

---

## Gelecek Planlar

- [ ] Stripe ile abonelik sistemi
- [ ] A/B testi (iki farklı mail versiyonu)
- [ ] Drip campaign (otomatik takip mailleri)
- [ ] CRM entegrasyonları (HubSpot, Pipedrive)
- [ ] Cevap detection (Gmail inbox okuma)
