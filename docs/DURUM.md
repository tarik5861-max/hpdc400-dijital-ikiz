# Durum — kaldığımız yer

_Son güncelleme: 2026-11-19. Her `/kapanis`'te yeniden yazılır (en fazla ~60 satır)._

## Şu an
- A14 arka dikme tasarımı modern endüstriyel form ve şase taban bağlantı kaburgalarıyla güncellendi (`parts/A14_kolon_arka_dikme.py`).
- Kademe 3 hidrolik bileşenleri (A64 toplayıcı boru, A65 enjeksiyon valf bloğu, A66 konum sensörü, A67 basınç vericisi) modellemesi ve parametreleri tamamlandı (`114` instance).
- Statik kontrol YEŞİL: 114 instance, 0 hata, 0 uyarı.

## Açık noktalar
- Yok (tüm Kademe 1–3 model ve simülasyon ögeleri tamamlandı).
- A62 pompası gerçek 4520VQ tandem geometrisine çevrildi: A98..A119 (14 script, 22 ID, 52 instance), bom A62 altında alt ağaç; assemble.leaves alt ağaçları okur; hidrolik.json P1/P2 bagli_id eklendi. Kontroller YEŞİL: 166 instance, 0 hata (3 vuruş + hareket). Önizleme out/preview_pompa_*.png.
- Kademe 1 eksik kalan A13 sabit plaka destek kolonlarının ön flanş bağlantısı cıvatalı (M24) olarak detaylandırıldı ve kodlandı (`parts/A13_sabit_plaka_destek.py`).
- Kademe 3 hidrolik şema ve valf/sensör haritalaması (`params/hidrolik.json`) tamamlandı, testler doğrulandı.
- Statik kontrol YEŞİL: 166 instance, 0 hata, 0 uyarı.

## Açık noktalar
- P1 debi uyuşmazlığı: en küçük 45VQ42 ~136 cm3/dev → 1460 d/dk'da ~195 L/dk (hidrolik.json 120 L/dk); 140 bar'da ~45 kW > 30 kW motor. Şema P1'i değişken debili pistonlu sayıyor, 4520VQ sabit deplasmanlı kanatlı.

## Sıradaki adım
- Kademe 4 (Yazılım / PLC durum makinesi ve sıralama mantığı) çalışmalarına başlanması.
