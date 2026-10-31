# TEKNOFEST & ROKETSAN SU ALTI ROKETİ YARIŞMASI
## TEST VE FİNAL DEĞERLENDİRME RAPORU ŞABLONU

**Takım Adı:** [Takım Adınız]  
**Takım ID:** [Takım ID Numaranız]  
**Tarih:** [GG.AA.YYYY]  

---

### 1. Üretim ve Montaj Doğrulaması
* **1.1. Üretilen Nihai Sistem Görselleri:** Gövde, kanatçık montajı, itki sistemi ve faydalı yük mekanizması fotoğrafları.
* **1.2. Nihai Kütle ve Boyut Tablosu:** Hedeflenen ile gerçekleşen değerlerin karşılaştırması ($m_{gercek}$ vs $m_{hedef}$).
* **1.3. Ağırlık ve Sephiye Dengeleme Sonuçları:** Araç statik olarak suya bırakıldığında pozitif sephiye davranışı ve trim açısı doğrulaması.

---

### 2. Laboratuvar ve Havuz Test Sonuçları
* **2.1. Basınç ve Sızdırmazlık Test Raporu:**
  * Test edilen derinlik / basınç değeri (bar).
  * Test süresi ve gövde içi nem sensörü logları.
* **2.2. Sensör Kalibrasyonu ve Gürültü Analizi:**
  * BNO055 Cayro & İvmeölçer sıfır kayması (*bias drift*).
  * MS5837 Derinlik gürültüsü ve 1D Kalman/ESKF filtreleme performansı grafikleri.
* **2.3. I2C Bus Lock Recovery Saha Deneyimi:**
  * Tuzlu su ortamında hatta kasıtlı elektriksel parazit verildiğinde 9-clock recovery algoritmasının tepki süresi.

---

### 3. Otonom Görev İcra Grafikleri ve Telemetri Analizi
* **3.1. Görev 1 (50m Seyir, 180° Dönüş ve Başlangıca Varış):**
  * Blackbox telemetri grafikleri: Zaman - Derinlik ($z$), Zaman - Yönelim ($\psi$), Zaman - İleri Hız ($v_x$).
  * 180° dönüş manevrasının tamamlanma süresi ve dönüş yarıçapı ($R_{turn}$).
* **3.2. Görev 2 (Yunuslama Manevrası ve Roket Ateşleme):**
  * Su sathına yaklaşırken pitch açısı grafiği ($\theta(t)$).
  * Su yüzeyine çıkış anında derinlik sensörünün sıfırlanması ($z \le 0.05\text{ m}$).
  * Mekanik kapağın açılma süresi ($t_{kapak}$) ve elektronik ateşleme rölesinin tetiklenme anı.

---

### 4. Saha Kriz Yönetimi ve Kazanılan Deneyimler
* **4.1. Sahada Karşılaşılan Donanımsal/Yazılımsal Problemler:** Karşılaşılan hatalar ve geliştirilen çözümler.
* **4.2. "Yeniden Yapsaydık" Mühendislik Öz-Eleştirisi:** Gelecek senelere aktarılacak kritik tavsiyeler.
