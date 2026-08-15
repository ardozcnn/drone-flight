# Uçuş Kontrol

Open-Meteo API üzerinden anlık ve kısa vadeli hava durumu verilerini alan, drone / İHA uçuş uygunluğunu değerlendiren bir Flask uygulamasıdır.

Konum bilgisi (manuel koordinat veya tarayıcı konumu) ve seçilen drone limitleri doğrultusunda rüzgar, hamle, yağış ve ilgili meteorolojik parametreler analiz edilir; sonuç **Uçabilir**, **Dikkatli ol** veya **Uçma** şeklinde sunulur.

## Gereksinimler

- Python 3.10 veya üzeri
- İnternet bağlantısı (Open-Meteo; konum adı için isteğe bağlı OpenStreetMap Nominatim)

## Kurulum

```bash
pip install -r requirements.txt
python app.py
```

Uygulama varsayılan olarak [http://127.0.0.1:5000](http://127.0.0.1:5000) adresinde çalışır.

## Proje Yapısı

| Dosya | Açıklama |
|-------|----------|
| `app.py` | Flask uygulaması ve `/api/analyze` uç noktası |
| `weather_service.py` | Open-Meteo hava verisi ve ters geokodlama |
| `flight_analyzer.py` | Uçuş uygunluk değerlendirme kuralları |
| `http_client.py` | HTTPS istekleri ve SSL uyumluluk katmanı |
| `templates/index.html` | Kullanıcı arayüzü |

## API

```
GET /api/analyze?lat=41.0082&lon=28.9784&preset=dji_mavic
```

| Parametre | Açıklama |
|-----------|----------|
| `lat`, `lon` | WGS84 koordinatları |
| `preset` | `dji_mini`, `dji_mavic`, `dji_inspire`, `fpv_racing`, `custom` |
| `custom=1` | Özel limit kullanımı (`max_wind`, `max_gust`, `max_precip` vb.) |

Yanıt JSON formatındadır: konum, anlık hava verisi, saatlik tahmin, analiz sonucu (karar, skor, kontroller).

## Değerlendirme Kriterleri

| Karar | Anlamı |
|-------|--------|
| **Uçabilir** | Tüm parametreler tanımlı limitler içinde |
| **Dikkatli ol** | Parametreler sınıra yakın |
| **Uçma** | Limit aşımı, yağış veya olumsuz hava kodu |

Örnek (Mavic sınıfı): azami rüzgar 36 km/h, azami hamle 50 km/h, yağış 0 mm.

## Sorumluluk Reddi

Bu yazılım yalnızca bilgilendirme amaçlıdır. Yasal düzenlemelerin, NOTAM bilgilerinin veya pilotun operasyonel kararının yerini tutmaz.

Hava verisi [Open-Meteo](https://open-meteo.com) üzerinden sağlanmaktadır.

## Lisans

Kişisel ve eğitim amaçlı kullanım için serbesttir.
