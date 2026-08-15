from dataclasses import dataclass, field, asdict


@dataclass
class FlightLimits:
    name: str
    max_wind_kmh: float = 36.0
    max_gust_kmh: float = 50.0
    max_precip_mm: float = 0.0
    max_cloud_cover: float = 85.0
    min_temp_c: float = -10.0
    max_temp_c: float = 40.0
    max_rain_probability: float = 30.0


DRONE_PRESETS: dict[str, FlightLimits] = {
    "dji_mini": FlightLimits(
        name="DJI Mini / Avata",
        max_wind_kmh=28.0,
        max_gust_kmh=40.0,
    ),
    "dji_mavic": FlightLimits(
        name="DJI Mavic / Air",
        max_wind_kmh=36.0,
        max_gust_kmh=50.0,
    ),
    "dji_inspire": FlightLimits(
        name="DJI Inspire / Matrice",
        max_wind_kmh=45.0,
        max_gust_kmh=60.0,
    ),
    "fpv_racing": FlightLimits(
        name="FPV Racing",
        max_wind_kmh=25.0,
        max_gust_kmh=35.0,
        max_cloud_cover=70.0,
    ),
    "custom": FlightLimits(name="Özel Limitler"),
}


@dataclass
class CheckResult:
    parameter: str
    label: str
    value: float | str
    unit: str
    limit: str
    status: str
    message: str


@dataclass
class FlightAnalysis:
    decision: str
    score: int
    checks: list[CheckResult] = field(default_factory=list)
    summary: str = ""
    warnings: list[str] = field(default_factory=list)


def _status(actual: float, limit: float, warn_ratio: float = 0.85) -> str:
    if actual > limit:
        return "fail"
    if actual > limit * warn_ratio:
        return "warn"
    return "pass"


def analyze_flight(weather: dict, limits: FlightLimits) -> FlightAnalysis:
    current = weather.get("current", {})
    hourly = weather.get("hourly", {})

    wind = current.get("wind_speed_10m") or 0
    gust = current.get("wind_gusts_10m") or wind
    precip = current.get("precipitation") or 0
    cloud = current.get("cloud_cover") or 0
    temp = current.get("temperature_2m") or 20
    weather_code = current.get("weather_code", 0)

    rain_probs = hourly.get("precipitation_probability") or [0]
    next_rain_prob = rain_probs[1] if len(rain_probs) > 1 else rain_probs[0]

    checks: list[CheckResult] = []

    wind_status = _status(wind, limits.max_wind_kmh)
    checks.append(CheckResult(
        parameter="wind_speed",
        label="Rüzgar Hızı (10m)",
        value=round(wind, 1),
        unit="km/h",
        limit=f"≤ {limits.max_wind_kmh}",
        status=wind_status,
        message="Rüzgar limitin üzerinde" if wind_status == "fail"
        else "Rüzgar limite yaklaşıyor" if wind_status == "warn"
        else "Rüzgar uygun",
    ))

    gust_status = _status(gust, limits.max_gust_kmh)
    checks.append(CheckResult(
        parameter="wind_gust",
        label="Rüzgar Hamleleri",
        value=round(gust, 1),
        unit="km/h",
        limit=f"≤ {limits.max_gust_kmh}",
        status=gust_status,
        message="Hamle hızı tehlikeli" if gust_status == "fail"
        else "Hamle hızı yüksek" if gust_status == "warn"
        else "Hamle hızı kabul edilebilir",
    ))

    precip_status = "fail" if precip > limits.max_precip_mm else "pass"
    checks.append(CheckResult(
        parameter="precipitation",
        label="Yağış (son 1 saat)",
        value=round(precip, 1),
        unit="mm",
        limit=f"≤ {limits.max_precip_mm}",
        status=precip_status,
        message="Aktif yağış — uçuş yasak" if precip_status == "fail" else "Yağış yok",
    ))

    cloud_status = _status(cloud, limits.max_cloud_cover, 0.9)
    checks.append(CheckResult(
        parameter="cloud_cover",
        label="Bulut Örtüsü",
        value=round(cloud),
        unit="%",
        limit=f"≤ {limits.max_cloud_cover}%",
        status=cloud_status,
        message="Yoğun bulut — görüş riski" if cloud_status == "fail"
        else "Bulut artıyor" if cloud_status == "warn"
        else "Bulut durumu uygun",
    ))

    temp_low = temp < limits.min_temp_c
    temp_high = temp > limits.max_temp_c
    temp_status = "fail" if (temp_low or temp_high) else "pass"
    checks.append(CheckResult(
        parameter="temperature",
        label="Sıcaklık",
        value=round(temp, 1),
        unit="°C",
        limit=f"{limits.min_temp_c} – {limits.max_temp_c}",
        status=temp_status,
        message="Sıcaklık limit dışı" if temp_status == "fail" else "Sıcaklık uygun",
    ))

    rain_status = _status(next_rain_prob, limits.max_rain_probability, 0.8)
    checks.append(CheckResult(
        parameter="rain_probability",
        label="Yağmur Olasılığı (1 saat)",
        value=round(next_rain_prob),
        unit="%",
        limit=f"≤ {limits.max_rain_probability}%",
        status=rain_status,
        message="Yüksek yağmur riski" if rain_status == "fail"
        else "Yağmur riski artıyor" if rain_status == "warn"
        else "Düşük yağmur riski",
    ))

    severe_weather_codes = {45, 48, 51, 53, 55, 56, 57, 61, 63, 65, 66, 67,
                            71, 73, 75, 77, 80, 81, 82, 85, 86, 95, 96, 99}
    wx_status = "fail" if weather_code in severe_weather_codes else "pass"
    wx_label = _weather_code_label(weather_code)
    checks.append(CheckResult(
        parameter="weather_code",
        label="Hava Durumu",
        value=wx_label,
        unit="",
        limit="Açık / Parçalı",
        status=wx_status,
        message="Olumsuz hava koşulu" if wx_status == "fail" else "Hava koşulu uygun",
    ))

    fail_count = sum(1 for c in checks if c.status == "fail")
    warn_count = sum(1 for c in checks if c.status == "warn")

    if fail_count > 0:
        decision = "NO-GO"
        score = max(0, 100 - fail_count * 25 - warn_count * 10)
        summary = f"{fail_count} kritik ihlal — uçuş önerilmez."
    elif warn_count > 0:
        decision = "CAUTION"
        score = max(40, 100 - warn_count * 15)
        summary = f"{warn_count} uyarı — dikkatli uçuş veya erteleme düşünün."
    else:
        decision = "GO"
        score = 100
        summary = "Tüm parametreler limitler dahilinde — uçuş için uygun."

    warnings = [c.message for c in checks if c.status in ("fail", "warn")]

    return FlightAnalysis(
        decision=decision,
        score=score,
        checks=checks,
        summary=summary,
        warnings=warnings,
    )


def _weather_code_label(code: int) -> str:
    labels = {
        0: "Açık", 1: "Az Bulutlu", 2: "Parçalı Bulutlu", 3: "Kapalı",
        45: "Sis", 48: "Donlu Sis",
        51: "Hafif Çisenti", 53: "Çisenti", 55: "Yoğun Çisenti",
        61: "Hafif Yağmur", 63: "Yağmur", 65: "Şiddetli Yağmur",
        71: "Hafif Kar", 73: "Kar", 75: "Yoğun Kar",
        80: "Sağanak", 81: "Sağanak", 82: "Şiddetli Sağanak",
        95: "Fırtına", 96: "Dolu", 99: "Şiddetli Dolu",
    }
    return labels.get(code, f"Kod {code}")


def analysis_to_dict(analysis: FlightAnalysis) -> dict:
    data = asdict(analysis)
    data["checks"] = [asdict(c) for c in analysis.checks]
    return data
