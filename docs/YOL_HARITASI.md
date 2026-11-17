# Yol Haritası — HPDC-400 Dijital İkiz

**Nihai hedef:** Makine arıza verdiğinde ikiz sebebi nokta atışı bulsun; dış servise bağımlılık bitsin.
Ortak adres: ürün ağacındaki ID'ler (A24, A56…). Hidrolik eleman, kablo, sensör ve arıza kaydı bu ID'lere bağlanır.

| Kademe | İçerik | Durum |
|---|---|---|
| 0. Mekanik iskelet | Geometri, montaj, mafsal + kalıp yüksekliği kinematiği, otomatik çakışma kontrolleri, agent ekibi, GitHub + MCP | ✅ Bitti (71 parça) |
| 1. Makineyi tamamlamak | Eksik mekanik tamamlanıyor: itici / pim düzeni (sabit plaka 16 delik), enjeksiyon–sabit plaka bağlantı çubukları (A58); satın alınan parçalar; pilot makinenin (LK) gerçek ölçüleri | 🔄 Devam ediyor |
| 2. Elektrik ve kartlar | Elektrik şemasından: güç/kontrol devresi, güvenlik zinciri, I/O listesi, kablo/klemens no, bobin ve sensör ID'leri, kart + test noktası | Öncelik 2 — LK (Microstar) şeması geliyor |
| 3. Hidrolik | Şema → ağ modeli, basınç/debi simülasyonu, eleman arıza modları (kaçak, takılma, yavaş tepki) | Öncelik 3 |
| 4. Yazılım (PLC ve sıralama) | Program → durum makinesi; duruşta "hangi adım, hangi koşul, hangi sensör". Seçenek: kontrol yazılımını kendimiz yazmak | Öncelik 4 |
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
