# Durum — kaldığımız yer

_Son güncelleme: 2026-11-18. Her `/kapanis`'ta yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Kademe 1 (Makineyi tamamlamak) devam ediyor. Kontroller YEŞİL: 104 instance, 0 hata, 0 uyarı; hareket ve kalıp yüksekliği taramalarında çarpışma yok.
- İtici grubu bitti: A21'de itici deliği yok; A41 çift silindirli (Ø100/Ø56, yatay simetrik); A42 390 mm çubuk; A82 itici kutusu + A83 itici plakası + 24×A84 pim + 4×A85 geri dönüş pimi (kalıp strok ayarı 65).
- Sabit plaka (A21) şaseye 2 adet A13 destek direğiyle bağlandı (taban + kolon + üçgen gusset); A21 sabit, kızakta kaymaz.
- checks/kurallar.py eklendi (KURAL_* kontrolleri); kinematics: A13/A58 sabit grupta, A83-85 hareketli grupta.
- Hesaplar: docs/olcu_notlari.md ve out/olcu_2026-11-18_itici_destek.txt.

## Açık noktalar
- ONAY BEKLİYOR: A13 hesabındaki kazara yatay yük H = 0,1·F (400 kN) ajan varsayımı, standart değil; direk ölçüleri geçici.
- Kalıp yüksekliği taramasında somun açısı -12000..21000° çıkıyor (script hata saymıyor); olcu-mimari ile doğrulanmalı.
- A41–diz pimi boşluğu 7,5 mm artık silindir boyunca; itici ileri konumu modellenmedi.
- FreeCAD'e basma yapılmadı (canlı FreeCAD kullanıcının PC'sinde gerekir).
- İkinci bilgisayarda statik_kontrol ilk çalıştırmada geometri çekirdeğini (OCP) indirir.
- Redüktör motor gücü için kabul edilen 5 kN/somun eksenel yük sahada doğrulanmalı.
- Modellenmeyenler: enjeksiyon ünitesi detayları, kalıplar temsili.

## Sıradaki adım
- H yükü katsayısını onayla (gerekirse A13 yeniden hesapla), FreeCAD'e bas + görsel kontrol, somun açısı gözlemini doğrula.
- Sonra Kademe 2 (Elektrik ve kartlar): LK / Microstar elektrik şeması ve EPLAN verileri geldiğinde ayrı sohbette.
