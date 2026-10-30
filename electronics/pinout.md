# Su Altı Roketi Referans Uçuş Kontrol Kartı (FC) Pin ve Donanım Mimarisi

Bu doküman, TEKNOFEST ve Roketsan Su Altı Roketi yarışmalarına hazırlanan tüm takımlara rehberlik etmesi amacıyla, sahada doğrulanmış tek parça Uçuş Kontrol Kartı (STM32F407VG + ESP32-S3) pin konfigürasyonunu ve haberleşme topolojisini tanımlar.

---

## 1. Ana Mimari Bileşenleri

* **Ana Uçuş Kontrolcüsü (FC):** STM32F407VG (168 MHz ARM Cortex-M4F, Donanımsal FPU, CMSIS-DSP, FreeRTOS)
* **Kablosuz Ağ, FOTA ve Kara Kutu:** ESP32-S3 (240 MHz Dual-Core, 16 MB Flash, 8 MB PSRAM, Wi-Fi AP/Web Server)
* **Aktüatör Sürücü Arayüzü:** Maestro UART-to-PWM Entegresi (38400 baud, 4x Fin Servosu + ESC BLDC Motor)
* **Seyrüsefer ve Basınç Sensörleri:** BNO055 (9-DoF Mutlak Yönelim IMU), MS5837 (Yüksek Hassasiyetli Derinlik/Basınç)

---

## 2. STM32F407VG Ana Pin Eşleşmesi ve Bus Topolojisi

| Fonksiyon / Hat | STM32F407VG Pin / Perifer | Karşı Donanım / Modül | Protokol / Mod | Açıklama |
| :--- | :--- | :--- | :--- | :--- |
| **I2C1 SCL** | PB6 (I2C1_SCL) | BNO055 & MS5837 | I2C (Bus Recovery Destekli) | DMA ile non-blocking okuma. Bus kilitlenmesinde 9 clock vuruşu. |
| **I2C1 SDA** | PB7 (I2C1_SDA) | BNO055 & MS5837 | I2C (Bus Recovery Destekli) | Pull-up dirençli. |
| **Maestro TX** | PA9 (USART1_TX) | Maestro UART-PWM | UART DMA (38400 baud) | Gatekeeper Task ve Queue üzerinden tek kanaldan sürülür. |
| **Maestro RX** | PA10 (USART1_RX) | Maestro UART-PWM | UART | Telemetri & onay hatları. |
| **FOTA / AP UART TX** | PC6 (USART6_TX) | ESP32-S3 RX | UART (128-byte chunk) | Bootloader & FOTA ikili veri transferi. |
| **FOTA / AP UART RX** | PC7 (USART6_RX) | ESP32-S3 TX | UART (128-byte chunk) | ESP32-S3'ten binary akışı ve telemetri aktarımı. |
| **Hardware Reset** | NRST (nRESET) | ESP32-S3 GPIO | Digital LOW Aktif | ESP32-S3 FOTA öncesi STM32'yi donanımsal resetler. |
| **SWD Clock** | PA14 (SWCLK) | SWD Header / ST-Link | SWD Debug | Saha içi GDB / Cortex-Debug / Segger RTT & SystemView. |
| **SWD I/O** | PA13 (SWDIO) | SWD Header / ST-Link | SWD Debug | SVD register izleme ve canlı bellek profilleme. |
| **USB DFU D-** | PA11 (USB_DM) | Micro-USB / USB-C | USB DFU | Acil durum bootloader yükleme portu. |
| **USB DFU D+** | PA12 (USB_DP) | Micro-USB / USB-C | USB DFU | ST DFU protokolü. |
| **Yedek Port 1** | PB10 / PB11 | Yedek Sensör Başlığı | USART3 / I2C2 | Sahada ikame sensör veya ek görev yükü için açık portlar. |
| **Yedek Port 2** | PC10 / PC11 | Harici Arayüz Başlığı | UART4 / SPI | Sahada telemetri testleri için yedek hatlar. |

---

## 3. ESP32-S3 Pin ve Ağ Konfigürasyonu

| Fonksiyon | ESP32-S3 Pin | Bağlı Olduğu Hat | Açıklama |
| :--- | :--- | :--- | :--- |
| **STM32 nRESET** | GPIO 4 | STM32 NRST | STM32'yi FOTA Custom Bootloader moduna sokmak için LOW'a çeker. |
| **STM32 UART TX** | GPIO 18 (U1TXD) | STM32 PC7 (USART6_RX) | 128 baytlık chunk'lar halinde binary iletimi. |
| **STM32 UART RX** | GPIO 17 (U1RXD) | STM32 PC6 (USART6_TX) | STM32 ACK baytı ve PSRAM kara kutu telemetri verisi. |
| **Wi-Fi Modu** | Dahili Radyo | AP (Access Point) | Mühendislik bilgisayarı için web arayüzü sunar. |
| **Blackbox Bellek**| 8 MB PSRAM | Dahili SPI/QPI | Pitch, Heading, Depth ve PID verilerini kesintisiz kaydeder. |

---

## 4. Sensör I2C Adresleri ve Parametreleri

* **BNO055 (9-DoF Mutlak Yönelim IMU):** `0x28` (varsayılan) veya `0x29`
* **MS5837-30BA (Yüksek Hassasiyetli Derinlik/Basınç):** `0x76` (Tatlı su / Tuzlu su kalibrasyonu destekli)

---

## 5. Donanımsal Koruma ve Saha İpuçları

1. **I2C Bus Lock Koruması:** MS5837 tuzlu su testlerinde kilitlendiğinde STM32 PB6 (SCL) 9 clock darbesi üreterek SDA hattını serbest bırakır.
2. **Optik / Galvanik İzolasyon:** Fırçasız motor (ESC) ve servo güç hatları lojik katmandan optik/diyot koruması ile izole edilmiştir.
3. **Yedekleme:** Kart üzerinde açık bırakılan UART ve I2C hatları sayesinde sahada sensör arızalarında lehim yapmaya gerek kalmadan port yönlendirmesi yapılabilir.
