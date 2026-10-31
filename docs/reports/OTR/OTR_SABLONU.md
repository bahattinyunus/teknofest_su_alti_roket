# TEKNOFEST & ROKETSAN SU ALTI ROKETİ YARIŞMASI
## ÖN TASARIM RAPORU (OTR) ŞABLONU

**Takım Adı:** [Takım Adınız]  
**Takım ID:** [Takım ID Numaranız]  
**Kurum / Üniversite:** [Üniversite veya Lise Adı]  
**Tarih:** [GG.AA.YYYY]  

---

### 1. Takım Organizasyonu ve Görev Dağılımı
* **1.1. Takım Yapısı:** Aviyonik, Mekanik, Hidrodinamik ve Sponsorluk alt ekipleri.
* **1.2. İş Zaman Çizelgesi (Gantt Şeması):** Tasarım, analiz, üretim, montaj ve havuz testleri takvimi.
* **1.3. Bütçe ve Tedarik Planı:** Malzeme maliyetleri ve sponsorluk bütçesi.

---

### 2. Görev Analizi ve Sistem Gereksinimleri
* **2.1. Görev 1 (Seyir ve Dönüş):** 50m su altı seyri, 180° dönüş manevrası ve başlangıç çizgisine geri dönüş gereksinimleri.
* **2.2. Görev 2 (Yunuslama ve Model Roket Ateşleme):** 30m seyir sonrası su sathına çıkış, mekanik kapak açılması ve roket motorunun otonom ateşlenmesi.
* **2.3. Tasarım Kısıtları Özeti:**
  * Torpido formunda eksenel simetrik gövde.
  * Yan itici olmaksızın 4 kanatçık (+ veya X) ile yönelim.
  * Tek ana fırçasız motor (hovering kesinlikle yasaktır).

---

### 3. Mekanik ve Hidrodinamik Ön Tasarımı
* **3.1. Dış Geometri ve Ölçüler:** Boy, çap, burun formu (Myring / Eliptik / Parabolik).
* **3.2. Ağırlık ve Sephiye (Buoyancy) Dengesi:**
  * Kütle kestirimi: $m_{toplam}$ (kg).
  * Batma hacmi: $V_{govde}$ ($m^3$).
  * Sephiye Merkezi ($CB$) ve Ağırlık Merkezi ($CG$) dikey ayrımı ($z_{CB} < z_{CG}$).
* **3.3. Kontrol Kanatçığı Seçimi:** Haç (+) veya X-Rudder (X) konfigürasyon tercihi ve gerekçesi.
* **3.4. Gövde Malzemesi ve Sızdırmazlık Konsepti:** Akrilik / Alüminyum basınç tüpü ve O-ring conta kanalı tasarımı.

---

### 4. Aviyonik ve Elektronik Mimarisi
* **4.1. Uçuş Kontrol Kartı (FC) Mimarisi:**
  * Ana Mikrodenetleyici: STM32F407VG (168 MHz ARM Cortex-M4F, Donanımsal FPU).
  * Sensör Grubu: BNO055 (9-DoF Mutlak Yönelim IMU), MS5837 (Derinlik ve Basınç Sensörü).
* **4.2. Güç Dağıtım ve Batarya Sistemi:**
  * Li-Po Batarya seçimi (4S 14.8V).
  * 5V izole regülatör ve motor güç anahtarlama katmanı.
* **4.3. Kablosuz Güncelleme ve Kara Kutu:** ESP32-S3 Wi-Fi SoftAP ve FOTA mimarisi.

---

### 5. Gömülü Yazılım ve Otonom Kontrol Stratejisi
* **5.1. İşletim Sistemi Tercihi:** FreeRTOS ve deterministik görev öncelikleri.
* **5.2. Seyrüsefer ve Filtreleme:** Zero-Allocation ESKF (Error State Kalman Filter).
* **5.3. Görev Sonlu Durum Makinesi (FSM):** Kalibrasyon, dalış, seyir, dönüş ve ateşleme adımları.

---

### 6. Risk Yönetimi ve Emniyet Tedbirleri
* **6.1. Su Sızması Durumunda Failsafe:** Pozitif sephiye ile yüzeye çıkış.
* **6.2. Motor ve Ateşleme Güvenlik Kilidi:** Çift aşamalı donanımsal ve yazılımsal Safe-to-Arm kilidi.
