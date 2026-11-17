# Durum — kaldığımız yer

_Son güncelleme: 2026-11-17 (öncelik sırası işlendi). Her `/kapanis`'ta yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Kademe 0 bitti: 71 parça, statik kontrol 0 hata, mengene ve kalıp yüksekliği hareket taramaları 0 çarpışma.
- `cadquery-ocp-novtk` ve `matplotlib` yerel ortamda kuruldu; `checks/check.py`, `checks/motion_check.py`, `checks/render.py` ve `assembly/assemble.py` başarıyla çalışıyor.
- Kademe 1 eksik mekanik unsurlarından itici ve kalıp pim delikleri analizi yapıldı.

## Açık noktalar
- İkinci bilgisayarda `statik_kontrol` ilk çalıştırmada geometri çekirdeğini indiriyordu; sonucu `out/mcp_test2.log`'da kontrol et.
- Modellenmeyenler: itici ileri konumu, A81'de itici pim delikleri, enjeksiyon ünitesi–sabit plaka bağlantı çubukları, kalıplar temsili.
- Redüktör motor gücü için kabul edilen 5 kN/somun eksenel yük sahada doğrulanmalı.

## Sıradaki adım
Öncelik sırası: makineyi tamamlamak → elektrik → hidrolik → yazılım.
1. Kademe 1: eksik mekanik parçalar ve satın alınan parçalar; pilot makine LK (Microstar) ölçüleri.
2. Kullanıcı LK makinenin elektrik şemasını getirecek: yeni sohbette `/devam` + şema → envanter çıkar, işe yarar mı, eksik ne, nereye bağlanır değerlendir.
Ayrıntı: `docs/YOL_HARITASI.md`.
