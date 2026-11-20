# Durum — kaldığımız yer

_Son güncelleme: 2026-11-20 (gece). Her `/kapanis`'te baştan yazılır (en fazla ~60 satır)._

## Şu an
- Model 273 instance, 44 hat (A160). Kontroller YEŞİL: check.py HATA 0 / UYARI 0, motion_check (+ `--kalip-yuksekligi`) 0 çarpışma, itici taraması 0, elektrik 11 senaryo 0 hata, hidrolik + hidrolik ağ testleri geçti.
- Bu oturumda: portlar/delikler (A130, A35, A41 boss, A65 T2 tapalı, A59 nipel + tabla delikleri, A61 d80 dönüş, A11 -Y geçişi d150; H24 tanka ulaşıyor); Y4 maça hortumları H30..H37 + P/T besleme H38/H39 (sert boru); yağlama H40 (A170→A171) + H41..H52 (→A23 nipelleri, PA12 tüp); H01 → H01a/b/c (A172 CV1, A173 PF1); A168/A170/A23 port ve nipel çizimi; 109 parçaya ad_tr/ad_en/islev (bom.json, FreeCAD Label, `docs/PARCA_ADLARI.md`, `tools/adlar_tablo.py`).
- Hidrolik/mekanik ana ölçüler değişmedi: tank A61 +X bölmesi 784 L; A62 motor-pompa şase dışı; hızlı vuruş 3,0 m/s (2771 L/dk, ACC1 ×4); P1 191 L/dk, mil gücü 57,2 kW (%104 sınırda); A14 dikme min SF 1,11.
- Olcu-mimari bu oturumda Fable kredi hatası nedeniyle Opus ile çalıştı (yalnız bu oturum).
- FreeCAD'e basma bulut oturumunda yapılamaz: kendi PC'nde `git pull` → `HPDC400_yukle.FCMacro`; Report view'da `SON COMMIT` kontrol.

## Açık noktalar
- A11 +X bölmesi (1540 mm kaburgasız açıklık) mukavemet sağlaması (OLCU_TALEBI, olcu-mimari).
- A65 T dönüşü hızlı vuruşta ~1625 L/dk (DN51 13,4 m/s; T2 tapalı yedek var): dönüş devresi kararı (2. hortum / rejeneratif / doğrudan tank valfi).
- Maça P (H38): 140 bar basınç düşürücüsüz = KARAR ÖNERİSİ, onaylanmadı; H38 son bacağı 25 mm, porta 90° dirsek rakoru gerekir.
- Çizilmedi: plunger ucu su yolu (A52), kamara arka desteği, A54/A55 ek portları, hat rafı kelepçeleri, yağlama iç kanalları (nipel→pim).
- A41 A portu d16 7,8 m/s (kapak dar); A41 çapraz hortum H08 açık konumda A31'e 13 mm; hortumlar referans konumda sabit; bükülme ihlalleri (H22 8, H03 9, H12 7 dirsek).
- Saha teyidi (sonra): ST2 yeri, maça hızı 100 mm/s ve hangi yağlama çıkışı hangi pime, M1 katalog, DI5.30/31 eşlemesi, A127 kontak/KA9, KT1, TC1, DB68.A09 ölçekleme, S424/U16 debisi.
- 26 parçada ad/işlev "(varsayım)": A14 A42 A57 A59 A63 A64 A66 A92 A96 A97 A122 A123 A127 A128 A142..A145 A161 A164 A165 A170 A171 A175..A177.
- Temizlik: `parts/A21_sabit_plaka.py` ~satır 29 sabit sayı; `lib/kinematics.py` eski yorum; `docs/olcu_notlari.md` eski A14 tablosu; `lib/hidrolik_mantik.py` eski sabitler. Faz geçişleri süre tabanlı, DB68.ENC ile konum tabanlı olmalı.

## Sıradaki adım
- A11 +X mukavemeti ve A65 dönüş devresi; Kademe 1b çevrim makrosu (`HPDC400_cevrim.FCMacro`, KARARLAR 2026-11-20); sonra Kademe 4 (PLC durum makinesi).
- Alt plan A (tonaj → ölçülendirme motoru, 1000 t gibi makineler için) en sonda; şimdilik tüm ölçüler 400 t'ye elle yazılı.
