# main.py
import sys
import os
import threading
from datetime import datetime
from PIL import Image, ImageQt

from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                             QHBoxLayout, QLabel, QLineEdit, QPushButton, QFrame, QGraphicsDropShadowEffect)
from PyQt6.QtGui import QPixmap, QFont, QColor, QCursor
from PyQt6.QtCore import Qt, pyqtSignal, QObject
from PyQt6.QtGui import QIcon

# Grafik Kütüphanesi
from matplotlib.backends.backend_qtagg import FigureCanvasQTAgg
import matplotlib.pyplot as plt

import config
import weather_logic

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

# --- Tıklanabilir Kart Sınıfı ---
class DailyCard(QFrame):
    clicked = pyqtSignal(str) # Tıklanınca gün ismini sinyal olarak gönderir

    def __init__(self, day_name, parent=None):
        super().__init__(parent)
        self.day_name = day_name
        self.setCursor(QCursor(Qt.CursorShape.PointingHandCursor)) # Üzerine gelince el işareti

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.LeftButton:
            self.clicked.emit(self.day_name)
        super().mousePressEvent(event)

# --- Thread Sinyalleri ---
class WeatherSignals(QObject):
    data_ready = pyqtSignal(object, object, object, dict, list) 
    error_occurred = pyqtSignal(str)
    icon_ready = pyqtSignal(object, QLabel)
    clothes_ready = pyqtSignal(list)

class WeatherApp(QMainWindow):
    def __init__(self):
        super().__init__()

        icon_path = resource_path("icon.ico")
        self.setWindowIcon(QIcon(icon_path))
        self.setWindowTitle(config.APP_TITLE)

        self.resize(config.APP_WIDTH, config.APP_HEIGHT)
        self.setStyleSheet(f"background-color: {config.MAIN_BG_COLOR}; transition: background-color 0.5s;")
        
        self.weather_cache = {} 
        
        self.signals = WeatherSignals()
        self.signals.data_ready.connect(self.on_data_ready)
        self.signals.error_occurred.connect(self.show_error)
        self.signals.icon_ready.connect(self.update_icon)
        self.signals.clothes_ready.connect(self.render_clothes)

        # --- ANA DÜZEN ---
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout(central_widget)
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # SOL PANEL
        self.create_sidebar()
        main_layout.addWidget(self.sidebar, 3)

        # SAĞ PANEL
        self.create_content_area()
        main_layout.addWidget(self.content_area, 9)

        self.start_search("Kocaeli")

    def add_shadow(self, widget, blur=15):
        shadow = QGraphicsDropShadowEffect()
        shadow.setBlurRadius(blur)
        shadow.setColor(QColor(0, 0, 0, 150))
        shadow.setOffset(2, 2)
        widget.setGraphicsEffect(shadow)

    def create_sidebar(self):
        self.sidebar = QFrame()
        self.sidebar.setStyleSheet(f"""
            QFrame {{
                background-color: {config.SIDEBAR_BG};
                border-radius: 20px;
                border: 1px solid rgba(255, 255, 255, 10);
            }}
            QLabel {{ background-color: transparent; color: {config.TEXT_WHITE}; border: none; }}
        """)
        
        layout = QVBoxLayout(self.sidebar)
        layout.setContentsMargins(20, 20, 20, 20)
        layout.setSpacing(5)

        # Arama Kısmı
        search_layout = QHBoxLayout()
        self.entry_search = QLineEdit()
        self.entry_search.setPlaceholderText("Şehir Ara...")
        self.entry_search.setStyleSheet(f"""
            QLineEdit {{
                background-color: {config.INPUT_BG};
                border: 1px solid rgba(255,255,255,30); 
                border-radius: 12px; color: white; padding: 10px; font-size: 14px;
            }}
        """)
        self.entry_search.returnPressed.connect(lambda: self.start_search())
        
        btn_search = QPushButton("🔍")
        btn_search.setFixedSize(45, 45)
        btn_search.setCursor(Qt.CursorShape.PointingHandCursor)
        btn_search.setStyleSheet(f"""
            QPushButton {{
                background-color: {config.INPUT_BG};
                color: white; border-radius: 12px; font-weight: bold; font-size: 18px;
                border: 1px solid rgba(255,255,255,20);
            }}
            QPushButton:hover {{ background-color: {config.HOVER_COLOR}; }}
        """)
        btn_search.clicked.connect(lambda: self.start_search())
        
        search_layout.addWidget(self.entry_search)
        search_layout.addWidget(btn_search)
        layout.addLayout(search_layout)

        layout.addSpacing(10)

        # Bilgi
        self.lbl_city = QLabel("--")
        self.lbl_city.setFont(QFont("Segoe UI", 24, QFont.Weight.Bold))
        self.lbl_city.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_shadow(self.lbl_city)
        layout.addWidget(self.lbl_city)

        # Başlangıç tarihi
        self.lbl_date = QLabel(datetime.now().strftime("%d %B, %A"))
        self.lbl_date.setFont(QFont("Segoe UI", 11))
        self.lbl_date.setStyleSheet(f"color: {config.TEXT_GRAY}; background-color: transparent;")
        self.lbl_date.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(self.lbl_date)
        
        layout.addSpacing(5)

        # İkon (Hava Durumu Resmi)
        self.icon_label = QLabel()
        self.icon_label.setFixedSize(120, 120)
        self.icon_label.setStyleSheet("background-color: transparent; border: none;") 
        self.icon_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_shadow(self.icon_label, blur=25)

        icon_cont = QWidget()
        icon_cont.setStyleSheet("background-color: transparent; border: none;")
        icon_box = QHBoxLayout(icon_cont)
        icon_box.setContentsMargins(0,0,0,0) 
        icon_box.addWidget(self.icon_label, alignment=Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(icon_cont)

        # Derece
        self.lbl_temp = QLabel("--°")
        self.lbl_temp.setFont(QFont("Segoe UI", 65, QFont.Weight.Bold))
        self.lbl_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_shadow(self.lbl_temp)
        layout.addWidget(self.lbl_temp)

        # Durum (Açık, Yağmurlu vb.)
        self.lbl_desc = QLabel("--")
        self.lbl_desc.setFont(QFont("Segoe UI", 16))
        self.lbl_desc.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.add_shadow(self.lbl_desc)
        layout.addWidget(self.lbl_desc)

        layout.addStretch()

        # Asistan Kartı
        advice_card = QFrame()
        advice_card.setMinimumHeight(320)
        advice_card.setStyleSheet(f"""
            QFrame {{ 
                background-color: {config.CARD_BG}; 
                border-radius: 20px; 
                border: 1px solid rgba(255,255,255,10); 
            }}
            QLabel {{ background-color: transparent; border: none; }}
        """)
        ac_layout = QVBoxLayout(advice_card)
        ac_layout.setContentsMargins(20, 20, 20, 20)
        ac_layout.setSpacing(10)
        
        # Başlık
        header_layout = QHBoxLayout()
        header_layout.setContentsMargins(0,0,0,0)
        header_layout.setSpacing(0)

        lbl_asst = QLabel("Asistan & Öneri")
        lbl_asst.setStyleSheet(f"color: {config.ACCENT}; font-weight: bold; font-size: 15px; border: none;")
        header_layout.addWidget(lbl_asst)
        
        header_layout.addStretch()
        ac_layout.addLayout(header_layout)

        # Çizgi
        line = QFrame()
        line.setFrameShape(QFrame.Shape.HLine)
        line.setStyleSheet("background-color: rgba(255,255,255,30); border: none;")
        ac_layout.addWidget(line)
        
        # Metin
        self.lbl_advice = QLabel("Veri bekleniyor...")
        self.lbl_advice.setWordWrap(True)
        self.lbl_advice.setAlignment(Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignTop)
        self.lbl_advice.setStyleSheet("font-size: 14px; line-height: 1.4; color: #EEE; margin-top: 5px; border: none;") 
        ac_layout.addWidget(self.lbl_advice, stretch=1)

        # İkonlar
        self.clothing_container = QWidget()
        self.clothing_container.setStyleSheet("background-color: transparent; border: none;") 
        
        self.clothing_layout = QHBoxLayout(self.clothing_container)
        self.clothing_layout.setContentsMargins(0, 10, 0, 0)
        self.clothing_layout.setSpacing(15)
        self.clothing_layout.setAlignment(Qt.AlignmentFlag.AlignCenter) 
        
        ac_layout.addWidget(self.clothing_container)

        layout.addWidget(advice_card)

    def create_content_area(self):
        self.content_area = QWidget()
        self.content_area.setStyleSheet("background-color: transparent; border: none;")
        
        layout = QVBoxLayout(self.content_area)
        layout.setContentsMargins(10, 10, 10, 10)
        layout.setSpacing(15)

        # İstatistikler
        stats_frame = QWidget()
        stats_frame.setStyleSheet("background-color: transparent;")
        stats_layout = QHBoxLayout(stats_frame)
        stats_layout.setContentsMargins(0,0,0,0)
        stats_layout.setSpacing(15)
        
        self.stat_labels = {}
        stats_info = [("hum", "💧 Nem"), ("feels", "🌡️ His"), ("vis", "👁️ Görüş"), ("pres", "⏲️ Basınç")]
        
        for key, title in stats_info:
            card = QFrame()
            card.setStyleSheet(f"""
                QFrame {{ 
                    background-color: {config.CARD_BG}; 
                    border-radius: 15px; 
                    border: 1px solid rgba(255,255,255,10);
                }}
                QLabel {{ color: {config.TEXT_WHITE}; background-color: transparent; border: none; }}
            """)
            cl = QVBoxLayout(card)
            t_lbl = QLabel(title)
            t_lbl.setAlignment(Qt.AlignmentFlag.AlignCenter)
            t_lbl.setStyleSheet(f"color: {config.TEXT_GRAY}; font-size: 12px;")
            cl.addWidget(t_lbl)
            
            lbl_val = QLabel("--")
            lbl_val.setFont(QFont("Segoe UI", 16, QFont.Weight.Bold))
            lbl_val.setAlignment(Qt.AlignmentFlag.AlignCenter)
            cl.addWidget(lbl_val)
            
            self.stat_labels[key] = lbl_val
            stats_layout.addWidget(card)
            
        layout.addWidget(stats_frame)

        # GRAFİK ALANI
        chart_card = QFrame()
        chart_card.setStyleSheet(f"""
            background-color: {config.CARD_BG}; 
            border-radius: 20px;
            border: 1px solid rgba(255,255,255,10);
        """)
        chart_layout = QVBoxLayout(chart_card)
        
        # Grafik Başlığı
        self.lbl_chart_title = QLabel("24 Saatlik Detaylı Analiz")
        self.lbl_chart_title.setStyleSheet("color: white; font-weight: bold; font-size: 20px; background: transparent; border: none;")
        self.lbl_chart_title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        chart_layout.addWidget(self.lbl_chart_title)

        self.fig, (self.ax_rain, self.ax_temp, self.ax_wind) = plt.subplots(3, 1, figsize=(6, 6), dpi=90, sharex=True)
        self.fig.subplots_adjust(top=0.92, bottom=0.1, hspace=0.5) 
        
        self.fig.patch.set_facecolor("none")
        for ax in [self.ax_rain, self.ax_temp, self.ax_wind]:
            ax.set_facecolor("none")
            ax.tick_params(axis='x', colors='white', labelsize=9)
            ax.tick_params(axis='y', colors='white')
            ax.spines['bottom'].set_color('white')
            ax.spines['top'].set_visible(False)
            ax.spines['right'].set_visible(False)
            ax.spines['left'].set_visible(False)
            ax.get_yaxis().set_visible(False) 
        
        self.canvas = FigureCanvasQTAgg(self.fig)
        self.canvas.setStyleSheet("background-color: transparent;")
        chart_layout.addWidget(self.canvas)
        
        layout.addWidget(chart_card, stretch=5)

        # GÜNLÜK TAHMİN (Tıklanabilir Kartlar)
        self.daily_frame = QWidget()
        self.daily_frame.setStyleSheet("background-color: transparent;")
        self.daily_layout = QHBoxLayout(self.daily_frame)
        self.daily_layout.setContentsMargins(0,0,0,0)
        self.daily_layout.setSpacing(15) 
        
        layout.addWidget(self.daily_frame)

    def start_search(self, city_arg=None):
        city = city_arg if city_arg else self.entry_search.text()
        if not city: return
        self.lbl_desc.setText("Yükleniyor...")
        threading.Thread(target=self.process_weather, args=(city,), daemon=True).start()

    def process_weather(self, city):
        data = weather_logic.fetch_weather_data(city)
        if not data:
            self.signals.error_occurred.emit("Bulunamadı!")
            return

        curr = data["list"][0]
        desc = curr["weather"][0]["description"].title()
        
        weather_by_day = {}
        daily_summary = []
        
        seen_days = set()
        
        for item in data["list"]:
            dt = datetime.fromtimestamp(item["dt"])
            d_name = dt.strftime("%A")
            
            if d_name not in weather_by_day:
                weather_by_day[d_name] = {
                    "times": [], "temps": [], "rains": [], "winds": [], "degs": [], "items": []
                }
            
            weather_by_day[d_name]["items"].append(item)

            weather_by_day[d_name]["times"].append(dt.strftime("%H:%M"))
            weather_by_day[d_name]["temps"].append(item["main"]["temp"])
            weather_by_day[d_name]["rains"].append(item.get("pop", 0) * 100)
            weather_by_day[d_name]["winds"].append(item["wind"]["speed"])
            weather_by_day[d_name]["degs"].append(item["wind"]["deg"])
            
            if d_name not in seen_days:
                daily_summary.append({
                    "day": d_name,
                    "icon": item["weather"][0]["icon"],
                    "temp_sample": item["main"]["temp"] 
                })
                seen_days.add(d_name)
        
        # Min/Max hesapla
        for d_sum in daily_summary:
            day_key = d_sum["day"]
            temps = weather_by_day[day_key]["temps"]
            d_sum["min"] = min(temps)
            d_sum["max"] = max(temps)

        # Sinyal ile veriyi gönder
        self.signals.data_ready.emit(curr, data["city"]["name"], desc, weather_by_day, daily_summary)
        
        self.download_and_emit_icon(curr["weather"][0]["icon"], self.icon_label, (130, 130))
        temp = curr['main']['temp']
        clothing_urls = weather_logic.get_clothing_icon_urls(temp, desc)
        self.download_clothes(clothing_urls)

    def on_data_ready(self, curr, city, desc, weather_map, daily_summary):
        """Veri geldiğinde çalışır"""
        self.weather_cache = weather_map 
        self.daily_summary_cache = daily_summary
        
        self.lbl_city.setText(city)
        self.lbl_temp.setText(f"{curr['main']['temp']:.0f}°")
        self.lbl_desc.setText(desc)
        
        # Tarih Gösterimi (Bilgisayarın o anki zamanını kullanır)
        now = datetime.now()
        day_eng = now.strftime("%A")
        tr_days = {"Monday":"Pazartesi", "Tuesday":"Salı", "Wednesday":"Çarşamba", "Thursday":"Perşembe", "Friday":"Cuma", "Saturday":"Cumartesi", "Sunday":"Pazar"}
        day_tr = tr_days.get(day_eng, day_eng)
        
        tr_months = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}
        month_eng = now.strftime("%B")
        month_tr = tr_months.get(month_eng, month_eng)
        
        self.lbl_date.setText(f"{now.day} {month_tr}, {day_tr}")

        icon_code = curr['weather'][0]['icon'] 
        new_bg_color = config.WEATHER_BG_COLORS.get(icon_code, config.MAIN_BG_COLOR)
        self.setStyleSheet(f"background-color: {new_bg_color}; transition: background-color 0.5s;")

        self.stat_labels["hum"].setText(f"%{curr['main']['humidity']}")
        self.stat_labels["feels"].setText(f"{curr['main']['feels_like']:.0f}°")
        self.stat_labels["vis"].setText(f"{curr.get('visibility', 10000)/1000:.1f} km")
        self.stat_labels["pres"].setText(f"{curr['main']['pressure']} hPa")

        advice = weather_logic.get_smart_advice(curr['main']['temp'], desc.lower(), curr['wind']['speed'])
        self.lbl_advice.setText(advice)

        self.create_daily_cards(daily_summary)

        if daily_summary:
            # Otomatik olarak listedeki ilk günün grafiğini çiz
            first_day = daily_summary[0]["day"]
            if first_day in weather_map:
                data = weather_map[first_day]
                tr_name = tr_days.get(first_day, first_day)
                self.lbl_chart_title.setText(f"{tr_name} Günü Detaylı Analiz")
                self.draw_charts(data["times"], data["temps"], data["rains"], data["winds"], data["degs"])

    def create_daily_cards(self, daily_data):
        while self.daily_layout.count():
            child = self.daily_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
            
        tr_days = {"Monday":"PZT", "Tuesday":"SAL", "Wednesday":"ÇAR", "Thursday":"PER", "Friday":"CUM", "Saturday":"CMT", "Sunday":"PAZ"}

        # 6 GÜN GÖSTERME (Eğer API'de o kadar gün varsa)
        for i, d in enumerate(daily_data[:6]): 
            d_name_raw = d["day"]
            d_name_tr = tr_days.get(d_name_raw, d_name_raw[:3])
            
            card = DailyCard(d_name_raw)
            card.clicked.connect(self.switch_chart_day)

            card.setStyleSheet(f"""
                DailyCard {{ 
                    background-color: {config.CARD_BG}; 
                    border-radius: 15px;
                    border: 1px solid rgba(255,255,255,10);
                }}
                DailyCard:hover {{
                    background-color: rgba(255, 255, 255, 30);
                    border: 1px solid {config.ACCENT};
                }}
                QLabel {{ background-color: transparent; border: none; }}
            """)
            
            cl = QVBoxLayout(card)
            cl.setContentsMargins(5, 5, 5, 5) 
            
            lbl_day = QLabel(d_name_tr)
            lbl_day.setStyleSheet("color: white; font-weight: bold;")
            lbl_day.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            lbl_icon = QLabel()
            lbl_icon.setFixedSize(50, 50)
            lbl_icon.setAlignment(Qt.AlignmentFlag.AlignCenter)
            threading.Thread(target=self.download_and_emit_icon, args=(d["icon"], lbl_icon, (50,50)), daemon=True).start()
            
            icon_wrap = QWidget()
            iw_box = QHBoxLayout(icon_wrap); 
            iw_box.addWidget(lbl_icon, alignment=Qt.AlignmentFlag.AlignCenter)
            iw_box.setContentsMargins(0,0,0,0)

            lbl_temp = QLabel(f"{d['max']:.0f}° / {d['min']:.0f}°")
            lbl_temp.setStyleSheet(f"color: {config.TEXT_GRAY};")
            lbl_temp.setAlignment(Qt.AlignmentFlag.AlignCenter)
            
            cl.addWidget(lbl_day)
            cl.addWidget(icon_wrap)
            cl.addWidget(lbl_temp)
            
            self.daily_layout.addWidget(card)

    def switch_chart_day(self, day_name):
        """Seçilen güne göre TÜM ekranı günceller"""
        if day_name not in self.weather_cache:
            return

        data = self.weather_cache[day_name]
        
        temps = data["temps"]
        max_idx = temps.index(max(temps))
        rep_item = data["items"][max_idx]

        dt = datetime.fromtimestamp(rep_item["dt"])
        day_eng = dt.strftime("%A")
        tr_days = {"Monday":"Pazartesi", "Tuesday":"Salı", "Wednesday":"Çarşamba", "Thursday":"Perşembe", "Friday":"Cuma", "Saturday":"Cumartesi", "Sunday":"Pazar"}
        day_tr = tr_days.get(day_eng, day_eng)
        tr_months = {"January": "Ocak", "February": "Şubat", "March": "Mart", "April": "Nisan", "May": "Mayıs", "June": "Haziran", "July": "Temmuz", "August": "Ağustos", "September": "Eylül", "October": "Ekim", "November": "Kasım", "December": "Aralık"}
        month_eng = dt.strftime("%B")
        month_tr = tr_months.get(month_eng, month_eng)
        
        self.lbl_date.setText(f"{dt.day} {month_tr}, {day_tr}")

        curr_temp = rep_item["main"]["temp"]
        desc = rep_item["weather"][0]["description"].title()
        
        self.lbl_temp.setText(f"{curr_temp:.0f}°")
        self.lbl_desc.setText(desc)

        icon_code = rep_item["weather"][0]["icon"]
        threading.Thread(target=self.download_and_emit_icon, args=(icon_code, self.icon_label, (130, 130)), daemon=True).start()

        new_bg_color = config.WEATHER_BG_COLORS.get(icon_code, config.MAIN_BG_COLOR)
        self.setStyleSheet(f"background-color: {new_bg_color}; transition: background-color 0.5s;")

        self.stat_labels["hum"].setText(f"%{rep_item['main']['humidity']}")
        self.stat_labels["feels"].setText(f"{rep_item['main']['feels_like']:.0f}°")
        vis = rep_item.get('visibility', 10000) / 1000
        self.stat_labels["vis"].setText(f"{vis:.1f} km")
        self.stat_labels["pres"].setText(f"{rep_item['main']['pressure']} hPa")

        wind_speed = rep_item['wind']['speed']
        advice = weather_logic.get_smart_advice(curr_temp, desc.lower(), wind_speed)
        self.lbl_advice.setText(advice)

        clothing_urls = weather_logic.get_clothing_icon_urls(curr_temp, desc)
        threading.Thread(target=self.download_clothes, args=(clothing_urls,), daemon=True).start()

        tr_name = tr_days.get(day_name, day_name)
        self.lbl_chart_title.setText(f"{tr_name} Günü Detaylı Analiz")

        self.draw_charts(data["times"], data["temps"], data["rains"], data["winds"], data["degs"])

    def draw_charts(self, times, temps, rains, winds, wind_degs):
        self.ax_rain.clear()
        self.ax_temp.clear()
        self.ax_wind.clear()

        self.ax_rain.tick_params(labelbottom=True)
        self.ax_temp.tick_params(labelbottom=True)

        self.ax_rain.set_title("Yağış İhtimali (%)", loc='left', color=config.RAIN_COLOR, fontsize=10, fontweight='bold', pad=10)
        self.ax_temp.set_title("Sıcaklık (°C)", loc='left', color=config.ACCENT, fontsize=10, fontweight='bold', pad=10)
        self.ax_wind.set_title("Rüzgar (km/s)", loc='left', color=config.WIND_COLOR, fontsize=10, fontweight='bold', pad=10)

        # 1. Yağmur
        bars = self.ax_rain.bar(times, rains, color=config.RAIN_COLOR, alpha=0.7, width=0.5)
        self.ax_rain.set_ylim(0, 115) 
        for bar in bars:
            height = bar.get_height()
            if height > 0:
                self.ax_rain.text(bar.get_x() + bar.get_width()/2., height + 1,
                                  f'%{int(height)}', ha='center', va='bottom', color='white', fontsize=8)

        # 2. Sıcaklık
        self.ax_temp.plot(times, temps, color=config.ACCENT, linewidth=3, marker='o', markerfacecolor='white')
        self.ax_temp.fill_between(times, temps, min(temps)-5, color=config.ACCENT, alpha=0.2)
        if temps: self.ax_temp.set_ylim(min(temps)-2, max(temps)+2)
        for i, t in enumerate(temps):
            self.ax_temp.annotate(f"{t:.0f}°", (times[i], t), xytext=(0,10), 
                             textcoords="offset points", ha='center', color='white', fontweight='bold', fontsize=9)

        # 3. Rüzgar
        self.ax_wind.plot(times, winds, color=config.WIND_COLOR, linewidth=2)
        if winds: self.ax_wind.set_ylim(min(winds)-1, max(winds)+5)
        
        for i, w in enumerate(winds):
            self.ax_wind.annotate(f"{w:.0f}", (times[i], w), xytext=(0, -15), 
                                  textcoords="offset points", ha='center', color='white', fontsize=9)
            rotation = -wind_degs[i] 
            self.ax_wind.annotate("⬇", (times[i], w), xytext=(0, 15),
                              textcoords="offset points",
                              color=config.WIND_COLOR, ha='center', va='center', 
                              fontsize=14, rotation=rotation)

        self.canvas.draw()

    def download_and_emit_icon(self, code, label_widget, size):
        pil_img = weather_logic.download_icon(code)
        if pil_img:
            pil_img = pil_img.resize(size, Image.Resampling.LANCZOS)
            qim = ImageQt.ImageQt(pil_img)
            pix = QPixmap.fromImage(qim)
            self.signals.icon_ready.emit(pix, label_widget)

    def update_icon(self, pixmap, label):
        label.setPixmap(pixmap)

    def download_clothes(self, urls):
        images = []
        for url in urls:
            pil_img = weather_logic.download_image_from_url(url)
            if pil_img:
                pil_img = pil_img.resize((45, 45), Image.Resampling.LANCZOS)
                qim = ImageQt.ImageQt(pil_img)
                pix = QPixmap.fromImage(qim)
                images.append(pix)
        self.signals.clothes_ready.emit(images)

    def render_clothes(self, pixmaps):
        while self.clothing_layout.count():
            child = self.clothing_layout.takeAt(0)
            if child.widget(): child.widget().deleteLater()
        for pix in pixmaps:
            lbl = QLabel()
            lbl.setPixmap(pix)
            lbl.setStyleSheet("background-color: transparent; border: none;") 
            self.clothing_layout.addWidget(lbl)

    def show_error(self, msg):
        self.lbl_desc.setText(msg)

if __name__ == "__main__":
    app = QApplication(sys.argv)
    window = WeatherApp()
    window.show()
    sys.exit(app.exec())