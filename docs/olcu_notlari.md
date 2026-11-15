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
