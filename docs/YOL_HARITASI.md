# Yol Haritası — HPDC-400 Dijital İkiz

**Nihai hedef:** Makine arıza verdiğinde ikiz sebebi nokta atışı bulsun; dış servise bağımlılık bitsin.
Ortak adres: ürün ağacındaki ID'ler (A24, A56…). Hidrolik eleman, kablo, sensör ve arıza kaydı bu ID'lere bağlanır.

| Kademe | İçerik | Durum |
|---|---|---|
| 0. Mekanik iskelet | Geometri, montaj, mafsal + kalıp yüksekliği kinematiği, otomatik çakışma kontrolleri, agent ekibi, GitHub + MCP | ✅ Bitti (71 parça) |
| 1. Gerçek makineye geçiş | Pilot makinenin gerçek ölçüleri; ürün ağacına valf/sensör/pompa/kart ID'leri; doküman arşivi | ⏳ Sırada — pilot makine ve dokümanlar bekleniyor |
| 2. Hidrolik | Şema → ağ modeli, basınç/debi simülasyonu, eleman arıza modları (kaçak, takılma, yavaş tepki) | Bekliyor |
| 3. PLC ve sıralama | Program → durum makinesi; duruşta "hangi adım, hangi koşul, hangi sensör" | Bekliyor |
| 4. Elektrik ve kartlar | Güç/kontrol devresi, güvenlik zinciri, kablo no, kart + test noktası | Bekliyor |
| 5. Pnömatik ve yağlama | Sprey havası, tutucular, merkezi yağlama ↔ mafsal aşınması | Bekliyor |
| 6. Hücre çevresi | Kepçe, sprey robotu, parça alma, çapak presi, kalıp ısıtma, vakum, kilitlemeler | Bekliyor |
| 7. Teşhis motoru | Sebep-sonuç grafiği, aday daraltma, test önerisi, zorunlu güvenlik adımları; arızalı parça FreeCAD'de kırmızı | Bekliyor |
| 8. Canlı veri ve kestirim | PLC + döküm eğrisi verisi; akümülatör, filtre, pompa verimi, iç kaçak trendleri | Bekliyor |

**Her kademenin kabul kriteri:** geçmiş servis vakaları ikize oynatılır; doğru arıza ilk 3 aday içinde mi?

## Kademe 1 için gerekenler
- Pilot makine: marka / model / kontrol sistemi
- Hidrolik şema (ISO 1219), elektrik projesi (EPLAN), PLC programı ve I/O listesi
- Valf ve kart datasheet'leri
- Son 1 yılın servis çağrıları ve arıza kayıtları
