# Parça Adları

Kaynak: params/bom.json (tools/adlar_tablo.py ile üretilir; elle düzenleme).

## A10 Sase grubu

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A11 | Ana şase (kaynaklı gövde) | Machine base / frame | 1 | Makine gövdesini taşıyan, tüm üniteleri üzerinde toplayan kaynaklı çelik şase. |
| A12 | Hareketli plaka kızak rayları | Moving platen slide rails | 2 | Hareketli plakayı şase üzerinde yataklayıp kapama ekseninde yönlendiren raylar. |
| A13 | Sabit plaka destek kolonu | Stationary platen support | 3 | Sabit plakayı şaseye oturtup kalıp yükünü şaseye ileten destek ayakları. |
| A14 | Kolon arka dikmesi | Rear tie bar support post | 1 | Şase arka ucunda kolon/arka plaka tarafını destekleyen kaynaklı dikme. (varsayım) |

## A20 Kapama unitesi

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A21 | Sabit plaka | Stationary (fixed) platen | 1 | Sabit kalıp yarısını taşıyan ve kolonların ön ucunu tutan plaka. |
| A22 | Hareketli plaka | Moving platen | 1 | Hareketli kalıp yarısını taşıyıp kolonlar üzerinde kayarak kalıbı açıp kapatan plaka. |
| A23 | Arka plaka (mafsal taşıyıcı) | Rear (toggle) platen | 1 | Mafsal mekanizmasının dayanak noktası olan ve kolonların arka ucunu tutan plaka. |
| A24 | Kolon (tie bar) | Tie bar | 4 | Kapama kuvvetini taşıyan, sabit plaka ile arka plakayı bağlayan gerilme çubuğu. |
| A25 | Kolon ön somunu | Tie bar front nut | 4 | Kolonu sabit plakaya bağlayıp kapama kuvvetini plakaya aktaran somun. |
| A26 | Kalıp yüksekliği ayar somunu (dişli) | Die height adjusting nut (geared) | 4 | Arka plakayı kolon üzerinde kaydırarak kalıp yüksekliğini ayarlayan dişli somun. |
| A28 | Hareketli plaka kolon burcu | Moving platen tie bar bushing | 4 | Hareketli plakanın kolon üzerinde sürtünmesiz kaymasını sağlayan burç. |

## A30 Mafsal mekanizmasi (5 noktali cift mafsal)

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A31 | Çapraz kafa (crosshead) | Crosshead | 1 | Kapama silindirinin hareketini bağlantı kolları üzerinden mafsallara ileten kayar gövde. |
| A32 | Büyük mafsal kolu | Toggle link (rear / long) | 4 | Arka plaka ile orta mafsal noktası arasında kuvveti çoğaltıp ileten mafsal kolu. |
| A33 | Ön mafsal kolu | Toggle link (front / short) | 4 | Mafsal orta noktasını hareketli plakaya bağlayıp kapama kuvvetini ileten kol. |
| A34 | Mafsal pimi | Toggle pin | 12 | Mafsal kollarını birbirine ve plakalara mafsallı bağlayan pim. |
| A35 | Kapama silindiri | Clamping cylinder | 1 | Çapraz kafayı hareket ettirerek mafsal mekanizmasını süren hidrolik silindir. |
| A130 | Kapama valf bloğu (manifold) | Clamping valve manifold | 1 | Kapama silindirinin yön ve debi kontrol valflerini taşıyan manifold bloğu. |
| A131 | Kapama valf bloğu konsolu | Clamping valve block bracket | 1 | Kapama valf bloğunu kapama silindirine bilezikle tespit eden konsol. |
| A132 | Kapama kartuş valf | Clamping cartridge valve | 4 | Kapama devresinde yağ akışını açıp kapayan kartuş tipi valf. |
| A133 | Kapama solenoid bobini | Clamping solenoid coil | 2 | Kapama valfini elektrik sinyaliyle tetikleyen solenoid bobin. |
| A36 | Çapraz kafa bağlantı kolu | Crosshead link | 4 | Çapraz kafayı mafsal kollarına bağlayıp hareketi ileten kol. |
| A37 | Kapama silindiri piston kolu | Clamping cylinder piston rod | 1 | Kapama silindirinin kuvvetini çapraz kafaya ileten piston kolu. |
| A170 | Mafsal merkezi yağlama pompası | Central lubrication pump (toggle) | 1 | Mafsal noktalarına periyodik gres/yağ basan merkezi yağlama pompası. (varsayım) |
| A171 | Mafsal yağlama dağıtıcı bloğu | Progressive lubrication distributor | 1 | Yağlama pompası yağını 12 mafsal noktasına paylaştıran progresif dağıtıcı. (varsayım) |

## A40 Itici unitesi

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A41 | Hidrolik itici silindiri | Ejector cylinder | 1 | Dökümü kalıptan çıkaran itici plakayı süren çift silindirli hidrolik grup. |
| A42 | İtici plakası | Ejector plate (machine side) | 1 | İtici silindir kuvvetini kalıp itici plakasına ileten makine tarafı plaka. (varsayım) |
| A161 | İtici strok sınırlama mansonu | Ejector stroke limiter sleeve | 4 | İtici strokunu ayarlı olarak sınırlayan manşon. (varsayım) |
| A162 | İtici konum sensörü | Ejector position sensor | 2 | İtici plakasının ileri/geri konumunu algılayan endüktif sensör. |

## A50 Enjeksiyon unitesi

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A51 | Dolum burcu (shot sleeve) | Shot sleeve / cold chamber | 1 | Dökülen metalin alındığı ve plunger ile kalıba itildiği soğuk kamara. |
| A52 | Enjeksiyon pistonu + piston kolu | Shot plunger tip and rod | 1 | Metali kamarada kalıba iten piston ve onu enjeksiyon silindirine bağlayan kol. |
| A54 | Enjeksiyon silindiri | Injection (shot) cylinder | 1 | Plunger'ı yüksek hızda süren enjeksiyon hidrolik silindiri. |
| A55 | Çarpan (multiplikatör) | Intensifier (multiplier) | 1 | Enjeksiyon sonu metal basıncını yükselten basınç çoğaltıcı. |
| A56 | Akümülatör tüpü | Accumulator | 4 | Enjeksiyon için yüksek debiyi hızlı sağlayan basınçlı yağ depolayan akümülatör. |
| A57 | Enjeksiyon taşıyıcı konsol | Injection unit carrier / bracket | 1 | Enjeksiyon ünitesini şaseye oturtup taşıyan konsol. (varsayım) |
| A65 | Enjeksiyon valf bloğu | Injection valve manifold | 1 | Enjeksiyon silindirinin hız/basınç valflerini taşıyan manifold bloğu. |
| A66 | Enjeksiyon konum sensörü + LS2 | Injection position sensor + limit switch LS2 | 1 | Plunger konumunu/hızını ölçen sensör ve LS2 limit anahtarı. (varsayım) |
| A67 | Enjeksiyon basınç vericisi | Injection pressure transmitter | 2 | Enjeksiyon hat basıncını ölçüp kontrolöre ileten verici. |
| A140 | Kamara flanşı cıvataları | Chamber flange bolts | 1 | Dolum burcunu sabit plakaya bağlayan M12 cıvatalar. |
| A141 | Dolum ağzı hunisi (pour cup) | Pour cup / pouring hole | 1 | Sıvı metalin kamaraya döküldüğü huni. |
| A142 | Kamara soğutma bağlantı stub'ları | Chamber cooling connection stubs | 1 | Dolum burcu soğutma suyu devresi bağlantı uçları. (varsayım) |
| A143 | Plunger yağlama ünitesi | Plunger lubrication unit | 1 | Plunger ve kamara yüzeyine yağlayıcı uygulayan ünite. (varsayım) |
| A144 | Piston kolu koruyucu kapak | Plunger rod guard | 1 | Hareketli piston kolunu çevreden koruyan kapak. (varsayım) |
| A145 | Ön kafa tutucu saplama uçları (A54) | Cylinder tie rod ends (A54) | 1 | Enjeksiyon silindiri ön kafasını tutan M24 saplama uçları. (varsayım) |
| A182 | Kamara arka desteği | Shot sleeve rear support | 1 | Soğuk kamaranın arka ucunu şase üst yüzüne dayayan eyer ve dikme. (varsayım) |
| A183 | Enjeksiyon bağlantı borusu | Injection unit rigid pipe | 2 | A54 kol tarafı ve A55 çarpan tahrik portunu A65'e bağlayan sert boru. (varsayım) |
| A186 | Enjeksiyon piston ve kolu | Injection piston and rod | 1 | A54 silindirinin hareketli iç grubu; kol ucu A52 bağlantısına değer, A52 ile birlikte ilerler. (varsayım) |

## A60 Hidrolik unite

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A61 | Hidrolik tank | Hydraulic reservoir / tank | 1 | Hidrolik yağı depolayan, soğutup çökelten tank. |
| A62 | Motor-pompa grubu | Motor-pump unit | 1 | Hidrolik basınç ve debiyi üreten motor ve tandem pompa grubu. |
| A120 | Elektrik motoru M1 55 kW | Electric motor M1 55 kW | 1 | Hidrolik pompayı döndüren ana tahrik motoru. |
| A98 | Pompa ön gövde 45VQ | Pump front body 45VQ | 1 | Pompanın montaj flanşını ve P1 çıkışını taşıyan ön gövde. |
| A99 | Giriş gövdesi (ortak emiş) | Pump inlet body (common suction) | 1 | İki pompa kartuşuna ortak emiş sağlayan giriş gövdesi. |
| A100 | Arka kapak 20VQ | Pump rear cover 20VQ | 1 | 20VQ kartuşunu kapatan, P2 çıkışı ve emniyet valfi yuvası olan kapak. |
| A101 | Pompa mili | Pump drive shaft | 1 | Motor torkunu iki pompa kartuşunun rotoruna ileten kamalı mil. |
| A102 | 45VQ halka (cam ring) | 45VQ cam ring | 1 | Kanatların izlediği eliptik/kam yüzeyi oluşturan halka. |
| A103 | 45VQ rotor | 45VQ rotor | 1 | Kanatları taşıyıp mil ile dönen rotor. |
| A104 | 45VQ kanat (vane) | 45VQ vane | 10 | Halka ile rotor arasında basınç odacıklarını oluşturan kanat. |
| A105 | 45VQ yan plaka (flex-side) | 45VQ side plate (flex-side) | 2 | Rotor yüzünü sızdırmazlayan, yağ giriş/çıkış kanallarını taşıyan plaka. |
| A106 | 45VQ giriş destek plakası | 45VQ inlet support plate | 1 | Kartuşun giriş tarafını destekleyen plaka. |
| A107 | 45VQ çıkış destek plakası | 45VQ outlet support plate | 1 | Kartuşun çıkış tarafını destekleyen plaka. |
| A108 | 20VQ halka (cam ring) | 20VQ cam ring | 1 | Kanatların izlediği kam yüzeyini oluşturan halka. |
| A109 | 20VQ rotor | 20VQ rotor | 1 | Kanatları taşıyıp mil ile dönen rotor. |
| A110 | 20VQ kanat (vane) | 20VQ vane | 10 | Halka ile rotor arasında basınç odacıklarını oluşturan kanat. |
| A111 | 20VQ yan plaka (flex-side) | 20VQ side plate (flex-side) | 2 | Rotor yüzünü sızdırmazlayan, yağ kanallarını taşıyan plaka. |
| A112 | 20VQ giriş destek plakası | 20VQ inlet support plate | 1 | Kartuşun giriş tarafını destekleyen plaka. |
| A113 | 20VQ çıkış destek plakası | 20VQ outlet support plate | 1 | Kartuşun çıkış tarafını destekleyen plaka. |
| A114 | Kartuş konum pimi | Cartridge locating pin | 4 | Kartuş parçalarını doğru açısal konumda sabitleyen pim. |
| A115 | Gövde bağlantı cıvatası | Pump body bolt | 4 | Pompa gövdelerini birbirine bağlayan yüksek torklu cıvata. |
| A116 | Arka kapak cıvatası | Rear cover bolt | 4 | Arka kapağı gövdeye bağlayan cıvata. |
| A117 | Emniyet valfi kartuşu | Relief valve cartridge | 1 | 20VQ çıkışında aşırı basıncı sınırlayan emniyet valfi kartuşu. |
| A118 | Emniyet valfi yayı | Relief valve spring | 1 | Emniyet valfinin açma basıncını belirleyen yay. |
| A119 | Tapa (valf yuvası) | Plug (valve port) | 2 | Kullanılmayan valf yuvası deliklerini kapatan tapa. |
| A121 | Emiş hattı (sert boru) | Suction line (rigid pipe) | 1 | Tank yağını pompa giriş gövdesine ileten emiş borusu. |
| A122 | Basınç hattı stub'ı | Pressure line stub | 2 | Pompa P1/P2 çıkışlarından basınç hattına geçiş yapan kısa boru ucu. (varsayım) |
| A123 | Boru tespit konsolu | Pipe support bracket | 2 | Boru hatlarını dikme ve kelepce ile sabitleyen konsol. (varsayım) |
| A160 | Hidrolik hatlar (boru + hortum) | Hydraulic lines (pipe + hose) | 46 | Hidrolik üniteleri birbirine bağlayan sert boru ve hortum hatları. |
| A59 | Akümülatör sepeti + valf bloğu | Accumulator rack + valve block | 1 | Akümülatörleri taşıyan sepet ve emniyet/boşaltma valf bloğu. (varsayım) |
| A63 | Akümülatör kelepce bantları | Accumulator clamp straps | 2 | Akümülatör tüplerini sepete sabitleyen bantlar. (varsayım) |
| A64 | Akümülatör toplayıcı borusu | Accumulator manifold pipe | 1 | Akümülatörlerin çıkışlarını ortak hatta toplayan boru. (varsayım) |
| A172 | Çek valf CV1 | Check valve CV1 | 1 | H01 hattında akışı tek yöne izin veren çek valf. |
| A173 | Basınç filtresi PF1 | Pressure filter PF1 | 1 | Basınç hattındaki yağı süzen filtre. |
| A174 | Dönüş filtresi RF1 | Return filter RF1 | 1 | Tanka dönen yağı süzen dönüş filtresi. |
| A175 | Hat rafı konsolu | Pipe rack bracket | 6 | Şase yan duvarında P/pilot/T hatlarını katmanlı taşıyan konsol. (varsayım) |
| A181 | Hat kelepçesi | Pipe clamp | 18 | P/pilot/T hatlarını A175 rafına bağlayan kelepçe. (varsayım) |
| A176 | A65 hortum geçiş braketi | A65 hose transition bracket | 1 | A65 bloğundaki hortumlardan sert boruya geçişi tutan braket. (varsayım) |
| A177 | A130 T hortum braketi | A130 T hose bracket | 1 | A130 T hortumunu d89 sert boruya bağlayan braket. (varsayım) |

## A70 Guvenlik / elektrik

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A71 | Operatör koruma kapısı | Operator safety gate | 1 | Operatörü kalıp bölgesinden ayıran, kilitli güvenlik kapısı. |
| A124 | Kapı polikarbonat panelleri | Gate polycarbonate panels | 1 | Kapıda görüş sağlayıp sıçramaya karşı koruyan şeffaf paneller. |
| A125 | Üst ray + makara arabaları + dikmeler | Gate top rail + roller carriages + posts | 1 | Koruma kapısını asıp kaydıran ray, makara ve dikmeler. |
| A126 | Pnömatik kapı tahrik silindiri | Pneumatic gate actuator cylinder | 1 | Koruma kapısını açıp kapatan pnömatik silindir. |
| A127 | Kilitli güvenlik anahtarı | Safety interlock switch | 1 | Kapı konumunu algılayıp açıkken makine hareketini engelleyen kilitli anahtar. (varsayım) |
| A128 | Kapı kolu + koruyucu kenar | Gate handle + safety edge | 1 | Kapıyı elle hareket ettirme kolu ve sıkışma koruyucu kenar. (varsayım) |
| A72 | Elektrik panosu | Electrical control cabinet | 1 | PLC, sürücü ve güç elemanlarını barındıran pano. |
| A163 | Acil durdurma istasyonu | Emergency stop station | 4 | Basıldığında makineyi güvenli duruma alan mantar başlı acil stop kutusu. |
| A164 | Arka koruma kapısı paneli | Rear safety gate panel | 1 | Makine arka tarafını kapatan kayar koruma kapısı paneli. (varsayım) |
| A165 | Arka kapı alt iz + üst ray + dikmeler | Rear gate track, rail and posts | 1 | Arka koruma kapısını yönlendiren iz, ray ve dikmeler. (varsayım) |
| A166 | Arka kapı kapalı limit anahtarı + dil | Rear gate closed limit switch + tongue | 2 | Arka kapının kapalı olduğunu güvenlik zincirine bildiren anahtar ve dil. |
| A178 | Alarm lambası / sinyal kulesi (HL1) | Signal tower / alarm beacon (HL1) | 1 | Makine durumunu renk ve siren ile bildiren sinyal kulesi. |
| A179 | Operatör kutusu (HMI) + sehpa | Operator control box (HMI) + stand | 1 | Operatörün jog/start/stop ve HMI ile makineyi yönettiği kutu ve sehpası. |

## A80 Kalip (temsili)

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A81 | Sabit kalıp yarısı | Fixed die half (cover die) | 1 | Sabit plakaya bağlı, döküm boşluğunun bir yarısını oluşturan kalıp (temsili). |
| A82 | Hareketli kalıp yarısı | Moving die half (ejector die) | 1 | Hareketli plakaya bağlı, döküm boşluğunun diğer yarısını oluşturan kalıp (temsili). |
| A83 | Kalıp itici plakası | Die ejector plate set | 1 | İtici pimlerini taşıyıp hareket ettiren kalıp içi itici plakası. |
| A84 | İtici pimi | Ejector pin | 24 | Soğuyan dökümü kalıp boşluğundan dışarı iten pim. |
| A85 | Geri dönüş pimi | Return pin | 4 | Kalıp kapanırken itici plakayı geri başlangıç konumuna iten pim. |
| A167 | Maça çekme silindiri | Core pull cylinder | 4 | Kalıp maçasını döküm sonrası çeken/süren hidrolik silindir. |
| A184 | Maça çekirdeği | Core slide pin | 4 | A167 silindirinin kolu ucunda kaviteye giren kayar maça pimi; çekili/ileri konum. (varsayım) |
| A168 | Maça valf manifoldu | Core pull valve manifold | 1 | 4 adet NG6 maça valfini taşıyan alt plaka. |
| A169 | Maça NG6 yön valfi | Core pull NG6 directional valve | 4 | Maça silindirinin yönünü belirleyen 4/3 çift solenoidli valf. |

## A90 Kalip yuksekligi ayar tahriki (elektrikli redüktörlü motor)

| ID | Türkçe ad | İngilizce ad | Adet | İşlev |
|---|---|---|---|---|
| A91 | Merkez dişli | Central (ring) gear | 1 | Dört ayar somununu birlikte döndüren merkez dişli. |
| A92 | Merkez dişli taşıyıcı yatak halkası | Central gear bearing ring | 1 | Merkez dişliyi arka plaka üzerinde yataklayan halka. (varsayım) |
| A93 | Pinyon + mil | Pinion + shaft | 1 | Redüktör çıkışından merkez dişliyi döndüren pinyon ve mili. |
| A94 | Redüktör (helisel) | Gear reducer (helical) | 1 | Motor devrini düşürüp tork artıran helisel redüktör. |
| A95 | Elektrik motoru 1,1 kW | Electric motor 1.1 kW | 1 | Kalıp yüksekliği ayar tahrikini döndüren elektrik motoru. |
| A96 | Motor-redüktör braketi | Motor-reducer bracket | 1 | Motor ve redüktörü arka plakaya tespit eden braket. (varsayım) |
| A97 | Motor enkoderi | Motor encoder | 1 | Kalıp yüksekliği ayarı için motor dönüşünü sayan enkoder. (varsayım) |
