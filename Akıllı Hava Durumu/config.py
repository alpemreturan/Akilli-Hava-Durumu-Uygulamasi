# config.py

API_KEY = "BURAYA_KENDI_API_KEYINIZI_YAZIN"
FORECAST_URL = "http://api.openweathermap.org/data/2.5/forecast"

APP_TITLE = "Akıllı Hava Durumu"
APP_WIDTH = 1200
APP_HEIGHT = 900

# --- RENKLER ---
MAIN_BG_COLOR = "#2B2B2B"

# DİNAMİK ARKA PLAN RENKLERİ (Aynı kalıyor)
WEATHER_BG_COLORS = {
    "01d": "#E67E22", "01n": "#1A253A",
    "02d": "#2980B9", "02n": "#2C3E50",
    "03d": "#7F8C8D", "03n": "#34495E",
    "04d": "#7F8C8D", "04n": "#34495E",
    "09d": "#30336B", "09n": "#130f40",
    "10d": "#30336B", "10n": "#130f40",
    "11d": "#2d3436", "11n": "#000000",
    "13d": "#95a5a6", "13n": "#535c68",
    "50d": "#636e72", "50n": "#2d3436"
}

# --- YENİ AYARLAR ---
# Sol panel artık dümdüz değil, sağ taraf gibi "kart" görünümünde ama daha koyu
SIDEBAR_BG  = "rgba(0, 0, 0, 180)" 

# Asistan kartı rengi
CARD_BG     = "rgba(40, 40, 40, 220)" 

INPUT_BG    = "rgba(255, 255, 255, 30)"
HOVER_COLOR = "rgba(255, 255, 255, 50)"

TEXT_WHITE  = "#FFFFFF"
TEXT_GRAY   = "#D0D0D0"

ACCENT      = "#FFD700"
RAIN_COLOR  = "#4A90E2"
WIND_COLOR  = "#50E3C2"

# config.py içindeki ilgili kısmı bununla değiştir:

# config.py içindeki CLOTHING_URLS kısmını bununla değiştir:

CLOTHING_URLS = {
    # TEMEL KIYAFETLER
    "winter_coat": "https://cdn-icons-png.flaticon.com/128/1926/1926322.png", # Kışlık Mont
    "jacket":      "https://cdn-icons-png.flaticon.com/128/3893/3893192.png", # Mevsimlik Ceket
    "tshirt":      "https://cdn-icons-png.flaticon.com/512/863/863684.png",   # Tişört
    
    # YAĞMUR & KAR EKİPMANLARI
    "raincoat":    "https://cdn-icons-png.flaticon.com/128/3333/3333534.png", # Yağmurluk
    "umbrella":    "https://cdn-icons-png.flaticon.com/128/1147/1147591.png", # Şemsiye (YENİ)
    "snow_boots":  "https://cdn-icons-png.flaticon.com/128/17257/17257525.png", # Kar Botu (YENİ)
    
    # AKSESUARLAR
    "sunglasses":  "https://cdn-icons-png.flaticon.com/128/11554/11554135.png", # Gözlük
    "scarf":       "https://cdn-icons-png.flaticon.com/128/6371/6371544.png",    # Atkı/Bere (YENİ)
    "cap":         "https://cdn-icons-png.flaticon.com/128/2806/2806186.png"     # Şapka (YENİ)
}