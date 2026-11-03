# 🛠️ Uçuş Kontrol Kartı (FC) PCB Tasarım ve Üretim Kılavuzu

Bu kılavuz, su altı otonom roketi aviyonik kartının (Cemalettin & Gökhan referans mimarisi) 4 katmanlı PCB yerleşimi, termal yönetimi ve marin ortamlara karşı korunması için kritik tasarım kurallarını içerir.

---

## 1. 4 Katmanlı PCB Stackup Mimarisi

Sinyal bütünlüğünü (Signal Integrity) korumak ve motor gürültüsünü sönümlemek amacıyla standart 4 katmanlı (JLC04161H veya eşdeğeri) FR-4 stackup tercih edilmelidir:

```text
Katman 1 (Top Layer):      Yüksek Hızlı Sinyaller (SWD, I2C, USART6) + Dekuplaj Kondansatörleri
Katman 2 (Inner Layer 1):  Kesintisiz Katı Toprak Düzlemi (GND Plane)
Katman 3 (Inner Layer 2):  Güç Düzlemleri (3.3V Aviyonik Rayı & 5V Servo Rayı)
Katman 4 (Bottom Layer):   Yüksek Akım Güç Yolları (Motor 14.8V) + İkincil Sinyal Hatları
```

> [!IMPORTANT]
> **Katı Toprak Düzlemi Kuralı:**  
> Katman 2 üzerinde kesinlikle sinyal yolu geçirilmemeli, kesintisiz bir toprak referansı (Solid Ground Plane) olarak bırakılmalıdır. Bu kural, BNO055 IMU ve MS5837 I2C hatlarının parazit kapmasını engeller.

---

## 2. Hat Genişlikleri ve Akım Kapasiteleri (IPC-2152 Standartları)

* **Ana Batarya & Motor Hatları ($20 - 30\text{A}$ pik):**
  * Bakır Kalınlığı: **2 oz ($70\mu\text{m}$)** tercih edilmelidir.
  * Hat Genişliği: Minimum **$4.5\text{ mm}$** veya çift katmanda poligon döküm (*copper pour*) olarak geçirilmelidir.
  * Termal Delikler (*Thermal Vias*): MOSFET ve şant dirençleri etrafına $0.3\text{ mm}$ matkap çaplı çoklu via dizileri konmalıdır.
* **5V Servo Güç Hatları ($3 - 5\text{A}$ tepe):**
  * Hat Genişliği: Minimum **$1.8\text{ mm}$**.
* **3.3V Aviyonik ve Sinyal Hatları ($< 500\text{mA}$):**
  * Hat Genişliği: **$0.25 - 0.35\text{ mm}$** ($10 - 14\text{ mil}$).
  * I2C SDA/SCL hatları $4.7\text{ k}\Omega$ pull-up ile desteklenmeli ve uzun paralel hatlardan kaçınılmalıdır.

---

## 3. Nem, Kondansasyon ve Korozyon Koruması (Marin Önlemleri)

Su altı roketleri denizden veya soğuk havuzdan çıkarıldığında, gövde içi hava soğur ve bağıl nem hızla yoğuşarak PCB üzerinde mikroskobik su damlacıkları oluşturur.

1. **Konformal Kaplama (Conformal Coating):**
   * Üretim ve testler tamamlandıktan sonra PCB; konnektörler, SWD pinleri ve MS5837 basınç portu maskelenerek akrilik veya silikon bazlı koruyucu sprey (`HumiSeal 1B31` veya `Electrolube AFA`) ile 2 kat kaplanmalıdır.
2. **Konnektör İzolasyonu:**
   * Kart üzerindeki kablo lehim bağlantı noktaları RTV silikon veya sıcak eriyik yapıştırıcı ile mekanik olarak kilitlenmelidir.
3. **Nem Alıcı Paket (Silica Gel):**
   * Basınç tüpü kapatılmadan önce aviyonik kartının yanına en az bir adet $5\text{g}$ fırınlanmış silika jel paketi yerleştirilmelidir.
