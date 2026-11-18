# Ölçü notları (olcu-mimari / Fable)

Tasarım esası: 400 t horizontal cold-chamber HPDC machine, 5-point double toggle; Buhler H-400D as primary baseline (platens, tie bars, die height, ejector, injection force), Idra OLCS 400 / HPM II-400 for platen thicknesses, mass and motor. Simplified-but-realistic digital twin geometry.

## Referanstan sapmalar
- Açılma kursu 420 mm (H-400D: 600). İçe katlanan mafsal + plaka içi pivotlar (Z=±400) ile diz ~430 mm'de eksene ulaşıyor.
- Piston kursu 500 mm (H-400D: 400). 220 mm plaka + döküm ağzı + 170 mm sabit kalıp için 400 yetmiyor.

## Hesap ve geometri notları
- Units mm/deg. Global CS per bom.json: origin = center of fixed platen die face, +X toward moving/rear platen, +Y operator side, +Z up, floor Z=-1150.
- Instance transform: p_global = Rz(rz)*Ry(ry)*Rx(rx)*p_local + pos (right-handed; Ry(t): x'=x cos t + z sin t, z'=-x sin t + z cos t). Only A32 uses a non-zero rotation ([0,180,0]).
- Each instance carries 'bbox' = global AABB [xmin,ymin,zmin,xmax,ymax,zmax] of the part as dimensioned (mandatory features only) for self-checking.
- Baseline Buhler H-400D: 4000 kN, platens 920x980, clear space between bars 580x640 -> centers 700x760 with d120 bars, die height 200-750, ejector 145 mm / 22 t, injection 43 t.
- Tie bar check: 4000 kN/4 = 1000 kN per bar; M120x6 minor d = 120-1.22687*6 = 112.64 mm, root area 9965 mm2 -> 100.4 MPa (shank 88.4 MPa) < 150 MPa OK.
- X stack (die closed, die height 400): A21 -220..0 | A81 0..170 | A82 170..400 | A22 400..600 | toggle 600..1625 | A23 1625..1805 | A26 to 1925 | tie bar -350..2305 (rear length covers die height 750).
- Toggle (locked, links collinear and parallel to X at Z=+-400): C.x = 600+aC(140) = 740; B.x = C.x+L2(320) = 1060; A.x = B.x+L1(335) = 1395; A23 front = A.x+aA(230) = 1625. Closure: 140+320+335+230 = 1025 = 1625-600.
- Crosshead (locked): E on big link 150 from A -> E=(1245, +-400); D at Z=+-200; arm DE=205 -> dx = sqrt(205^2-200^2) = 45.0 -> D.x = 1290.0; arm at 77.3 deg to the machine axis.
- Toggle open check (stroke 420): sqrt(335^2-h^2)+sqrt(320^2-h^2) = 655-420 -> knee drop h=305.1, knee Z=+-94.9, big link 65.6 deg, front link 72.4 deg; E=(1333.0,263.4), D.x=1528.0; crosshead travel 238.0 (cylinder stroke 260); crosshead rear face 1598.0 < A23 front 1625. Crosshead travel is monotonic over the stroke.
- DEVIATION: opening stroke is 420 mm, not the H-400D 600 mm. With inward-folding knees and pivots inside the 980 mm platen outline (Z=+-400) the knee reaches the machine axis at ~430 mm; 600 mm would need pivots at about Z=+-510.
- Crosshead links are separate parts A36 x4 (see motion section). 12 pins: A,C,E,D x top/bottom + split knee pins B x4.
- Toggle Y layers (each side of center): A31 tongue 0..20; A36 links 25..55; A23 inner lugs 60..125; big links A32 130..200 (center 165); front links A33 205..275 (center 240) and A23 outer lugs 205..275; A22 lug -200..200; tie bar surface at |Y|=290. Side gaps 5 mm.
- Pin d90 shear at 2000 kN per toggle half: joint C has 2 shear planes -> 157 MPa; joints A/B effectively 4 planes -> 79 MPa. Link section 70x180: 79 MPa.
- Injection: 430 kN on plunger d70/80/90 -> 111.7/85.5/67.6 MPa casting pressure; default d80. Cylinder bore 140 at 140 bar = 216 kN; intensifier 200/140 (ratio 2.04) -> 440 kN (~43-45 t).
- DEVIATION: plunger stroke 500 mm (H-400D: 400). Retracted tip face X=-360 (10 mm behind pour hole X -350..-250), end of shot X=+140 = 30 mm biscuit before the parting line of the 170 mm fixed die half. 400 mm cannot span a 220 mm platen plus pour hole plus die half.
- Shot sleeve A51 ends flush with the fixed platen die face (X=0); the d80 bore continues through fixed die A81. Shot position 150 mm below center.
- Rails A12 run under all three platens from X=-220 to the rear platen back face at die height 750. Platen bottoms Z=-490, frame top Z=-530.
- Rear tie-bar thread covers nut travel for die height 200..750; rear platen/nuts move with die height, fixed platen end is fixed.
- Tank + motor-pump and electrical cabinet stand on the floor on the non-operator (-Y) side; guard door on +Y side rides on a track bolted to the frame side.
- Features flagged optional are cosmetic; if drawn they must not exceed the instance bbox.

## Değişiklik günlüğü
| Tarih | Parça | Eski -> Yeni | Neden |
|---|---|---|---|
| 2026-11-15 | tümü | ilk sürüm | faz 1-4 ilk ölçülendirme |
| 2026-11-15 | bom | A36 x4, A37 x1 eklendi (faz 2); A34 adet 10 -> 12 | hareket: kollar ve piston kolu ayrı parça, diz pimleri bölündü |
| 2026-11-15 | A31 | gövde 140x200x540 + kaynaşık kollar -> göbek 140x200x260 + dil 140x40x540 (D delikleri dilde); bbox x 1185..1360, z ±460 -> x 1220..1360, z ±270 | kollar A36 oldu; A36 (|Y| 25..55) dili iki yandan sarar, göbek üstü |Z|=130 kol gözünün (140) 10 mm altında |
| 2026-11-15 | A35 | gövde+piston kolu -> yalnız gövde (flanşta d100 kol deliği, d160 boş delik); bbox x 1360..2285 -> 1805..2285 | kol çapraz kafa ile hareket etmeli |
| 2026-11-15 | A36 (yeni) | E-D 205, d90 delikler, 30 kalın, 120 geniş, R60; pos E=(1245, ±40, ±400), rot Ry ±77.32° | çapraz kafa–E kolu, E etrafında döner |
| 2026-11-15 | A37 (yeni) | kol d90 x 495 + piston d160 x 60; pos (1360,0,0) | çapraz kafa ile öteleme (238 mm); piston 1855..1915 -> 2093..2153, delik 1845..2245 |
| 2026-11-15 | A34 | B pimi 560 (tek) -> 2 x 150 (Y ±127.5..277.5); D 220 -> 120; E 420 -> 400 | merkez iticiye boş kalsın; D dil+2 kol genişliği; E pimi s=1'de ön kola (|Y|>=205) 2.3 cm3 giriyordu |
| 2026-11-15 | A41 | boy 510 -> 425 (direk 0..205, flanş 205..230 / 230x230, gövde 230..405, kapak ..425); direkler ±95 -> ±85 | s=1'de çapraz kafa göbeği önü 1458, itici arkası 1445 |
| 2026-11-15 | A42 | plaka 340x340 -> 240(Y)x340(Z); kılavuz delikleri ±85; itici milleri (±140,±140) -> (±90,±140) | katlanan büyük kollar (|Y|>=130) ve diz pimleri yanından geçsin |
| 2026-11-15 | A22 | itici mil delikleri (±140,±140) d42 -> (±90,±140) d46 | A42 mil düzeni; 5 mm boşluk |
| 2026-11-15 | clearances | (A31,A35) çıkarıldı; (A34,A36), (A31,A37), (A35,A37) eklendi | yeni temaslar |
| 2026-11-18 | A21 | ejector_return_holes 16 x d32 -> kaldırıldı; support_mount (opsiyonel M36 delikler) eklendi | Karar 2026-11-17: sabit tarafta itici deliği yok; A21 A13 ile şaseye sabit |
| 2026-11-18 | A22 | delik deseni değişmedi (merkez d80 + 4 x d46 (±90,±140)); ejector_unit_mount 4 x M30 (±62.5,±70) opsiyonel eklendi | A41 gergi direkleri yeni konumda |
| 2026-11-18 | A41 | tek silindir d140/d70 merkezde -> 2 silindir d100/d56, (Y,Z)=(±62.5,0); gövde OD 170 -> 115; flanş 230x230x25 -> köprü 240x200x35 (42CrMo4+QT), x 205..240; gövde 230..405 -> 240..405; piston 20 eklendi; direkler (±85,±85) -> (±62.5,±70); bbox Y ±115 -> ±120, Z ±115 -> ±100; boy 425 aynı | Karar 2026-11-17 (çift, yatay simetrik). d = sqrt(4F/(πp)) = 99,0 -> 100; itme 2 x 110,0 = 219,9 kN (22,4 t). Köprü eğilmesi 195 MPa (direk aralığı 170 -> 140, kalınlık 25 -> 35). Diz pimi 7,5 mm, büyük kol 10 mm |
| 2026-11-18 | A42 | kılavuz delikleri (±85,±85) -> (±62.5,±70); köşe çubuk boyu 345 -> 390 (uç X=360, A83'e temas); rod_attach M42x2 (±62.5,0) ve opsiyonel merkez çubuk eklendi; bbox xmin 405 -> 360 | Çift silindir bağlantısı; kalıp itici plakasını itmesi |
| 2026-11-18 | A82 | 4 x d36 tam boy pim deliği -> bağlama plakasında 4 x d46 + d80 merkez; itici kutusu eklendi (bağlama plakası 40 + raylar 120 (|Y| 200..270) + kalıp plakası 70); 24 x d10 + 4 x d25 pim yuvası | Karar 2026-11-17: "24" kalıbın pimleri; kalıp yüksekliği 230 değişmedi |
| 2026-11-18 | A83 (yeni) | kalıp itici plakası 370x520, arka 30 + tutucu 25, X 305..360; kurs 65 | itici kutusu |
| 2026-11-18 | A84 (yeni) | 24 itici pimi d10 x 145, baş d16x5; 6x4 ızgara Y ±25/75/125, Z -17.5/47.5/112.5/177.5; uç X=185 | gözde, kalıp boşluğu tabanında |
| 2026-11-18 | A85 (yeni) | 4 geri dönüş pimi d25 x 160, baş d35x6, (±160,±230); uç X=170 (ayrım yüzü) | kalıp kapanırken A83'ü geri iter |
| 2026-11-18 | A13 (yeni) | 2 destek direği Y=±150: taban 620x160x40 (X -620..0), kolon 50x160x230 (Z -490..-260), 2 x 25 kalın üçgen takviye; A21'e 4+2 x M36, A11'e 6 x M30 (10.9) | A21 yalnız raylara oturuyordu. Kapama kuvveti iç döngü (net 0); kazara yatay yük H = 0,1·F = 400 kN (VARSAYIM) -> 196 kNm; takviye 153 MPa, cıvata 265 kN < ön gerilme 538 kN |
| 2026-11-18 | mates/clearances | A21 SABİT notu; A13, A42-A83, A83-A82, A84, A85 mate'leri; 9 izinli temas çifti eklendi | yeni parçalar |
| 2026-11-18 (rev2) | A13 | 2 kısa pedestal (Y=±150, taban 620x160x40 + kolon 50x160x230 + gusset, M36/M30 cıvata) -> 3 UZUN yuvarlak kolon: alt 2 × Ø100 (Y=±220, Z=-150), üst 1 × Ø120 (Y=0, Z=370); flanştan flanşa 2430 (X -220..-2650); ön flanş OD200/220 × 40, A21 arka yüzüne 6×M24 10.9 (PCD 160/180) + 0-3 mm şim; arka flanş aynı ölçü, A14'e KAYNAKLI (a=12 çevre); üst kolon ölçüleri instance override | Kullanıcı fotoğrafı (ZLC300 tipi): kolonlar plakanın arkasından şase arka ucuna uzanır. Pedestallerin işini kolonlar + A14 üstlendi, taban plakası/gusset/M30 gereksiz → kaldırıldı. A21 döküm olduğu için ön uç cıvatalı |
| 2026-11-18 (rev2) | A14 (yeni) | şase arka ucunda dikme: levha 50 × 800 × 1050 (X -2700..-2650, Z -530..520), 2 gusset t40 (|Y| 340..380, taban X -2000'e kadar), 2 üst nervür 30×200 (Z 220..250, 490..520), 2 alt nervür t20 (|Y| 90..110); A11'e a=20 kaynak | Kolon arka uçları şase üst kotundan 380-900 mm yukarıda; dikme olmadan şaseye kaynak edilemez. Gusset ucu A11 kaburgası X=-2000 üstünde |
| 2026-11-18 (rev2) | A58 | 2 × Ø45 (Y=±175, Z=-150, X -1670..-220) -> KALDIRILDI (BOM'dan çıktı, params'ta status + instances_removed) | Alt kolonlar aynı kotta ve A58 ile çakışıyordu (A58 |Y| 152,5..197,5). A58 görevini alt kolonlar alır; ancak enjeksiyon tepkisi artık A57-A11-A14-A13 yolundan geçer (KARAR gerekli, bkz. açık riskler) |
| 2026-11-18 (rev2) | A56 | instance Y -330 -> -390; bbox Y -440..-220 -> -500..-280 | A13_2 alt kolon (Y -270..-170) ile 10 mm boşluk; ayak halkası şase kenarına (Y=-500) dayanır |
| 2026-11-18 (rev2) | A21 | support_mount: bottom_tapped_M36 + rear_tapped_M36 (8) kaldırıldı -> rear_tapped_M24 18 adet (3 flanş × 6, PCD 160/160/180), opsiyonel | yeni kolon flanşları |
| 2026-11-18 (rev2) | mates/clearances | eski 6 A13 mate'i ve A58 mate'leri silindi; A13-A21 (cıvatalı), A13-A14 (kaynaklı), A14-A11 (kaynaklı) + 4 boşluk mate'i; izinli temas: (A11,A13) çıkarıldı, (A13,A14), (A11,A14) eklendi | yeni bağlantılar |
| 2026-11-18 (rev2) | bom | A13 qty 2 -> 3, ad "Sabit plaka destek kolonu (uzun, 2 alt + 1 üst)"; A14 eklendi (faz 1, parts/A14_kolon_arka_dikme.py); A58 çıkarıldı (faz 3) | yukarıdaki değişiklikler |
| 2026-11-18 (shot) | global | yok -> `shot_position: "alt"`, `shot_positions_z: {alt -150, orta -75, ust 0}`, `shot_follow` (türetme kuralı); `shot_offset_z` -150 aynı, artık TÜRETİLMİŞ | Kullanıcı isteği: ayarlanabilir 3 konumlu vuruş ekseni (ZHENLI/Idra tipi); mevcut -150 = alt. Üst = makine merkezi |
| 2026-11-18 (shot) | A21 | shot_hole d140 center [0,-150] değişmedi; `center_z_from`, `positions_z_ref`, `drawn`, `physical_note`, `edge_margins_mm` eklendi | Yalnız seçili delik çizilir, diğerleri tıkalı. Adım 75 < 140 → gerçekte dikey pencere 140×290 (Z -220..+70) + 2 dolgu takozu (modellenmez) |
| 2026-11-18 (shot) | A81 | sleeve_bore center [0,-150] değişmedi; `center_z_from` eklendi | seçiciyi izler |
| 2026-11-18 (shot) | A51, A52, A54, A55 | pos Z -150 değişmedi; instance `note` (türetilmiş) eklendi | pos[2] = z_sel, bbox Z += dz |
| 2026-11-18 (shot) | A57 | saddles local_z_range [30,230] değişmedi (alt), not: üst = 230+dz (230/305/380); `height_adjust` eklendi (kaide + 0/1/2×75 ara takoz, 2×Ø25 pim, 1×M24 kriko, 4×M24 10.9 saplama / semer, her ara yüzde 300×40 kama, A11'e kaynaklı 80×400×60 dayama takozu, 8×M30 taban); gusset notu | vuruş yüksekliği ayar mekanizması ve 430 kN yük yolu (sürtünme 2150 kN sıkma isterdi → kama) |
| 2026-11-18 (shot) | A13 | design_loads.injection_reaction metni konum bazlı oldu (215/184/153 kN alt kolon, 0/62/124 kN üst kolon) | vuruş ekseni kayınca tepki kolonlar arasında yeniden dağılır |
| 2026-11-18 (shot) | meta.notes | 1 not güncellendi (Shot position ... = 'alt'), 3 not eklendi (konumlar/boşluklar, sınırlar, tepki) | izlenebilirlik |

## Hareket (kapama) doğrulaması – 2026-11-15
Açılma kursu 420 mm KORUNDU. Çözüm: itici ünitesi |Y|<=120, |Z|<=170, boy 425 zarfına alındı; diz pimleri bölündü; çapraz kafa göbek+dil oldu.
Yöntem: değişen/yeni parçalar (A31, A35, A36, A37) params ölçülerinden vekil katı olarak, diğerleri mevcut scriptlerden kuruldu; kinematics.pose ile s=0..1 adım 0.05 (21 konum); izinli olmayan her çift için en küçük katı-katı mesafe (BRepExtrema), izinli temaslar için ortak hacim.
Sonuç: en küçük boşluk 5.00 mm, çakışma yok; izinli temaslarda en büyük ortak hacim 0.2 mm3.

| Çift | min boşluk (mm) | s | Not |
|---|---|---|---|
| A31–A36 | 5.0 | tümü | kol yan yüzü / dil |
| A23–A36 | 5.0 | tümü | kol / iç kulak (Y) |
| A22–A42 | 5.0 | sabit | mil d36 / delik d46 |
| A42–A82 | 5.0 | sabit | mil ucu / kalıp arkası |
| A22–A33, A23–A32, A32–A33 | 5.0 | tümü | mevcut yan boşluklar |
| A34(B)–A42 | 7.5 | 1.00 | bölünmüş diz pimi / itici plakası (Y) |
| A32–A32, A33–A33 | 9.9 | 1.00 | üst/alt diz uçları eksende |
| A23–A37 | 10.0 | tümü | kol / arka plaka deliği d110 |
| A32–A42 | 10.0 | 0.90 | büyük kol / itici plakası (Y) |
| A34(B)–A41 | 12.5 | 0.95 | diz pimi / itici flanşı (Y) |
| A31–A41 | 13.0 | 1.00 | göbek önü / itici arka kapağı (X) |
| A32–A41 | 15.0 | 0.85 | büyük kol / itici flanşı |
| A23–A31 | 27.0 | 1.00 | çapraz kafa arkası / arka plaka önü |
| A22–A32 | 34.0 | 1.00 | |
| A36–A41 | 76.9 | 1.00 | |
| A22–A36 | 70.5 | 1.00 | |
| A31–A32 | 84.4 | 1.00 | |

Açık kalanlar: A31 ve A35 scriptleri eski dims anahtarlarını okuyor (check.py: KeyError) – yeniden çizilecek; A36/A37 scriptleri yok. İtici ileri konumu (plaka -145) modellenmedi; zarf lokal x 5..200 içinde kalır, A82'de mil deliği yok (temsili kalıp).

## İtici grubu ve sabit plaka desteği – 2026-11-18
- Hesap dökümü: out/olcu_2026-11-18_itici_destek.txt (kaynak: formül; H = 0,1·F_kapama varsayımdır, standart değildir).
- Vekil katı doğrulaması (params ölçüleri, s=0..1, 21 adım): statik çakışma yok; hareket boyunca en küçük boşluklar A41–A34(B) 7,5 mm, A41–A32 10,0 mm, A41–A31 13,0 mm (değişmedi).
- Açık: lib/kinematics.py'de MOVING_PLATEN_GROUP'a A83/A84/A85, DIE_HEIGHT_GROUP_FIXED'e A13 (ve zaten eksik olan A58) eklenmeli; motion_check --kalip-yuksekligi A81/A82 ile birlikte A83/A84/A85'i de dışarıda bırakmalı.
- İtici kursu: makine 145 (H-400D); bu kalıp için ayar 65 (kutu sınırı).

## Sabit plaka destek kolonları – 2026-11-18 rev2 (3 uzun kolon + A14)
- Kaynak: kullanıcı fotoğrafı (ZHENLI ZLC300 tipi) + formül. Hesap dökümü: out/olcu_2026-11-18_A13_3kolon.txt; boşluklar: out/olcu_2026-11-18_A13_bosluk.txt (params ölçülerinden vekil katı, BRepExtrema).
- Yük yolu: kapama 4000 kN A24 çevriminde kendi kendini dengeler (kolonlara gelmez). Ağırlık (~24 kN) A21 → A12 raylarına oturur. Kolonlar X yönündeki kazara yatay yükü H taşır; iki kol kotu (alt Z=-150, üst Z=+370), H etki kotu Z -320..+320 zarfı.
- **H = c·F_kapama VARSAYIMDIR, kullanıcı onayında değil.** Ölçüler c=0,1 ve c=0,2 için sağlanıyor:

| Kontrol | c = 0,1 (H = 400 kN) | c = 0,2 (H = 800 kN) | Sınır |
|---|---|---|---|
| Alt kolon Ø100, |N|max | 265 kN, 34 MPa | 531 kN, 68 MPa | S355 |
| Alt kolon burkulma (K=1, L=2430) | Euler SF 6,5; EC3 kullanım 0,20 | SF 3,2; kullanım 0,39 | < 1 |
| Üst kolon Ø120, |N|max | 362 kN, 32 MPa | 723 kN, 64 MPa | S355 |
| Üst kolon burkulma | SF 9,9; kullanım 0,14 | SF 4,9; kullanım 0,29 | < 1 |
| Ön flanş cıvatası 6×M24 10.9 | 60 / 44 kN | 121 / 88 kN | ön gerilme 232 kN |
| Arka flanş kaynağı a=12 | 44 / 35 MPa | 87 / 70 MPa | ~241 MPa |
| A14 gusset dikmesi (200×40) | 33 MPa | 66 MPa | 345 MPa |
| A14 taban kaynağı a=20 | 16 MPa | 32 MPa | ~241 MPa |
| A14 üst kiriş (üst kolon yükü) | 76 MPa | 152 MPa | 345 MPa |
| A14 alt levha yerel eğilme | 46 MPa | 92 MPa | 345 MPa |

- Yanal (Y) yük: uzun kolonlar taşımaz (yanal rijitlik ~216 N/mm). A21'in Y'de tutulması için A21–A12/A11 enine kama gerekir (modellenmedi, açık karar).
- Enjeksiyon tepkisi 430 kN (0,107·F) A58 kalktığı için her atışta A57-A11-A14-A13 yolundan geçer: alt kolon başına 215 kN çekme, 27 MPa (yorulma uygun). Seçenek: A54 ön kafasını alt kolonlara bağlamak (faz 3, karar gerekli).
- Isıl: kolon-şase sıcaklık farkı 20 K → 0,58 mm; uçlar rijit kalırsa büyük zorlama doğar → ön flanşta şim/oval delik önerildi (açık risk).
- Boşluklar (min 10 hedefi sağlandı): A13–A56 10,0 (A56 Y -390'a taşındı); A13–A54 başlıkları 20; A13–A51 flanşı 25; A13–A55 30; A14–A55 40; A14–A11 X=-2000 kaburgası 40 (toe kaburga üstünde, temas üst plaka üzerinden); A13–A21 shot hole kenarı 50; A13–A25 69; A13–A52 (ileri, +500) 95; A13–A57 115,5; A13–A54 kol süpürmesi 125; A13–biscuit açıklığı 369; A13–A11 üst plakası 280. Üst kolon altında döküm ağzı üstü serbest yükseklik 390 mm (Z -80..310), kepçe yandan girer.

## Ayarlanabilir 3 konumlu vuruş ekseni – 2026-11-18
- Kaynak: formül + params ölçüleriyle tam montaj taraması (mevcut parça scriptleri, BRepExtrema). Döküm: out/olcu_2026-11-18_shot_3konum.txt.
- Tek doğruluk kaynağı: `global.shot_position` (alt|orta|ust, varsayılan alt) + `global.shot_positions_z`. Diğer Z alanları türetilmiş, şu an 'alt' değerinde; resolver (assemble) yazılana kadar seçici yalnız 'alt'ta tutarlıdır.

| Konum | Z | A57 semer üstü (lokal) | Ara takoz | A21 et: kolon deliği / alt A13 flanşı / üst A13 flanşı / plaka altı | Kepçe serbest yük. (çubuk / flanş altı) |
|---|---|---|---|---|---|
| alt | -150 | 230 | 0 | 289 / 50 / 340 / 270 | 390 / 340 |
| orta | -75 | 305 | 1 × 75 | 334 / 62 / 265 / 345 | 315 / 265 |
| ust | 0 | 380 | 2 × 75 | 387 / 96 / 190 / 420 | 240 / 190 |

| Çift (min boşluk mm) | alt | orta | ust | Not |
|---|---|---|---|---|
| A55–A57 arka semer | 10 | 10 | 10 | düşey, semer kafayla birlikte yükselir |
| A54–A13 alt kolonlar | 20 | 20 | 20 | Y (kafa ±150 / çubuk 170) |
| A57 semer–A13 alt kolonlar | 115,5 | 52,6 | 20 | üstte semer çubuk kotuna çıkar; Y 20 |
| A51 flanş–A13 alt flanş | 25 | 37 | 71 | |
| A55–A14 (X) | 40 | 40 | 40 | alt nervür X; üst nervür Z220 ile üstte 80 |
| A54 / A55 / A51–A13_3 üst kolon | >200 | >200 | 160 / 153 / 165 | |
| A57–A56, A54–A56 | 80, 154 | 80, 154 | 80, 154 | değişmez |
| A52 ileri–A21 | 45 | 45 | 45 | |
Üç konumda da çakışma 0, BBOX sapması 0. A12 raylar (X≥-220, |Y|≥300), A25 somunları (|Y|≥255, X≥-330) ve A11 biscuit açıklığı (X 20..580) vuruş Z'sinden bağımsız; uzak.
- Sınırlar: üst konum Z ≤ +70 (A55–A14 üst nervür), Z ≤ +150 (A54–A13_3). Üst kolonu kaydırmak gerekmedi; 3 kolon kararı korundu. 3 ayrı Ø140 delik mümkün değil (aralık -150..+70) → pencere + dolgu takozu.
- Yük yolu (430 kN, konservatif bileşke Z_s'de): A52 → A54 gövdesi (-X) → kafa/takoz kamaları → A57 kaide → dayama takozu → A11 üst plakası (A57→A14 arası basma) → A14 → A13 (çekme) → A21 ← kolon somunları A25 ← A24 ← A23 ← mafsal ← A22 ← kalıp. Alt kolon 215/184/153 kN, üst kolon 0/62/124 kN; devrilme 163/196/228 kNm. Statik uygun; A14 kaynak yorulması (her atış) doğrulanmadı.
- Eksen hizası hedefi Y/Z ±0,10 mm (taşlanmış takoz + pim); ince X-Y-Z ayarı kapsam dışı.
