# weather_logic.py
import requests
from io import BytesIO
from PIL import Image
from config import API_KEY, FORECAST_URL, CLOTHING_URLS

def fetch_weather_data(city):
    try:
        params = {"q": city, "appid": API_KEY, "units": "metric", "lang": "tr"}
        response = requests.get(FORECAST_URL, params=params)
        return response.json() if response.status_code == 200 else None
    except: return None

def get_smart_advice(temp, desc, wind_speed):
    """
    Sıcaklık, hava durumu açıklaması ve rüzgar hızına göre
    detaylı ve arkadaş canlısı tavsiyeler üretir.
    """
    advice = ""
    desc = desc.lower()
    
    # --- 1. ÖZEL HAVA DURUMLARI (KAR & YAĞMUR) ---
    
    # KAR
    if "kar" in desc or "snow" in desc:
        advice += "❄️ KAR YAĞIŞI: Dışarısı beyaz bir masal gibi ama soğuk şakaya gelmez! Mutlaka su geçirmeyen botlarını ve en kalın montunu giy.\n\n"
        advice += "🎒 İPUCU: Atkı, bere ve eldiven üçlüsü olmadan çıkma. Araç kullanacaksan buz kazıyıcıyı unutma."
        return advice # Kar varsa başka şeye bakmaya gerek yok

    # YAĞMUR
    elif "yağmur" in desc or "sağanak" in desc or "rain" in desc:
        if temp < 12:
            advice += "☔ SOĞUK YAĞMUR: Hava hem ıslak hem üşütücü. Su geçirmeyen kalın bir mont ve sağlam botlar şart.\n\n"
            advice += "🎒 İPUCU: Rüzgara dayanıklı bir şemsiye al. Ayakların ıslanırsa günün zehir olur, dikkat et!"
        else:
            advice += "🌦️ ILIK YAĞMUR: Yağmur var ama hava yumuşak. İnce bir yağmurluk veya trençkot işini görür.\n\n"
            advice += "🎒 İPUCU: Şemsiyeni yanından ayırma. Islanan elektronik cihazlar için çantanda yer aç."

    # --- 2. SICAKLIK BAZLI TAVSİYELER (YAĞIŞ YOKSA) ---
    
    # DONDURUCU SOĞUK (< 5°C)
    elif temp < 5:
        advice += "🥶 KURU SOĞUK: Hava buz gibi! Termal içliklerin varsa tam zamanı. Lahana gibi kat kat giyinmek seni sıcak tutar.\n\n"
        advice += "🎒 İPUCU: Soğuk cildini kurutabilir, nemlendirici sürmeyi ve kulaklarını bereyle korumayı unutma."

    # SERİN / BAHAR (5°C - 18°C)
    elif 5 <= temp <= 18:
        advice += "☁️ SERİN HAVA: Tam bir geçiş havası. Tişört üstüne hırka veya mevsimlik bir ceket alarak 'katmanlı' giyin.\n\n"
        advice += "🎒 İPUCU: Güneşe aldanma, akşam serinliği çarpar. Yanına yedek bir üst al."

    # KEYİFLİ / GÜZEL (18°C - 25°C)
    elif 18 < temp <= 25:
        advice += "🌤️ HARİKA HAVA: Ne üşütür ne terletir. En sevdiğin tişörtünü, kotunu veya rahat spor kıyafetlerini giy.\n\n"
        advice += "🎒 İPUCU: Dışarıda vakit geçirmek için mükemmel gün. Güneş gözlüğün yanında olsun."

    # SICAK (25°C - 32°C)
    elif 25 < temp <= 32:
        advice += "☀️ SICAK: Güneş kendini hissettiriyor. Açık renkli, pamuklu ve terletmeyen ince kıyafetler tercih et.\n\n"
        advice += "🎒 İPUCU: Güneş gözlüğü ve şapka şart. Susuz kalmamak için su mataranı mutlaka yanına al."

    # AŞIRI SICAK (> 32°C)
    elif temp > 32:
        advice += "🔥 AŞIRI SICAK: Hava bunaltıcı seviyede. Mümkünse gölgeden ayrılma ve en ferah, en ince kıyafetlerini giy.\n\n"
        advice += "🎒 İPUCU: Sıcakta telefon şarjı çabuk biter, powerbank al. Ve tabii ki bol bol su iç!"

    # --- 3. RÜZGAR EKLENTİSİ ---
    if wind_speed > 20:
        advice += "\n\n🌬️ UYARI: Rüzgar sert esiyor! Rüzgar kesici (Windbreaker) bir mont giymezsen üşütürsün."
        
    # Hata durumunda boş dönmesin
    if advice == "":
        advice = "Hava değişken olabilir, tedbirli olmakta fayda var!"

    return advice

# weather_logic.py içindeki get_clothing_icon_urls fonksiyonunu bununla değiştir:

def get_clothing_icon_urls(temp, desc):
    icons = []
    desc = desc.lower()
    
    # --- 1. Temel Kıyafet Seçimi (Sıcaklığa Göre) ---
    if temp < 5:
        icons.append(CLOTHING_URLS["winter_coat"])
        icons.append(CLOTHING_URLS["scarf"]) # Çok soğuksa atkı/bere ekle
    elif 5 <= temp < 15:
        icons.append(CLOTHING_URLS["winter_coat"])
    elif 15 <= temp < 22:
        icons.append(CLOTHING_URLS["jacket"])
    else:
        icons.append(CLOTHING_URLS["tshirt"])
        
    # --- 2. Hava Olayına Göre Ekipmanlar ---
    
    # KAR VARSA
    if "snow" in desc or "kar" in desc:
        icons.append(CLOTHING_URLS["snow_boots"]) # Kar botu
        if CLOTHING_URLS["scarf"] not in icons:   # Eğer yukarıda eklenmediyse ekle
            icons.append(CLOTHING_URLS["scarf"])
            
    # YAĞMUR VARSA
    elif "rain" in desc or "yağmur" in desc or "sağanak" in desc: 
        icons.append(CLOTHING_URLS["raincoat"]) # Yağmurluk
        icons.append(CLOTHING_URLS["umbrella"]) # Şemsiye (İstediğin özellik)
    
    # GÜNEŞLİ / SICAKSA
    if ("clear" in desc or "açık" in desc or "sun" in desc) and temp > 18:
        icons.append(CLOTHING_URLS["sunglasses"])
        
    # ÇOK SICAKSA ŞAPKA EKLE
    if temp > 25:
        icons.append(CLOTHING_URLS["cap"])
        
    return icons

def download_icon(icon_code):
    try:
        url = f"https://openweathermap.org/img/wn/{icon_code}@4x.png"
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except: return None

def download_image_from_url(url):
    try:
        response = requests.get(url, stream=True)
        if response.status_code == 200:
            return Image.open(BytesIO(response.content))
    except: return None