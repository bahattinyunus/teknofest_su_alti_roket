# 📋 Aviyonik ve Donanım Malzeme Listesi (Bill of Materials - BOM)

Bu doküman, TEKNOFEST ve Roketsan Su Altı Roketi referans uçuş kontrol ve güç dağıtım mimarisinde kullanılan tüm elektronik bileşenleri, sensörleri, üretici parça kodlarını ve tahmini birim maliyetleri listeler.

---

## 1. Ana Kontrol ve Haberleşme Katmanı

| Bileşen | Açıklama / Fonksiyon | Üretici Parça Kodu (MPN) | Kılıf / Paket | Adet | Tahmini Fiyat (USD) |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Ana Mikrodenetleyici (FC)** | 168 MHz ARM Cortex-M4F, Donanımsal FPU, 1MB Flash, 192KB RAM | `STM32F407VGT6` | LQFP-100 | 1 | \$11.50 |
| **Kablosuz Ağ & FOTA Köprüsü** | 240 MHz Dual-Core Xtensa, 16MB Flash, 8MB PSRAM, Wi-Fi & BLE | `ESP32-S3-WROOM-1-N16R8` | Modül (SMD) | 1 | \$4.80 |
| **UART-PWM Servo Denetleyici** | 6-Kanal Yüksek Hassasiyetli UART Servo Entegresi | `Pololu Micro Maestro` (veya PIC18F14K50) | DIP-14 / Modül | 1 | \$14.00 |
| **Osilatör Kristali** | 8.000 MHz ±10ppm Yüksek Kararlılıklı Kristal (HSE) | `ABM3B-8.000MHZ-B2-T` | SMD-5032 | 1 | \$0.65 |
| **RTC Kristali** | 32.768 kHz Düşük Güç Saat Kristali (LSE) | `ABS07-32.768KHZ-T` | SMD-3215 | 1 | \$0.45 |

---

## 2. Seyrüsefer ve Basınç Sensörleri

| Sensör | Açıklama / Fonksiyon | Arayüz | Çalışma Gerilimi | Adet | Tahmini Fiyat (USD) |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **9-DoF Mutlak Yönelim IMU** | Cayro, İvmeölçer ve Manyetometre Füzyon İşlemcisi | `BNO055` (Bosch Sensortec) | I2C (3.3V) | 1 | \$22.00 |
| **Yüksek Hassasiyetli Basınç** | 30 Bar (300m) Su Geçirmez Derinlik Sensörü | `MS5837-30BA` (TE Connectivity) | I2C (3.3V) | 1 | \$48.00 |
| **Gövde İçi Nem & Sıcaklık** | Olası sızıntı tespiti için gövde içi güvenlik sensörü | `SHT31-DIS` (Sensirion) | I2C (3.3V) | 1 | \$3.50 |
| **Voltaj & Akım Algılama** | 0-36V, 50A Yüksek Taraf Şant Akım Monitörü | `INA219` / `INA226` | I2C (3.3V) | 1 | \$2.80 |

---

## 3. Güç Dağıtımı ve Galvanik İzolasyon

| Bileşen | Açıklama | MPN / Model | Paket | Adet | Tahmini Fiyat (USD) |
| :--- | :--- | :--- | :--- | :---: | :---: |
| **Ana DC-DC Düşürücü (Buck)** | 14.8V $\rightarrow$ 5.0V, 5A Senkron Buck Regülatör | `TI TPS5450DDAR` / `MP2307` | SOIC-8-EP | 1 | \$2.20 |
| **Aviyonik LDO Regülatör** | 5.0V $\rightarrow$ 3.3V Düşük Gürültülü LDO (800mA) | `AMS1117-3.3` / `TI TLV75733P` | SOT-223 | 2 | \$0.80 |
| **Yüksek Hızlı Optokuplör** | ESC ve servo PWM hatları için galvanik izolasyon | `6N137` (10 MBd Hızlı Lojik) | SOP-8 | 4 | \$2.40 |
| **Ters Polarite Koruması** | Düşük $R_{DS(on)}$ (< 3 mΩ) P-Kanal Güç MOSFET'i | `IRF4905` / `Infineon IPB120P04P4` | TO-220 / D2PAK | 1 | \$1.90 |
| **TVS Aşırı Gerilim Diyotu** | 18V Çift Yönlü Güç Hattı Transient Koruması | `SMCJ18CA` | SMC (DO-214AB) | 2 | \$0.90 |
| **Ferrit Filtre Boncuğu** | Motor gürültüsünü filtrelemek için EMI Boncuğu | `Murata BLM18PG121SN1D` | 0603 | 6 | \$0.60 |

---

## 4. Eyleyiciler, Motor ve Batarya

| Parça | Model / Özellikler | Çalışma Şartları | Adet | Tahmini Fiyat (USD) |
| :--- | :--- | :--- | :---: | :---: |
| **Ana İtki Fırçasız Motoru** | Su Altı Korozyona Dayanıklı BLDC Motor (900 - 1200 KV) | 14.8V, 20-30A tepe akımı | 1 | \$65.00 |
| **Elektronik Hız Kontrolcü (ESC)** | Çift Yönlü, Su Soğutmalı / Reçineli BLDC Sürücü (30-40A) | 4S Li-Po, DShot / PWM | 1 | \$28.00 |
| **Kontrol Kanatçığı Servoları** | Metal Dişli, Su Geçirmez Çift Bilyalı Mikro Servo ($2.5 - 4.0\text{ kg}\cdot\text{cm}$) | 5V - 6V, 0.10s/60° | 4 | \$48.00 |
| **Mekanik Kapak Açma Servosu** | Metal Dişli Mini Servo ($3.0\text{ kg}\cdot\text{cm}$) | 5V | 1 | \$9.00 |
| **Ana Batarya** | 4S (14.8V) 5000 mAh 50C Li-Po Batarya Paketi | 14.8V Nominal | 1 | \$55.00 |
| **Roket Ateşleme Rölesi / MOSFET** | Katı yakıt e-match ateşleme katı (Opto-izole N-Kanal MOSFET) | `AOD4184A` (40V, 50A) | TO-252 | 1 | \$0.85 |

---

## 5. Konnektör ve Mekanik Arayüzler

* **Güç Girişi:** Amass XT60-H Yüksek Akım Konnektörü (1 Çift)
* **SWD Debug Portu:** 1x4 2.54mm Pin Header (3.3V, SWDIO, SWCLK, GND)
* **USB DFU Girişi:** IP68 Su Geçirmez Panel Montaj Type-C Konnektör
* **Basınç Geçişleri (Penetrator):** Blue Robotics M10 Alüminyum Kablo Geçişleri (8 Adet)
* **Gövde O-Ringleri:** Nitril (NBR70) 140mm x 3mm Conta (2 Adet)

**Genel Toplam Tahmini Elektronik Aviyonik Maliyeti:** $\approx \$310 - \$360$ USD
