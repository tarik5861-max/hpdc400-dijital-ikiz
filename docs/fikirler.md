# Fikir park alanı

Beyin fırtınasında çıkan, henüz kademeye girmemiş fikirler. Tek satır: tarih — fikir — ilgili kademe.

- 2026-11-15 — Tam döküm çevrimi animasyonu: kalıp aç, itici it, kapat, enjeksiyon pistonu — K0/K2
- 2026-11-15 — Mevcut HPDC simülasyon motoru (dolum, basınç eğrisi) ile piston hareketini bağlamak — K2/K8
- 2026-11-15 — Somun dişlisi boşalması / sıkışmasını kolon gerilme dengesizliğinden yakalamak — K7/K8
- 2026-11-15 — Ucuz ek sensörler: kritik basınç noktaları, pompa akım pensi + titreşim, yağ partikül sayacı — K8
- 2026-11-17 — Makinenin kontrol yazılımını (PLC/sıralama) kendimiz yazmak — K4

- 2026-11-18: Sabit plaka penceresi (gerçek makinede geniş dikdörtgen açıklık) modele eklensin mi; A21–şase enine kama (Y yük); A54 ön kafasını alt kolonlara bağlama (faz 3).
- 2026-11-18: Enjeksiyon ünitesi X-Y-Z ince ayar mekanizması (kovan hizalama); kepçe/robot erişimi üst konumda.
- 2026-11-19 — Hidrolik akış simülasyonu için döküm anı geçici basınç dalgalanmaları (waterhammer) modellemesi eklenebilir — K3

- 2026-11-20 — Hortumların kalıp yüksekliği/vuruşla gerçek takibi (esnek hortum animasyonu; geo.py'ye sweep) — K1/K7
- 2026-11-20 — Su soğutmalı plunger ucu için A52 içi su yolu + dönel rakor modeli — K1
- 2026-11-20 — A65 hızlı vuruş dönüşü için rejeneratif devre/yüksek debili dönüş alternatiflerinin hidrolik modelde karşılaştırılması — K3
- 2026-11-20 — Hortum hareketi: A160 hortumları (H06/H07: A130→A41) sabit grupta, platen açılınca (420 mm) ve kalıp yüksekliği ayarında A41'den ayrılıyor. Çözüm: hortumu pozisyona bağlı çiz (uçlar A130/A41'e bağlı, U-halka stroka göre), makro + kontrol güncelle; uzunluk/min bükülme açık-kapalı-kalıp yüksekliği uçlarında kontrol. Onay verildi, sıra bekliyor.
- 2026-11-20 — İtici: strok 145 (A41) vs kalıp limiti 65 → mekanik stop + ileri/geri proximity sensör parçası BOM'da yok; motion_check itici stroku taramıyor (out/itici_tarama.py ile elle tarandı, strok 65'te çarpışma 0).
- 2026-11-20 — A65 T dönüşü 1625,8 L/dk: A65'te T2 (d51, tapalı) ayrıldı; 2. DN51 dönüş hortumu mu, rejeneratif (kol→kapak) mı, ön-dolum/doğrudan tank valfi mi — KARAR 2026-11-20: 2. DN51 hortum (KARARLAR) — K3
- 2026-11-20 — 1000 t gibi baska tonajlar: Alt plan A (olculendir motoru) gerekir; elle 1000 t params kurmak mumkun ama uzun ve tahmin olur. Maca P basinc dusurucu (RV/PRV) karari saha ile.
- 2026-11-22: Plunger geri açık kalıpta / itici 300 mm açıklıkta geometrik doğrulama (cevrim.py s=0/s=1 kuralıyla çelişki); maça limit sensörü kanalı eklenmesi.
