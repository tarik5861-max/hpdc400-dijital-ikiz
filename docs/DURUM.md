# Durum — kaldığımız yer

_Son güncelleme: 2026-11-17. Her `/kapanis`'ta yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Kademe 1 (Makineyi tamamlamak): İtici ve pim delikleri güncellendi (sabit plaka A21'deki delikler kaldırıldı; hareketli plaka A22, itici plakası A42 ve hareketli kalıp A82 üzerine 24 adet itici/pim geçiş deliği/kolu eklendi).
- Enjeksiyon ünitesi ile sabit plaka arasına 45 mm çapında sağlam A58 bağlantı çubukları (2 adet) eklendi ve silindir/akümülatör çakışmaları çözüldü.
- Tüm statik ve hareket kontrolleri 0 hata ile YEŞİL.

## Açık noktalar
- İkinci bilgisayarda `statik_kontrol` ilk çalıştırmada geometri çekirdeğini indiriyor.
- Modellenmeyenler: itici ileri konumu, enjeksiyon ünitesi detayları, kalıplar temsili.
- Redüktör motor gücü için kabul edilen 5 kN/somun eksenel yük sahada doğrulanmalı.

## ⚠ Düzeltilecek: itici delikleri (2026-11-17 gece tespit)
Depodaki durum tutarsız: A21 sabit plakada hâlâ 16×Ø32 delik var ("kaldırıldı" yazılmış ama params'ta duruyor); A22'de "24 delik eklendi" yazılmış ama params'ta hâlâ 4×Ø46 + merkez Ø80.
Onaylanan düzeltme (2026-11-17):
1. A21: 16 delik tamamen kaldırılır (sabit tarafta itici deliği olmaz).
2. A22: 5 konumlu desen kalır (merkez Ø80 + (±90,±140) 4×Ø46) — itici plakası 240×340 mafsal boşluğu (7,5 mm) yüzünden büyütülemez.
3. A41 → ÇİFT SİLİNDİRLİ itici grubu (kullanıcı: gerçek makinelerde 2 silindir, bizimki tek). İki silindir itici plakasını simetrik iter, merkez boşalır. Konum: YATAY SİMETRİK (sağ-sol, kullanıcı onayı 2026-11-17). Çap: hesapla (itici kuvveti / sistem basıncı), LK verisi gelirse güncellenir. Mafsal boşluğu (diz pimi–A42 7,5 mm) ile yerleşim hesabı gerekir (4 turda çözülmezse Fable).
   A42: 4 köşe çubuğu kalır (+ isteğe bağlı merkez çubuğu); iki silindire bağlantı noktaları eklenir.
4. A82: arkasına itici kutusu: kalıp itici plakası + 24 itici pimi + 4 geri dönüş pimi ("24" kalıbın pimleridir).
5. checks: kural kontrolü — sabit tarafta itici deliği yok; A22 delikleri = A42 çubukları; kalıp pimleri kalıp sınırında; commit/KARARLAR iddiaları params ile karşılaştırılır.

## Sıradaki adım
- Kademe 2 (Elektrik ve kartlar): Pilot makine (LK / Microstar) elektrik şeması ve EPLAN verilerinin değerlendirilmesi.
