# Durum — kaldığımız yer

_Son güncelleme: 2026-11-21 (sabah). Her `/kapanis`'te baştan yazılır (en fazla ~60 satır)._

## Şu an
- Model 300 instance, 46 hat (A160). Kontroller YEŞİL: check.py HATA 0 / UYARI 0, motion_check (+ `--kalip-yuksekligi`) 0 çarpışma, itici taraması 0, elektrik 11 senaryo 0 hata, hidrolik + hidrolik ağ testleri geçti.
- Maça: A81 kavite + yan cepler + kılavuz, A82 eş cepler, A184 maça çekirdeği ×4 (A167 koluna bağlı); çevrim makrosu maçayı hareket ettirir (faz 3 gir, faz 12 çek). Model 300 instance.
- Akşam: Kademe 1b çevrim makrosu yazıldı: `lib/cevrim.py` (16 faz, saf python, `python3 lib/cevrim.py` kural testi 0 ihlal) + `HPDC400_cevrim.FCMacro` (cevrim_baslat/tek/durdur/hiz/faz). Plunger 0..500 temiz (tarama), itici yalnız s=1, plunger yalnız s=0. FreeCAD'de canlı denenmedi (sahte FreeCAD ile duman testi geçti). Sınır: A54 kol ucu sabit (plunger kaplini ondan ayrılır), yağlama yalnız faz adı (maça artık gerçek hareket).
- Öğleden sonra: A54 B / A55 PA hatları kapandı (A183 ×2 sert boru, A65'e B/PA portu, ayrıntı KARARLAR). Model 296 instance.
- Bu oturumda (2026-11-21 sabah): A52 plunger su yolu (kör delik d26 + iç boru d14/d10, coupling'de radyal giriş +Y x-790 / çıkış -Y x-740), A182 kamara arka desteği (eyer+dikme, A11'e dayanır, vuruş konumuyla yükselir), A54 (5 port: B -Y yüz, 2 hava alma, 2 basınç) ve A55 (5 port: PA üst, 2 hava alma, PT, DR) ek portları, A181 hat kelepçesi ×18 (6 konsol × P/pilot/T; A175 P/pilot rafı genişletildi). Hepsi DESIGN ASSUMPTION. check HATA 0, 3 vuruş konumu 0, motion 0 (+kalıp yüksekliği 0), hidrolik testler geçti.
- Önceki oturum: A11 +X mukavemeti kapandı (`tools/a11_mukavemet.py`, SF 4,7, takviye yok); A65 dönüşü 2 × DN51 hortum (H20H + H20H2, 6,7 m/s) + H20R2 kol (60,3×3,6, TEE_T2R), A176 braket T2 deliği. Önceki oturum: portlar/delikler, Y4 maça hortumları H30..H52, yağlama hatları, 109 parça adı (`docs/PARCA_ADLARI.md`).
- Hidrolik/mekanik ana ölçüler değişmedi: tank A61 +X bölmesi 784 L; A62 motor-pompa şase dışı; hızlı vuruş 3,0 m/s (2771 L/dk, ACC1 ×4); P1 191 L/dk, mil gücü 57,2 kW (%104 sınırda); A14 dikme min SF 1,11.
- FreeCAD'e basma bulut oturumunda yapılamaz: kendi PC'nde `git pull` → `HPDC400_yukle.FCMacro`; Report view'da `SON COMMIT` kontrol.

## Açık noktalar
- (KAPANDI 2026-11-20) A11 +X mukavemeti: SF 4,7, takviye yok. A65 dönüşü: 2 × DN51 hortum (6,7 m/s), H20R2 kol. Kalan: DN51 6,7 m/s > 6 m/s sadece 60 ms (saha); H20R2 bracket konsolu 370 mm uzatma, gusset yok (varsayım).
- Maça P (H38): 140 bar basınç düşürücüsüz = KARAR ÖNERİSİ, onaylanmadı; H38 son bacağı 25 mm, porta 90° dirsek rakoru gerekir.
- Çizilmedi: kamara arka desteği için civata/kelepçe bandı, yağlama iç kanalları (nipel→pim), A52 su hortumu/döner rakor (portlar A144 koruyucu içinde, yuva yok). A54 iç kanalı + A65 B/PA iç valf tanımı yok (hidrolik-muhendisi).
- A41 A portu d16 7,8 m/s (kapak dar); A41 çapraz hortum H08 açık konumda A31'e 13 mm; hortumlar referans konumda sabit; bükülme ihlalleri (H22 8, H03 9, H12 7 dirsek).
- Saha teyidi (sonra): ST2 yeri, maça hızı 100 mm/s ve hangi yağlama çıkışı hangi pime, M1 katalog, DI5.30/31 eşlemesi, A127 kontak/KA9, KT1, TC1, DB68.A09 ölçekleme, S424/U16 debisi.
- A181/A182 + A52 su yolu + A54/A55 ek portları ad/işlev "(varsayım)"; 26 parçada ad/işlev "(varsayım)": A14 A42 A57 A59 A63 A64 A66 A92 A96 A97 A122 A123 A127 A128 A142..A145 A161 A164 A165 A170 A171 A175..A177.
- Temizlik: `parts/A21_sabit_plaka.py` ~satır 29 sabit sayı; `lib/kinematics.py` eski yorum; `docs/olcu_notlari.md` eski A14 tablosu; `lib/hidrolik_mantik.py` eski sabitler. Faz geçişleri süre tabanlı, DB68.ENC ile konum tabanlı olmalı.

## Sıradaki adım
- Kendi PC'nde `git pull` → `HPDC400_yukle.FCMacro` sonra `HPDC400_cevrim.FCMacro` ile 1b'yi dene; Kademe 4 adım 1 YAPILDI (PLC MACA_GIR/MACA_CEK, elektrik 15 senaryo 0 HATA). Sıradaki: adım 2 kapalı döngü (çıkış→hareket→sensör) + cevrim.py faz 10–11 ile PLC eşle (katılaşma süresi / piston dönüşü farkı); adım 3 arıza enjeksiyonu.
- Alt plan A (tonaj → ölçülendirme motoru, 1000 t gibi makineler için) en sonda; şimdilik tüm ölçüler 400 t'ye elle yazılı.
