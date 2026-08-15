# Uçuş Kontrol

Open-Meteo'dan anlık hava çekip drone uçuşuna uygun mu diye bakıyor. Konum giriyorsun (veya tarayıcıdan alıyorsun), drone tipini seçiyorsun, sonuç geliyor: uçabilir / dikkatli ol / uçma.

## Çalıştırma

```bash
pip install -r requirements.txt
python app.py
```

Sonra: http://127.0.0.1:5000

Python 3.10+ lazım, internet de lazım.

## Dosyalar

- `app.py` — Flask + API
- `weather_service.py` — Open-Meteo
- `flight_analyzer.py` — go/no-go mantığı
- `http_client.py` — SSL işleri (Windows'ta bazen takılıyor)
- `templates/index.html` — arayüz

## API

```
GET /api/analyze?lat=41.0082&lon=28.9784&preset=dji_mavic
```

preset: `dji_mini`, `dji_mavic`, `dji_inspire`, `fpv_racing`, `custom`

custom için `custom=1` + `max_wind`, `max_gust` vs. gönderebilirsin.

## Karar

- **Uçabilir** — her şey limit içinde
- **Dikkatli ol** — sınıra yakın
- **Uçma** — limit aşımı, yağış veya kötü hava

Örnek Mavic limitleri: rüzgar 36 km/h, hamle 50 km/h, yağış 0.

Bu araç sadece fikir verir. Gerçek uçuşta kendi kararın, kurallar ve NOTAM geçerli.

Hava verisi Open-Meteo'dan (ücretsiz, key yok).
