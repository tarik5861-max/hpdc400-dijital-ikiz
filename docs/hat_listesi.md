# Hat listesi (params/hatlar.json ozeti)

Kaynak: params/hatlar.json (tek dogruluk kaynagi; params.json A160 tools/hat_senkron.py ile uretilir). Referans poz: kalip yuksekligi 400, vurus alt, mafsal kapali. Hepsi ikiz_tasarim varsayimi.
Guvenlik: onarim/teshis oncesi S121 DV1 akumulator desarji + PT2 < 2 bar dogrula + basinc bosaltma + LOTO (CLAUDE.md kural 10). H01c/H10/H21 A59 akumulator blogunda biter; Y4 (H30..H39) A168 uzerinden sistem basinci tasir (H38 P, H01c'den dogrudan; A59 akumulator deşarji H38'i de bosaltir, A168 P portunda manometre ile 0 bar dogrula).

Toplam 44 hat (A160 adedi 44; bom.json qty 42 -> BOM_TALEBI).

| ID | Hat | Kaynak -> Hedef | Tip | Dis/ic mm | Q L/dk | p bar | v m/s | L mm | Hareket | Bukum uyari |
|---|---|---|---|---|---|---|---|---|---|---|
| H01a | P1 ana basinc hatti (a): A122 P1 cikis stub -> CV1 (A172) giris | A122.P1_cikis -> A172.giris_+Y | sert | 48/38 | 191.2 | 140 | 2.81 | 495 | sabit | 1 |
| H01b | P1 ana basinc hatti (b): CV1 (A172) cikis -> PF1 (A173) giris | A172.cikis_-Y -> A173.giris_+X | sert | 48/38 | 191.2 | 140 | 2.81 | 860 | sabit | 0 |
| H01c | P1 ana basinc hatti (c): PF1 (A173) cikis -> P rafi -> A59 akumulator  | A173.cikis_-X -> A59.P_alt | sert | 48/38 | 191.2 | 140 | 2.81 | 6675 | sabit | 1 |
| H02R | P dallanma (sert kisim): ana hat T-tee -> A65 braket | H01c.TEE_PA65 -> BRK.BRK_A65_P | sert | 48/38 | 191.2 | 140 | 2.81 | 340 | sabit | 0 |
| H02H | P dallanma (hortum): braket -> A65 P (hizli-yavas vurus P1 beslemesi); | BRK.BRK_A65_P -> A65.P | hortum | 48/31.8 | 191.2 | 140 | 4.01 | 815 | Z[0, 150] | 0 |
| H03 | P kapama dali (hortum): ana hat T-tee -> A130 P; A130 X kaymasi -200.. | H01c.TEE_PA130 -> A130.P | hortum | 48/31.8 | 191.2 | 140 | 4.01 | 775 | X[-200, 350] | 5 |
| H04 | Kapama A hortumu: A130 A -> A35 kapak tarafi A portu (genislemede 280  | A130.A -> A35.A_kapak | hortum | 48/31.8 | 279.7 | 140 | 5.87 | 355 | sabit | 5 |
| H05 | Kapama B hortumu: A130 B -> A35 on flans arka yuz B portu (A92 tupu ic | A130.B -> A35.B_kol | hortum | 40/25.4 | 191.2 | 140 | 6.29 | 730 | sabit | 3 |
| H06 | Itici A (kapak) hortumu: A130 A2 -> A41 -Y silindir kapak portu; A22 a | A130.A2 -> A41.A_kapak_-Y | hortum | 40/25.4 | 94.2 | 140 | 3.1 | 2170 | X[0, 420] | 1 |
| H07 | Itici B (kol tarafi) hortumu: A130 B2 -> A41 -Y arka kapak B portu (ic | A130.B2 -> A41.B_kapak_-Y | hortum | 32/19.0 | 65.0 | 140 | 3.82 | 2280 | X[0, 420] | 1 |
| H08 | Itici kapak capraz hortumu: A41 -Y kapak alt -> +Y kapak alt (paralel  | A41.A_kapak_alt_-Y -> A41.A_kapak_alt_+Y | hortum | 32/19.0 | 47.1 | 140 | 2.77 | 220 | sabit | 3 |
| H10 | P2 pilot ana hatti: A122_2 ucu -> A59 pilot portu | A122.P2_cikis -> A59.Pi_alt | sert | 25/19 | 23.1 | 140 | 1.36 | 9245 | sabit | 0 |
| H11R | Pilot dali (sert): tee -> A65 braket | H10.TEE_PLA65 -> BRK.BRK_A65_PL | sert | 16/12 | 6.0 | 140 | 0.88 | 405 | sabit | 0 |
| H11H | Pilot dali (hortum): braket -> A65 pilot portu; A65 Z kaymasi 0..150 | BRK.BRK_A65_PL -> A65.Pi | hortum | 21/9.5 | 6.0 | 140 | 1.41 | 795 | Z[0, 150] | 0 |
| H12 | Pilot kapama dali (hortum): tee -> A130 pilot portu; A130 X kaymasi | H10.TEE_PLA130 -> A130.Pi | hortum | 21/9.5 | 6.0 | 140 | 1.41 | 1305 | X[-200, 350] | 3 |
| H21 | T: A59 DV1/RV2 bosaltma portu -> T rafi (A65 tee) | A59.T_alt -> H20.TEE_TA65 | sert | 48/38 | 290.0 | 5 | 4.26 | 2205 | sabit | 0 |
| H20H | T: A65 T portu -> braket (hortum, A65 Z kaymasi 0..150) | A65.T -> BRK.BRK_A65_T | hortum | 70/50.8 | 1625.8 | 5 | 13.37 | 850 | Z[0, 150] | 1 |
| H20R | T: A65 braket -> T rafi -> tank T-tee (ana donus) | BRK.BRK_A65_T -> H24.TEE_T | sert | 89/80.0 | 1625.8 | 5 | 5.39 | 3625 | sabit | 1 |
| H22 | T: A130 T -> braket (hortum; A130 X kaymasi) | A130.T -> BRK.BRK_A130_T | hortum | 48/31.8 | 280.0 | 5 | 5.88 | 1195 | X[-200, 350] | 3 |
| H23 | T: A130 braket -> T rafi -> tank T-tee | BRK.BRK_A130_T -> H24.TEE_T | sert | 89/80.0 | 280.0 | 5 | 0.93 | 1800 | sabit | 1 |
| H24 | T: tank donus portu (A11 -Y duvar gecisi d150 + tank -Y yuz T portu d8 | H20R.TEE_T -> A61.T_donus | sert | 89/80.0 | 1905.8 | 5 | 6.32 | 125 | sabit | 1 |
| H30 | Y4.1 maca B hortumu: A168 B1 -> A167_1 kol (B, maca geri/out) portu | A168.B1 -> A167.B_kol | hortum | 21/9.5 | 8.09 | 140 | 1.9 | 2465 | sabit | 3 |
| H31 | Y4.1 maca A hortumu: A168 A1 -> A167_1 kapak (A, maca ileri/in) portu | A168.A1 -> A167.A_kapak | hortum | 21/9.5 | 11.78 | 140 | 2.77 | 2540 | sabit | 3 |
| H32 | Y4.2 maca B hortumu: A168 B2 -> A167_2 kol (B, maca geri/out) portu | A168.B2 -> A167.B_kol | hortum | 21/9.5 | 8.09 | 140 | 1.9 | 2523 | sabit | 4 |
| H33 | Y4.2 maca A hortumu: A168 A2 -> A167_2 kapak (A, maca ileri/in) portu | A168.A2 -> A167.A_kapak | hortum | 21/9.5 | 11.78 | 140 | 2.77 | 2528 | sabit | 4 |
| H34 | Y4.3 maca B hortumu: A168 B3 -> A167_3 kol (B, maca geri/out) portu | A168.B3 -> A167.B_kol | hortum | 21/9.5 | 8.09 | 140 | 1.9 | 2391 | sabit | 3 |
| H35 | Y4.3 maca A hortumu: A168 A3 -> A167_3 kapak (A, maca ileri/in) portu | A168.A3 -> A167.A_kapak | hortum | 21/9.5 | 11.78 | 140 | 2.77 | 2366 | sabit | 3 |
| H36 | Y4.4 maca B hortumu: A168 B4 -> A167_4 kol (B, maca geri/out) portu | A168.B4 -> A167.B_kol | hortum | 21/9.5 | 8.09 | 140 | 1.9 | 2449 | sabit | 4 |
| H37 | Y4.4 maca A hortumu: A168 A4 -> A167_4 kapak (A, maca ileri/in) portu | A168.A4 -> A167.A_kapak | hortum | 21/9.5 | 11.78 | 140 | 2.77 | 2354 | sabit | 4 |
| H38 | Y4 maca P besleme: H01c P rafi T-tee (X-350) -> A168 ust yuz P portu | H01c.TEE_PA168 -> A168.P | sert | 20/16 | 47.1 | 140 | 3.91 | 1685 | sabit | 1 |
| H39 | Y4 maca T donus: A168 ust yuz T portu -> T rafi T-tee (H20R X-280) | A168.T -> H20R.TEE_TA168 | sert | 25/19 | 47.1 | 5 | 2.77 | 2450 | sabit | 1 |
| H40 | Yaglama besleme: A170 M10 pompa cikisi -> A171 dagitici girisi | A170.cikis -> A171.giris | hortum | 8.0/6.0 | 0.15 | 30.0 | 0.09 | 1965 | sabit | 3 |
| H41 | Yaglama cikisi 1: A171 +Y1 -> A23 nipel -> mafsal pimi A34_AT | A171.cikis_+Y1 -> A23.yag_AT_ust | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 85 | sabit | 0 |
| H42 | Yaglama cikisi 2: A171 +Y2 -> A23 nipel -> mafsal pimi A34_BT1 | A171.cikis_+Y2 -> A23.yag_BT1_ust | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 125 | sabit | 0 |
| H43 | Yaglama cikisi 3: A171 +Y3 -> A23 nipel -> mafsal pimi A34_CT | A171.cikis_+Y3 -> A23.yag_CT_ust | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 165 | sabit | 0 |
| H44 | Yaglama cikisi 4: A171 +Y4 -> A23 nipel -> mafsal pimi A34_AB | A171.cikis_+Y4 -> A23.yag_AB_yan | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 1135 | sabit | 1 |
| H45 | Yaglama cikisi 5: A171 +Y5 -> A23 nipel -> mafsal pimi A34_BB1 | A171.cikis_+Y5 -> A23.yag_BB1_yan | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 1135 | sabit | 1 |
| H46 | Yaglama cikisi 6: A171 +Y6 -> A23 nipel -> mafsal pimi A34_CB | A171.cikis_+Y6 -> A23.yag_CB_yan | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 1135 | sabit | 1 |
| H47 | Yaglama cikisi 7: A171 -Y1 -> A23 nipel -> mafsal pimi A34_ET | A171.cikis_-Y1 -> A23.yag_ET_ust | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 85 | sabit | 0 |
| H48 | Yaglama cikisi 8: A171 -Y2 -> A23 nipel -> mafsal pimi A34_BT2 | A171.cikis_-Y2 -> A23.yag_BT2_ust | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 125 | sabit | 0 |
| H49 | Yaglama cikisi 9: A171 -Y3 -> A23 nipel -> mafsal pimi A34_DT | A171.cikis_-Y3 -> A23.yag_DT_ust | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 165 | sabit | 0 |
| H50 | Yaglama cikisi 10: A171 -Y4 -> A23 nipel -> mafsal pimi A34_EB | A171.cikis_-Y4 -> A23.yag_EB_yan | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 1135 | sabit | 1 |
| H51 | Yaglama cikisi 11: A171 -Y5 -> A23 nipel -> mafsal pimi A34_BB2 | A171.cikis_-Y5 -> A23.yag_BB2_yan | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 1135 | sabit | 1 |
| H52 | Yaglama cikisi 12: A171 -Y6 -> A23 nipel -> mafsal pimi A34_DB | A171.cikis_-Y6 -> A23.yag_DB_yan | hortum | 6.0/4.0 | 0.0125 | 30.0 | 0.02 | 1135 | sabit | 1 |

## Guzergah ozeti
- P1 ana hat 3 parca: H01a A122 P1 stub (2960,485,-400) -> Z-330 -> CV1 A172 +Y yuzu (Y60); H01b CV1 -Y yuzu (Y-60) -> P rafi Y-540 -> PF1 A173 +X yuzu (X2580); H01c PF1 -X yuzu (X2420) -> X2385 dikey (TEE_PA130 Z-380, H03 dali) -> P rafi Y-540 Z-640 (TEE_PA65 X-1990, H02R dali) -> X-2800 -> A59 P_alt (-2945,0,-180).
- Pilot H10 A122_2 -> pilot rafi Y-585 Z-705 -> A59 Pi; dallar H11R/H11H (A65), H12 (A130).
- T: H21 A59 T -> T rafi; H20H/H20R A65 T -> T rafi Y-595 Z-800 -> TEE_T; H22/H23 A130 T -> TEE_T; H24 TEE_T -> A61 T donus portu (1000,-470,-800).
- Kapama/itici: H04/H05 A130 -> A35; H06/H07 A130 A2/B2 -> A41 (-Y serit Y-495/-545); H08 A41 capraz.
- Y4 maca (H30..H37, DN10): A168 -X yuzu (X-400, A Y165 / B Y215, Z valf 36/98/160/222) -> ic ice L dusus X-490..-595 -> A21 ustu Z520..730 katmanli -> X-110 Y kosusu -> Y+-478 serit (kolon Y410 ile kapi Y500 arasi) -> A167 port stub'lari (Y+-315 B, Y+-420 A). A22 min kalip yuksekliginde X200: hatlar X<=146.
- Y4 maca P/T (H38/H39, sert boru; A168 sabit plaka arka yuzu, goreli hareket yok): H38 H01c TEE_PA168 (-350,-540,-640) -> Y-540 dikey (sase duvari ile A165 kapi izi arasi) -> Z290 +Y (A13_3 cubugu alti, A25_3 somunu -X tarafi) -> A168 P (-350,190,265). H39 A168 T (-280,190,265) -> Z470 -Y -> Y-200'de Z500 (A25_3 ustu) -> Y-540 dikey -> Z-595 kapi izi alti -> Y-660 yukseltici -> TEE_TA168 (-280,-595,-800) H20R. H30..H37 Z520..730 katmanina girmez.
- Yaglama: H40 A170 cikis (+X salter blogu) -> Z600 -> A171 -X girisi; H41..H52 (PA12 6x1) A171 +-Y cikislari -> A23 nipelleri: ust yuz Z490 (AT/BT1/CT/ET/BT2/DT), yan yuz Y+-460 Z-150 (AB/BB1/CB/EB/BB2/DB); nipeller A23.dims.yaglama_nipelleri (2026-11-20), pime A23 ic kanallari cizilmez (VARSAYIM). Hepsi A23 ile kalip yuksekliginde kayar.

## Kontrol
- check.py hat-parca cakismasi 0; hat-hat mesafe taramasi (kapsul, <5 mm): yalniz tee/braket/fitting birlesimleri (H01c-H02R/H03, H10-H11R/H12, H20R-H21/H23/H24, H02R-H02H, H11R-H11H, H20H-H20R, H22-H23).
- motion_check (mafsal s 0..1, kalip yuk. 200..750) ve itici_tarama: hortum carpismasi 0.

## Riskli yerler
- RISK: A41 hortumlari mafsal kollarina en yakin s~0.75 (X_rel 1015 penceresi |z|<75; H06 z-30 r20, H07 z+30 r16 -> ~25 mm); H08 A36 kollarina 20 mm (s=1)
- RISK-YUKSEK: A65 T hizli vurus donusu 1625 L/dk: H20H DN51 13 m/s, H20R 5.4 m/s
- RISK: A130 hortumlari 550 mm kayar (kalip yuksekligi): sabit uclar hareketli blok bolgesi disinda (TEE_PA130 X2385, TEE_PLA130 X2700, BRK_A130_T Y-660); H12 serit A120 motor ustune 9.5 mm, H03 serit PF1 kasesine 11 mm
- RISK: A41 hortumlari her cevrimde 420 mm gidip gelir (yorulma/ome)
- RISK: H38 A13_3 cubugu / A25_3 somunu 10 mm; H39 A13_3 flansi 7,5 mm, H01c 8,5 mm, A25_3 12,5 mm
- RISK: T rafi A72 panosuna 12 mm, P rafi sase duvarina 16 mm bosluk
- RISK: tum rijit/hortum kisa bacaklar (<2Rb) bukum uyarisi: dirsek fitting ile (hat.kontrol.bukum_uyari)

## OLCU_TALEBI (acik ve COZULDU)
- COZULDU 2026-11-20 (A130.dims.ports.ek_portlar): OLCU_TALEBI: A130 Y3 icin ek portlar A2/B2 (-Y yuz X2210, Z-230/-175, d30 stub 30) ve pilot portu Pi (+X yuz 2250,0,-260 d12); bloktaki 4 port yalniz P/T/A/B
- COZULDU 2026-11-20 (A35.dims.ports): OLCU_TALEBI: A35 baglanti portlari: A_kapak (alt, 2265,0,-100) ve B_kol (on flans arka yuz, 1845,150,-80) dims.ports yalniz d30 optional
- COZULDU 2026-11-20 (A41.dims.ports): OLCU_TALEBI: A41 port tanimi: -Y arka kapak yan portlari A (1015,-120,-30) ve B (1015,-120,+30, kol odasina cift cidarli ic boru), alt kapak capraz portlari (1010,+-62.5,-57.5); eski X822 kopru portu mafsal zarfinda kaldigi icin iptal
- COZULDU 2026-11-20 (A65.dims.ports): OLCU_TALEBI: A65 -Y yuz port tanimi: P (-1990,-150,125), T (-2060,-150,40), Pi (-1945,-150,60)
- COZULDU 2026-11-20 (A59.dims.ports): OLCU_TALEBI: A59 valf blogu alt portlari P(-2945,0,-180), Pi(-3000,0,-180), T(-3055,0,-180) + sepet plakasi 3 delik d60 (Z-220..-180)
- COZULDU 2026-11-20 (A61.dims.return_port + A11.pipe_passages): OLCU_TALEBI: A61 -Y yuz tank T donus portu (1000,-470,-800) + A11 -Y yan duvar gecisi d95 (X1000,Z-800) + A11.pipe_passages girdisi
- COZULDU 2026-11-20 (A175 hat rafi konsolu x6, A176 A65 braketi, A177 A130 T braketi agacta): OLCU_TALEBI: hat rafi konsollari (sase -Y yan duvari, Y-540/-585/-595, Z-640/-705/-800), BRK_* hortum braketleri; bom.json ID yok
- COZULDU 2026-11-20 (A172/A173 agacta, H01 -> H01a/b/c bolundu): OLCU_TALEBI: CV1 cek valf ve PF1 basinc filtresi govdesi bom.json de yok (ID uydurulmadi)
- COZULDU 2026-11-21: A54 kol tarafi (B, +X on yuz d76) ve A55 PA (ust, d50) portlari A65'e A183 sert borulariyla baglandi: H60 88,9x5 (1625,8 L/dk, 5,54 m/s, L~1030), H61 60,3x5,6 (578 L/dk, 5,09 m/s, L~330). A160 disinda (vurusla birlikte kayar); kayit hatlar.json `hatlar_a183`. Kalan: A54 ic kanal cizilmez, flans temsili (SAE kod 61 3in daha buyuk), A65 ic valf/kanal B/PA tanimsiz (hidrolik-muhendisi), 210 bar tepe varsayim.
- OLCU_TALEBI: A168 port tanimi (A1..A4 / B1..B4 -X yuzu X-400 Y165/Y215 Z36/98/160/222 VARSAYIM) + P/T besleme portlari; A168.dims.ports 'modellenmez'
- OLCU_TALEBI: A170 yaglama pompasi cikis portu (VARSAYIM +X salter blogu 2105,455,-210 d8)
- OLCU_TALEBI: A23 yaglama nipelleri (12): ust yuz Z490 X1675/1695/1715 Y+-110/150/190; yan yuz Y+-460 Z-150 X1735/1755/1775; pime ic kanallar
- OLCU_TALEBI: A172/A173 dims.ports (giris/cikis) alani; simdilik yuzler len/head_len'den (CV1 Y+-60, PF1 X+-80)

## SAHA_DOGRULAMA
- Hortum min bukulme yaricaplari ve dis caplar (DN10..DN51) katalogdan
- Itici hizi 100 mm/s (VARSAYIM) -> A41 hat debileri 94/65 L/dk
- DV1 acil desarj debisi 290 L/dk (VARSAYIM) ve T hat boyutu
- Kelepce araliklari (ISO tipik tablo) uretici/ISO 4413 ile
- A65 kol tarafi donus debisi ~1626 L/dk icin dönüs devresi (regeneratif/yuksek debili T) karari
- Maca silindiri hizi 100 mm/s (VARSAYIM) -> Y4 A 11.78 / B 8.09 L/dk; NG6 valf ve maca kalip-bagimli
- Yaglama: M10 debi 0.15 L/dk @ 30 bar, PA12 6x1/8x1 tup, 12 nokta pim eslemesi ve A23 ic kanallari (VARSAYIM)
