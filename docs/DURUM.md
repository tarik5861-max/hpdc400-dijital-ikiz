# Durum — kaldığımız yer

_Son güncelleme: 2026-11-17. Her `/kapanis`'ta yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Kademe 0 bitti: 71 parça, statik kontrol 0 hata, mengene ve kalıp yüksekliği hareket taramaları 0 çarpışma.
- FreeCAD'de açılır: Makro → `HPDC400_yukle.FCMacro` veya `hpdc400` MCP aracı `freecad_montaji_yukle`.
- İki bilgisayar depoya bağlı (masaüstündeki `hpdc400` klasörü). İkinci bilgisayarda MCP zinciri gerçek FreeCAD'de uçtan uca test edildi.

## Açık noktalar
- İkinci bilgisayarda `statik_kontrol` ilk çalıştırmada geometri çekirdeğini indiriyordu; sonucu `out/mcp_test2.log`'da kontrol et.
- Modellenmeyenler: itici ileri konumu, A81'de itici pim delikleri, enjeksiyon ünitesi–sabit plaka bağlantı çubukları, kalıplar temsili.
- Redüktör motor gücü için kabul edilen 5 kN/somun eksenel yük sahada doğrulanmalı.

## Sıradaki adım
Kademe 1: pilot makine ve dokümanları (hidrolik şema, elektrik projesi, PLC programı, servis kayıtları) belirlenince başlar. Ayrıntı: `docs/YOL_HARITASI.md`.
