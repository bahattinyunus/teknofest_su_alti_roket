<div align="center">
  <img src="media/brand/banner_v2.png" alt="Su Altı Roketi Açık Kaynak Rehberi" width="100%">
  <br>
  <img src="media/brand/logo.png" alt="Logo" width="120">
  
  # 🌊 TEKNOFEST SU ALTI ROKETİ
  ### *Açık Kaynak Geliştirici Rehberi ve Referans Aviyonik Mimarisi*
  ### *Advanced Autonomous Underwater Rocket Framework for All Teams*
  
  [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
  [![Platform: STM32F407](https://img.shields.io/badge/MCU-STM32F407VG%20%28ARM%20Cortex--M4F%29-007ACC?style=flat-square&logo=stmicroelectronics)](electronics/pinout.md)
  [![RTOS: FreeRTOS](https://img.shields.io/badge/RTOS-FreeRTOS%20%2B%20DMA-00A98F?style=flat-square)](docs/ENGINEERING_ANATOMY.md)
  [![FOTA: ESP32-S3](https://img.shields.io/badge/FOTA-ESP32--S3%20%28Web%20%26%20Blackbox%29-E94E32?style=flat-square)](docs/ENGINEERING_ANATOMY.md#5-kablosuz-güncelleme-mimarisi-esp32-s3-ile-fota-ve-kara-kutu-blackbox)
  [![Filter: ESKF](https://img.shields.io/badge/Filter-Zero--Allocation%20ESKF%20%28CMSIS--DSP%29-orange?style=flat-square)](docs/ENGINEERING_ANATOMY.md#c-template-tabanlı-kalman-filtresi-eskf)
  [![Target: All Teams](https://img.shields.io/badge/Audience-All%20TEKNOFEST%20Teams-success?style=flat-square)](#-bu-deponun-amacı-ve-açık-kaynak-vizyonu)

  ---
  
  **TEKNOFEST ve Roketsan Su Altı Roketi Yarışması**'na katılan tüm üniversite ve lise takımlarına, araştırmacılara ve mühendis adaylarına rehberlik etmek üzere kurulmuş **bağımsız ve açık kaynaklı bir referans geliştirme platformudur.**
</div>

---

## 💡 Bu Deponun Amacı ve Açık Kaynak Vizyonu

Su altı roketi konsepti, geleneksel ROV sistemlerinden ve hava roketlerinden köklü biçimde ayrılan, hidrodinamik kısıtları son derece yüksek bir mühendislik alanıdır. Dünyada ve ülkemizde bu özel konsepte yönelik açık kaynaklı mimari, referans gömülü kod ve saha tecrübesi eksikliğini gidermek amacıyla bu depo oluşturulmuştur.

> 🏆 **Vaka Analizi & Referans Mimari:**  
> Depo içeriğindeki donanım şemaları, FreeRTOS görev kurguları, FOTA kablosuz yükleme mekanizması ve seyrüsefer (ESKF) algoritmaları; Roketsan Su Altı Roketi Yarışması'nda **Türkiye Birinciliği (Şampiyonluk)** elde eden İTÜ Sungur Takımı'nın ve sahada başarı göstermiş ekiplerin kanıtlanmış mühendislik çözümleri referans alınarak genelleştirilmiş ve tüm takımların istifadesine sunulmuştur.

---

## 📖 Kapsamlı Mühendislik Rehberi ve Vaka Analizi

> 🔗 Donanım tasarımından FreeRTOS DMA yapılandırmasına, I2C Bus Lock kriz yönetiminden FOTA mimarisine kadar tüm teknik ayrıntılar için ana raporu inceleyin:  
> **👉 [Şampiyon Roketin Mühendislik Anatomisi: STM32, FreeRTOS ve FOTA ile Su Altı Otonomisi](docs/ENGINEERING_ANATOMY.md)**

---

## 🚀 Öne Çıkan Referans Mimari Özellikleri

- **STM32F407VG Ana Uçuş Kontrolcüsü (FC):** 168 MHz ARM Cortex-M4F, donanımsal FPU ve CMSIS-DSP statik kütüphaneleriyle optimize edilmiş deterministik uçuş kontrol çekirdeği.
- **ESP32-S3 ile FOTA & Blackbox:** Gövde sızdırmazlığını bozmadan Wi-Fi üzerinden 128-byte chunk'larla kablosuz STM32 yazılım güncellemesi ve 8MB PSRAM üzerinde yüksek frekanslı kara kutu telemetri kaydı.
- **FreeRTOS & DMA Gatekeeper Mimarisi:** HAL kütüphanesinin bloklayan çağrılarını devre dışı bırakan, UART erişimlerini atomik ve thread-safe hale getiren Gatekeeper Task & Queue yapısı.
- **Zero-Allocation C++ Template ESKF:** Heap tahsisini sıfırlayan, heap fragmentation riskini yok eden Error State Kalman Filter (CMSIS-DSP destekli).
- **I2C Bus Lock Recovery (Saha Dayanıklılığı):** Tuzlu su ve elektriksel gürültü kaynaklı I2C kilitlenmelerinde SCL hattına 9 clock vurarak köle sensörün SDA hattını serbest bırakan donanımsal kurtarma mekanizması.
- **OS-Agnostic Sürücü Katmanı:** Hem FreeRTOS altında hem de bootloader/startup aşamasında tek kod tabanıyla çalışan function pointer delay callback mimarisi.
- **Yunuslama ve Roket Ateşleme Döngüsü:** 4 adet aerodinamik kontrol kanatçığıyla pitch-up (yunuslama) manevrası, su yüzeyine çıkış, mekanik kapak açılışı ve model roket otonom ateşleme sekansı.

---

## 🎯 Yarışma Konsepti ve Görev Profilleri (Roketsan Şartnamesi)

Roketsan Su Altı Roketi Yarışması; standart ROV sistemlerinden farklı olarak kapsül atım ve torpido dinamiğine dayanır. Yan iticiler veya hovering yasaktır; yönelim 4 kontrol kanatçığıyla (+ veya X konfigürasyonu), itki ise tek bir fırçasız motorla sağlanır.

```mermaid
flowchart TD
    subgraph "Görev 1: Otonom Seyir & Geri Dönüş (300 Puan)"
        G1_A[Başlangıç Çizgisi] -->|50m Su Altı Otonom Seyir| G1_B[Hedef Nokta]
        G1_B -->|180° Keskin Dönüş Manevrası| G1_C[Geri Dönüş Seyri]
        G1_C -->|50m Geri Seyir| G1_D[Başlangıç Noktasına Varış & Motor Stop]
    end

    subgraph "Görev 2: Yunuslama & Roket Ateşleme (400 Puan)"
        G2_A[Otonom Seyir] -->|Hedef Güvenli Bölge| G2_B["Yunuslama Manevrası (Pitching)"]
        G2_B -->|Sathına Çıkış| G2_C[Yüzeye Ulaşma]
        G2_C -->|Mekanik Kapak Açılışı| G2_D[Faydalı Yük Hazırlığı]
        G2_D -->|Otonom Ateşleme| G2_E[Model Roket Fırlatılışı 🚀]
    end
```

---

## 🔌 Referans Donanım ve Aviyonik Topolojisi

Tüm takımlar için önerilen tek parça veya modüler Uçuş Kontrol Kartı (FC) topolojisi; sahada karşılaşılabilecek tüm kriz senaryolarına karşı yedekli donanımsal hatlar ve izole güç katmanı ile kurgulanmalıdır.

```mermaid
graph TD
    subgraph "Güç Katmanı"
        BATT[Li-Po Batarya] --> BMS[BMS & Koruma]
        BMS --> REG_5V[5V İzole LDO / Regülatör]
        BMS --> REG_PWR[ESC & Servo Güç Hattı]
    end

    subgraph "Aviyonik Kontrol Kartı (Referans Mimari)"
        STM32[STM32F407VG - Ana İşlemci 168MHz]
        ESP32[ESP32-S3 - FOTA & Blackbox]
        IMU[BNO055 9-DoF IMU]
        PRESS[MS5837 Basınç / Derinlik]
        MAESTRO[Maestro UART-to-PWM Entegresi]
        REDUNDANT[Yedek UART / I2C / SWD / DFU]
    end

    subgraph "Eyleyiciler (Actuators)"
        SERVOS[4x Kontrol Kanatçığı Servoları]
        BLDC[Ana Fırçasız Motor & ESC]
        HATCH[Kapak Açma & Ateşleme Rölesi]
    end

    REG_5V --> STM32
    REG_5V --> ESP32
    ESP32 <-->|UART & nRESET| STM32
    STM32 <-->|I2C1 DMA + 9-Clock Recovery| IMU
    STM32 <-->|I2C1 DMA + 9-Clock Recovery| PRESS
    STM32 -->|UART1 DMA / Gatekeeper Queue| MAESTRO
    MAESTRO --> SERVOS
    MAESTRO --> BLDC
    STM32 --> HATCH
```

Detaylı pin konfigürasyonu ve donanım hatları için [electronics/pinout.md](electronics/pinout.md) dosyasına göz atın.

---

## 📡 FOTA (Firmware Over-The-Air) & Kara Kutu Akışı

Saha testlerinde gövde sızdırmazlık vidalarını açmadan saniyeler içinde yeni yazılım yüklenmesini sağlayan mimari:

```mermaid
sequenceDiagram
    participant PC as Mühendislik Bilgisayarı
    participant ESP as ESP32-S3 (AP & Web Server)
    participant STM as STM32F407VG (Bootloader)

    PC->>ESP: Wi-Fi üzerinden .bin yükle
    ESP->>ESP: CRC32 Doğrulaması yap
    ESP->>STM: nRESET pinini LOW'a çek (Reset)
    STM->>STM: 0x08000000 Bootloader Başlat
    ESP->>STM: 0x7F Senkronizasyon Baytı (UART)
    loop 128-Byte Parçalar (Chunks)
        ESP->>STM: 128 Byte Payload
        STM->>STM: Flash Belleğe Yaz
        STM-->>ESP: ACK Baytı
    end
    STM->>STM: VTOR Kaydır & 0x08010000 App Adresine Zıpla
```

---

## ⚙️ Modern Geliştirme Ortamı (VS Code + CMake + Ninja)

STM32CubeIDE'nin hantallığını aşmak için takımlara tavsiye edilen modern gömülü araç zinciri:

* **Derleyici:** ARM GNU Toolchain (`arm-none-eabi-gcc` / `g++`)
* **Derleme Sistemi:** CMake + Ninja (3 kat daha hızlı artımlı derleme)
* **Intellisense:** Clangd (`compile_commands.json` ile `#ifdef` dostu sembol çözümleme)
* **Canlı Hata Ayıklama:** Cortex-Debug + SVD (System View Description) üzerinden anlık register takibi
* **Profilleme:** Segger SystemView & RTT ile FreeRTOS context-switching ve ISR jitter analizi

```bash
# Firmware yapılandırma (PCB donanım hedefi ile)
cd firmware
cmake -B build -G Ninja -DTARGET_HARDWARE=PCB

# Derleme
ninja -C build
```

---

## 📂 Proje Dizin Yapısı

```text
teknofest_su_alti_roket/
├── docs/
│   ├── ENGINEERING_ANATOMY.md   # Şampiyon Roketin Mühendislik Anatomisi (Detaylı Rapor)
│   ├── specs/                   # Yarışma şartnameleri (Roketsan V1.2)
│   └── reports/                 # OTR, KTR ve Final tasarım rapor şablonları
├── firmware/                    # STM32F407VG + FreeRTOS + FOTA Üretim Kodları
│   ├── include/                 # Header dosyaları (ESKF, PID, Watchdog, Sürücüler)
│   ├── src/                     # C/C++ kaynak kodları (Gatekeeper, Görev Yöneticisi)
│   ├── esp32_s3_firmware/       # ESP32-S3 FOTA Wi-Fi Server & PSRAM Blackbox
│   └── CMakeLists.txt           # Modüler derleme mimarisi
├── electronics/
│   ├── pinout.md                # STM32F407 & ESP32-S3 referans pin haritası
│   ├── schematics/              # Devre şemaları
│   └── pcb/                     # Kart yerleşim ve üretim dosyaları
├── sim/
│   └── mission_simulator.py     # Görev 1 & Görev 2 hidrodinamik simülatörü
├── src/
│   ├── navigation/              # Python prototip algoritmaları
│   └── gcs/                     # Yer Kontrol İstasyonu ve Blackbox log parser
├── analysis/                    # CFD, itki ve yapısal analiz klasörleri
├── design/                      # CAD modelleri ve teknik çizimler
└── tests/                       # ESKF, Blackbox ve FSM birim testleri (100% Pass)
```

---

## 🏆 Mühendislik Karnesi (Tüm Takımlar İçin Do's & Don'ts)

| Yapılması Gerekenler (Do's) | Kaçınılması Gerekenler (Don'ts) |
| :--- | :--- |
| **Sensör Birleştirme:** Tüm sensörleri tek bir IO task'ı altında toplayıp Getter/Setter ile dağıtmak. | **Over-Tasking:** Her sensör için ayrı Task açıp işlemciyi Context Switch yüküne boğmak. |
| **Thread-Safe Haberleşme:** Görevler arası veri aktarımında Queue ve Semaphore kullanmak. | **Kritik Bölge Suistimali:** Değişken paylaşımlarında `portENTER_CRITICAL()` ile kesmeleri kapatmak. |
| **Bütünleşik Watchdog:** Task sağlıklarını 100 ms yenileme pencereli Software Watchdog ile izlemek. | **Teşhis Eksikliği:** HardFault handler'ları boş bırakmak ve register dökümünü ihmal etmek. |
| **Modern C++:** Tüm katmanları baştan C++ OOP, RAII ve Template yapılarıyla kurgulamak. | **Sabit dt Varsayımı:** `vTaskDelay` sürelerinin mükemmel sabitliğine güvenmek (Donanımsal Timer ile dt ölçülmeli). |

---

## 💻 Simülasyon ve Testleri Çalıştırma

```bash
# Birim testleri çalıştırma
python -m unittest discover tests

# Hidrodinamik görev simülasyonunu koşturma
python sim/mission_simulator.py
```

---

## 🤝 Katkıda Bulunma
Bu repo tüm TEKNOFEST ekiplerinin ortak faydalanması ve katkı sunması için kurulmuştur. Yeni sensör sürücüleri, simülasyon modelleri veya mimari iyileştirmeler için PR (Pull Request) gönderebilirsiniz.

## 📜 Lisans
Bu proje **MIT Lisansı** altında lisanslanmıştır. Detaylar için [LICENSE](LICENSE) dosyasına göz atın.

---
<div align="center">
  <b>Designed for Reliability, Engineered for the Deep.</b><br>
  Tüm <b>TEKNOFEST Su Altı Roketi</b> Takımlarına Başarılar Dileriz! 🚀🌊
</div>
