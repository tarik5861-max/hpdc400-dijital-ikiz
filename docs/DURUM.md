# Durum — kaldığımız yer

_Son güncelleme: 2026-11-25. Her `/kapanis`'te baştan yazılır (en fazla ~60 satır)._

## Şu an
- Model 301 instance, 46 hat (A160). Kontroller YEŞİL: check.py HATA 0 / UYARI 0, motion_check 0 çarpışma (2026-11-25), elektrik 32 senaryo 0 hata, hidrolik testleri 5/5 + ağ testleri geçti. `--kalip-yuksekligi` taraması koşulmadı (geometri değişmedi, son YEŞİL 2026-11-21).
- 2026-11-25: Kademe 1 açık nokta #1 YAPILDI (hidrolik-muhendisi): A54 iç kanalları (A kapak oval 50×90→d140, 12,2 m/s; B kol +X d76→d60→halka oluk, 9,6 m/s) ve A65 iç devre 11 valf (Y1.1..Y1.11, NG16..NG50, en yüksek dP 5,4 bar). Faz 2 bütçe: kapak 122,4 bar, kısma payı 107 bar, 3,0 m/s tutuyor; geri vuruş P1 ile 0,353 m/s. Kod: `a65_ic_devre_hesabi()`, `HidrolikAgModeli.a65_valf_durumu(faz)`, hidrolik.json `a65_ic_devre_tasarim`. Hepsi DESIGN ASSUMPTION (Cd 0,7, ISO 7368, dP sınırı 10 bar, faz 2 metal basıncı 40 bar). Döküm: out/hidrolik_2026-11-25_a65_ic_devre.txt.
- Kademe 4 adım 3 (arıza enjeksiyonu) 2026-11-25'te bitti: 12 arıza (ARZ01..12), `teshis_kaydi()`, testler S20..S32. Adım 2 kapalı döngü konum tabanlı (ENC ≥150 / ≥490 mm).
- Geometrik doğrulama kapandı (`checks/acik_kalip_tarama.py`): plunger açık kalıpta TEMİZ; itici s≥0,841 (300 mm) TEMİZ.
- Kademe 1 kapanmış işler (KARARLAR 2026-11-20/21): A11 +X mukavemeti SF 4,7; A65 dönüşü 2×DN51; A52 su yolu; A182 kamara arka desteği; A181 omega kelepçe; A54/A55/A65 portları.
- Kademe 1b çevrim makrosu (16 faz) yazıldı, FreeCAD'de canlı denenmedi. FreeCAD'e basma kendi PC'nde: `git pull` → `HPDC400_yukle.FCMacro` → `HPDC400_cevrim.FCMacro`.
- Ana ölçüler: tank A61 784 L; hızlı vuruş 3,0 m/s (2771 L/dk, ACC1 ×4); P1 191 L/dk, mil 57,2 kW (%104); A14 min SF 1,11.
- Bulutta `pip install -r requirements.txt` gerekir (OCP); `--kalip-yuksekligi` taraması >8 dk.

## Açık noktalar
- **OLCU_TALEBI-1:** A65 blok zarfı 160×300×160 kartuşlara yetmiyor (gereken kapak yüzü 149 100 mm², serbest 111 700). Asgari ~570×300×180 (A55 üstünde -X'e uzar); A64, B, PA, P/T port yerleri yeniden düzenlenecek → olcu-mimari.
- **OLCU_TALEBI-2:** A55 PB halka portu yok, en az d32 (295 L/dk, 6,1 m/s); Y1.10 buna bağlanacak.
- **ELEKTRIK_TALEBI:** DO7.02 (S120) PLC ifadesi yok, öneri `S.ENJ_IZIN and S.FAZ2`; DO7.16 (S118) piston geri (DO7.26) süresince de açık olmalı; `plunger.geri_mm_s` 400 vs P1 353 mm/s tutarsız.
- **KARAR_ONERI:** kapama vanası + emniyet + deşarj + ölçüm `KURAL_HIDR_*` kuralları `checks/kurallar.py`'ye (Y1.4 arkasında hapsolan 285,7 bar dahil). Onay bekliyor.
- Adım zaman aşımı alarmı YOK: KAPAMA/ACMA/ITICI_* adımlarında arıza sessiz takılır (karar bekliyor). Maça limit sensörü kanalı yok.
- Maça P (H38): 140 bar basınç düşürücüsüz = KARAR ÖNERİSİ, onaysız; H38 son bacak 25 mm, 90° dirsek rakoru.
- Hat ihlalleri: A41 A portu d16 7,8 m/s; A65 dönüşü DN51 6,7 m/s (60 ms); H08 A31'e 13 mm; H20R2 gusset yok; bükülme H22 8, H03 9, H12 7 dirsek.
- Saha teyidi (sonra): faz-geçiş konumları, enkoder gecikmesi, ST2, maça hızı, yağlama çıkışı↔pim, M1 katalog, DI5.30/31, A127/KA9, KT1, TC1, DB68.A09, S424/U16, kartuş dP-Q eğrileri, RF1 dP.
- 26 parçada ad/işlev "(varsayım)": A14 A42 A57 A59 A63 A64 A66 A92 A96 A97 A122 A123 A127 A128 A142..A145 A161 A164 A165 A170 A171 A175..A177.
- Not: B portu +X d76 (params.json, KARARLAR 2026-11-21); eski "-Y" ifadesi geçersiz.
- Temizlik: `parts/A21_sabit_plaka.py` ~satır 29 sabit sayı; `lib/kinematics.py` eski yorum; `docs/olcu_notlari.md` eski A14 tablosu; `lib/hidrolik_mantik.py` eski sabitler.

## Sıradaki adım
- Yeni sohbet, tek iş: OLCU_TALEBI-1+2 → olcu-mimari (A65 blok zarfı + A55 PB portu), sonra hat/port senkronu ve check.
- Sonra: ELEKTRIK_TALEBI (elektrik-mantik), KURAL_HIDR_* kararı, hat ihlalleri, zaman aşımı alarmı kararı, Kademe 7.
- Alt plan A (tonaj → ölçülendirme motoru) en sonda.
