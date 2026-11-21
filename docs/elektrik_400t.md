# HPDC-400 elektrik katmanı — fonksiyon düzeyinde uyarlama (Kademe 2, taslak v1)

Tarih: 2026-11-18 (karar turu aynı gün, bölüm 9-10) · Hazırlayan: olcu-mimari · Tek doğruluk kaynağı: `params/elektrik.json`
Üretim kaydı ve hesaplar: `out/elektrik_400t_olustur.py` (tek seferlik), `out/elektrik_400t_hesap.txt`

**Yaklaşım:** LK DCC630 (630 t) elektrik şeması ŞABLON olarak alındı; 400 t ikizin ürün ağacına (bom.json) ve params.json değerlerine göre yeniden boyutlandırıldı. Gerçek 400 t şeması gelince değiştirilecek. Her kanal/bileşende `koken` = `dcc630_sablon` / `400t_hesap` / `yeni`, ayrıca `guven` ve `durum` (aktif / istege_bagli / ayrilmis / kapsam_disi) var.
Kaynak: `docs/kaynak/sema/lk_dcc630_dogrulanmis_io.json` + PDF sayfa 9-1, 9-2, 9-3 bu oturumda yeniden görüntülendi. `docs/kaynak/lk_dcc630_io_teshis.py` KULLANILMADI (şemayla çelişiyor).

## 1. Modüller ve kanal sayıları
| Slot | Kart | Köken | 400 t notu |
|---|---|---|---|
| 4 | SM323 DI16/DO16 | dcc630_sablon | DI: 16 operatör butonu (1B10 ayrılmış: işlevi belirsiz). DO: 15'i robot/DCM/motorlu kapı → isteğe bağlı; alarm lambası aktif |
| 5 | SM321 DI32 | dcc630_sablon | 23 okunabilen satır; 9 kanal okunamadı (ayrılmış). Core 1-4 seçici kapsam dışı. **Kanal no = okuma sırası, klemens doğrulanmadı** |
| 7 | SM322 DO32 | dcc630_sablon | 1-16 valfler; 17-22 core kapsam dışı; 23/24 (el yazısı Start1/2) ayrılmış; **29/30 → KM5/KM4 (sapma)** |
| 9 | SM321 DI16 | **yeni** | DCC630'daki kolon çekme/somun kartı kapsam dışı; yerine 400 t yeni girişler (A97 enkoder, QM2, KA9/KM2/KM3 geri bildirimleri, itici limitleri, DV1 konumu …) |
| 10 | SM335 AI4/AO4 | dcc630_sablon + yeni | AI1 VR1 kalıp cetveli; AI2 PT1 ana hat (yeni); AI3 yağ sıcaklığı (yeni, isteğe bağlı); AO1/AO2 → U12 basınç/akış |
| 11 | AO4 (332-5HD01) | dcc630_sablon | AO1 U17 çarpan, AO2 U18 2. faz hız |
| DB68 | harici enjeksiyon kartı | dcc630_sablon | U16 analog (A09), PT2 akümülatör, çarpan, enjeksiyon giriş/çıkış basıncı; kapama kuvveti isteğe bağlı; enjeksiyon enkoderi ayrılmış |

Sayım (131 kayıt): DI 65 (aktif 43, isteğe bağlı 6, ayrılmış 12, kapsam dışı 4) · DO 48 (aktif 23, isteğe bağlı 16, ayrılmış 3, kapsam dışı 6) · AI 9 (aktif 6, isteğe bağlı 2, ayrılmış 1) · AO 9 (aktif 5, ayrılmış 4).

## 2. DCC630'dan farklar
| Konu | DCC630 | HPDC-400 ikiz | Köken / gerekçe |
|---|---|---|---|
| Kalıp yüksekliği | DO7.29/30 S203/S202 valf (düşük güven) | KM5 (ince) / KM4 (kalın) ters yönlü kontaktör → A95 1,1 kW motor + A94 redüktör + A93/A91 dişli; A97 enkoder (DI9.01/02), QM2 koruma; uç limitler bobin yolunda | 400t_hesap; ağaç A91–A97 (2026-11-15 kararı) |
| Kolon çekme / somun | Slot 9 DI16 + U20 | kapsam dışı | 400 t'de hidrolik kolon çekme yok |
| Maça (core 1-4) | DO7.17-24, DI5 seçiciler | kapsam dışı / ayrılmış | hidrolik taslak Y4 "model dışı" |
| Robot/DCM/sprey | Slot 4 DO16 | isteğe bağlı (arayüz rezerve) | ikizde hücre yok |
| Ön kapı | M4 0,75 kW motorlu kapı + buton/emniyet | A71 elle sürgülü varsayıldı; motor/buton isteğe bağlı; limitler aktif | params A71 (kızak üzerinde sürgü) |
| Arka kapı | arka kapı limit 1/2, ST3-1 | aktif ama **ağaçta arka koruma yok** (A71'e bağlandı) | açık nokta: bom'a arka koruma eklenmeli mi |
| FR1 | 37–50 A | 28–40 A, ayar 33 A (faz yolunda) | 400t_hesap (aşağıda) |
| TC1 | 630 VA, U1 de bundan beslenir | **Seçenek A (karar K-EL-03):** U1 ayrı L-N + 6 A MCB, TC1 630 VA kalır (yük 425 VA, kalkış 785 VA SINIRDA) | 400t_hesap, Claude kararı |
| FU12 | 16 A tek kol | 2×10 A (valf / oransal kart) önerisi | 400t_hesap |
| Y-Δ geçişi | KT1 + KM2/KM3 NC yardımcı kilit | + 50 ms ölü zaman, KM2/KM3 geri bildirimi PLC'de izlenir | 400t_hesap / yeni |
| KA9 | kapı limit 2 kontaklarına paralel bulanık kontaklar | paralel köprü YOK, seri zincir | güvenlik |
| E-stop | ST1-1…ST4-1 yalnız motor bobin zincirinde | + KA_ES: valf beslemesini (S24V) keser (karar K-EL-01) | 400t_hesap, Claude kararı |
| Sensörler | PT1 yok | AI10.2 PT1, DI9.12 DV1 konumu, DI9.10/11 itici limitleri, isteğe bağlı TT1/RF1 | yeni (teşhis) |
| Enjeksiyon konumu | DB68 enkoderi | ayrılmış (ikizde faz geçişi süre parametresiyle) | gerçek makinede zorunlu |

Şema okumasında bu oturumda netleşenler: E-stop zinciri etiketleri **ST1-1 (pano), ST2-1 (enjeksiyon), ST3-1 (arka kapı), ST4-1 (operatör kutusu)**, sayfa 9-2 L9–L12 seri. Eski dosyadaki "1B1-1…1B4-1" büyük olasılıkla bu etiketlerin yanlış okunmuş hâli. Motor devresi: E-stop → 1B12A stop NC → 1B11A1 start NO ∥ KM1 mühür → KA2 → KM1; KT1 NC gecikmeli → KM2 NC → KM3; KT1 NO gecikmeli → KM3 NC → KM2; FR1 NC tüm bobinlerin N dönüşünde. FU10 400 dpi'de "AS10-4A" okundu (önceki okuma 1 A).

## 3. Hidrolik ↔ elektrik eşlemesi (docs/hidrolik_sema_taslak.md)
| Hidrolik | Elektrik | ID |
|---|---|---|
| Y1 enjeksiyon | DO7.25 yavaş (1. faz) · DO7.01 S113 + U16/S424 hızlı (2. faz, akümülatör) · DO7.11 S119 + U18 · DO7.10 S116 3. faz · DO7.12 S126 + U17 çarpan · DO7.16 S118 çarpan boşaltma · DO7.26 piston geri · DO7.02 S120 birleştirme | A54, A55, A56, A52 |
| Y2 kapama | DO7.05 S210A (KA9 üzerinden) · DO7.04 S211 · U12 (AO10.1/2) | A35 |
| Y3 itici | DO7.13 S301 / DO7.14 S302: **tek valf çifti iki A41 silindirini paralel besler** | A41, A42 |
| Y4 maça | kapsam dışı | – |
| ACV1 şarj | aday DO7.03 S180 stop valfi (DÜŞÜK güven) | A56 |
| DV1 deşarj | DO7.15 S121 + DI9.12 elle vana konumu (yeni) | A56 |
| RV1/RV2 | mekanik, elektrik kanalı yok (PT1/PT2 ile dolaylı) | A62, A56 |
| PT1 / PT2 | AI10.2 (yeni) / DB68.PT2 | A62 / A56 |
| P1 pompa | U12 (AO10.1/2), KA2 → KM1 | A62 |

Vuruş konumu (global.shot_position alt/orta/üst) mekanik ayardır (A57 takoz); elektrik kanalı yoktur. Konum bilgisi **operatör HMI girişidir** (P.VURUS_KONUMU_GIRILDI, enjeksiyon izninde). Yanlış giriş riskine karşı isteğe bağlı 3 endüktif sensör önerilir.

## 4. Hesaplar (formül, varsayım, sonuç)
Kaynak tablo: IEC 60364-5-52 B.52.4 (Cu/PVC, yöntem B2). Motor verileri 55 kW 4p tipik katalog değerleri = **ikiz_tasarim varsayımı** (2026-11-19: M1 30 → 55 kW, IEC 280S/M, A120; saha verisi istenmedi, etiket gelince değişir). Eskiden KULLANICI_ONAYI işaretli kalemler 2026-11-18'de Claude kararı oldu (JSON'da `CLAUDE_KARARI_SAHA_DOGRULAMASI`); liste bölüm 9.

| Kalem | Formül / gerekçe | Sonuç |
|---|---|---|
| M1 In (55 kW, 380 V, η 0,936, cosφ 0,88; ikiz_tasarim varsayımı) | P/(√3·U·η·cosφ) | **101,5 A**; faz sargısı In/√3 = 58,6 A; DOL ≈ 710 A, Y-Δ yıldızda ≈ 237 A (1/3 DOL) |
| FR1 konumu | şema 9-1: KM1 → FR1 → U1V1W1 = faz yolu | ayar **58,6 A**, aralık **45–63 A** (ayar/üst sınır 0,93 → **SINIRDA**). DCC630 37–50 A: 55 kW için **FAIL** (faz akımı 58,6 A > 50 A) |
| KM1 / KM2 | faz akımı 58,6 A; 65 A sınıfı kullanım 0,90 = SINIRDA | **80 A AC-3** (kullanım 0,73) |
| KM3 | In/3 = 33,8 A | **40 A AC-3**, kullanım 0,85 = **SINIRDA** (yalnız 8 s yıldız görevi; 50 A sınıfı alternatif 0,68) |
| Kontaktör bobinleri | ikiz_tasarim varsayımı: KM1/KM2/KM3 çekme 200 VA, tutma 20 VA | TC1 yükünü artırır (aşağıda) |
| KT1 / ölü zaman | 55 kW rotor ataleti, yıldız akımı 237 A; yüksüz kalkış varsayımı | **8 s** / 50 ms (ikiz_tasarim varsayımı; 30 kW'ta 6 s) |
| Ana besleme | Ib = 101,5 + 2,7 + 4,2 = 108,4 A; koruma **125 A MCCB** (Ib/In 0,87 = SINIRDA); ayırıcı 160 A | **70 mm²** (Iz 151 A; 50 mm² Iz 119 A < 125 A FAIL), ΔU %0,31 @20 m. DCC630 3×25 mm² / 100 A bu motorda YETERSİZ. B2 tablosunda 50/70 mm² değerleri tablo uzantısı (ikiz_tasarim varsayımı) |
| Motor ayakları (6 iletken) | 58,6 A / (0,87 ortam 40 °C × 0,80 gruplama) | **35 mm²** (Iz 99 × 0,696 = 68,9 A, kullanım 0,85 = **SINIRDA**; 50 mm² alternatif 0,71); 25 mm² FAIL; katsayılar Claude kararı (bölüm 9) |
| 24 V bütçesi | 5×35 W solenoid + oransal kartlar 8,1 A + 2,15 A lojik | 17,5 A / 20,8 A = **%84 (sınırda)**; FU12 16 A'da yük/In 0,96 (sınırda) → 2×10 A kol; FU10 4 A ise 0,54 OK (1 A olsaydı yetersiz) |
| TC1 | U1 753 VA (PF 0,65 varsayım) + PS307 230 + M10 107 + fan 19 + bobin 69 (eskiden 32) | tepe **1178 VA > 630 VA** (kalkış 1538 VA). Öneri A: U1 ayrı L-N → TC1 yükü 425 VA (surekli 0,67 OK; KM1+KM3 çekme anında ~785 VA = 1,25×630, **SINIRDA**, ~100 ms). B: 1600 VA (FU11 10 A; kalkış 0,96 SINIRDA). Gerçek akım pensle ölçülmeli (DCC630 sahada çalışıyor; gerçek yük muhtemelen düşük) |
| A95 (1,1 kW, 4p) | η 0,81, cosφ 0,76 | In **2,7 A**, QM2 2,5–4 A ayar 2,7 A; KM4/KM5 9 A AC-3 ters yön kilitli; 1,5 mm² |
| A95 moment | 87 Nm pinyon / (35·0,94) | 2,64 Nm / 7,24 Nm = %37 |
| A97 enkoder | 103,6 mm/dk / 1450 d/dk = 0,0714 mm/devir | 2 darbe/devir A/B → 48 Hz (standart DI yeter), 0,036 mm/darbe; >4 ppr ise hızlı sayıcı gerekir. Durma kayması 0,17 mm |
| Eşikler | 0,9/1,07/0,8 × 140 bar | PT2 enjeksiyon min 126, yüksek 150, deşarj tamam <2 bar 10 s; PT1 düşük 112; yağ 55/65 °C (Claude kararı, bölüm 9) |

## 5. Güvenlik zinciri (veri: elektrik.json → mantik)
- **Donanım katmanı** (PLC yalnız izler): HW.ESTOP_OK = ST1-1∧ST2-1∧ST3-1∧ST4-1 → motor bobin zinciri; KM1 mühürleme (start ∥ KM1) + stop NC + KA2 + FR1 NC; KM3 = L15 ∧ ¬KT1 ∧ ¬KM2; KM2 = L15 ∧ KT1 ∧ ¬KM3 ∧ TON(¬KM3, 50 ms) → **KM3 düşmeden KM2 çekmez**; KA9 = ön kapı L2 ∧ arka kapı L2 (paralel köprü yok); S210A bobini = DO7.05 ∧ KA9 ∧ KA_ES; KM4/KM5 uç limitler ve QM2 bobin yolunda, karşılıklı kilitli.
- **PLC katmanı:** KA2 izni (E-stop, seviye, emiş, FR1, Y-Δ hata), kapı limit1/limit2 çeşitli izleme (500 ms), KA9 geri bildirim uyumsuzluğu (300 ms), Y-Δ hata (KM2∧KM3 veya yıldızda >10 s), kapama/açma/itici/enjeksiyon izinleri, kalıp yüksekliği izni (mafsal kuvvet altında kilitliyken yasak), sayaç hatası.
- **Akümülatör deşarjı (S121):** istek = E-stop ∨ LOTO ∨ motor durdu (parametre) ∨ operatör ∨ yağ seviye alarmı. Aktifken enjeksiyon yasak, NL buzzer + alarm lambası + HMI ikazı. **Karar K-EL-01: ENERJİSİZ = BOŞALT** (P.S121_ENERJILI_DESARJ = 0, fail-safe): E-stop → KA_ES S24V'yi keser → S121 düşer → akümülatör boşalır; şebeke kesintisinde de aynı. Normal çalışmada PLC S121'i enerjili tutar. P = 1 (DCC630 yorumu) yalnız karşılaştırma için modelde kalır. Saha doğrulaması bölüm 9-10.
- **LOTO (Kademe 7, kural 10):** doğrulama: adım 1, 2, 3, 4, 5, 9 → `S.LOTO_A<n>_OK` (plc); 6, 7, 8 elle (`elle_dogrulama: true`). 1 manuel mod, piston/itici geri · 2 kalıbı aç (kilitli mafsalda kolonlarda 4000 kN elastik enerji) · 3 pompa dur · 4 S121 + elle DV1 aç, PT2 < 2 bar 10 s + manometre · 5 PT1/çarpan < 2 bar · 6 ana şalter kilit + etiket · 7 enerji yokluğu ölçümü, U1 için ≥1 dk; UPS/PC577 ve CZ1 prizi ayrı beslemeli olabilir · 8 KA9/limit köprüleme yasak, sıcak yüzey · 9 ters sıra ile devreye alma.

## 6. Teşhis tohumu (veri: elektrik.json → teshis_tohumu)
Her satırın ilk adımı: **GÜVENLİK ÖN ADIMI = LOTO 1–7** (kalıp açık, motor durdu, akümülatör deşarj ve PT2 < 2 bar doğrulandı, ana şalter kilitli, enerji yokluğu ölçüldü). Canlı ölçüm gerekiyorsa yalnız yetkili, kapılar kapalı, E-stop erişilebilir.

| Belirti | Kanal / tag → sebep | Bağlı ID |
|---|---|---|
| Kalıp kapanmıyor | DI5.01/DI5.03 + DI9.04 KA9 · S.KAPI_UYUMSUZ · DI9.10 itici geride değil · DO7.05 S210A var, bobinde yok → KA9 kontağı · DI5.09 motor · kalıp yüksekliği ayarı açık · U12 komutu · S211 kilidi | A71, A41, A35, A62, A95 |
| Pompa kalkmıyor | DI5.12 E-stop (ST1-1…ST4-1) · DO7.31 KA2 izni (DI5.13 seviye, DI5.21 emiş, DI5.11 FR1, Y-Δ hata) · FR1 (33 A) · TC1/FU11/QF11 · 1B12A/1B11A1 · KM1 bobini | A72, A61, A62 |
| Motor yıldızda kalıyor / geçişte atıyor | DI9.05/06 KM3 yapışık · KT1 · S.YD_HATA · FR1 geçiş darbesi | A62, A72 |
| Enjeksiyon hareket etmiyor | S.ENJ_IZIN (DI5.08, kapılar, motor, PT2 ≥ 126 bar, S121 isteği, vuruş konumu girilmedi) · DO7.25/DO7.01 S113 → U16 + DB68.A09 · FU12/KA_ES valf beslemesi · basınç var hareket yok → A51/A52 sıkışma · U18 | A54, A56, A51, A52 |
| İtici çalışmıyor | DO7.13/14 S301/S302 (tek valf iki silindir) · AI10.1 açıklık · DI9.10/11 limit · pompa · tek silindir sıkışık → köprü eğilmesi | A41, A42, A83, A22 |
| Kalıp yüksekliği ayarı çalışmıyor | DI4.08 + DI4.14 1B13 + DI9.07/08 jog · DI9.03 QM2 (2,7 A) · DI5.05/06 uç limit (200/750) · S.KY_IZIN · KM4/KM5 · S.KY_SAYAC_HATA: motor dönüyor sayaç yok → A97; sayaç var hareket yok → A94/A93/A91 | A95, A97, A94, A93, A91, A26 |
| Akümülatör basınç alarmı | DB68.PT2 vs manometre · S121/DV1 kaçırma · S180 (ACV1 adayı) · PT1/U12 pompa · azot ön dolum kaybı (yetkili) · RV2 | A56, A62 |
| Yağ seviyesi alarmı | DI5.13 (bulanık okunan kanal) · gözle seviye · keçe/hortum kaçağı (vuruş konumu değişiminde hortum payı) · sıcaklık | A61, A35, A41, A54 |

## 7. Açık noktalar
1. **HW Config adres eşlemesi:** şema klemens notasyonu (I10…I115) Siemens bayt.bit'e bağlanmadı; DI32 ve DO32 klemensleri boş.
2. **DI5 kanal sırası** okuma sırasıdır, doğrulanmadı; DI5.24–32 okunamadı (itici limitleri muhtemelen burada; şimdilik DI9.10/11'de).
3. **DO7.17–30 (KAPANDI, ikiz kararı):** DO7.23/24 core4 → kapsam dışı (core1-3 gibi). DO7.25/26 etiketleri Y1_YAVAS/Y1_GERI kalıcı kabul. KA9 paralel kontaklar = kapı kilit/extractor bypass kabul, modellenmez.
4. ~~S121 polaritesi ve KA_ES~~ → karar K-EL-01 (enerjisiz = boşalt + KA_ES); saha doğrulaması bölüm 10.
5. KA9 limit-2 kontaklarına paralel bulanık kontaklar (DCC630) — köprü mü, robot bypass'ı mı?
6. 1B10 "displacement lock" / S601 "displacement flat" işlevi belirsiz → ayrılmış.
7. S180 ↔ ACV1 eşlemesi düşük güven; S120 birleştirme valfinin tek pompalı 400 t'de karşılığı teyit edilmeli.
8. FU10 4 A (bu oturum) vs 1 A (önceki okuma) — elle/etiketten teyit.
9. M1 etiket akımı, U1/PS307 gerçek modeli ve PF'si, solenoid güçleri → TC1/U1 sonuçları ölçümle değişebilir.
10. Arka koruma kapısı ve E-stop ST3-1 ağaçta yok (A71'e bağlandı).
11. Enjeksiyon konum enkoderi ikizde ayrılmış; faz geçişleri süre parametresiyle (gerçek makinede konum tabanlı).

## 8. KARARLAR için önerilen satır
| 2026-11-18 | Elektrik katmanı fonksiyon düzeyinde uyarlandı: DCC630 şablon, 400 t'ye göre yeniden boyutlandırıldı; tek kaynak params/elektrik.json (131 kanal kaydı, köken/güven/durum alanlı). Kalıp yüksekliği valf değil KM4/KM5 + A97 enkoder; kolon çekme ve maça kapsam dışı; FR1 faz yolu (30 kW tasarımında 28–40 A / 33 A; 55 kW güncellemesi 2026-11-19: 45–63 A / 58,6 A); TC1 için U1 ayrı besleme (seçenek A); S121 enerjisiz = boşalt + KA_ES; S.AKU_BOS katı PT2 < 2 bar; kullanıcı bekleyen kararları devretti → hepsi `400t_hesap` / `claude_karari_saha_dogrulamasi_gerekir` (elektrik.json → kararlar[]) | Gerçek 400 t şeması yok; teşhis kademeleri için çalışan elektrik katmanı gerekli. Hesap: docs/elektrik_400t.md, out/elektrik_400t_hesap.txt |

## 9. Claude kararı, saha ölçümü gerekir (2026-11-18)
Kullanıcı bekleyen tüm kararları devretti ("doğru olanı yap"). Aşağıdakiler `koken: 400t_hesap`, `durum: claude_karari_saha_dogrulamasi_gerekir` (elektrik.json → `kararlar[]`, ilgili kayıtlarda `karar` alanı). Saha ölçümü/etiket gelince değişir.

| Kalem | Karar / varsayım | Sahada ne ölçülecek |
|---|---|---|
| K-EL-01 S121 polaritesi | enerjisiz = boşalt (P.S121_ENERJILI_DESARJ = 0) + KA_ES (E-stop → S24V kesilir) | S121 valf tipi ve etiketi; deşarj orifisi ve boşalma süresi (PT2 < 2 bar); **E-stop'ta kontrolsüz silindir hareketi**: KA_ES oransal kart beslemesini de kestiğinden U16/S424 servo valfin enerjisiz sürgü konumu, S113 kapanma süresi; akümülatör boşalırken enjeksiyon silindirine yol açılıyor mu; A35 pilot çek valfi (mafsal ara konumda) |
| K-EL-03 TC1 / U1 | seçenek A: U1 ayrı L-N + 6 A MCB; TC1 630 VA, yük 425 VA (oran 0,67; kalkış 785 VA SINIRDA) | U1 ve TC1 sekonder akımı pensle (motor kalkışı + tüm valfler) |
| 24 V bütçesi | 5 × 35 W solenoid, oransal kartlar 8,1 A, lojik 2,15 A → 17,5 A / 20,8 A (%84); FU12 2 × 10 A kola bölünür | valf etiket güçleri, U1 çıkış akımı |
| Güç faktörü | U1 S-500-24 PFC'siz PF 0,65; motor cosφ 0,88 (ikiz_tasarim varsayımı) / A95 0,76 | U1 etiketi; M1 etiket akımı (In 101,5 A hesap) |
| FR1 | faz yolunda 45–63 A, ayar 58,6 A (SINIRDA) | M1 etiket akımı; FR1 konumu (şema 9-1) |
| KT1 / ölü zaman | yıldız 8 s, Y→Δ 50 ms | pompa yüksüz kalkış süresi (akım düşüşü) |
| Kablo katsayıları | ortam 40 °C (0,87) × gruplama 0,80 → 35 mm² (SINIRDA) | pano içi sıcaklık |
| Eşikler | PT2 enj. min 126 / yüksek 150 / deşarj tamam < 2 bar 10 s (K-EL-05, **katı lt**); PT1 düşük 112; yağ 55/65 °C; LOTO: AI10.1 > 20 mm, PT1 < 2, PCARP < 2 bar | işletme basınçları, PT2 sıfır kayması < 0,5 bar |
| K-EL-06d FKAP eşiği | S.KILITLI_KUVVET_ALTINDA = DI5.08 ∧ (sensör yok ∨ FKAP > 50 kN); P.KAPAMA_KUVVET_SENSORU_VAR = 0 | DI5.08 mafsal kilidini mi kalıp temasını mı gösteriyor; sensör varsa sıfır kayması ≤ %1 FS |
| Çevrim süreleri | FAZ1 800 / FAZ2 60 / FAZ3 3000 ms; piston geri 2500 ms; mafsal yağlama 5000 ms her 10 çevrimde; itici açıklık min 300 mm; S118 1500 ms | gerçek çevrim kaydı |

**FKAP eşiği hesabı:** 5 kN/somun eksenel yükte motor momenti 2,64 Nm (params die_height_drive.torque_note, doğrusal kabul) → A95 nominal 7,24 Nm ile 13,7 kN/somun × 4 = 54,8 kN. Kilitli mafsalda kolon başına ~1000 kN → ayar fiziksel olarak imkânsız, denenirse QM2 atar / dişli zorlanır. Kuvvet sensörü isteğe bağlı olduğundan **varsayılan kural: kalıp kapalıyken (DI5.08) kalıp yüksekliği ayarı YASAK**; sensör varsa ve FKAP ≤ 50 kN (nominal momentin %91'i) ise izin verilir.

**Diğer kararlar (mekanik, docs/olcu_notlari.md):** kazara yatay yük katsayısı c = 0,2 esas; A58 kaldırılması kesinleşti (kullanıcı fotoğrafından 3 kolon onayı).

## 10. lib/elektrik_mantik.py için yeni JSON alanları ve açık riskler
| lib sabiti | JSON yolu / anahtar |
|---|---|
| NO_HW_GIRIS | `mantik.hw_girisler[]` {`id`, `tip` NC/NO, `saglam_deger`} → `saglam_deger == 0` olanlar (yalnız HW.1B11A1) |
| SAGLAM_DI | `kanallar[].saglam_deger == 1` (DI5.02, DI5.04, DI5.07, DI5.10, DI5.13, DI5.21, DI9.10); alan yoksa 0 |
| GERI_BILDIRIM | `mantik.donanim[].izleme` {HW: DI} (eklenen: HW.ESTOP_OK→DI5.12, HW.KM1→DI5.09, HW.KM3→DI9.05, HW.KM2→DI9.06, HW.KA_ES→DI9.15) + `mantik.donanim[HW.L15].izleme_ters` {HW.FR1_NC: DI5.11} (DI = not HW) |
| RESET | `muhur: true` tanımlarda `reset` = "HMI.RESET" |
| S.KILITLI_KUVVET_ALTINDA (sabit kod) | `mantik.plc[S.KILITLI_KUVVET_ALTINDA].ifade`; `P.KAPAMA_KUVVET_SENSORU_VAR`; `esikler.FKAP_kilitli_esik_kN` |
| _sirala() | `mantik.siralayici`: `baslatma.kosul` (HMI.OTO_BASLAT), `genel_iptal`, `adimlar[]` {`ad`, `cikis`, `bitis`, `sonraki`, `iptal`, `alt_fazlar`}, `piston_geri` (P.PISTON_GERI_SURE_ms, ACMA bitişinde başlar), `piston_yaglama`, `mafsal_yaglama` (P.MAFSAL_YAGLAMA_SURE_ms, zamanlar.yaglama_aralik_cevrim), `a97_sayac` (`yon_kurali` {B_0: +1, B_1: -1}, `baslangic_mm`, `referans[]`) |
| loto_adim_dogrula(no) | `loto.adimlar[].dogrulama_sinyal` (S.LOTO_A1/2/3/4/5/9_OK, plc'de), `elle_dogrulama`, `elle_not` |

Lib davranışından bilinçli farklar (lib güncellenince testler gözden geçirilmeli): piston geri ACMA boyunca değil ACMA bitişinden itibaren süreli; yeni çevrim piston geri bitmeden başlamaz; mafsal yağlama süreli (eski: sonraki ENJ'ye kadar); A97 sayaç başlangıcı die_height_current (eski: die_height_min); FKAP varken eşik 50 kN (eski: > 0).

Açık riskler:
1. **E-stop'ta kontrolsüz silindir hareketi** (K-EL-01): servo valf enerjisiz konumu ve deşarj yolu doğrulanmadan fail-safe varsayımı tam değildir.
2. **A97 darbe kaçırma (KARAR K-EL-07, 2026-11-19: redüktör çıkışı, 25 ppr; A97 konum/ppr için olcu-mimari'ye OLCU_TALEBI):** 1450/60 × 2 = 48,3 Hz, darbe genişliği ~10,3 ms; S7-300 standart DI (giriş gecikmesi 3 ms) + tarama 10–30 ms ile kenar kaçabilir → hızlı sayıcı girişi veya enkoderi redüktör çıkışına almak (41,4 d/dk, 2,50 mm/devir; 25 ppr → 0,1 mm, 17 Hz). Mekanik/BOM kararı, açık.
3. Otomatik çevrim başlatmada aktif alarm (ör. AL_YAGLAMA "N çevrim sonra yasak") kontrol edilmiyor; sayaçlı yasak tanımı yok.
4. params die_height_drive notu: kalıp yüksekliği ayarı kalıp SÖKÜLÜ iken (dh < 400'de kalıplar çarpışır) — elektrik izni bunu bilmiyor (kalıp takılı bilgisi yok).
5. DI5.08'in anlamı (mafsal kilitli mi, kalıp teması mı) doğrulanmadı; K-EL-06d buna dayanıyor.

## Enjeksiyon konum sensoru (A66) - guncelleme
- DB68.ENC artik `aktif`, bagli_id A54/A52/A66. Faz gecisleri ikizde hala sure tabanli; gercek makine dogrulamasi gerekir.
- DB68.PENJ_G / PENJ_C -> A67; DB68.A09, U16, hidrolik_esleme Y1 -> A65 eklendi.
- VERI_BEKLIYOR: A66 sensor tipi/cozunurluk/sinyal tipi; LS2 (DI1.02) elektrik.json'da kanal kaydi yok (yalniz hidrolik.json'da); S424 icin ayri kayit yok.

## Yeni geometri parcalari: elektrik baglantilari (ikiz_tasarim, saha verisi yok)
| Kanal / kayit | Yon | Durum | bagli_id | Not |
|---|---|---|---|---|
| DI5.01, DI5.02 (kapi KAPALI limit 2/1, KA9 zinciri) | DI | aktif (mevcut) | + A127 | kilitli guvenlik anahtari kapali konum kontagi |
| DI5.22 (on kapi ACIK limiti) | DI | aktif (mevcut) | + A127 | guvenlik anahtari acik konum kontagi |
| DO4.13 / DO4.14 (motorlu kapi ac/kapa) | DO | istege_bagli (mevcut) | + A126 | pnomatik kapi silindiri; A71/A124/A125/A128 zaten A71 uzerinden (kapi grubu) |
| Y2 kapama / Y3 itici (hidrolik_esleme) | - | mevcut | + A133, A130, A132 | bom'da A133/A132 qty 2 (A133_1/_2 ayri id degil, KURAL_ELEK_BAGLI yalniz bom id kabul eder); bobin ayrimi Y2 = S210A/S211, Y3 = S301/S302 |
| DO7.06 (S605 piston yaglama) | DO | aktif (mevcut) | + A143 | plunger yaglama dozaj valfi/pompasi; slot 7'de bos DO YOK, mevcut kanal kullanildi |
| DI5.30 (A143 rezervuar seviye DUSUK, NC: OK=1) | DI | aktif, YENI | A143 | ikiz_tasarim; slot 5 eski "okunamadi/ayrilmis" kanal; slot 9 tam dolu |
| DI5.31 (A142 giris hatti su akis anahtari, akis=1) | DI | aktif, YENI | A142 | ikiz_tasarim; slot 5 eski ayrilmis kanal |
| AI10.4 (TT2 kamara sogutma cikis suyu sicakligi) | AI | istege_bagli, YENI | A142 | ikiz_tasarim; eski yedek analog, 0-100 C |

Sayim guncel (131 kayit): DI 65 (aktif 47, istege_bagli 6, ayrilmis 8, kapsam disi 4) · DO 48 (aktif 23, istege_bagli 16, ayrilmis 1, kapsam disi 8) · AI 9 (aktif 6, istege_bagli 3) · AO 9. Mantik eki yok (yalniz kanal tanimi).
VERI_BEKLIYOR: DI5.30/DI5.31 bayt.bit eslemesi (HW Config), A127 kontak sayisi/KA9 zincirine baglanma sekli.

## Maca (core) adimlari (Kademe 4, adim 1) - VARSAYIM
- Siralayici: BOSTA -> MACA_GIR -> KAPAMA -> ENJ -> MACA_CEK -> ACMA -> ITICI_ILERI -> ITICI_GERI -> BOSTA (lib/cevrim.py faz 3 maca gir, faz 12 maca cek ile ayni sira).
- MACA_GIR yalniz kalip ACIKKEN (S.KALIP_ACIK: DI5.08=0 ve AI10.1>20 mm, itici geride); MACA_CEK yalniz kalip KAPALI ve S.FAZ3_BITTI iken.
- Cikislar: core1..4 in = DO7.17/19/21/23, out = DO7.18/20/22/24 (PLC ifadesi + HW.MACAn_GIR/CEK_BOBIN: valf beslemesine VE karsi cikis kilidi).
- VARSAYIM secici: DI5.14..17 = n. maca otomatik cevrimde kullanilsin (1) / atlansin (0). Hic secili yoksa adimlar ayni taramada gecilir. VERI_BEKLIYOR: gercek secici anlami.
- Geri bildirim yok: sure tabanli P.MACA_SURE_ms = 2000 ms (VARSAYIM, A167 80 mm). Zaman asimi = sure x 2 -> S.MACA_ALARM (muhurlu, HMI.RESET) + BOSTA; AL_MACA_ZAMAN_ASIMI.
- Oneri (kanal eklenmedi): maca basina ileri/geri limit sensoru (koken yeni).
- Acik: cevrim.py faz 10-11 (katilasma, plunger geri) maca cekmeden once; PLC'de katilasma suresi yok, piston geri ACMA bitisinden (karar). Maca manuel (DI4.08) jog yok.
