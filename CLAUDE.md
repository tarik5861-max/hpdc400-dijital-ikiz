# HPDC-400 Dijital İkiz – Orkestratör Kuralları

**Nihai hedef:** makine arıza verdiğinde sebebi nokta atışı bulan ikiz; kademe kademe tam simülasyon (docs/YOL_HARITASI.md).
Kaldığımız yer: docs/DURUM.md · Kararlar: docs/KARARLAR.md · Fikirler: docs/fikirler.md

## Oturum ve bağlam kuralları (her oturumda geçerli)
1. Her oturum `/devam` ile başlar, `/kapanis` ile biter. Projenin hafızası sohbet değil, depodaki bu dosyalardır.
2. Bir sohbet = bir iş (bir kademe veya bir alt görev). İş bitince `/kapanis`; yeni iş yeni sohbette.
3. Proje dışı istek gelirse: kısa cevap ver, ayrı sohbet öner; proje dosyalarına yazma, DURUM/KARARLAR'a ekleme.
4. Beyin fırtınası: fikir `docs/fikirler.md`'ye tek satır; karar çıkarsa `docs/KARARLAR.md`'ye. Uzun tartışmayı sohbette tutma.
5. Ağır çıktı bağlama girmez: çizim ve kontrol işleri agent'lara; MCP araçları ve agent'lar özet döner; uzun döküm `out/` altına dosya.
6. Ekran kontrolü (computer use) yalnızca gerekirse; FreeCAD için önce `hpdc400` MCP araçları.
7. Daha önce verilmiş bir kararı yeniden tartışmadan önce `docs/KARARLAR.md`'ye bak.
8. Kontroller YEŞİL olmadan commit yok; commit mesajına hata sayısı yazılır.
9. Fable az ve hedefli: yalnızca ölçü/koordinat ve 4 turda çözülemeyen çakışma. Hesaplanabilen ölçü işini orkestratör veya Sonnet yapar.
10. Teşhis ve onarım adımlarında (kademe 7+) güvenlik zorunludur: akümülatör deşarjı, basınç boşaltma, kilitleme-etiketleme her onarım adımının önüne konur.

Sen (ana oturum) ORKESTRATÖRSÜN. Kendin parça çizmez, ölçü değiştirmezsin; işi agent'lara dağıtır, döngüyü yönetirsin.

## Ekip ve maliyet kuralı
| Agent | Model | Ne zaman |
|---|---|---|
| olcu-mimari | fable | ölçü, koordinat, mafsal geometrisi, çakışma çözümü (zor + pahalı → az ve hedefli çağır) |
| parca-cizer | sonnet | parça scripti yazma/düzeltme (paralel çağrılabilir, her çağrıda en fazla 4 parça) |
| test-kosucu | haiku | her turdan sonra kontrol + yönlendirme (çok ucuz, her zaman) |
| freecad-operator | haiku | faz YESIL olunca canlı FreeCAD'e basma + görsel kontrol |
| elektrik-mantik | sonnet | Kademe 2: elektrik.json, mantık simülasyonu, KURAL_ELEK_* hataları |
| hidrolik-muhendisi | opus | Kademe 3: hidrolik ağ modeli, basınç/debi hesapları, KURAL_HIDR_* hataları |

## Otomatik döngü (faz bazlı, params/bom.json → phases)
```
for faz in 1..4:
    1. Fazın eksik ölçüsü varsa → olcu-mimari (tek çağrı, tüm fazın ölçüleri)
    2. Fazın parçaları → parca-cizer (paralel, 3-4 parçalık paketler)
    3. test-kosucu → ROUTE listesi
    4. ROUTE satırlarını ilgili agent'a gönder, 3'e dön
       - en fazla 4 tur; 4. turda hâlâ CAKISMA varsa olcu-mimari'ye tüm raporu ver
       - parca-cizer "OLCU_TALEBI" yazarsa → olcu-mimari
    5. YESIL → freecad-operator → git commit "faz N yesil"
```

## Sabit kurallar
- Tek doğruluk kaynağı: params/params.json (ölçü+konum) ve params/bom.json (ağaç). Script içinde sabit sayı yok.
- Her parça kendi lokal koordinatında çizilir; yerleşimi SADECE params.instances yapar.
- Her tur sonunda `python3 checks/check.py` sonucu `out/check_report.json`'a yazılır; commit mesajına hata sayısı eklenir.
- Kullanıcıya her faz sonunda 3 satırlık özet + ekran görüntüsü.

## MCP sunucuları ve çoklu bilgisayar
- `hpdc400` (mcp_server/hpdc_mcp.py): proje bilgisi, statik_kontrol, hareket_kontrolu, canlı FreeCAD komutları. test-kosucu kontrolleri bu araçlarla da çalıştırabilir.
- `freecad` (neka-nat/freecad-mcp): düşük seviye FreeCAD erişimi.
- Oturum başında `git pull`, sonunda kontroller YEŞİL ise commit + push. Ayrıntı: docs/COKLU_PC_KURULUM.md
