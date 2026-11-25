# Yol Haritası — HPDC-400 Dijital İkiz

**Nihai hedef:** Makine arıza verdiğinde ikiz sebebi nokta atışı bulsun; dış servise bağımlılık bitsin.
Ortak adres: ürün ağacındaki ID'ler (A24, A56…). Hidrolik eleman, kablo, sensör ve arıza kaydı bu ID'lere bağlanır.

| Kademe | İçerik | Durum |
|---|---|---|
| 0. Mekanik iskelet | Geometri, montaj, mafsal + kalıp yüksekliği kinematiği, otomatik çakışma kontrolleri, agent ekibi, GitHub + MCP | ✅ Bitti (71 parça) |
| 1. Makineyi tamamlamak | Eksik mekanik tamamlanıyor: itici / pim düzeni, pompa/motor/tank, T kanalları, kapı, kapama valf bloğu, enjeksiyon eksikleri, boru/hortum hatları (A160); satın alınan parçalar; pilot makinenin gerçek ölçüleri | 🔄 Devam ediyor (273 instance, 44 hat; portlar/hatlar/adlandırma tamam; 2026-11-25: A54 iç kanal + A65 iç valf tanımlandı; kalan: A65 blok zarfı + A55 PB portu (OLCU_TALEBI), hat ihlalleri, varsayım adları) |
| 1b. Cevrim animasyonu | Tam dokum cevrimi makrosu (HPDC400_cevrim.FCMacro): kapa, kilitle, yavas+hizli vurus, bekle, ac, itici ileri/geri, maca cek/gir, yaglama; zaman tabanli, mevcut kinematik ustune | ✅ Makro yazildi 2026-11-21 (lib/cevrim.py + HPDC400_cevrim.FCMacro, 16 faz, 14,9 s animasyon); FreeCAD'de canli deneme bekliyor |
| 2. Elektrik ve kartlar | Elektrik şemasından: güç/kontrol devresi, güvenlik zinciri, I/O listesi, kablo/klemens no, bobin ve sensör ID'leri, kart + test noktası | 🔄 Taslak v1 yapıldı (2026-11-18): DCC630 şeması 400 t'ye uyarlandı (elektrik.json, mantık simülasyonu, testler); A97 ve TC1 kararları verildi (K-EL-07, K-EL-03); M1 55 kW hesapları, yeni parça bağlantıları (A127, A130..A133, A142, A143) işlendi, bulanık DO7.17-30 ve KA9 ikiz kararlarıyla kapatıldı; sıradaki: HW Config adres eşlemesi (saha) |
| 3. Hidrolik | Şema → ağ modeli, basınç/debi simülasyonu, eleman arıza modları (kaçak, takılma, yavaş tepki) | 🔄 Taslak v1 yapıldı (2026-11-19): lib/hidrolik_ag_modeli.py ve akü deşarj/enjeksiyon faz simülasyon testleri eklendi; 2026-11-25 A65 iç devre (11 valf) + A54 iç kanallar |
| 4. Yazılım (PLC ve sıralama) | Program → durum makinesi (1b'deki çevrim adımları sensör/valf/basınç koşullu);  duruşta "hangi adım, hangi koşul, hangi sensör". Seçenek: kontrol yazılımını kendimiz yazmak | 🔄 Adım 1 (PLC maça) + adım 2 kapalı döngü yapıldı (2026-11-22, konum tabanlı geçiş, elektrik 19 senaryo 0 HATA); sıradaki adım 3 arıza enjeksiyonu |
| 5. Pnömatik ve yağlama | Sprey havası, tutucular, merkezi yağlama ↔ mafsal aşınması | Bekliyor |
| 6. Hücre çevresi | Kepçe, sprey robotu, parça alma, çapak presi, kalıp ısıtma, vakum, kilitlemeler | Bekliyor |
| 7. Teşhis motoru | Sebep-sonuç grafiği, aday daraltma, test önerisi, zorunlu güvenlik adımları; arızalı parça FreeCAD'de kırmızı | Bekliyor |
| 8. Canlı veri ve kestirim | PLC + döküm eğrisi verisi; akümülatör, filtre, pompa verimi, iç kaçak trendleri | Bekliyor |

**Her kademenin kabul kriteri:** geçmiş servis vakaları ikize oynatılır; doğru arıza ilk 3 aday içinde mi?

## Alt plan A — Boyutlandırma (hesap) motoru  · zamanlama: en son işlerden biri (Kademe 8 ile birlikte / sonrası)
Amaç: tonajdan (230–850 t ve ötesi) otomatik ölçülendirme; "makine filosunun ikizi".
1. **Girdi:** kapama kuvveti (zorunlu); kolon aralığı, kalıp yüksekliği aralığı, açılma kursu, enjeksiyon kuvveti, piston çapları (isteğe bağlı; gerçek makinede katalog değeri girilir ve tahminin önüne geçer).
2. **Kurallar:**
   - Mühendislik formülleri: kolon çapı/diş (gerilme), mafsal kapanma geometrisi (sayısal çözücü), piston–basınç, çarpan, akümülatör hacmi, kalıp yüksekliği dişlileri ve motor torku, plaka eğilmesi.
   - Katalog ilişkileri: üretici kataloglarından (Bühler, Idra, LK…) tonaja göre kolon aralığı, plaka boyutu, makine boyu, motor gücü.
3. **Çıktı:** `machines/<makine>.json`; her değerin kaynağı yazılı (formül / katalog / kullanıcı). Statik + hareket kontrolleri YEŞİL değilse kabul edilmez.
4. **Kullanım:** MCP aracı `olculendir(tonaj, …)` → ölçülendir → çiz → kontrol → FreeCAD.
5. **Bağlantı:** enjeksiyon tarafı mevcut HPDC hesap motorundan (proses: piston çapı, döküm basıncı, dolum süresi) beslenir.
6. **İlk test:** mevcut 400 t modeli birebir yeniden üretmek; sonra pilot makine ve filodaki diğer makineler.
Sınır: katalog tahmini gerçekçi olur ama birebir değildir; teşhis için gerçek makine ölçüleri girilmelidir.

## Kademe 1–2 için gerekenler
- Pilot makine: marka / model / kontrol sistemi
- Hidrolik şema (ISO 1219), elektrik projesi (EPLAN), PLC programı ve I/O listesi
- Valf ve kart datasheet'leri
- Son 1 yılın servis çağrıları ve arıza kayıtları
