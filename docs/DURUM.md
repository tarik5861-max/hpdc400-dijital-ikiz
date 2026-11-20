# Durum — kaldığımız yer

_Son güncelleme: 2026-11-20 (akşam)._ Her `/kapanis`'te yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Model 248 instance (19 yeni parça: itici stop/sensör, E-stop, arka kapı, maça, yağlama, CV1/PF1/RF1, konsollar, HL1, operatör kutusu; ikiz varsayımı); hortumlar artık pozisyona bağlı (lib/hortum_pose.py, makro her adımda yeniden çizer); hareket/kalıp yüksekliği/vuruş taramaları 0 çarpışma; itici stroku checks/itici_tarama.py. Önceki: 210 instance; kontroller YEŞİL: check.py (+ 3 vuruş taraması) 0 hata/0 uyarı, motion_check (+ `--kalip-yuksekligi`) 0 çarpışma, elektrik 11 senaryo 0 hata, hidrolik testleri geçti.
- Hidrolik ünite: tank A61 şase içinde +X bölmesi (X 605..2135, 784 L, erişim +Y); motor-pompa grubu (A62, A120 55 kW, A98..A119 4520VQ tandem) şase dışında +X ucunda, rz 90, mil Y boyunca X 2730, plaka X 2410..3050 / Y ±800 ortada; emiş A121 tank +X yüzüne (Y 380). overall_length 6220.
- Hızlı vuruş 3,0 m/s (2771 L/dk, ACC1 A56 ×4, V0 129 L, p0 113,4 bar). P1 191 L/dk, P2 23 L/dk; mil gücü 57,2 kW (%104 SINIRDA, yalnız P1+P2 eşzamanlı tam yük). A64 ana hat dış Ø90/iç Ø80 (9 m/s).
- A14 dikme: 2 kaburga, min SF 1,11 (taban kaynağı yorulması).
- Bu oturumda eklenenler: A21/A22 T kanalları (DIN 650 benzeri); otomatik kapı A71 + A124..A128; kapama valf bloğu A130..A133 (A35 altında); enjeksiyon eksikleri A140..A145; 19 hat boru/hortum A160 (`params/hatlar.json`, `tools/hat_senkron.py`).
- Elektrik: A127 kapı anahtarları, Y2/Y3 (A130/A132/A133), A143 yağlama (DO7.06 + DI5.30 seviye), A142 su akış DI5.31 + TT2 (AI10.4), M1 55 kW hesapları (KM1/KM2 80 A, FR1 58,6 A, 125 A MCCB, 70 mm²).
- FreeCAD'e basma bu bulut oturumunda yapılamadı (MCP yok); kullanıcı kendi bilgisayarında makroyu çalıştırır. Makro artık A6/A7'yi gösterir (`HPDC_GIZLE=1` ile gizle) ve kök yol + son commit yazar.

## Açık noktalar
- Y4 maça hortumları (A168→4 silindir, 8 hat) hatlar.json'da yok; A171 dağıtıcı 12 çıkış boruları yok; CV1/PF1 H01'i sarıyor (H01 bölünmeli); hat_listesi.md eski güzergahı anlatıyor; hortum bükülme ihlalleri (H22 8, H03 9, H12 7 dirsek) saha/katalog doğrulaması; ST2 yeri saha fotoğrafıyla teyit.
- A11 +X bölmesi (1540 mm kaburgasız açıklık) mukavemet sağlaması (OLCU_TALEBI, olcu-mimari).
- Portlar/delikler çizilmedi: A130 (Y3 A2/B2, Pi), A35, A41, A65, A59 (P/Pi/T + sepet plakası 3 delik d60), A61 T dönüş portu + A11 -Y duvar geçişi d95 (H24 tanka ulaşmıyor); hat rafı konsolları/kelepçeler, CV1 çek valf, PF1 filtre ağaçta yok.
- A65 T dönüşü hızlı vuruşta ~1625 L/dk (DN51 hortum 13 m/s): yüksek debili/rejeneratif dönüş devresi kararı.
- A41 çapraz hortum H08: açık konumda A31 crosshead yüzüne 13 mm; hortumlar referans konumda sabit (kayan uçları takip etmez).
- Enjeksiyon: su soğutmalı plunger ucu (A52 içi su yolu) ve kamara arka desteği çizilmedi; A54/A55 ek portları yok.
- `parts/A21_sabit_plaka.py` ~satır 29 sabit sayı (vuruş ekseni listesi) params'a taşınmalı.
- `lib/kinematics.py` içinde eski yerleşimi anlatan yorum güncellenmeli.
- Elektrik VERI_BEKLIYOR (ikiz varsayımı, saha sonrası): DI5.30/DI5.31 bayt.bit eşlemesi, A127 kontak sayısı/KA9 zinciri, KT1 gerçek yıldız süresi, M1 katalog değerleri, TC1 kalkış gerilim çökmesi.
- DB68.A09 hız komutu ölçeklemesi ve S424/U16 (TDP050EH) ~2,8 m³/dk debi doğrulaması; faz geçişleri süre tabanlı, DB68.ENC ile konum tabanlı olmalı.
- `docs/olcu_notlari.md` eski A14 tablosu güncellenmedi.
- `lib/hidrolik_mantik.py` eski sabitleri (2 tüp × 1,3 L) içerir, kullanılmıyor.

## Sıradaki adım
- Port/delik eksiklerini ve tank dönüş geçişini kapat, hatlar tamamlansın; sonra A11 +X mukavemeti ve A65 dönüş devresi. Kademe 4 (PLC durum makinesi) ondan sonra.
- Yeni pencerede: `git pull` → `/devam` → FreeCAD makrosu (`HPDC400_yukle.FCMacro`) doğrudan klon klasöründen; Report view'da `SON COMMIT` hash'ini kontrol et.
