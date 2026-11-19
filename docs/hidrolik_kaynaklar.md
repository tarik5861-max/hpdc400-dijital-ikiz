# Hidrolik hesap kaynakları (Kademe 3)

Karar: hat kayıpları `fluids` ile, dinamik bileşenler (akümülatör, çarpan, silindir, valf) kendi kodumuzla `lib/hidrolik_ag.py` içinde; denklemler aşağıdaki açık kaynaklarla çapraz kontrol edilir. Hiçbirinin kodu projeye kopyalanmaz; yalnızca `fluids` pip bağımlılığıdır.

| Kaynak | Ne için | Lisans | Kullanım |
|---|---|---|---|
| fluids (github.com/CalebBell/fluids) | hat/rakor/filtre basınç kaybı, emniyet valfi ve pompa boyutlandırma | MIT | pip bağımlılığı olarak kullan |
| petermaginot/hydraulics | boru-dirsek-valf zinciriyle basınç düşümü; yapı referansı | MIT | referans; gerekirse kod uyarlanabilir (lisans notu ekle) |
| OpenHydraulics (Modelica, github.com/wushuaibuaa/openhydraulics) | pompa, silindir, valf, akümülatör denklemleri | Modelica License 2 (Georgia Tech) | yalnızca denklem referansı; kod kopyalama |
| Hopsan (Linköping) | akışkan gücü dinamiği (TLM), hızlı vuruş modeli doğrulaması | GPL | yalnızca dışarıdan doğrulama aracı; projeye kod alma (GPL bulaşır) |
| Hydraulic Modelica Library 0.1 (2025, açık erişim) | ISO 1219 sembol/bileşen yapısı | belirtilmemiş, kullanmadan önce kontrol et | ISO 1219 şemasına geçerken referans |

Not: `fluids` boru standartları proses borusudur; hidrolik hortum/boru iç çapları ve pürüzlülük `params/hidrolik.json`'dan gelir. Yağ viskozitesi/yoğunluğu sıcaklığa bağlı girilir, VARSAYIM etiketiyle.
