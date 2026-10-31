# 📊 Mühendislik Analiz ve Simülasyon Araçları (Analysis)

Bu dizin, otonom su altı roketi için hidrodinamik direnç hesaplamaları, itki-motor eşleşmesi, su altı basınç gövdesi dayanım analizleri ve kontrol kanatçığı polar modellemelerini içerir.

---

## 📁 Analiz Modülleri

### 1. `propulsion/thrust_drag_matching.py`
* **ITTC-1957 Sürtünme Hattı:** Torpido geometrisi için Reynolds sayısı, ıslak alan ve form faktörü hesabı.
* **İtki-Direnç Eşleşmesi:** $0.5 - 4.0\text{ m/s}$ hız aralığında gereken pervane itkisi ($T$) ve motor gücü ($P_{elec}$).
* **Görev Enerji Bütçesi:** 4S Li-Po bataryanın 50m ve 100m seyirlerde tükettiği kapasite (mAh ve %).

```bash
python analysis/propulsion/thrust_drag_matching.py
```

---

### 2. `structural/pressure_hull_thickness.py`
* **Hidrostatik Gerilme Hesabı:** Hedeflenen derinliklerde ($10\text{m} - 30\text{m}$) gövde üzerindeki çevre (*hoop*) ve eksenel (*longitudinal*) gerilmeler, von Mises eşdeğer gerilmesi.
* **Elastik Burkulma ve Çökme Basıncı ($P_{cr}$):** Silindirik denizaltı gövdeleri için Southwell/Windenburg formülü.
* **Malzeme Kıyaslaması:** Döküm Akrilik (PMMA), Polikarbonat ve 6061-T6 Alüminyum emniyet katsayıları ($FOS_{yield}$ ve $FOS_{buckling}$).

```bash
python analysis/structural/pressure_hull_thickness.py
```

---

### 3. `cfd/fin_lift_drag_polar.py`
* **Simetrik Kanatçık Polarları (NACA 0012/0015):** Hücum açısına göre kaldırma ($C_L$) ve sürüklenme ($C_D$) katsayıları.
* **Stall Açısı Tespiti:** $14^\circ - 16^\circ$ üzeri akış ayrılması simülasyonu.
* **Servo Menteşe Torku:** Maksimum seyir hızında kontrol yüzeyini tutmak için servonun üretmesi gereken tork ($kg\cdot cm$) hesabı.

```bash
python analysis/cfd/fin_lift_drag_polar.py
```
