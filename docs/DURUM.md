# Durum — kaldığımız yer

_Son güncelleme: 2026-11-18. Her `/kapanis`'ta yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Kademe 1 (Makineyi tamamlamak) devam ediyor. Kontroller YEŞİL: 104 instance, 0 hata, 0 uyarı; hareket ve kalıp yüksekliği taramalarında çarpışma yok.
- İtici grubu bitti: A21'de itici deliği yok; A41 çift silindirli (Ø100/Ø56); A42 390 mm çubuk; A82 itici kutusu + A83 + 24×A84 + 4×A85 (kalıp strok ayarı 65).
- Sabit plaka (A21) destekleri: 3 uzun kolon A13 (2 alt Ø100, 1 üst Ø120), ön uç cıvatalı flanşla A21'e, arka uç kaynakla A14 dikmesine; A14 şase ucuna (A11) kaynaklı. A21 sabit.
- checks/kurallar.py (KURAL_* kontrolleri) var. A56 akümülatörler Y=-390'a kaydı (A13 boşluğu için).
- Masaüstü oturumu (2026-11-18): FreeCAD canlı yükleme + görsel doğrulama yapıldı (A13 rev2 öncesi hâl); kullanıcı A58 konum/bağlantısını eleştirdi → bu oturumda 3 kolon çözümüyle karşılandı. Yeni hâli FreeCAD'e yeniden basmak gerek.
- Hesaplar: docs/olcu_notlari.md (rev2), out/olcu_2026-11-18_A13_3kolon.txt, out/olcu_2026-11-18_A13_bosluk.txt.

## Açık noktalar
- ONAY BEKLİYOR: A58 enjeksiyon bağlantı çubukları ağaçtan çıkarıldı (alt kolonlar aynı kotta, görevi devraldı); 430 kN enjeksiyon tepkisi artık A13/A14 üzerinden. Onay yoksa geri alınır.
- ONAY BEKLİYOR: kazara yatay yük katsayısı H = c·F (c = 0,1 ve 0,2 için ölçüler sağlanıyor); standart değil.
- Yan (Y) yük taşınmıyor: A21–A12/A11 arasına enine kama gerekebilir, modellenmedi.
- Isıl zorlama (20 K → 0,58 mm): ön flanşta şim/oval delik önerildi; FEM veya sahada ölçüm.
- Servis erişimi: üst kolon A54/A55'i üstten vinçle sökmeyi engelliyor mu — fotoğrafla teyit.
- A56 akümülatörlerin hidrolik boru güzergâhı kontrol edilmeli (ayak halkası şase kenarında).
- Kalıp yüksekliği taramasında somun açısı -12000..21000° (script hata saymıyor); doğrulanmalı.
- A41–diz pimi boşluğu 7,5 mm silindir boyunca; itici ileri konumu modellenmedi.
- FreeCAD'e basma yapılmadı (canlı FreeCAD kullanıcının PC'sinde gerekir).
- Redüktör 5 kN/somun eksenel yükü sahada doğrulanmalı. Modellenmeyenler: enjeksiyon ünitesi detayları, kalıplar temsili.

## Sıradaki adım
- A58 kaldırma ve H katsayısı kararları; sonra FreeCAD'e bas + görsel kontrol.
- Sonra Kademe 2 (Elektrik ve kartlar): LK / Microstar elektrik şeması geldiğinde ayrı sohbette.
