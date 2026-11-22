# Durum — kaldığımız yer

_Son güncelleme: 2026-11-22 (öğlen). Her `/kapanis`'te baştan yazılır (en fazla ~60 satır)._

## Şu an
- Model 301 instance, 46 hat (A160). Kontroller YEŞİL: check.py HATA 0 / UYARI 0, motion_check 0 çarpışma (bu oturumda geometri değişmedi; `--kalip-yuksekligi` taraması koşulmadı, son YEŞİL 2026-11-21), elektrik 19 senaryo 0 hata, hidrolik + hidrolik ağ testleri geçti (son koşu 2026-11-21).
- 2026-11-22: Kademe 4 adım 2 (kapalı döngü) YAPILDI: `KapaliDongu` (lib/elektrik_mantik.py) PLC bobinlerinden mafsal/plunger/itici/maça hareketini üretir; sensör DI + DB68.ENC (mm) PLC'ye döner. Geçişler konum tabanlı: FAZ1→2 ENC ≥150 mm, FAZ2→3 ≥490 mm, piston geri ENC ≤2 mm (`P.ENC_BILDIRIM=0` eski süre modu yedek). Zaman aşımı alarmları: AL_ENJ_KONUM_ZAMAN_ASIMI, AL_PISTON_GERI_ZAMAN_ASIMI (mühürlü, HMI.RESET). Testler S16..S19 (S19 = cevrim.py eşleme kontrolü).
- PLC ↔ cevrim.py etiketli VARSAYIM farkları: FARK_KATILASMA_SURE (PLC tek FAZ3, 3000 ms), FARK_SIRA_PISTON_GERI (cevrim faz 11 kalıp kapalı, PLC açmadan sonra), FARK_ACMA_300 (PLC 300 mm, cevrim 420), FARK_SPREY_PLC_YOK.
- Kademe 1b: çevrim makrosu (lib/cevrim.py + HPDC400_cevrim.FCMacro, 16 faz) yazıldı, FreeCAD'de canlı denenmedi.
- Mekanik/hidrolik ana ölçüler değişmedi: tank A61 784 L; hızlı vuruş 3,0 m/s (2771 L/dk, ACC1 ×4); P1 191 L/dk, mil gücü 57,2 kW (%104 sınırda); A14 dikme min SF 1,11; A11 SF 4,7.
- FreeCAD'e basma bulut oturumunda yapılamaz: kendi PC'nde `git pull` → `HPDC400_yukle.FCMacro`; Report view'da `SON COMMIT` kontrol.
- Telefon/bulut çalışma düzeni: iş repo üzerinden; bulutta `pip install -r requirements.txt` gerekir (OCP yok); `--kalip-yuksekligi` taraması >8 dk sürer.

## Açık noktalar
- Plunger geri açık kalıpta ve itici 300 mm açıklıkta geometrik doğrulama gerekir (cevrim.py s=0/s=1 kuralıyla çelişiyor). Maça limit sensörü kanalı yok, maça süre tabanlı.
- VERI_BEKLIYOR (saha): gerçek faz-geçiş konumları, enkoder kartı kesme gecikmesi. ENC eşikleri hidrolik.json (165,6 / 180 mm) ile birebir değil, cevrim.py'ye uyuldu.
- Maça P (H38): 140 bar basınç düşürücüsüz = KARAR ÖNERİSİ, onaylanmadı; H38 son bacağı 25 mm, porta 90° dirsek rakoru gerekir.
- A65 dönüşü: DN51 6,7 m/s > 6 m/s sadece 60 ms (saha); H20R2 bracket konsolu 370 mm uzatma, gusset yok (varsayım).
- Çizilmedi: kamara arka desteği civata/kelepçe bandı, yağlama iç kanalları (nipel→pim), A52 su hortumu/döner rakor. A54 iç kanalı + A65 B/PA iç valf tanımı yok (hidrolik-muhendisi).
- A41 A portu d16 7,8 m/s; A41 çapraz hortum H08 açık konumda A31'e 13 mm; hortumlar referans konumda sabit; bükülme ihlalleri (H22 8, H03 9, H12 7 dirsek).
- Saha teyidi (sonra): ST2 yeri, maça hızı 100 mm/s, yağlama çıkışı↔pim, M1 katalog, DI5.30/31 eşlemesi, A127 kontak/KA9, KT1, TC1, DB68.A09 ölçekleme, S424/U16 debisi.
- 26 parçada ad/işlev "(varsayım)": A14 A42 A57 A59 A63 A64 A66 A92 A96 A97 A122 A123 A127 A128 A142..A145 A161 A164 A165 A170 A171 A175..A177; ayrıca A181/A182/A52 su yolu/A54-A55 ek portları.
- Temizlik: `parts/A21_sabit_plaka.py` ~satır 29 sabit sayı; `lib/kinematics.py` eski yorum; `docs/olcu_notlari.md` eski A14 tablosu; `lib/hidrolik_mantik.py` eski sabitler.

## Sıradaki adım
- Kendi PC'nde `git pull` → `HPDC400_yukle.FCMacro` sonra `HPDC400_cevrim.FCMacro` ile 1b'yi dene.
- Kademe 4 adım 3: arıza enjeksiyonu (sensör/valf/enkoder arızası → hangi adımda, hangi koşulda durur). Önce yukarıdaki açık geometrik doğrulamayı (plunger geri / itici 300 mm) kapat.
- Alt plan A (tonaj → ölçülendirme motoru) en sonda.
