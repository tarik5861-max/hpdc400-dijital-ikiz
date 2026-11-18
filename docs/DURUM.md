# Durum — kaldığımız yer

_Son güncelleme: 2026-11-19. Her `/kapanis`'te yeniden yazılır (en fazla ~60 satır)._

## Şu an
- Kademe 1 tamamlandı. Kontroller YEŞİL: 104 instance, 0 hata, 0 uyarı; hareket taramasında çarpışma çifti 0; elektrik testleri 11 senaryo, 0 hata.
- Kademe 2 (elektrik) taslak v1: DCC630 şeması 400 t'ye uyarlandı (params/elektrik.json, mantık simülasyonu, KURAL_ELEK kontrolleri).
- 2026-11-19: K-EL-07 karar verildi: A97 enkoder redüktör çıkışına, 25 ppr A/B (0,1 mm/darbe, 17 Hz), standart DI yeter. TC1/U1 için K-EL-03 (U1 ayrı L-N) geçerli.
- Bu ortamda `cadquery` kuruldu (pip); `hpdc400` MCP aracı yok, kontroller `python3 checks/check.py` ile koşuldu.

## Açık noktalar
- OLCU_TALEBI (olcu-mimari'ye henüz gönderilmedi): A97 enkoderin konumu (A94 çıkış mili) ve ppr değeri.
- Veri bekleyenler: gerçek 400 t elektrik şeması, PLC HW Config bayt.bit eşlemesi, DI32 ve DO17-30 bulanık kanalları, KA9 paralel kontakları (köprü mü, robot bypass mı).
- Saha doğrulaması: U1/TC1 akımı (pensle), PLC tarama süresi (OB1), S121 enerjisiz=boşalt ve KA_ES davranışı, güç faktörü, solenoid gücü, eşikler, KT1 süresi.
- A58 enjeksiyon bağlantı çubuklarının sahayla teyidi.
- elektrik.json küçük eksikler: siralayici.piston_geri baslangic_adim, a97_sayac.baslangic_mm, P.A97_REF_mm, mafsal yağlama penceresi kapanışı; lib'de kalan sinyal adı sabitleri.
- Arka koruma kapısı ve ST3-1 bom'da yok (A71'e bağlı).

## Sıradaki adım
- Yeni sohbette Kademe 3 (Hidrolik): docs/hidrolik_sema_taslak.md + elektrik valf eşlemesi (S121=DV1, S118, S301/S302…) ile ağ modeli taslağı.
- A97 OLCU_TALEBI'ni olcu-mimari'ye göndermek; FreeCAD'e yeni hâli basıp görsel kontrol.
- Gerçek şema/HW Config gelince elektrik.json DCC630 şablon satırlarını değiştirmek.
