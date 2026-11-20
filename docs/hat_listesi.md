# Hat listesi (params/hatlar.json ozeti)

Kaynak: params/hatlar.json (tek dogruluk kaynagi). Referans poz: kalip yuksekligi 400, vurus alt, mafsal kapali. Hepsi ikiz_tasarim varsayimi.
Guvenlik: onarim/teshis oncesi S121 DV1 desarj + PT2 < 2 bar dogrula + LOTO (CLAUDE.md kural 10). H01/H10/H21 A59 akumulator blogunda biter.

| ID | Hat | Tip | Dis/ic mm | Q L/dk | v m/s | L mm | Hareket | Uyari |
|---|---|---|---|---|---|---|---|---|
| H01 | P1 ana basinc hatti: A98 cikis stub -> A59 akumulator blogu P (CV1 + P | sert | 48/38 | 191.2 | 2.81 | 8310 | sabit | 1 |
| H02R | P dallanma (sert kisim): ana hat T-tee -> A65 braket | sert | 48/38 | 191.2 | 2.81 | 340 | sabit |  |
| H02H | P dallanma (hortum): braket -> A65 P (hizli-yavas vurus P1 beslemesi); | hortum | 48/31.8 | 191.2 | 4.01 | 1675 | Z[0, 150] |  |
| H03 | P kapama dali (hortum): ana hat T-tee -> A130 P; A130 X kaymasi -200.. | hortum | 48/31.8 | 191.2 | 4.01 | 1995 | X[-200, 350] | 2 |
| H04 | Kapama A hortumu: A130 A -> A35 kapak tarafi A portu (genislemede 280  | hortum | 48/31.8 | 279.7 | 5.87 | 355 | X[0, 0] | 5 |
| H05 | Kapama B hortumu: A130 B -> A35 on flans arka yuz B portu (A92 tupu ic | hortum | 40/25.4 | 191.2 | 6.29 | 755 | X[0, 0] | 3 |
| H06 | Itici A (kapak) hortumu: A130 A2 -> A41 -Y silindir kapak portu; A22 a | hortum | 40/25.4 | 94.2 | 3.1 | 3068 | X[0, 420] | 1 |
| H07 | Itici B (kol tarafi) hortumu: A130 B2 -> A41 on flans galerisi (iki si | hortum | 32/19.0 | 65.0 | 3.82 | 3191 | X[0, 420] |  |
| H08 | Itici kapak capraz hortumu: A41 -Y kapak -> +Y kapak (paralel silindir | hortum | 32/19.0 | 47.1 | 2.77 | 580 | X[0, 0] | 4 RISK |
| H10 | P2 pilot ana hatti: A122_2 ucu -> A59 pilot portu | sert | 25/19 | 23.1 | 1.36 | 9245 | sabit |  |
| H11R | Pilot dali (sert): tee -> A65 braket | sert | 16/12 | 6.0 | 0.88 | 405 | sabit |  |
| H11H | Pilot dali (hortum): braket -> A65 pilot portu; A65 Z kaymasi 0..150 | hortum | 21/9.5 | 6.0 | 1.41 | 1153 | Z[0, 150] |  |
| H12 | Pilot kapama dali (hortum): tee -> A130 pilot portu; A130 X kaymasi | hortum | 21/9.5 | 6.0 | 1.41 | 1593 | X[-200, 350] | 1 |
| H21 | T: A59 DV1/RV2 bosaltma portu -> T rafi (A65 tee) | sert | 48/38 | 290.0 | 4.26 | 2210 | sabit |  |
| H20H | T: A65 T portu -> braket (hortum, A65 Z kaymasi 0..150) | hortum | 70/50.8 | 1625.8 | 13.37 | 2339 | Z[0, 150] | 1 RISK |
| H20R | T: A65 braket -> T rafi -> tank T-tee (ana donus) | sert | 89/80.0 | 1625.8 | 5.39 | 3625 | sabit | 1 |
| H22 | T: A130 T -> braket (hortum; A130 X kaymasi) | hortum | 48/31.8 | 280.0 | 5.88 | 2035 | X[-200, 350] | 2 |
| H23 | T: A130 braket -> T rafi -> tank T-tee | sert | 89/80.0 | 280.0 | 0.93 | 1800 | sabit | 1 |
| H24 | T: tank donus portu (A11 -Y duvar gecisi + tank -Y yuz T portu, filtre | sert | 89/80.0 | 1905.8 | 6.32 | 125 | sabit | 1 |

## Riskli yerler
- RISK-YUKSEK: A41 kapak caprazi (H08) ve H06 hortum ucu acik konumda A31 crosshead yuzune 13 mm (motion_check ile dogrula)
- RISK-YUKSEK: A65 T hizli vurus donusu 1625 L/dk: H20H DN51 13 m/s, H20R 5.4 m/s
- RISK: A130 hortumlari 550 mm kayar (kalip yuksekligi): DN32 Rb 250 U-halka sase -Y yan bosluguna sigmali
- RISK: A41 hortumlari her cevrimde 420 mm gidip gelir (yorulma/ome)
- RISK: T rafi A72 panosuna 12 mm, P rafi sase duvarina 16 mm bosluk
- RISK: tum rijit/hortum kisa bacaklar (<2Rb) bukum uyarisi: dirsek fitting ile (hat.kontrol.bukum_uyari)

## OLCU_TALEBI
- OLCU_TALEBI: A130 Y3 icin ek portlar A2/B2 (-Y yuz X2200, Z-225/-295, d30 stub 30) ve pilot portu Pi (+X yuz merkez 2250,0,-260 d12); bloktaki 4 port yalniz P/T/A/B
- OLCU_TALEBI: A35 baglanti portlari: A_kapak (alt, 2265,0,-100) ve B_kol (on flans arka yuz, 1845,150,-80) dims.ports yalniz d30 optional
- OLCU_TALEBI: A41 port tanimi: kapak yan portlari (1015,+-120,0) ve ortak flans galeri portu (822,-120,0)
- OLCU_TALEBI: A65 -Y yuz port tanimi: P (-1990,-150,125), T (-2060,-150,40), Pi (-1945,-150,60)
- OLCU_TALEBI: A59 valf blogu alt portlari P(-2945,0,-180), Pi(-3000,0,-180), T(-3055,0,-180) + sepet plakasi 3 delik d60 (Z-220..-180)
- OLCU_TALEBI: A61 -Y yuz tank T donus portu (1000,-470,-800) + A11 -Y yan duvar gecisi d95 (X1000,Z-800) + A11.pipe_passages girdisi
- OLCU_TALEBI: hat rafi konsollari (sase -Y yan duvari, Y-540/-585/-595, Z-640/-705/-800), BRK_* hortum braketleri; bom.json ID yok
- OLCU_TALEBI: CV1 cek valf ve PF1 basinc filtresi govdesi bom.json de yok (ID uydurulmadi)
- OLCU_TALEBI: A54-A65 arasi dogrudan flansli varsayildi (hat yok); A54 kol tarafi portu ve A55 baglanti portu params de yok

## SAHA_DOGRULAMA
- Hortum min bukulme yaricaplari ve dis caplar (DN10..DN51) katalogdan
- Itici hizi 100 mm/s (VARSAYIM) -> A41 hat debileri 94/65 L/dk
- DV1 acil desarj debisi 290 L/dk (VARSAYIM) ve T hat boyutu
- Kelepce araliklari (ISO tipik tablo) uretici/ISO 4413 ile
- A65 kol tarafi donus debisi ~1626 L/dk icin dönüs devresi (regeneratif/yuksek debili T) karari
