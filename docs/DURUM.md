# Durum — kaldığımız yer

_Son güncelleme: 2026-11-18. Her `/kapanis`'te yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Kademe 1 tamamlandı. Kontroller YEŞİL: 104 instance, 0 hata, 0 uyarı; hareket ve kalıp yüksekliği taramalarında çarpışma yok.
- Sabit plaka (A21) vuruş eksenleri güncellendi: 3 vuruş ekseninin tamamı (alt Z=-150, orta Z=-75, üst Z=0) sabit plaka üzerinde delik/yatak olarak modellendi.
- FreeCAD canlı yükleme ve görsel doğrulama başarıyla tamamlandı.

## Açık noktalar
- A58 enjeksiyon bağlantı çubuklarının konum ve bağlantı detaylarının (veya alt kolonlar üzerinden aktarımın) sahayla teyidi.
- Kademe 2 (Elektrik ve kartlar) hazırlığı (LK / Microstar elektrik şeması bekleniyor).
- Elektrik (hepsi Claude kararı / varsayım, saha ölçümü gerekir): S121 enerjisiz=boşalt ve KA_ES (E-stop'ta kontrolsüz silindir hareketi, U16/S424 enerjisiz sürgü konumu, A35 pilot çek valfi); TC1 630 VA aşımı (öneri A: U1 ayrı L-N) ve 24 V bütçesi %84; güç faktörü, solenoid gücü, eşikler, KT1 süresi.
- Elektrik: PLC bayt.bit adres eşlemesi (HW Config) yok; DI32 ve DO 17-30'un bulanık satırları; A97 enkoder darbe kaçırma (hızlı sayıcı veya redüktör çıkışı kararı, mekanik/BOM); kalıp yüksekliği ayarı kalıp takılıyken yasak bilgisi; DI5.08 anlamı; otomatik çevrimde aktif alarm kontrolü.
- Elektrik JSON küçük eksikler (OLCU_TALEBI): siralayici.piston_geri baslangic_adim alanı, a97_sayac.baslangic_mm temiz alan, P.A97_REF_mm parametresi, mafsal yağlama penceresi kapanışı; lib'de kalan sinyal adı sabitleri (HMI.LOTO_*, S.S121, bobin()/aku_bosaltiyor() id'leri).
- Arka koruma kapısı ve ST3-1 bom'da yok (A71'e bağlı).

## Sıradaki adım
- Gerçek 400 t makinenin elektrik şeması geldiğinde elektrik.json'daki DCC630 şablon satırlarını değiştir; HW Config eşlemesi; bulanık kanallar.
- FreeCAD'e yeni hâli bas + görsel kontrol (A13/A14, vuruş konumları, itici grubu).
- Kademe 3 (Hidrolik): docs/hidrolik_sema_taslak.md + elektrik valf eşlemesi (S121=DV1, S118, S301/S302…) ile ağ modeli.
