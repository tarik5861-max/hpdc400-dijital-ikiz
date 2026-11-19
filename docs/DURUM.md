# Durum — kaldığımız yer

_Son güncelleme: 2026-11-19. Her `/kapanis`'te yeniden yazılır (en fazla ~60 satır)._

## Şu an
- A14 arka dikme tasarımı modern endüstriyel form ve şase taban bağlantı kaburgalarıyla güncellendi (`parts/A14_kolon_arka_dikme.py`).
- Kademe 3 hidrolik bileşenleri (A64 toplayıcı boru, A65 enjeksiyon valf bloğu, A66 konum sensörü, A67 basınç vericisi) modellemesi ve parametreleri tamamlandı (`114` instance).
- Statik kontrol YEŞİL: 114 instance, 0 hata, 0 uyarı.

## Açık noktalar
- Yok (tüm Kademe 1–3 model ve simülasyon ögeleri tamamlandı).
- A62 pompası gerçek 4520VQ tandem geometrisine çevrildi: A98..A119 (14 script, 22 ID, 52 instance), bom A62 altında alt ağaç; assemble.leaves alt ağaçları okur; hidrolik.json P1/P2 bagli_id eklendi. Kontroller YEŞİL: 166 instance, 0 hata (3 vuruş + hareket). Önizleme out/preview_pompa_*.png.
- Kademe 1 eksik kalan A13 sabit plaka destek kolonlarının ön flanş bağlantısı cıvatalı (M24) olarak detaylandırıldı ve kodlandı (`parts/A13_sabit_plaka_destek.py`).
- Kademe 3 hidrolik şema ve valf/sensör haritalaması (`params/hidrolik.json`) tamamlandı, testler doğrulandı.
- Statik kontrol YEŞİL: 166 instance, 0 hata, 0 uyarı.

## Açık noktalar
- KAPANDI (2026-11-19): Hızlı vuruş hızı/akümülatör. Faz 2 hedef 3,0 m/s (ikiz_tasarim) → 2771 L/dk (ACC1 2718 + P1 191); A56 ×4 V0 129 L yeterli (min 2 tüp), p0 113,4 bar, vuruş sonu 135,3 bar; şarj 0,95 s faz 3 içinde; şarj anı P1+P2 %102 SINIRDA, 60 s çevrim RMS %24 OK. A64 SINIRDA notu GİDERİLDİ (2026-11-19): ana hat dış Ø90/iç Ø80 (et 5), header dış Ø100, riser dış Ø50/iç Ø40 → faz 2 hız 9,0 m/s, sabit kayıp 1,2 bar, ivme Δp 12,4 bar.
- KAPANDI (2026-11-19): P1 debi/motor uyuşmazlığı. P1 191,2 L/dk, P2 23,1 L/dk (A120 55 kW, 1480 d/dk); 140 bar mil gücü 57,2 kW = %104 SINIRDA (yalnız P1+P2 eşzamanlı tam yükte). Sabit deplasman + U12 oransal valf ikiz_tasarim kararı.

## 2026-11-19 tank + motor-pompa yerleşimi (rev: redüktör tarafı)
- Arka yerleşim iptal. A61 tank şase içinde +X bölmesi (X 605..2135, 783,8 L), erişim +Y yan duvar X 740..1490. A62 grubu şase -Y yanında zeminde (X 620..2203, mil X ekseni). A121 emiş -Y yan duvardan (X 2025), A122 P1/P2 stub, A123 A62 plakası üstünde. A11 kaburga -1300/-600 geri; +X 700/1400/2000 → 590/2150. overall_length 5100. 172 instance, kontroller YEŞİL. Önizleme out/preview_redk_*.png.
- OLCU_TALEBI: A11 +X bölmesi 1540 mm açıklık (kaburgasız, A22/A23 + mafsal ağırlığı raylar üzerinden) mukavemet sağlaması (olcu-mimari). -X bölmesi OLCU_TALEBI'si kapandı (kaburgalar geri).
- Elektrik: A72 → A120 klemens ~5,1 m < L_motor_m 8; ELEKTRIK_TALEBI yok.

## Sıradaki adım
- Kademe 4 (Yazılım / PLC durum makinesi ve sıralama mantığı) çalışmalarına başlanması.
