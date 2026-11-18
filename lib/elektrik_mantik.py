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
                   "sayac": 0, "a_son": 0, "ofset_mm": None}
        self.hata_yok = True

    def _sayi(self, x):
        """'params.global.<ad>' -> params.global; P.<ad> / esik adi / sayi -> deger."""
        if isinstance(x, str) and x.startswith("params.global."):
            return self.G.get(x[len("params.global."):].split()[0], 0)   # sonrasi aciklama metni
        if isinstance(x, str) and x.startswith("zamanlar."):
            return self.mk["zamanlar"][x[len("zamanlar."):]]
        return self._deger(x)

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
                if q["faz_t"] >= self._sayi(alt[q["faz"] - 1]["sure"]):
                    if q["faz"] < len(alt):
                        q["faz"] += 1
                        q["faz_t"] = 0.0
                    else:
                        q["faz"] = 0
                        q["faz3_bitti"] = 1
                        adim = t["sonraki"]
            elif q["faz"] != 0:
                adim, q["faz"] = ilk, 0                   # izin vurus ortasinda kayboldu
        elif self.ev(t["bitis"], "bitis." + adim):
            adim = t["sonraki"]
            if t.get("cikis_eylemi"):                     # cevrim sonu: sayac, yaglama tetigi
                q["cevrim"] += 1
                q["faz3_bitti"] = 0
                if q["cevrim"] % self._sayi(c["mafsal_yaglama"]["aralik_cevrim"]) == 0:
                    q["yag"], q["yag_t"] = 1, 0.0
        # --- adim gecisi yan etkileri
        pg, my = c["piston_geri"], c["mafsal_yaglama"]
        if adim != onceki:
            if onceki == pg["baslangic"].split()[0]:      # "ACMA adimi bitisi" -> sureli piston geri
                q["pg"], q["pg_t"] = 1, 0.0
            if "alt_fazlar" in tan[adim]:                 # bir sonraki ENJ girisi: yaglama penceresi kapanir
                q["yag"] = 0
        if q["pg"]:
            q["pg_t"] += dt
            if q["pg_t"] >= self._sayi(pg["sure"]):
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
