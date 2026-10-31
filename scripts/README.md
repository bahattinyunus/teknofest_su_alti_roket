# 🛠️ Geliştirici ve Otomasyon Araçları (Scripts)

Bu dizin, otonom su altı roketi projesinde derleme, kablosuz yazılım yükleme ve saha telemetrisi operasyonlarını otomatize eden yardımcı Python betiklerini içerir.

---

## 📜 Betikler ve Kullanım Kılavuzu

### 1. `build_firmware.py` — Otomatik Donanım Derleme Aracı
Tüm işletim sistemlerinde `CMake` ve `Ninja` altyapısını kullanarak STM32F407VG mikrodenetleyicisi için üretim binary ve ELF dosyalarını derler. Sistemdeki `arm-none-eabi-gcc` derleyicisini veya CubeIDE dizinlerini otomatik olarak tespit eder.

```bash
# PCB hedefi ile derleme (Varsayılan)
python scripts/build_firmware.py

# Pertinax prototip donanımı için derleme
python scripts/build_firmware.py --pertinax

# Temiz derleme (Clean build)
python scripts/build_firmware.py --clean
```

---

### 2. `flash_fota.py` — Kablosuz FOTA Güncelleme ve Kara Kutu Aracı
Gövde sızdırmazlık vidalarını açmadan, Wi-Fi üzerinden ESP32-S3 SoftAP ağına (`ROCKET_FOTA_ACCESS_POINT`) bağlanarak STM32 binary dosyasını kablosuz yükler veya 8MB PSRAM'de saklanan kara kutu telemetri logunu çeker.

```bash
# Derlenmiş binary dosyasını kablosuz flaşlama
python scripts/flash_fota.py firmware/build/teknofest_su_alti_roket.bin

# Farklı bir IP adresine yükleme
python scripts/flash_fota.py firmware/build/teknofest_su_alti_roket.bin --ip 192.168.4.1

# Görev sonrası araç sathına çıktığında kara kutu logunu indirme
python scripts/flash_fota.py --download-blackbox
```
