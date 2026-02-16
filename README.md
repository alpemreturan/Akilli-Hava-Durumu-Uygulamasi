# 🌦️ Smart Weather Assistant (Akıllı Hava Durumu)

![Python](https://img.shields.io/badge/Python-3.9%2B-blue?style=for-the-badge&logo=python)
![PyQt6](https://img.shields.io/badge/GUI-PyQt6-green?style=for-the-badge)
![Matplotlib](https://img.shields.io/badge/Charts-Matplotlib-orange?style=for-the-badge)
![OpenWeatherMap](https://img.shields.io/badge/API-OpenWeatherMap-red?style=for-the-badge)

**Smart Weather Assistant**, sadece hava durumu verilerini sunan standart bir uygulama değil; hava koşullarını analiz ederek size ne giymeniz ve nasıl önlemler almanız gerektiğini söyleyen, dinamik arayüzlü ve akıllı bir masaüstü asistanıdır.

---

## 📸 Uygulama Görselleri (Screenshots)

Uygulama, hava durumunun durumuna göre (Güneşli, Yağmurlu, Karlı vb.) arka plan rengini ve temasını otomatik olarak değiştirerek kullanıcıya görsel bir deneyim sunar.

| ☀️ Güneşli & Açık (İstanbul) | 🌧️ Yağmurlu & Soğuk (Amsterdam) | 🔥 Sıcak & Kapalı (Paraguay) | ❄️ Karlı & Soğuk (Oslo) |


<img width="1793" height="1372" alt="istanbul_sunny" src="https://github.com/user-attachments/assets/4713ee60-7b69-41be-b788-ca47f5692395" />


<img width="1792" height="1372" alt="amsterdam_rainy" src="https://github.com/user-attachments/assets/799bfbd9-20d1-4c41-9258-f89215e7b092" />


<img width="1788" height="1368" alt="paraguay_hot" src="https://github.com/user-attachments/assets/d43bfc8b-48ef-4801-aa23-c23809241c13" />


<img width="1797" height="1369" alt="Ekran görüntüsü 2026-02-16 152849" src="https://github.com/user-attachments/assets/17f8e427-e102-4a9e-878d-ee838859052b" />


---

## ✨ Öne Çıkan Özellikler

* **🎨 Dinamik Tema Sistemi:** Hava durumuna göre anlık değişen modern ve şık arayüz renkleri.
* **🤖 Akıllı Kıyafet Asistanı:** Sıcaklık, rüzgar hızı ve hava durumuna göre "Şemsiye al", "Katmanlı giyin" gibi mantıksal tavsiyeler.
* **📊 İnteraktif Grafikler:** Matplotlib ile entegre edilmiş 24 saatlik sıcaklık, rüzgar ve yağış analizi.
* **👗 Görsel Kıyafet Rehberi:** Hava durumuna en uygun kıyafetleri (Mont, Gözlük, Bot vb.) ikonlar ile gösterir.
* **📅 5 Günlük Tahmin:** Günlük kartlar arasında geçiş yaparak haftalık plan yapma imkanı.
* **🌍 Küresel Arama:** OpenWeatherMap API desteğiyle dünya üzerindeki her şehrin verisine erişim.

---

## 🛠️ Kurulum ve Çalıştırma (Installation)

Projeyi yerel makinenizde çalıştırmak için lütfen aşağıdaki adımları sırasıyla uygulayın:

### 1. Depoyu Klonlayın
```bash
git clone [https://github.com/alpemreturan/akilli-hava-durumu.git](https://github.com/alpemreturan/akilli-hava-durumu.git)
cd akilli-hava-durumu
```

### 2. Gerekli Kütüphaneleri Yükleyin
```bash
pip install -r requirements.txt
```

### 3. API Anahtarını Yapılandırın (ÖNEMLİ 🔑)
Güvenlik nedeniyle config.py dosyasındaki API_KEY paylaşılmamıştır. Uygulamanın çalışması için kendi anahtarınızı eklemelisiniz:

1. OpenWeatherMap sitesinden ücretsiz bir API anahtarı alın.

2. Yeni oluşturduğunuz config.py dosyasını açın ve anahtarınızı API_KEY kısmına yapıştırın:
   
   API_KEY = "BURAYA_KENDI_API_KEYINIZI_YAZIN"

### 4. Uygulamayı Başlatın
```bash
python main.py
```

### 🚀 Kullanılan Teknolojiler

PyQt6: Modern ve hızlı masaüstü arayüzü tasarımı.

Matplotlib: Hava durumu verilerinin grafiksel analizi ve görselleştirilmesi.

Requests: OpenWeather API üzerinden veri çekme işlemleri.

Pillow (PIL): İkon ve görsellerin dinamik olarak işlenmesi ve boyutlandırılması.

### 🤝 Katkıda Bulunma (Contributing)

Bu proje geliştirmeye açıktır! Eğer bir hata bulursanız veya yeni bir özellik (yeni tavsiyeler, farklı grafikler vb.) eklemek isterseniz lütfen bir "Issue" açın veya "Pull Request" gönderin.

👨‍💻 Geliştiriciler: 

Emre Turan https://github.com/alpemreturan

Berat Hatinoğlu https://github.com/fwexxy

Ahmet Talha Türkan https://github.com/atalhaturkan

Ve Abdülrahim Usta

Bu proje OpenWeatherMap API kullanılarak geliştirilmiştir.
