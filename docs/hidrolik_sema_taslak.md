# Hidrolik şema — taslak v1 (Kademe 3 girdisi)

Durum: TASLAK. Kullanıcının ASCII şeması değerlendirildi, hatalar düzeltildi. Henüz params/bom'a bağlı değil; Kademe 3'te (hidrolik ağ modeli) ayrı sohbette ISO 1219 şemasına ve ID'lere bağlanacak.
Güvenlik: akümülatör deşarjı ve basınç boşaltma her onarım adımının önüne konur (CLAUDE.md kural 10).

## Modelle eşleşen parçalar (ürün ağacı ID'leri)
| Şemadaki eleman | Ağaç ID | Modeldeki veri |
|---|---|---|
| TK1 yağ tankı | A61 | 784 L |
| M1 + P1 motor-pompa | A62 | motor 30 kW |
| ACC1 akümülatör | A56 (2 adet) | tüp OD220 × 1300 |
| Çarpan (basınç artırıcı) | A55 | Ø200/Ø140, oran 2,04 |
| CYL1 enjeksiyon silindiri | A54 | Ø140 sondaj |
| Kapama silindiri | A35 | Ø160 sondaj |
| İtici silindirler | A41 | 2 adet, Ø100/Ø56 |
Sistem basıncı: 140 bar (params.global).

## Orijinal şemadaki hatalar ve eksikler
Güvenlik (en önemli):
1. Akümülatör grubunda emniyet ve deşarj yok. Her akümülatöre kapama vanası, emniyet valfi, kilitlenebilir deşarj (tanka) valfi ve basınç göstergesi/sensörü gerekir. Onarımda basınç boşaltma buna bağlı.
2. Pompa hattında çek valf yok. Pompa durunca akümülatör pompa üzerinden boşalmamalı.

Fonksiyon:
3. Enjeksiyon 3 fazlı (yavaş / hızlı / basınç artırma) ama şemada tek valf bloğu ve silindir var. Çarpan (A55) hiç yok. Hızlı vuruş akümülatörden, yavaş vuruş pompadan gelir; Y1 ikisinden beslenmeli. Şemada Y1 yalnız akümülatörden besleniyor.
4. Aktüatör hatları tek çizgi. Çift etkili silindirin iki portu (ileri/geri) vardır; geri dönüş hattı eksik. Enjeksiyon silindirinin geri hattı da yok.
5. Pompa kaçak yağ (case drain) hattı yok. Eksenel pistonlu pompada zorunlu, doğrudan tanka gider.
6. Kapama devresi eksik: "Kalıp kont." kutusu tek başına, kapama silindiri (A35) ve basınç kontrolü yok. "İtici kont." çift silindirli itici grubunu (A41, 2 adet paralel) göstermiyor. Kutular aktüatöre bağlanmıyor.
7. Pompa kontrolü belirsiz: "eksenel pistonlu" yazmış ama basınç kompanzasyonlu değişken debili olduğu belirtilmemiş. Çıkışta basınç filtresi yok.
8. Emniyet valfi RV1 dönüşü soğutucudan geçen manifolda gidiyor; yüksek debide tanka doğrudan gitmeli.

Çizim / eksik ayrıntı:
9. Motor M1 şemada yok (A62 motor+pompa grubu). Emiş tarafında kapama vanası ve süzgeç yok (pistonlu pompa emişinde ince filtre kavitasyon riski; kaba süzgeç + kapama vanası).
10. Tank iki kez çizilmiş; aynı eleman (TK1) tek kez, dönüş ayrı hat olarak gösterilmeli. Tankta hava filtresi, seviye/sıcaklık göstergesi yok.
11. Dönüş filtresinde bypass (çek valf) ve kirlilik göstergesi yok. Soğutucuya termostat/bypass yok.
12. Basınç göstergesi/sensörü yok (teşhis için PT1, PT2 gerekir; Kademe 7).
13. "Yardımcı dağıtım manifoldu" kutu başlıkları (KALIP KONT. vb.) açık değil; eleman ID'leri (valf, sensör) atanmamış.

## Düzeltilmiş şema (taslak)
Eleman adları (TK1, P1, RV1, ACV1, ACC1, Y1, CYL1) kullanıcıdan; "öneri" işaretliler yeni, ID'leri Kademe 3'te kesinleşir.

```
 TK1 (A61) ── emiş vanası + kaba süzgeç ── P1 (A62: değişken debili pistonlu pompa, M1 30 kW)
   ▲                                          │            └── kaçak yağ (case drain) ──► TK1
   │                                          ▼
   │                                   CV1 çek valf (öneri) → PF1 basınç filtresi (öneri)
   │                                          │
   │                                  ANA BASINÇ HATTI P  [PT1] ──► RV1 emniyet ──► TK1 (doğrudan)
   │              ┌───────────────────────────┼───────────────────────────┐
   │              ▼                           ▼                           ▼
   │       ACV1 şarj bloğu              Y1 enjeksiyon valf bloğu     Yardımcı dağıtım manifoldu
   │              │                     (pompa + ACC1 beslemeli)      │      │        │
   │              ▼                           │                      Y2     Y3       Y4  (öneri)
   │   ACC1 (A56 ×2)                          ▼                       │      │        │
   │   her biri: kapama vanası,         A55 çarpan (3. faz)      A35 kapama  A41 itici  maça
   │   RV2 emniyet, DV1 deşarj→TK1,           │                  silindiri  2 silindir silindiri
   │   [PT2], azot ön dolum                   ▼                  (ileri/geri) (paralel,  (model
   │              │                    A54 CYL1 enjeksiyon        │      │      eş-zamanlı) dışı)
   │              └──► Y1 (hızlı vuruş)  silindiri (ileri/geri)   │      │        │
   │                                          │                   │      │        │
   └──── DÖNÜŞ FİLTRESİ RF1 (bypass'lı) ◄── yağ soğutucu (termostatlı) ◄── DÖNÜŞ MANİFOLDU ◄┘
```
Notlar:
- Her aktüatörün iki hattı vardır (ileri / geri); diyagramda tek çizgi sadeleştirmedir, ISO 1219 şemasında ikisi çizilecek.
- İtici silindirler (A41) iki adet olduğu için paralel besleme + senkron (akış bölücü veya mekanik köprü A41 köprüsü) Kademe 3'te kararlaştırılacak.
- Y2–Y4, CV1, PF1, RV2, DV1, PT1, PT2 öneridir; geçerli ID/şema numaraları LK/Microstar elektrik-hidrolik şeması gelince eşlenecek.

## Açık noktalar
- Pilot makine (LK) ISO 1219 hidrolik şeması gelince bu taslak onunla karşılaştırılacak.
- Pompa tipi/debisi ve akümülatör ön dolum basıncı (params'ta yok), enjeksiyon hızı gereksinimi hesaplanmadı.
- Hortum/döner bağlantı payı: vuruş ekseni 3 konumlu (Z değişimi 150 mm) olduğundan A54/A55/A56 arası hatlar bunu karşılamalı.
