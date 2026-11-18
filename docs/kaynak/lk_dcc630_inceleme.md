# LK DCC630 I/O ve teşhis verisi — ilk inceleme (Kademe 2 girdisi)

Kaynak: `docs/kaynak/lk_dcc630_io_teshis.py` (kullanıcıdan, 2026-11-18, DEĞİŞTİRİLMEDİ). Şema sayfaları (9-2…9-9) bizde yok; aşağıdaki kontroller yalnız dosyanın kendi içi tutarlılığıdır, şemayla karşılaştırma YAPILMADI.

## Sayısal özet (kod çalıştırılarak)
- 73 kanal: 41 DI, 26 DO, 3 AI, 3 AO. Dosya başlığı "128+ kanal" diyor; gerçekte 73 (eksik kanallar olabilir).
- 3 teşhis kuralı: kalıp kapanmıyor, pompa motoru kalkmıyor, enjeksiyon pistonu hareket etmiyor.

## Tutarsızlıklar (şemadan doğrulanmalı)
1. Aynı etiket iki kanalda: S120 (Q0.1 kalıp kapama valfi ve Q1.1 itici ileri), S121 (Q0.7 akümülatör boşaltma ve Q1.2 itici geri). Biri yanlış yazılmış olabilir.
2. LKPP-03 etiketi hem basınç (AI0) hem akış (AI1) sensöründe.
3. Kurallardaki bileşenler (KA9, KM1-3, FR1, TC1, AG10-6A, S424, PS307, FU12) kanal tablosunda tanımlı değil; yalnız metinde.
4. DO tablosunda Q2.7'den Q3.6'ya adres atlaması (Q3.0-Q3.5 yok); DI'da I5.1'den sonrası yok. Eksik veya kullanılmayan kanal olabilir.
5. Kural 1 sebep metni "E-Stop zinciri 1B1-1…1B4-1" gibi ifadeler tablodaki etiketlerle (1B1 = kalıp açma butonu) uyuşmuyor; şemadan teyit gerekir.
6. `diagnose()` kelime eşleştirmesi basit (sorgudaki herhangi bir kelime); "alarm" gibi sorgu eşleşmiyor.

## Güvenlik (teşhis motorunda zorunlu, CLAUDE.md kural 10)
Kuraldaki kontrol adımları (sigorta ölçme, röle, kontaktör, hidrolik valf) güvenlik adımı içermiyor. Her kurala önce: elektrik enerjisini kes ve kilitle-etiketle (LOTO), hidrolik akümülatörü deşarj et / basıncı boşalt, kapı emniyet zincirini köprüleme. Bu bölüm teşhis motoru yazılırken kurallara eklenmeli.

## Sıradaki adımlar (Kademe 2, ayrı sohbet)
- Şema sayfaları (PDF/EPLAN) ve I/O listesi gelince kanalları doğrula, tutarsızlıkları çöz.
- Kanalları ürün ağacı ID'lerine bağla (S113/S120… valfleri → hidrolik şema taslağı `docs/hidrolik_sema_taslak.md` ile eşle; örn. Y1/Y2/Y3 → hangi S-numarası).
- Doğrulanmış veriyi JSON'a taşı (`params/` altında, tek doğruluk kaynağı), kural kontrolleri ekle.

---
# 2. dosya: `docs/kaynak/lk_dcc630_elektrik_sim.py` (güç/kontrol bileşenleri + mantık simülatörü)
Yine şemayla karşılaştırılmadı; iki dosya birbiriyle ve modelimizle karşılaştırıldı.

## Dosyalar arası çelişkiler (şemadan doğrulanmalı)
1. Q1.4 / Q1.5 aynı etiket (S301 / S302) ama dosya 1'de "Core 1 In/Out valf", dosya 2'de "İtici ileri/geri". Dosya 1'de itici ayrıca S120/S121 (Q1.1/Q1.2) olarak tanımlı; o etiketler de Q0.1 ve Q0.7 ile çakışıyordu. İtici valf numaraları belirsiz.
2. Analog kartlar: dosya 1 Slot 10 = AI (SM335), Slot 11 = AO (6ES7332). Dosya 2 yorumu "Slot 9 & 10" diyor; U17 ve U18'in ikisi de "AO1 Slot11" olarak yazılmış (dosya 1: U17=AO1, U18=AO2); U12 "Slot10 AO1/AO2" (dosya 1'e göre Slot 10 AI kartı). Sayfa numaraları da farklı (DO: 9-8 vs 9-5).
3. Diğer fark yalnız ifade farkı (aynı adres ve etiket).

## Mantık simülatöründe eksikler
- `simulate_pump_motor_start`: başlat butonu bırakılınca motor duruyor (test edildi: "Motor Duruyor"); gerçek devrede mühürleme (self-hold) ve stop butonu (I1.3) var. Yıldız → üçgen geçişte ölü zaman/ara kilit yok (KM3 düşmeden KM2 çekilmemeli).
- "Acil stop zinciri 1B1-1 → 1B2-1 → 1B3-1 → 1B4-1": dosya 1'de 1B1 = kalıp açma butonu, 1B3-1 = piston ileri knob; bunlar acil stop elemanı gibi görünmüyor. Gerçek E-stop zinciri şemadan çıkarılmalı.
- KA9 güvenlik rölesi yazılımda basit AND olarak modellenmiş; gerçekte donanım zincirli. İkizde "donanım" ve "PLC" ayrı gösterilmeli.

## Bizim modelle uyum
- DCC630 = 630 t sınıfı pilot makine; mekanik ikizimiz HPDC-400 (Buhler H-400D tabanlı). Elektrik verisi doğrudan 400 t modelimize eşlenemez (motor, valf, enjeksiyon). Karar gerekir: ikizi DCC630'a mı çevireceğiz, yoksa elektrik pilotu ayrı bir makine olarak mı tutacağız (YOL_HARITASI Alt plan A: boyutlandırma motoru)?
- M1 30 kW (modelimizdeki A62 ile aynı değer). FR1 37–50 A aralığı 30 kW / 380 V motor için (tam yük akımı yaklaşık 55 A, yıldız-üçgende faz yolunda yaklaşık 32 A) tutmuyor görünüyor; şemadan teyit.

---
# Şema ile doğrulama (2026-11-18, taranmış PDF: docs/kaynak/sema/)
Doğrulanmış çıktı: `docs/kaynak/sema/lk_dcc630_dogrulanmis_io.json` (her satırda güven: yüksek/orta/düşük). Taramanın bir kısmı bulanık/el yazılı; okunamayan yerler boş bırakıldı.
**Dosya 1 (`lk_dcc630_io_teshis.py`) şemayla ÇELİŞİYOR, kullanılmamalı:**
1. DI32 kartı Slot 5 (dosya 1: Slot 6). DO32 Slot 7 doğru. Slot 9 (SM323 DI16, tie bar/somun limitleri) dosya 1'de hiç yok.
2. Slot 4 DI16'da 1B10 = displacement lock switch, 1B11A-2 = motor start, 1B12A-2 = motor stop, 1B13 = die adjust, 1B7-4 = semi-auto. Dosya 1 bu etiketleri bir kanal kaydırmış (1B10'a "motor start" vermiş) ve displacement lock + 1B7-4'ü atlamış.
3. DO32 ilk 16 kanal: S120 = confluence valve, S180 = stop valve, S211 = die open control, S210A (KA9 üzerinden) = die close, S605 = plunger lub, S208 = safety lock loose, S301/S302 = ejector FWD/BWD, S121 = accumulator oil discharge, S126 = intensifier control (U17). Dosya 1'de S120/S180/S211/S210A/S605/S208/S121 yanlış işlevlere atanmış; S301/S302 "Core 1" yazılmış (şemada itici).
4. Pompa motoru: KA2 = pump motor control, KA1 = lubrication pump control (orta güven; 9-2'deki motor start devresinde KA2 var). Dosya 1 bunları ters yazmış.
5. Analog: slot 10'daki AOV1/AOV2 çıkıştır (U12 LKPP-03 basınç/akış oransal kartına), "basınç/akış sensörü girişi" değil. AI olarak yalnız VR1 (kalıp pozisyon cetveli). U16 analog sinyali slot 11'den değil DB68 kartından (A09). Basınç sensörleri (akümülatör, çoğaltıcı, enjeksiyon giriş/çıkış, kapama kuvveti) DB68'e bağlı (9-8).
**Dosya 2 (`lk_dcc630_elektrik_sim.py`) ile uyum:** S301/S302 = itici (şemayla uyumlu), S126 → U17 (uyumlu), U12/U16/U17/U18 bağlantıları büyük ölçüde uyumlu; slot numaraları (DI32=5) ve S120/S180/S210A/S605/S208 açıklamaları dosya 2'de de yanlış.
**Açık/doğrulanmalı:** (a) PLC bayt.bit adresleri (şemada I10…I115 gibi klemens notasyonu; HW Config gerekir). (b) DI32 etiketlerinin klemens eşlemesi ve DO kanalları 17-30'un valf numaraları (bulanık). (c) FU10 değeri şemada AS10-1A gibi okunuyor, dosya 2'de 4 A; taramadan kesin değil. (d) Slot 7 kanal 23/24'te basılı etiket çizilip el yazısıyla Start1/Start2 yazılmış (makineye sonradan uyarlama).
**Elektrik şemasında hidrolik taslağıyla eşleşenler (docs/hidrolik_sema_taslak.md):** S121 = akümülatör yağ boşaltma (deşarj valfi DV1 karşılığı), S118 = çoğaltıcı yağ boşaltma, S113/S116/S119 = hızlı/3./2. faz enjeksiyon valfleri, S301/S302 = itici, S126 = çoğaltıcı kontrolü, S210A/S211 = kalıp kapama/açma, S120 = birleştirme (confluence), S180 = stop valfi.
