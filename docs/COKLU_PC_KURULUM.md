# Birden fazla bilgisayarda ortak çalışma

Depo: `https://github.com/tarik5861-max/hpdc400-dijital-ikiz` (özel). Tek doğruluk kaynağı GitHub'dır; her bilgisayar bir klondur.

## Bir bilgisayarı ilk kez hazırlamak (Windows)
1. **Git**, **FreeCAD 1.0+**, **uv** (`powershell -c "irm https://astral.sh/uv/install.ps1 | iex"`) ve **Claude Code** kurulu olsun.
2. Projeyi klonla (masaüstüne):
   ```
   cd %USERPROFILE%\Desktop
   git clone https://github.com/tarik5861-max/hpdc400-dijital-ikiz.git hpdc400
   ```
   (Masaüstünde eski bir `hpdc400` klasörü varsa önce adını değiştir, ör. `hpdc400_eski`.)
3. FreeCAD MCP eklentisi: `git clone https://github.com/neka-nat/freecad-mcp` → `addon\FreeCADMCP` klasörünü
   `%APPDATA%\FreeCAD\Mod\` içine kopyala → FreeCAD'i yeniden başlat → **MCP Addon** tezgâhı → **Auto-Start Server** işaretle.
4. VS Code'da `hpdc400` klasörünü aç, terminalde `claude` → `/mcp` ile **freecad** ve **hpdc400** sunucularının bağlı olduğunu gör
   (sunucu birkaç saniyede açılır; `statik_kontrol` / `hareket_kontrolu` bir bilgisayarda ilk kez çağrılınca geometri çekirdeğini (~60 MB) indirir, yavaş ağda birkaç dakika sürebilir).

## Her çalışma oturumu
```
git pull                 # başlarken: diğer bilgisayardaki değişiklikleri al
...çalış...
git add -A && git commit -m "ne yaptın" && git push   # bitirince
```
Kurallar:
- Aynı anda iki bilgisayarda **params/params.json**'u değiştirme (çakışma çıkarır). Büyük işler için dal aç: `git switch -c kademe-2-hidrolik`.
- Her commit'ten önce `statik_kontrol` ve `hareket_kontrolu` YEŞİL olmalı (CLAUDE.md döngüsü bunu otomatik yapar).
- `out/` (STEP, FCStd, raporlar) depoya girmez; her bilgisayar kendisi üretir.

## FreeCAD'de açmak (MCP olmadan)
FreeCAD → Makro → Makrolar… → `HPDC400_yukle.FCMacro`. Proje klasörünü kendisi bulur
(sırasıyla `HPDC_ROOT`, makronun klasörü, `~/Desktop/hpdc400`, `~/hpdc400`).

## hpdc400 MCP sunucusu araçları
| Araç | Ne yapar | FreeCAD gerekir mi |
|---|---|---|
| `proje_durumu` | ürün ağacı, fazlar, parça sayısı, son commit'ler | hayır |
| `parca_bilgisi` | bir parçanın ölçüleri, lokal orijini, konumları | hayır |
| `statik_kontrol` | geometri, BOM adedi, bbox, çakışma, gömülme | hayır |
| `hareket_kontrolu` | mengene veya kalıp yüksekliği boyunca çarpışma taraması | hayır |
| `freecad_montaji_yukle` | montajı kurar, animasyonu başlatır | evet |
| `freecad_konum` | mafsal (0-1) + kalıp yüksekliği konumu | evet |
| `freecad_animasyon` | aç-kapa animasyonu başlat/durdur | evet |
| `freecad_kalip_yuksekligi_ayarla` | redüktörlü motorla kalıp yüksekliği | evet |
| `freecad_ekran_goruntusu` | aktif görünümün PNG'si | evet |
