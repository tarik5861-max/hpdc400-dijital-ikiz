# Kararlar

Yeni karar en üste eklenir. Bir karar değişirse eskisi silinmez, yanına "→ değişti: <tarih>" yazılır.

| Tarih | Karar | Neden |
|---|---|---|
| 2026-11-18 | Vuruş ekseni ayarlanabilir 3 konum: global.shot_position alt/orta/ust = Z -150/-75/0 (varsayılan alt); A57 semer 0/1/2×75 mm ara takoz + kama + saplama; A21'de yalnız seçili delik; enjeksiyon grubu seçiciyi izler (assemble.py resolve_shot, KURAL_SHOT, --vurus-tarama) | Kullanıcı isteği (gerçek makinelerde ayarlanabilir vuruş yüksekliği); hesap: docs/olcu_notlari.md, out/olcu_2026-11-18_shot_3konum.txt |
| 2026-11-18 | Sabit plaka destek kolonları: 3 UZUN çubuk (2 altta Ø100 Y=±220 Z=-150, 1 üstte Ø120 Z=370); ön uç cıvatalı flanşla A21'e, arka uç kaynakla A14 dikmesine, A14 şase ucuna (A11) kaynaklı. A58 çubukları ağaçtan çıkarıldı (alt kolonlar görevini aldı) — A58 kaldırılması KULLANICI ONAYI BEKLİYOR | Kullanıcının gerçek makine fotoğraflarından (3 kolon: 2 alt, 1 üst; arka şaseye kaynaklı); hesap docs/olcu_notlari.md rev2 |
| 2026-11-18 | İtici grubu uygulandı: A21'de itici deliği yok; A41 çift silindir (Ø100/Ø56, 140 bar, iki silindir toplam 22,4 t itme), A42 390 mm çubuk, A82 itici kutusu + A83 itici plakası + 24×A84 Ø10 pim + 4×A85 Ø25 geri dönüş pimi (kalıp strok ayarı 65) | 2026-11-17 kararının uygulaması; hesaplar docs/olcu_notlari.md |
| 2026-11-18 (→ değişti: aynı gün, aşağıdaki satır) | Sabit plaka (A21) şaseye 2 adet A13 destek direğiyle bağlanır (taban + kolon + üçgen gusset, M36/M30 cıvata); A21 kızakta kaymaz, sabittir | Kullanıcı isteği: plakayı şaseye bağlayan direkler; kapama kuvveti plaka-kolon çevriminde dengelenir, destekler ağırlık + kazara yatay yük taşır |
| 2026-11-17 | İtici grubu çift silindirli, yatay simetrik; sabit tarafta itici deliği yok; A22 5 konumlu desen (merkez + 4); 24 itici pimi + 4 geri dönüş pimi kalıpta (A82 itici kutusu) | Gerçek makine düzeni; "24" kalıp pimleri; itici plakası mafsal boşluğu yüzünden büyütülemez |
| 2026-11-17 | Sabit plaka (A21) delikleri kaldırıldı; hareketli plakaya (A22) 24 adet itici/pim geçiş deliği eklendi (itici plakası A42 ve hareketli kalıp A82 güncellendi) | Kullanıcı isteği: itici delikleri hareketli plakada ve 24 adet |
| 2026-11-17 | Sabit plakaya (A21) 16 adet d32 itici dönüş/pim geçiş deliği eklendi; sabit kalıptan (A81) itici delikleri kaldırıldı → değişti: 2026-11-17 | Gerçek 400 t kalıp ve plaka standardı; itici mekanizması yalnız hareketli taraftadır |
| 2026-11-17 | Enjeksiyon ünitesi ile sabit plaka arasına 45 mm çapında A58 bağlantı çubukları (2 adet) eklendi | Enjeksiyon eksenel itme kuvvetine karşı mekanik denge ve kararlılık |
| 2026-11-17 | Öncelik sırası: makineyi tamamlamak → elektrik → hidrolik → yazılım (PLC). Yazılımı kendimiz yazma seçeneği açık | Kullanıcı kararı; LK (Microstar) elektrik şeması geliyor |
| 2026-11-17 | Boyutlandırma (hesap) motoru "Alt plan A" olarak yol haritasına alındı; en son işlerden biri olacak | Kullanıcı kararı: önce gerçek makine ve teşhis kademeleri |
| 2026-11-17 | Bağlam kuralları: bir sohbet = bir iş, `/devam` ile başla, `/kapanis` ile bitir; proje hafızası depoda (DURUM, KARARLAR, YOL_HARITASI) | Sohbet bağlamı büyüyüp pahalılaşıyordu |
| 2026-11-16 | MCP sunucusu hafif; geometri çekirdeği (cadquery-ocp-novtk) yalnızca kontrol araçlarında, ayrı uv ortamında | VTK (77 MB) yavaş ağda sunucunun açılmasını engelliyordu |
| 2026-11-16 | GitHub özel depo `tarik5861-max/hpdc400-dijital-ikiz`, çoklu PC, projeye özel `hpdc400` MCP sunucusu | Birden fazla bilgisayarda ortak çalışma |
| 2026-11-15 | Kalıp yüksekliği tahriki elektrikli redüktörlü motor: 1,1 kW, i=35, m4 merkez z210 / somun z48 / pinyon z20; işi Fable'a bırakmadan yapıldı | Kullanıcı tercihi; ~104 mm/dk ayar hızı |
| 2026-11-15 | Dişli kavramaları için sıkı girişim eşiği: < 50 mm³ | Yanlış faz ~4,9 cm³ veriyor, genel eşik (5 cm³) kaçırırdı |
| 2026-11-15 | Diz pimleri her yanda 2 × 150 mm'ye bölündü; itici boyu 425 mm, plaka 240×340 | Mengene açılırken itici mafsalla çarpışıyordu |
| 2026-11-15 | Çapraz kafa bağlantı kolları (A36) ve kapama silindiri piston kolu (A37) ayrı parça | Hareket ederken dönüp kaymaları gerekiyor |
| 2026-11-15 | Açılma kursu 420 mm (H-400D: 600), piston kursu 500 mm (H-400D: 400) | İçe katlanan mafsal sınırı; plaka + kalıp için 400 yetmiyor |
| 2026-11-15 | Kolon Ø120, 700×760 aralık, M120×6 → diş dibinde 100,4 MPa; piston Ø80 → 85,5 MPa döküm basıncı | Mukavemet sağlaması |
| 2026-11-15 | Referans makine Bühler H-400D (yardımcı: Idra OLCS 400, HPM II-400) | Genel 400 t soğuk kamaralı tasarım tabanı |
| 2026-11-15 | Fable yalnızca ölçü / koordinat ve çözülemeyen çakışma; çizim Sonnet, kontrol Haiku | Maliyet; kullanıcı isteği |
| 2026-11-15 | Nihai hedef arıza teşhisi; proje kademe kademe tam simülasyona büyüyecek | Servis bağımlılığını bitirmek |
