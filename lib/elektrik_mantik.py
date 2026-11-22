"""elektrik_mantik.py - params/elektrik.json -> mantik bolumunu yorumlayan degerlendirici.

Tek dogruluk kaynagi elektrik.json: mantik.donanim (HW, izleme/izleme_ters), mantik.hw_girisler,
mantik.plc, mantik.alarmlar, mantik.esikler, mantik.ifade_dili.parametreler, mantik.zamanlar,
mantik.siralayici, loto, kanallar[].saglam_deger. Bu dosyada olcu/esik/sinyal listesi yok; yalniz
yorumlayici vardir (siralayici da mantik.siralayici verisinden surulur).

Tarama modeli (step(dt_ms)):
  1. HW katmani   : donanim listesi SIRAYLA (ileri basvurular onceki tarama degeri; PLC cikislari de
                    onceki tarama + zorla). PLC donanimi asamaz: PLC yalniz HW ifadelerine VE ile girer.
  2. DI geri bildirim: donanim[].izleme (DI = HW) ve izleme_ters (DI = not HW).
  3. Siralayici   : dis_durumlar (S.FAZ*, S.OTO_*, yaglama, LOTO, A97 sayaci ...).
  4. PLC katmani  : plc + alarmlar, ihtiyac aninda (tembel) cozumlenir; dongu -> onceki tarama degeri.
Zamanlayici/muhur durumu taramalar arasinda saklanir. Zamanlayicilarda tum argumanlar HER zaman
degerlendirilir (kisa devre yok), yoksa zamanlayici durumu bozulur.

Girdi (self.girdi): HW.* fiziksel girisler, DI*/AI*/DB68.* kanallar, HMI.* (HMI.RESET, HMI.OTO_BASLAT,
HMI.LOTO_BASLAT, HMI.LOTO_BITIR, HMI.DESARJ), P.* parametre ezme. self.zorla: ariza enjeksiyonu
(her sinyalin ustune yazar; or. PLC arizasi = DO7.31 sabit 1).
"""
import copy
import json
import os

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OPERATORLER = {"and", "or", "not", "xor", "ton", "tof", "ge", "le", "gt", "lt", "muhur"}

def yukle(yol=None):
    with open(yol or os.path.join(ROOT, "params", "elektrik.json"), encoding="utf-8") as f:
        return json.load(f)


def _params_global():
    try:
        with open(os.path.join(ROOT, "params", "params.json"), encoding="utf-8") as f:
            return json.load(f)["global"]
    except Exception:
        return {}


class ElektrikMantik:
    def __init__(self, cfg=None, gparams=None):
        self.cfg = cfg if cfg is not None else yukle()
        self.mk = self.cfg["mantik"]
        self.G = gparams if gparams is not None else _params_global()
        self.esik = self.mk["esikler"]
        # parametreler
        self.P = {}
        for k, v in self.mk["ifade_dili"]["parametreler"].items():
            if k.startswith("P.") and isinstance(v, (int, float)):
                self.P[k] = v
        for e in self.mk["plc"]:
            if e["id"] == "S.KY_SAYAC":
                for k, v in e["parametreler"].items():
                    self.P["P." + k] = v
        # tanimlar
        self.hw = [e for e in self.mk["donanim"]]
        self.hw_ids = {e["id"] for e in self.hw}
        self.plc = {}
        for e in self.mk["plc"]:
            if "ifade" in e:
                self.plc[e["id"]] = e
        for e in self.mk["alarmlar"]:
            self.plc[e["id"]] = {"id": e["id"], "ifade": e["kosul"], "alarm": True}
        self.alarm_ids = [e["id"] for e in self.mk["alarmlar"]]
        # izleme: HW sinyali -> DI
        self.izleme = {}
        for e in self.hw:
            for hw, di in e.get("izleme", {}).items():
                self.izleme[di] = (hw, False)
            for hw, di in e.get("izleme_ters", {}).items():
                self.izleme[di] = (hw, True)
        # saglam durum varsayilanlari (JSON): HW girisleri ve DI kanallari
        self.hw_saglam = {e["id"]: e["saglam_deger"] for e in self.mk["hw_girisler"]}
        self.di_saglam = {k["id"] for k in self.cfg["kanallar"] if k.get("saglam_deger", 0) == 1}
        self.sq_cfg = self.mk["siralayici"]
        self.maca_bobin = {}
        for e in self.hw:
            if e["id"].startswith("HW.MACA") and e["id"].endswith("_BOBIN"):
                self.maca_bobin[e["ifade"][1]] = e["id"]
        self.adim_tanim = {a["ad"]: a for a in self.sq_cfg["adimlar"]}
        self.girdi = {}
        self.zorla = {}
        self.prev = {}
        self.cur = {}
        self.t = 0.0
        self.zam = {}
        self.muh = {}
        self._yigin = set()
        self._katman = "hw"
        self._sira_baslat()

    # ------------------------------------------------------------------ yardimcilar
    def varsayilan(self, n):
        if n.startswith("HW."):
            return self.hw_saglam.get(n, 1)       # listede yoksa NC kabul (hw_girisler_kurali)
        return 1 if n in self.di_saglam else 0

    def _param(self, n):
        if n in self.girdi:
            return self.girdi[n]
        return self.P.get(n, 0)

    def _get(self, n):
        if n in self.zorla:
            return self.zorla[n]
        if n in self.cur:
            return self.cur[n]
        if n.startswith("P."):
            return self._param(n)
        if n == "S.HERHANGI_ALARM":
            if self._katman == "plc":
                v = int(any(self._coz(a) for a in self.alarm_ids))   # (tum alarmlar; kisa devre yok)
                self.cur[n] = v
                return v
            return self.prev.get(n, 0)
        if self._katman == "plc" and n in self.plc:
            return self._coz(n)
        if n in self.hw_ids or n in self.plc:
            return self.prev.get(n, 0)          # ileri basvuru / PLC->HW: onceki tarama
        if n in self.izleme and n in self.prev and n not in self.girdi:
            return self.prev.get(n, 0)
        if n in self.girdi:
            return self.girdi[n]
        if n.startswith("S."):
            return self.prev.get(n, 0)
        return self.varsayilan(n)

    def _deger(self, x):
        if isinstance(x, (int, float)) and not isinstance(x, bool):
            return x
        if isinstance(x, str):
            if x in self.esik:
                return self.esik[x]
            return self._get(x)
        raise ValueError(f"deger bekleniyor: {x!r}")

    # ------------------------------------------------------------------ ifade
    def ev(self, ex, key):
        if isinstance(ex, bool):
            return int(ex)
        if isinstance(ex, (int, float)):
            return ex
        if isinstance(ex, str):
            return self._get(ex)
        op = ex[0]
        if op not in OPERATORLER:
            raise ValueError(f"bilinmeyen operator {op!r} ({key})")
        a = ex[1:]
        if op in ("and", "or"):
            vals = [bool(self.ev(x, f"{key}.{i}")) for i, x in enumerate(a)]   # kisa devre YOK
            return int(all(vals) if op == "and" else any(vals))
        if op == "not":
            return int(not self.ev(a[0], key + ".0"))
        if op == "xor":
            return int(bool(self.ev(a[0], key + ".0")) != bool(self.ev(a[1], key + ".1")))
        if op in ("ge", "le", "gt", "lt"):
            x = self._deger(a[0])
            y = self._deger(a[1])
            return int({"ge": x >= y, "le": x <= y, "gt": x > y, "lt": x < y}[op])
        if op == "ton":
            giris = bool(self.ev(a[0], key + ".0"))
            ms = a[1]
            s = self.zam.setdefault(key, {"t0": None})
            if giris:
                if s["t0"] is None:
                    s["t0"] = self.t
                return int(self.t - s["t0"] >= ms)
            s["t0"] = None
            return 0
        if op == "tof":
            giris = bool(self.ev(a[0], key + ".0"))
            ms = a[1]
            s = self.zam.setdefault(key, {"tf": None, "son": False})
            if giris:
                s["tf"] = None
                s["son"] = True
                return 1
            if s["son"]:
                s["tf"] = self.t
                s["son"] = False
            return int(s["tf"] is not None and self.t - s["tf"] < ms)
        if op == "muhur":
            st = bool(self.ev(a[0], key + ".0"))
            rs = bool(self.ev(a[1], key + ".1"))
            q = (self.muh.get(key, 0) or st) and not rs
            self.muh[key] = int(q)
            return int(q)

    def _tanim_deger(self, e):
        """Tanim degeri; muhur:true ise SET=ifade, RESET=HMI.RESET (reset baskin)."""
        v = self.ev(e["ifade"], e["id"])
        if e.get("muhur"):
            rs = bool(self.ev(e["reset"], e["id"] + ".reset")) if "reset" in e else False
            q = (self.muh.get(e["id"], 0) or bool(v)) and not rs
            self.muh[e["id"]] = int(q)
            return int(q)
        return v

    def _coz(self, n):
        if n in self.cur:
            return self.cur[n]
        if n in self._yigin:
            return self.prev.get(n, 0)
        self._yigin.add(n)
        v = self._tanim_deger(self.plc[n])
        self._yigin.discard(n)
        if n in self.zorla:
            v = self.zorla[n]
        self.cur[n] = v
        return v

    # ------------------------------------------------------------------ siralayici (mantik.siralayici)
    def _sira_baslat(self):
        self.sq = {"adim": self.sq_cfg["adimlar"][0]["ad"], "faz": 0, "faz_t": 0.0, "cevrim": 0,
                   "yag": 0, "yag_t": 0.0, "pg": 0, "pg_t": 0.0, "faz3_bitti": 0, "loto": 0,
                   "sayac": 0, "a_son": 0, "ofset_mm": None,
                   "adim_t": 0.0, "maca_t": 0.0, "maca_alarm": 0, "enj_alarm": 0, "pg_alarm": 0}
        self.hata_yok = True

    def _sayi(self, x):
        """'params.global.<ad>' -> params.global; P.<ad> / esik adi / sayi -> deger."""
        if isinstance(x, str) and x.startswith("params.global."):
            return self.G.get(x[len("params.global."):].split()[0], 0)   # sonrasi aciklama metni
        if isinstance(x, str) and x.startswith("zamanlar."):
            return self.mk["zamanlar"][x[len("zamanlar."):]]
        return self._deger(x)

    def _konum_modu(self):
        """P.ENC_BILDIRIM=1: faz/piston geri gecisleri DB68.ENC konumuna bagli; 0: eski sure tabani (yedek)."""
        return bool(self._param("P.ENC_BILDIRIM"))

    def _maca_secili(self, mc):
        """Secici DI5.14..17 (VARSAYIM: 1 = maca otomatik cevrimde kullanilir) -- en az biri 1 mi."""
        return any(bool(self._get(x)) for x in mc["secici"])

    def _sirala(self, dt):
        q, c = self.sq, self.sq_cfg
        tan = self.adim_tanim
        P = self._param
        g = self._get
        s = {}
        # --- A97 kuadratur sayaci (a97_sayac): sayac girisinin yukselen kenarinda yon girisine gore
        a97 = c["a97_sayac"]
        yon = a97["yon_kurali"]
        a, b = int(bool(g(a97["sayac_girisi"]))), int(bool(g(a97["yon_girisi"])))
        degisti = False
        if a and not q["a_son"]:
            q["sayac"] += yon["B_1"] if b else yon["B_0"]
            degisti = True
        q["a_son"] = a
        s["S.SAYAC_DEGISMIYOR"] = int(not degisti)
        mm_darbe = P("P.mm_per_darbe")
        if q["ofset_mm"] is None:
            q["ofset_mm"] = self._sayi(a97["baslangic_mm"])
        for r in a97["referans"]:                       # referans kosulu varsa mm referansa kilitlenir
            if self.ev(r["kosul"], "a97.ref"):
                q["ofset_mm"] = self._sayi(r["deger_mm"]) - q["sayac"] * mm_darbe
                break
        s["S.KY_SAYAC_MM"] = q["ofset_mm"] + q["sayac"] * mm_darbe
        # --- HMI kaynakli durumlar
        if g("HMI.LOTO_BITIR"):
            q["loto"] = 0
        elif g("HMI.LOTO_BASLAT"):
            q["loto"] = 1
        s["S.LOTO_MODU"] = q["loto"]
        if g("HMI.RESET"):
            q["maca_alarm"] = q["enj_alarm"] = q["pg_alarm"] = 0   # muhurlu zaman asimi alarmlari resetle silinir
        s["S.MACA_ALARM"] = q["maca_alarm"]
        s["S.ENJ_KONUM_ALARM"] = q["enj_alarm"]
        s["S.PISTON_GERI_ALARM"] = q["pg_alarm"]
        s["S.OPERATOR_DESARJ_ISTEGI"] = int(bool(g("HMI.DESARJ")))
        self.cur.update(s)        # kosullar bu taramanin degerlerini gorsun
        # --- OTO cevrim siralayicisi
        ilk = c["adimlar"][0]["ad"]
        adim = q["adim"]
        gi = c["genel_iptal"]
        if self.ev(gi["kosul"], "genel_iptal"):
            adim = gi["hedef"]
            q["faz"], q["faz_t"] = 0, 0.0
            if "faz3_bitti" in gi["sifirla"]:
                q["faz3_bitti"] = 0
        t = tan[adim]
        onceki = adim
        if adim == ilk:
            if self.ev(c["baslatma"]["kosul"], "baslatma"):
                adim = t["sonraki"]
                q["faz"], q["faz_t"], q["faz3_bitti"] = 0, 0.0, 0
        elif "alt_fazlar" in t:                           # enjeksiyon: izinle surulen sureli fazlar
            alt = t["alt_fazlar"]
            iptal = any(self.ev(i["kosul"], "iptal") for i in t.get("iptal", [])
                        if not isinstance(i["kosul"], str) or " " not in i["kosul"])
            izin = bool(self.ev(t["izin"], "izin"))
            if iptal:
                adim, q["faz"] = ilk, 0                   # (kalip acildi)
            elif izin:
                if q["faz"] == 0:
                    q["faz"], q["faz_t"] = 1, 0.0
                q["faz_t"] += dt
                f = alt[q["faz"] - 1]
                if self._konum_modu() and "bitis_konum" in f:     # konum tabanli gecis (DB68.ENC), zaman asimi = alarm
                    if self._get("DB68.ENC") >= self._sayi(f["bitis_konum"]):
                        q["faz"] += 1
                        q["faz_t"] = 0.0
                    elif q["faz_t"] >= self._sayi(f["zaman_asimi"]):
                        q["enj_alarm"] = 1
                        adim, q["faz"] = ilk, 0
                elif q["faz_t"] >= self._sayi(f["sure"]):
                    if q["faz"] < len(alt):
                        q["faz"] += 1
                        q["faz_t"] = 0.0
                    else:
                        q["faz"] = 0
                        q["faz3_bitti"] = 1
                        adim = t["sonraki"]
            elif q["faz"] != 0:
                adim, q["faz"] = ilk, 0                   # izin vurus ortasinda kayboldu
        elif "maca" in t:                                 # maca adimi (sure tabanli, geri bildirim kanali yok)
            mc = t["maca"]
            q["adim_t"] += dt
            if self.ev(mc["izin"], "maca.izin"):
                q["maca_t"] += dt                         # sure yalniz izin varken birikir (kalip durumu uygun)
            sure = self._sayi(mc["sure"])
            if not self._maca_secili(mc) or q["maca_t"] >= sure:
                adim = t["sonraki"]
            elif q["adim_t"] >= sure * self._sayi(mc["zaman_asimi_carpan"]):
                q["maca_alarm"] = 1                       # zaman asimi: alarm + BOSTA'ya iptal
                adim, q["faz"] = ilk, 0
        elif self.ev(t["bitis"], "bitis." + adim):
            adim = t["sonraki"]
            if t.get("cikis_eylemi"):                     # cevrim sonu: sayac, yaglama tetigi
                q["cevrim"] += 1
                q["faz3_bitti"] = 0
                if q["cevrim"] % self._sayi(c["mafsal_yaglama"]["aralik_cevrim"]) == 0:
                    q["yag"], q["yag_t"] = 1, 0.0
        while adim != onceki and "maca" in tan[adim] and not self._maca_secili(tan[adim]["maca"]):
            adim = tan[adim]["sonraki"]                   # hic maca secili degil: adim ayni taramada gecilir
        if adim != q["adim"]:
            q["adim_t"], q["maca_t"] = 0.0, 0.0
        s["S.MACA_ALARM"] = q["maca_alarm"]
        s["S.ENJ_KONUM_ALARM"] = q["enj_alarm"]
        # --- adim gecisi yan etkileri
        pg, my = c["piston_geri"], c["mafsal_yaglama"]
        if adim != onceki:
            if onceki == pg["baslangic"].split()[0]:      # "ACMA adimi bitisi" -> sureli piston geri
                q["pg"], q["pg_t"] = 1, 0.0
            if "alt_fazlar" in tan[adim]:                 # bir sonraki ENJ girisi: yaglama penceresi kapanir
                q["yag"] = 0
        if q["pg"]:
            q["pg_t"] += dt
            if self._konum_modu():                        # konum tabanli bitis: ENC geri konumda; sure dolarsa alarm
                if self._get("DB68.ENC") <= self._sayi(pg["bitis_konum"]) + self._sayi(pg["tolerans"]):
                    q["pg"] = 0
                elif q["pg_t"] >= self._sayi(pg["zaman_asimi"]):
                    q["pg"], q["pg_alarm"] = 0, 1
            elif q["pg_t"] >= self._sayi(pg["sure"]):
                q["pg"] = 0
        if q["yag"]:
            q["yag_t"] += dt
            if q["yag_t"] >= self._sayi(my["sure"]):
                q["yag"] = 0
        q["adim"] = adim
        for a_ in c["adimlar"]:
            if a_.get("cikis"):
                s[a_["cikis"]] = int(adim == a_["ad"])
            for i, f in enumerate(a_.get("alt_fazlar", [])):
                s[f["cikis"]] = int(adim == a_["ad"] and q["faz"] == i + 1)
            if a_.get("bitis_cikisi"):
                s[a_["bitis_cikisi"]] = int(q["faz3_bitti"])
        s["S.PISTON_GERI_ALARM"] = q["pg_alarm"]
        s[pg["cikis"]] = int(q["pg"])
        s[my["cikis"]] = int(q["yag"])
        self.cur.update(s)
        s[c["piston_yaglama"]["cikis"]] = int(bool(self.ev(c["piston_yaglama"]["ifade"], "piston_yaglama")))
        s["S.OTO_ADIM"] = adim
        s["S.CEVRIM_SAYAC"] = q["cevrim"]
        return s

    # ------------------------------------------------------------------ tarama
    def step(self, dt_ms=10.0, girdi=None, zorla=None):
        if girdi:
            self.girdi.update(girdi)
        if zorla is not None:
            self.zorla = dict(zorla)
        self.t += dt_ms
        self.cur = {}
        # 1. HW (sabit sira)
        self._katman = "hw"
        for e in self.hw:
            v = self._tanim_deger(e)
            self.cur[e["id"]] = self.zorla.get(e["id"], v)
        # 2. DI geri bildirim
        for di, (hw, ters) in self.izleme.items():
            v = int(bool(self.cur[hw]) != ters) if hw in self.cur else int(bool(self._get(hw)) != ters)
            self.cur[di] = self.zorla.get(di, v)
        # 3. siralayici
        self._katman = "hw"          # siralayici kosullari: S.*/PLC sinyalleri onceki tarama degeri
        self.cur.update(self._sirala(dt_ms))
        self._katman = "plc"
        for k, v in list(self.zorla.items()):
            self.cur[k] = v
        # 4. PLC (tembel, bagimlilik sirasiyla)
        for n in self.plc:
            self._coz(n)
        self._get("S.HERHANGI_ALARM")
        self.prev = dict(self.cur)
        return self.cur

    # ------------------------------------------------------------------ turetilmis gozlemler
    def bobin(self, kanal):
        """DO7.* valf bobini: PLC cikisi VE valf beslemesi (E-stop -> tum valfler duser). S210A ozel."""
        v = self.prev
        if kanal == "DO7.05":
            return v["HW.S210A_bobin"]
        if kanal in self.maca_bobin:                       # maca cift solenoid: HW bobini (beslemeye VE karsi cikis kilidi)
            return v[self.maca_bobin[kanal]]
        return int(bool(v.get(kanal, 0)) and bool(v["HW.VALF_BESLEME"]))

    def aku_bosaltiyor(self):
        """S121 bobin polaritesine gore akumulator fiilen bosaliyor mu (P.S121_ENERJILI_DESARJ)."""
        b = self.bobin("DO7.15")
        return int(bool(b)) if self._param("P.S121_ENERJILI_DESARJ") else int(not b)

    def loto_adim(self, no):
        """loto.adimlar[] kaydi (dogrulama_sinyal, elle_dogrulama, elle_not ...)."""
        for e in self.cfg["loto"]["adimlar"]:
            if e["no"] == no:
                return e
        raise KeyError(f"LOTO adim {no} tanimli degil")

    def loto_adim_dogrula(self, no, elle_onay=None):
        """LOTO adim dogrulamasi (loto.adimlar[]): dogrulama_sinyal (S.LOTO_A<n>_OK) = 1 VE
        elle_dogrulama true ise operator onayi (elle_onay). elle_onay=None -> yalniz makine tarafi
        (sinyal); sinyal null (6-8) -> yalniz elle: elle_onay yoksa 0."""
        e = self.loto_adim(no)
        sin = e.get("dogrulama_sinyal")
        if sin is None:
            return int(bool(elle_onay))
        v = bool(self.prev.get(sin, 0))
        if e.get("elle_dogrulama") and elle_onay is not None:
            v = v and bool(elle_onay)
        return int(v)


# ---------------------------------------------------------------------- kapali dongu (Kademe 4 adim 2)
def _params_tum():
    with open(os.path.join(ROOT, "params", "params.json"), encoding="utf-8") as f:
        return json.load(f)


class KapaliDongu:
    """PLC cikislari (DO bobinleri, m.bobin) -> hareket modeli (konum/zaman) -> sensor/limit DI + DB68.ENC -> PLC.

    Sabitler: elektrik.json mantik.hareket_modeli (DESIGN ASSUMPTION, saha olcumu gerekir) + params.json kurslari.
    Birim: mafsal s 0 kapali..1 acik (lib/cevrim.py ile ayni), px plunger +X mm, ej itici mm (pozitif = ileri,
    cevrim.py'de ej negatif), ma maca 0 kavitede..1 cekili. hiz_olcek={"plunger":0.5,...} hizlari olcekler;
    ariza={"enc_sabit":0.0} ENC okumasini dondurur (sensor/kablo arizasi).
    Kural izleme (cevrim.py ile ayni uzay): plunger yalniz s=0, itici yalniz s=1, maca kalip durmadayken.
    Bilinen farklar mantik.hareket_modeli.bilinen_fark; etiket self.fark (FARK_*), kural ihlali self.ihlal (IHLAL_*).
    """

    def __init__(self, m, hiz_olcek=None, ariza=None):
        self.m = m
        self.h = m.mk["hareket_modeli"]
        P = _params_tum()
        self.kurs_mafsal = float(P["global"]["opening_stroke"])
        self.kurs_pl = float(P["parts"]["A52"]["dims"]["stroke"])
        a82 = P["parts"]["A82"]["dims"]
        self.kurs_ej = float(a82.get("ejector_box", {}).get("die_ejection_stroke", P["global"].get("die_ejection_stroke", 65.0)))
        self.kurs_ma = float(P["parts"]["A167"]["dims"]["stroke"])
        self.olcek = hiz_olcek or {}
        self.ariza = ariza or {}
        self.s, self.px, self.ej, self.ma = 1.0, 0.0, 0.0, [1.0] * 4
        self.fark, self.ihlal = set(), set()
        self.olay = []                       # (t_ms, adim, faz) adim/faz degisimleri
        self._son = None
        self.max_px = 0.0
        self.gecis = {}                      # "ADIM[.fazN]" -> ilk giris zamani (ms)
        self.gecis_durum = {}                # ayni anahtar -> (px, s, ej, ma[]) gecis anindaki hareket durumu
        self.girdi_ilk = {"DI4.09": 1, "DB68.PT2": self.h["PT2_bar"], "P.VURUS_KONUMU_GIRILDI": 1,
                          "DI5.01": 1, "DI5.03": 1, "DI9.04": 1, "DI5.14": 1, "DI5.15": 1, "DI5.16": 1, "DI5.17": 1,
                          "P.MAFSAL_YAGLAMA_SURE_ms": 0}
        m.girdi.update(self.girdi_ilk)
        self._sensor()

    def _v(self, ad, anahtar):
        return self.h[ad][anahtar] * self.olcek.get(ad, 1.0)

    def _sensor(self):
        h, g = self.h, self.m.girdi
        mm = self.s * self.kurs_mafsal
        g["AI10.1"] = mm
        g["DI5.08"] = int(mm <= h["mafsal"]["kilit_mm"])
        g["DI9.10"] = int(self.ej <= h["itici"]["limit_mm"])
        g["DI9.11"] = int(self.ej >= self.kurs_ej - h["itici"]["limit_mm"])
        g["DI9.16"] = int(self.px >= self.kurs_pl - h["plunger"]["ls2_mm"])
        if "enc_sabit" in self.ariza:
            g["DB68.ENC"] = self.ariza["enc_sabit"]
        else:
            r = h["enkoder"]["cozunurluk_mm"]
            g["DB68.ENC"] = round(self.px / r) * r

    def step(self, dt_ms=None):
        m, h = self.m, self.h
        dt_ms = dt_ms or h["tarama_ms"]
        dt = dt_ms / 1000.0
        b = m.bobin
        s0, px0, ej0, ma0 = self.s, self.px, self.ej, list(self.ma)
        # kalip (mafsal): kapama DO7.05, acma DO7.04
        if b("DO7.05") and not b("DO7.04"):
            self.s = max(0.0, self.s - dt / (h["mafsal"]["kapama_s"] / self.olcek.get("mafsal", 1.0)))
        elif b("DO7.04") and not b("DO7.05"):
            self.s = min(1.0, self.s + dt / (h["mafsal"]["acma_s"] / self.olcek.get("mafsal", 1.0)))
        # plunger: geri DO7.26; hizli DO7.01+DO7.11; yavas DO7.25; faz 3 DO7.10+DO7.12
        if b("DO7.26"):
            self.px -= self._v("plunger", "geri_mm_s") * dt
        elif b("DO7.01") and b("DO7.11"):
            self.px += self._v("plunger", "hizli_mm_s") * dt
        elif b("DO7.25"):
            self.px += self._v("plunger", "yavas_mm_s") * dt
        elif b("DO7.10") and b("DO7.12"):
            self.px += self._v("plunger", "faz3_mm_s") * dt
        self.px = min(max(self.px, 0.0), self.kurs_pl)       # strok sonu = kavite dolu / mekanik dayanak
        self.max_px = max(self.max_px, self.px)
        # itici A41: ileri DO7.13, geri DO7.14
        if b("DO7.13") and not b("DO7.14"):
            self.ej = min(self.kurs_ej, self.ej + self._v("itici", "hiz_mm_s") * dt)
        elif b("DO7.14") and not b("DO7.13"):
            self.ej = max(0.0, self.ej - self._v("itici", "hiz_mm_s") * dt)
        # maca n: in DO7.17+2n (0'a), out DO7.18+2n (1'e)
        for n in range(4):
            gir, cek = b(f"DO7.{17 + 2 * n}"), b(f"DO7.{18 + 2 * n}")
            d = self._v("maca", "hiz_mm_s") * dt / self.kurs_ma
            if gir and not cek:
                self.ma[n] = max(0.0, self.ma[n] - d)
            elif cek and not gir:
                self.ma[n] = min(1.0, self.ma[n] + d)
        self._kural(s0, px0, ej0, ma0)
        self._sensor()
        v = m.step(dt_ms)
        adim, faz = v["S.OTO_ADIM"], v.get("S.FAZ1", 0) * 1 + v.get("S.FAZ2", 0) * 2 + v.get("S.FAZ3", 0) * 3
        if (adim, faz) != self._son:
            self._son = (adim, faz)
            self.olay.append((m.t, adim, faz))
            anahtar = adim if not faz else f"{adim}.FAZ{faz}"
            if anahtar not in self.gecis:
                self.gecis[anahtar] = m.t
                self.gecis_durum[anahtar] = (self.px, self.s, self.ej, list(self.ma))
        if v.get("S.OTO_PISTON_GERI") and "OTO_PISTON_GERI" not in self.gecis:
            self.gecis["OTO_PISTON_GERI"] = m.t
            self.gecis_durum["OTO_PISTON_GERI"] = (self.px, self.s, self.ej, list(self.ma))
        return v

    def _kural(self, s0, px0, ej0, ma0):
        e = 1e-9
        adim = self._son[0] if self._son else "BOSTA"
        pg = bool(self.m.prev.get("S.OTO_PISTON_GERI", 0))
        acik_mm = self.s * self.kurs_mafsal
        kalip_hareket = abs(self.s - s0) > e
        if abs(self.px - px0) > e and self.s > e:
            self.fark.add("FARK_SIRA_PISTON_GERI") if pg else self.ihlal.add("IHLAL_PLUNGER_KALIP_ACIK")
        if kalip_hareket and self.px > 1.0:
            self.fark.add("FARK_SIRA_PISTON_GERI") if adim == "ACMA" else self.ihlal.add("IHLAL_KALIP_PLUNGER_ILERIDE")
        if abs(self.ej - ej0) > e and self.s < 1.0 - e:
            if acik_mm >= self.m._param("P.ITICI_ACIKLIK_MIN_mm"):
                self.fark.add("FARK_ACMA_300")
            else:
                self.ihlal.add("IHLAL_ITICI_KALIP_KAPALI")
        if any(abs(a - b_) > e for a, b_ in zip(self.ma, ma0)) and kalip_hareket:
            self.ihlal.add("IHLAL_MACA_KALIP_HAREKET")

    def calistir_cevrim(self, max_ms=60000, baslat=True):
        """Bir tam OTO cevrimi: HMI.OTO_BASLAT -> ... -> BOSTA (piston geri dahil). Sure ms dondurur (None = bitmedi)."""
        m = self.m
        n0 = m.prev.get("S.CEVRIM_SAYAC", 0)
        t0 = m.t
        if baslat:
            m.girdi["HMI.OTO_BASLAT"] = 1
        baslamis = False
        while m.t - t0 < max_ms:
            v = self.step()
            if v["S.OTO_ADIM"] != "BOSTA":
                baslamis = True
                m.girdi["HMI.OTO_BASLAT"] = 0
            if (baslamis and v["S.OTO_ADIM"] == "BOSTA" and not v["S.OTO_PISTON_GERI"]
                    and v["S.CEVRIM_SAYAC"] > n0):
                return m.t - t0
            if baslamis and v["S.OTO_ADIM"] == "BOSTA" and (v["S.ENJ_KONUM_ALARM"] or v["S.PISTON_GERI_ALARM"] or v["S.MACA_ALARM"]):
                return None
        return None
