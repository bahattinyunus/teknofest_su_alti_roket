# TEKNOFEST & ROKETSAN SU ALTI ROKETİ YARIŞMASI
## KRİTİK TASARIM RAPORU (KTR) ŞABLONU

**Takım Adı:** [Takım Adınız]  
**Takım ID:** [Takım ID Numaranız]  
**Tarih:** [GG.AA.YYYY]  

---

### 1. Detaylı Mekanik ve Yapısal Tasarım
* **1.1. CAD Modeli ve Patlatılmış Montaj:** Tüm alt bileşenlerin 3B modelleri ve tolerans analizleri.
* **1.2. Basınç Gövdesi Dayanım Analizi (FEM):**
  * von Mises gerilme dağılımı ($\sigma_{vm} \le \sigma_y / 2$).
  * Kritik burkulma çökme basıncı ($P_{cr}$) analizi ve emniyet katsayısı ($FOS \ge 2.5$).
* **1.3. O-Ring ve Sızdırmazlık Hesabı:** Conta ezilme oranı (%15 - %25) ve gland kanal boyutları.
* **1.4. Faydalı Yük (Model Roket) Fırlatma Tüpü ve Kapak Mekanizması:** Servo tahrikli yaylı açılma sistemi.

---

### 2. Sayısal Akışkanlar Dinamiği (CFD) ve Hidrodinamik Analizler
* **2.1. Gövde Sürtünme Katsayısı ($C_d$) Analizi:** Farklı hızlarda ($1.0 - 3.5\text{ m/s}$) sürüklenme kuvveti.
* **2.2. Kontrol Kanatçığı Hidrodinamik Polarları:**
  * NACA 0012/0015 fin kaldırma ($C_L$) ve sürüklenme ($C_D$) eğrileri.
  * Stall açısı ($\alpha_{stall}$) tespiti.
  * Maksimum seyir hızında gereken servo torku ($M_{servo}$) hesabı ve servo seçimi.
* **2.3. İtki ve Pervane Eşleşmesi:** BLDC motor devri (RPM), pervane adımı/çapı ve itki verimi.

---

### 3. Detaylı Elektronik ve PCB Tasarımı
* **3.1. Uçuş Kontrol Kartı (FC) Devre Şeması (Schematic):**
  * STM32F407VG mikrodenetleyici çevresi, kristal osilatör ve filtre kondansatörleri.
  * BNO055 ve MS5837 I2C hatları, pull-up dirençleri ve Bus Lock Recovery GPIO yönlendirmesi.
  * Maestro UART-PWM dönüştürücü entegre bağlantıları.
  * ESP32-S3 FOTA nRESET ve USART6 hatları.
* **3.2. PCB Yerleşimi ve EMI/EMC Önlemleri:**
  * Güç rayları ile sinyal hatlarının galvanik/optik izolasyonu.
  * 4 katmanlı (GND-Signal-Power-Signal) PCB stackup mimarisi.
* **3.3. Batarya Yönetim Sistemi (BMS) ve Güç Tüketim Bütçesi:**
  * Akım tüketim tablosu (Seyir anı, pik servo anı, bekleme modu).

---

### 4. Gömülü Yazılım Mimarisi ve Kod Akış Şemaları
* **4.1. FreeRTOS Görev ve Öncelik Dağılımı:**
  * `vGatekeeperTask` (Öncelik: 5, UART DMA hattı tekil sahibi).
  * `vSensorIOTask` (Öncelik: 4, 50 Hz ESKF döngüsü).
  * `vMissionExecutionTask` (Öncelik: 3, State Machine).
  * `vSoftwareWatchdogTask` (Öncelik: 6, 100 ms denetleme penceresi).
* **4.2. State Machine Akış Şemaları:** `CMD_ARM`, `CMD_SET_DEPTH`, `CMD_GO_DISTANCE`, `CMD_TURN_HEADING`, `CMD_PITCH_UP`, `CMD_FIRE_ROCKET`.
* **4.3. C++ Template Zero-Allocation ESKF Algoritması:** Matris boyutları derleme zamanında sabitlenen durum kestirimi.
* **4.4. Kontrol Dağıtım Matrisi (Control Allocation):** X-Rudder sanal tork ($\tau_p, \tau_y, \tau_r$) - fin açısı dönüşümü.

---

### 5. Test ve Entegrasyon Planı
* **5.1. Kuru Testler:** Sensör kalibrasyonu, donanımsal Watchdog ve Gatekeeper UART stres testleri.
* **5.2. Basınç Odası Sızdırmazlık Testi:** 2 bar hidrostatik basınç altında sızdırmazlık doğrulaması.
* **5.3. Havuz Otonom Seyir Testleri:** İTÜ Olimpik Havuzu veya yerel tesislerde 50m seyir ve dönüş denemeleri.
