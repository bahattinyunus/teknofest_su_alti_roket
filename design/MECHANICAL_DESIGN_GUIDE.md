# 🚀 Torpido Gövdesi Mekanik ve Hidrodinamik Tasarım Kılavuzu

Bu doküman, TEKNOFEST ve Roketsan yarışma şartnamesine tam uyumlu, minimum sürtünme katsayısına ($C_d \le 0.18$) ve yüksek hidrostatik dayanıklılığa sahip torpido gövde tasarımı için mühendislik parametrelerini sunar.

---

## 1. Myring Torpido Dış Profil Geometrisi

Torpido gövdelerinde laminer akışı korumak ve kuyrukta akış ayrılmasını (*flow separation*) engellemek için naval mimaride standart kabul edilen **Myring (1976)** denklemleri kullanılır:

```text
|<---- a (Burun) ---->|<------- b (Gövde) ------->|<---- c (Kuyruk) ---->|
+---------------------+---------------------------+----------------------+
|                     |                           |                      |
|      BURUN          |    SİLİNDİRİK GÖVDE       |     KUYRUK KONİSİ    |
| (Myring Elipsoid)   |      (Basınç Tüpü)        | (Myring Paraboloit)  |
|                     |                           |                      |
+---------------------+---------------------------+----------------------+
|<-------------------------- Toplam Boy (L) ---------------------------->|
```

### Myring Profil Denklemleri:
1. **Burun Bölgesi ($0 \le x \le a$):**
   $$r(x) = \frac{1}{2} D \cdot \left[ 1 - \left( \frac{x - a}{a} \right)^2 \right]^{\frac{1}{n}}$$
   * $D$: Gövde çapı ($150\text{ mm}$)
   * $a$: Burun uzunluğu ($250\text{ mm}$, $a/D \approx 1.67$)
   * $n$: Burun formu üssü (İdeal değer: $n \approx 1.7 - 2.0$)

2. **Silindirik Gövde ($a \le x \le a + b$):**
   $$r(x) = \frac{1}{2} D = \text{sabit}$$
   * $b$: Silindirik gövde boyu ($600\text{ mm}$)

3. **Kuyruk Bölgesi ($a + b \le x \le L$):**
   $$r(x) = \frac{1}{2} D - \left[ \frac{3D}{2c^2} - \frac{\tan\theta}{c} \right] (x - a - b)^2 + \left[ \frac{D}{c^3} - \frac{\tan\theta}{c^2} \right] (x - a - b)^3$$
   * $c$: Kuyruk boyu ($350\text{ mm}$)
   * $\theta$: Kuyruk yarı tepe açısı (Akış ayrılmasını önlemek için **$\theta \le 12^\circ - 15^\circ$** olmalıdır!)

---

## 2. Ağırlık ve Sephiye Dengeleme (CG - CB Trim)

Su altı roketinin su içinde alabora olmadan düz seyredebilmesi ve acil durumda pasif güvenlik olarak kendiliğinden su yüzeyine çıkabilmesi için:
1. **Pozitif Sephiye Kuralı:**
   * Net yüzebilirlik: $F_{net} = B - W \approx +2.0\text{ N}$ ila $+4.0\text{ N}$ ($200 - 400\text{ gram}$ pozitif).
2. **Dikey Kararlılık (Metasentrik Yükseklik):**
   * Sephiye Merkezi ($CB$), Ağırlık Merkezinin ($CG$) kesinlikle üzerinde olmalıdır: $z_{CB} < z_{CG}$ (z aşağı pozitif eksende).
   * Ağır bataryalar gövdenin en alt tabanına yerleştirilirken, hafif şamandıra köpükleri (sintaktik köpük) gövdenin tavanına sabitlenmelidir.

---

## 3. O-Ring Conta Kanalı Tasarımı (Parker Standartları)

Gövde kapakları ve flanş birleşimlerinde çift O-Ring conta sistemi uygulanmalıdır:

* **Conta Malzemesi:** Nitril (NBR 70 Shore A) veya Floroelastomer (FKM/Viton).
* **Sıkışma Oranı (Squeeze):** Statik radyal contalarda **%18 - %25**.
* **Kanal Doluluk Oranı (Groove Fill):** Su basıncı altında contanın şişebilmesi için **%75 - %85**.
* **Yüzey Pürüzlülüğü:** O-Ring'in temas ettiği silindir iç yüzeyi $Ra \le 0.4\mu\text{m}$ (honlanmış veya taşlanmış) olmalıdır.
* **Gresleme:** Montaj esnasında contalar silikon bazlı vakum gresi (`Molykote 111` veya `Dow Corning 4`) ile yağlanmalıdır.

---

## 4. Dönen Şaft ve Kanatçık Sızdırmazlığı

Kanatçık şaftlarının gövdeden çıkış noktalarında çift radyal O-Ring veya marin mekanik dudaklı keçe (*rotary shaft seal*) kullanılır:
* Şaft Malzemesi: Taşlanmış Paslanmaz Çelik (AISI 316L, h7 tolerans).
* Yağ Haznesi: İki conta arasına gres doldurularak suyun aviyonik kompartımanına ulaşması çift bariyerle engellenir.
