"""elektrik_testleri.py - elektrik mantigi zorunlu senaryolari + negatif testler.

Kullanim: python3 checks/elektrik_testleri.py     (hata varsa cikis kodu 1)
Her senaryo: pozitif (gercek mantik gecmeli) + negatif (mantik BELLEKTE bozulur, test YAKALAMALI).
Dosya degistirilmez. Uzun dokum: out/elektrik_testleri.txt
"""
import copy
import os
import sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(ROOT, "lib"))
from elektrik_mantik import ElektrikMantik, KapaliDongu, yukle, teshis_kaydi   # noqa

DT = 10.0


# ---------------------------------------------------------------- yardimcilar
def yeni(mut=None):
    cfg = yukle()
    if mut:
        mut(cfg)
    return ElektrikMantik(cfg=cfg)


def tanim(cfg, id_):
    for e in cfg["mantik"]["donanim"] + cfg["mantik"]["plc"]:
        if e["id"] == id_:
            return e
    raise KeyError(id_)


def cikar(ex, hedef):
    """ifade agacindan 'hedef' elemanlarini (and/or listelerinden) siler; ton(x,ms) -> x yapmaz."""
    if isinstance(ex, list):
        out = [ex[0]] + [cikar(x, hedef) for x in ex[1:] if x != hedef]
        return out
    return ex


def ton_ac(ex):
    """ton(x, ms) -> x (zamanlayiciyi kaldir)."""
    if isinstance(ex, list):
        if ex[0] == "ton":
            return ton_ac(ex[1])
        return [ex[0]] + [ton_ac(x) if isinstance(x, list) else x for x in ex[1:]]
    return ex


def calistir(m, bekle_ms=8700):
    """Start bas-birak, yildiz->ucgen gecisi bitene kadar calistir."""
    m.girdi["HW.1B11A1"] = 1
    for _ in range(5):
        m.step(DT)
    m.girdi["HW.1B11A1"] = 0
    for _ in range(int(bekle_ms / DT)):
        m.step(DT)
    return m.prev


def adim(m, ms, **kw):
    v = None
    for _ in range(int(round(ms / DT))):
        v = m.step(DT, **kw)
    return v


class Sonuc:
    def __init__(self):
        self.hata = []

    def kos(self, kosul, mesaj):
        if not kosul:
            self.hata.append(mesaj)


# ---------------------------------------------------------------- senaryolar
def s1(m):
    r = Sonuc()
    v = calistir(m)
    r.kos(v["HW.KM1"] == 1, "start sonrasi KM1 cekmedi")
    adim(m, 500)
    r.kos(m.prev["HW.KM1"] == 1 and m.prev["S.MOTOR_CALISIYOR"] == 1, "start birakilinca motor calismaya devam etmedi (muhurleme)")
    # stop
    m.girdi["HW.1B12A"] = 0
    adim(m, 50)
    m.girdi["HW.1B12A"] = 1
    adim(m, 200)
    r.kos(m.prev["HW.KM1"] == 0, "stop motoru durdurmadi / stop birakilinca yeniden calisti")
    # E-stop (PLC calisirken) ve PLC arizasi (DO7.31 sabit 1) -> donanim yine durdurmali
    for etiket, zorla in (("PLC normal", {}), ("PLC ariza DO7.31=1", {"DO7.31": 1})):
        m.zorla = zorla
        calistir(m)
        r.kos(m.prev["HW.KM1"] == 1, f"[{etiket}] tekrar start calismadi")
        m.girdi["HW.ST2_1"] = 0
        adim(m, 50)
        durdu = m.prev["HW.KM1"] == 0 and m.prev["HW.KM2"] == 0 and m.prev["HW.KM3"] == 0
        m.girdi["HW.ST2_1"] = 1
        adim(m, 200)
        r.kos(durdu, f"[{etiket}] E-stop motoru durdurmadi")
        r.kos(m.prev["HW.KM1"] == 0, f"[{etiket}] E-stop birakilinca motor kendiliginden basladi")
    m.zorla = {}
    return r.hata


def s2(m):
    r = Sonuc()
    m.girdi["HW.1B11A1"] = 1
    for _ in range(5):
        m.step(DT)
    m.girdi["HW.1B11A1"] = 0
    t3_dusus = t2_cekme = None
    onceki3 = 0
    for i in range(int(10000 / DT)):
        v = m.step(DT)
        if v["HW.KM2"] and v["HW.KM3"]:
            r.hata.append(f"KM2 ve KM3 ayni taramada 1 (t={m.t} ms)")
            break
        if onceki3 and not v["HW.KM3"] and t3_dusus is None:
            t3_dusus = m.t
        if v["HW.KM2"] and t2_cekme is None:
            t2_cekme = m.t
        onceki3 = v["HW.KM3"]
    r.kos(t3_dusus is not None and t2_cekme is not None, "yildiz->ucgen gecisi gerceklesmedi")
    if t3_dusus is not None and t2_cekme is not None:
        r.kos(t2_cekme - t3_dusus >= 50, f"KM3 dususu ile KM2 cekmesi arasi {t2_cekme - t3_dusus} ms < 50 ms")
    # PLC arizasi + gecis sirasinda kisa E-stop darbesi: yine hicbir taramada ikisi birden olmamali
    m2 = ElektrikMantik(cfg=m.cfg)
    m2.zorla = {"DO7.31": 1}
    m2.girdi["HW.1B11A1"] = 1
    for _ in range(5):
        m2.step(DT)
    m2.girdi["HW.1B11A1"] = 0
    for i in range(int(10000 / DT)):
        v = m2.step(DT)
        if v["HW.KM2"] and v["HW.KM3"]:
            r.hata.append("[PLC ariza] KM2 ve KM3 ayni taramada 1")
            break
    return r.hata


def s3(m):
    r = Sonuc()
    calistir(m)
    adim(m, 50)
    m.zorla = {"DO7.05": 1}          # PLC cikisi zorla 1 (PLC hatasi)
    adim(m, 50)
    r.kos(m.prev["HW.S210A_bobin"] == 1, "kapilar kapaliyken DO7.05=1 bobini calistirmadi (pozitif kontrol)")
    for ad in ("HW.ON_KAPI_L2", "HW.ARKA_KAPI_L2"):
        m.girdi[ad] = 0
        adim(m, 50)
        r.kos(m.prev["HW.S210A_bobin"] == 0, f"{ad}=0 (kapi acik) iken DO7.05=1 -> S210A bobini 1")
        r.kos(m.prev["HW.KA9"] == 0, f"{ad}=0 iken KA9 1")
        m.girdi[ad] = 1
    m.girdi["HW.ST1_1"] = 0
    adim(m, 50)
    r.kos(m.prev["HW.S210A_bobin"] == 0, "E-stop iken S210A bobini 1 (KA_ES)")
    m.girdi["HW.ST1_1"] = 1
    return r.hata


def s4(m):
    r = Sonuc()
    adim(m, 50)
    m.girdi["DI5.02"] = 0            # on kapi limit 1 acik, limit 2 (HW) kapali -> uyumsuz
    adim(m, 480)
    r.kos(m.prev["S.KAPI_UYUMSUZ"] == 0, "uyumsuzluk 500 ms dolmadan alarm verdi")
    adim(m, 40)
    r.kos(m.prev["S.KAPI_UYUMSUZ"] == 1, "500 ms sonra uyumsuzluk alarmi yok")
    r.kos(m.prev["DO4.15"] == 1, "alarm lambasi yanmadi")
    m.girdi["DI5.02"] = 1            # uyumsuzluk bitti
    adim(m, 100)
    r.kos(m.prev["S.KAPI_UYUMSUZ"] == 1, "alarm muhurlu degil (uyumsuzluk bitince dustu)")
    r.kos(m.prev["S.KAPILAR_KAPALI"] == 0, "alarm varken kapilar kapali sayildi")
    m.girdi["HMI.RESET"] = 1
    adim(m, 30)
    m.girdi["HMI.RESET"] = 0
    adim(m, 50)
    r.kos(m.prev["S.KAPI_UYUMSUZ"] == 0, "reset alarmi silmedi")
    # kisa uyumsuzluk (< 500 ms) muhurlenmemeli; arka kapi cifti de izlenmeli
    m.girdi["DI5.04"] = 0
    adim(m, 300)
    m.girdi["DI5.04"] = 1
    adim(m, 100)
    r.kos(m.prev["S.KAPI_UYUMSUZ"] == 0, "300 ms'lik gecici uyumsuzluk alarm verdi")
    m.girdi["DI5.04"] = 0
    adim(m, 520)
    r.kos(m.prev["S.KAPI_UYUMSUZ"] == 1, "arka kapi limit1/limit2 uyumsuzlugu yakalanmadi")
    return r.hata


def enj_hazirla(m, **ek):
    calistir(m)
    m.girdi.update({"DI4.09": 1, "DI5.08": 1, "DB68.PT2": 150, "P.VURUS_KONUMU_GIRILDI": 1})
    m.girdi.update(ek)
    adim(m, 50)


def s5(m):
    r = Sonuc()
    enj_hazirla(m)
    r.kos(m.prev["S.ENJ_IZIN"] == 1, "hazirlik: istek yokken enjeksiyon izni 0 (pozitif kontrol)")
    r.kos(m.prev["S.DESARJ_ISTEGI"] == 0, "hazirlik: S121 istegi var")
    # operator istegi
    m.girdi["HMI.OTO_BASLAT"] = 1
    adim(m, 30)
    r.kos(m.prev["DO7.25"] == 1, "hazirlik: cevrimde 1. faz (DO7.25) baslamadi")
    v = m.step(DT, girdi={"HMI.DESARJ": 1})
    r.kos(v["S.DESARJ_ISTEGI"] == 1 and v["S.ENJ_IZIN"] == 0, "operator S121 istegi varken enjeksiyon izni 0 olmadi")
    r.kos(v["DO7.25"] == 0 and v["S.ENJ_AKTIF"] == 0, "S121 istegi ayni taramada enjeksiyon cikisini kesmedi")
    # kutup: varsayilan 0 -> enerjisiz = bosalt
    adim(m, 30)
    r.kos(m.aku_bosaltiyor() == 1, "P.S121_ENERJILI_DESARJ=0 iken akumulator bosalmiyor")
    m.girdi["HMI.DESARJ"] = 0
    m.girdi["HMI.OTO_BASLAT"] = 0
    adim(m, 50)
    # diger istek kaynaklari
    for etiket, girdi, geri in (("LOTO", {"HMI.LOTO_BASLAT": 1}, {"HMI.LOTO_BASLAT": 0, "HMI.LOTO_BITIR": 1}),
                                ("E-stop", {"HW.ST4_1": 0}, {"HW.ST4_1": 1}),
                                ("yag seviye alarmi", {"DI5.13": 0}, {"DI5.13": 1})):
        v = m.step(DT, girdi=girdi)
        v = m.step(DT)
        r.kos(v["S.DESARJ_ISTEGI"] == 1 and v["S.ENJ_IZIN"] == 0, f"{etiket} istegi varken enjeksiyon izni 0 olmadi")
        m.girdi.update(geri)
        adim(m, 50)
        m.girdi["HMI.LOTO_BITIR"] = 0
        if etiket == "E-stop":
            calistir(m)           # E-stop motoru da durdurdu
            m.girdi.update({"DI4.09": 1})
    # fail-safe kutup: E-stop'ta valf beslemesi gider; P=0 -> bosaltir, P=1 (DCC630 yorumu) -> bosaltmaz
    m3 = _klon(m)
    calistir(m3)
    m3.girdi["HW.ST1_1"] = 0
    adim(m3, 50)
    r.kos(m3.aku_bosaltiyor() == 1, "E-stop'ta (P=0) akumulator bosalmiyor")
    m3.girdi.update({"HW.ST1_1": 1, "P.S121_ENERJILI_DESARJ": 1})
    adim(m3, 50)
    m3.girdi["HW.ST1_1"] = 0
    adim(m3, 50)
    r.kos(m3.aku_bosaltiyor() == 0, "P=1 iken E-stop'ta bosaltma beklenmiyordu (celiski belgelemesi)")
    return r.hata


def s6(m):
    r = Sonuc()
    calistir(m)
    ky = {"DI4.08": 1, "DI4.14": 1}
    m.girdi.update(ky)
    m.girdi["DI9.07"] = 1                    # kalin jog
    adim(m, 50)
    r.kos(m.prev["DO7.30"] == 1 and m.prev["HW.KM4"] == 1, "kalin jog KM4'u calistirmadi (pozitif kontrol)")
    # KM5 de istenirse (iki jog birden) ve PLC arizasi: DO7.29 ve DO7.30 zorla 1
    m.girdi["DI9.08"] = 1
    for etiket, zorla in (("PLC normal", {}), ("PLC ariza DO7.29=DO7.30=1", {"DO7.29": 1, "DO7.30": 1})):
        m.zorla = zorla
        for _ in range(100):
            v = m.step(DT)
            if v["HW.KM4"] and v["HW.KM5"]:
                r.hata.append(f"[{etiket}] KM4 ve KM5 ayni taramada 1")
                break
    m.zorla = {}
    m.girdi["DI9.08"] = 0
    adim(m, 50)
    # uc limit: kalin limit NC acilinca KM4 duser (PLC ve bobin yolu)
    m.girdi["HW.LS_KALIN_NC"] = 0
    adim(m, 30)
    r.kos(m.prev["DO7.30"] == 0 and m.prev["HW.KM4"] == 0, "kalin uc limitte KM4 dusmedi")
    # PLC arizasi: DO7.30 sabit 1, donanim limiti yine kesmeli
    m.zorla = {"DO7.30": 1}
    adim(m, 30)
    r.kos(m.prev["HW.KM4"] == 0, "[PLC ariza] kalin uc limit bobin yolunda KM4'u kesmedi")
    m.zorla = {}
    m.girdi.update({"HW.LS_KALIN_NC": 1, "DI9.07": 0, "DI9.08": 1})
    adim(m, 50)
    r.kos(m.prev["HW.KM5"] == 1, "ince jog KM5'i calistirmadi (pozitif kontrol)")
    m.girdi["HW.LS_INCE_NC"] = 0
    adim(m, 30)
    r.kos(m.prev["DO7.29"] == 0 and m.prev["HW.KM5"] == 0, "ince uc limitte KM5 dusmedi")
    m.zorla = {"DO7.29": 1}
    adim(m, 30)
    r.kos(m.prev["HW.KM5"] == 0, "[PLC ariza] ince uc limit bobin yolunda KM5'i kesmedi")
    m.zorla = {}
    return r.hata


def s7(m):
    r = Sonuc()
    calistir(m)
    r.kos(m.prev["DO7.31"] == 1 and m.prev["HW.KM1"] == 1, "hazirlik: pompa calismiyor")
    m.girdi.update({"DI4.09": 1, "DI5.08": 1, "DB68.PT2": 150, "P.VURUS_KONUMU_GIRILDI": 1})
    adim(m, 50)
    m.girdi["DI5.13"] = 0                     # yag seviyesi alarmi
    adim(m, 30)
    v = m.prev
    r.kos(v["AL_YAG_SEVIYE"] == 1, "AL_YAG_SEVIYE olusmadi")
    r.kos(v["DO7.31"] == 0, "yag seviye alarminda KA2 (DO7.31) dusmedi")
    r.kos(v["HW.KM1"] == 0 and v["HW.KM2"] == 0 and v["HW.KM3"] == 0, "KA2 dusunce pompa kontaktorleri dusmedi")
    r.kos(v["S.DESARJ_ISTEGI"] == 1 and v["S.ENJ_IZIN"] == 0, "yag seviye alarminda desarj istegi/enjeksiyon yasagi yok")
    r.kos(v["DO4.15"] == 1, "alarm lambasi yok")
    m.girdi["DI5.13"] = 1
    adim(m, 300)
    r.kos(m.prev["HW.KM1"] == 0, "alarm gidince pompa kendiliginden basladi")
    return r.hata


def s8(m):
    r = Sonuc()
    calistir(m)
    m.girdi.update({"HMI.LOTO_BASLAT": 1, "DI9.12": 1, "DB68.PT2": 150})
    adim(m, 50)
    r.kos(m.prev["S.LOTO_MODU"] == 1 and m.prev["S.DESARJ_ISTEGI"] == 1, "LOTO modu desarj istegi uretmedi")
    r.kos(m.loto_adim_dogrula(4) == 0, "PT2=150 bar iken LOTO adim 4 gecti")
    for p in (60, 10):
        m.girdi["DB68.PT2"] = p
        adim(m, 200)
        r.kos(m.prev["S.AKU_BOS"] == 0, f"PT2={p} bar iken S.AKU_BOS 1")
    m.girdi["DB68.PT2"] = 1.5                 # < 2 bar
    adim(m, 9890)
    r.kos(m.prev["S.AKU_BOS"] == 0, "PT2<2 bar 10 s dolmadan S.AKU_BOS 1")
    adim(m, 130)
    r.kos(m.prev["S.AKU_BOS"] == 1, "PT2<2 bar 10 s sonra S.AKU_BOS 0")
    r.kos(m.loto_adim_dogrula(4) == 1, "S.AKU_BOS ve DV1 acik iken adim 4 dogrulanmadi")
    m.girdi["DI9.12"] = 0
    adim(m, 20)
    r.kos(m.loto_adim_dogrula(4) == 0, "DV1 kapaliyken adim 4 gecti")
    m.girdi["DI9.12"] = 1
    # basinc 2 bar'in ustune cikarsa sayac sifirlanir
    m.girdi["DB68.PT2"] = 5
    adim(m, 50)
    r.kos(m.prev["S.AKU_BOS"] == 0, "PT2 yeniden yukselince S.AKU_BOS dusmedi")
    m.girdi["DB68.PT2"] = 1.0
    adim(m, 5000)
    r.kos(m.prev["S.AKU_BOS"] == 0, "yeniden dususte 10 s beklenmedi (zamanlayici sifirlanmadi)")
    adim(m, 5100)
    r.kos(m.prev["S.AKU_BOS"] == 1, "ikinci dususte 10 s sonra S.AKU_BOS 0")
    return r.hata


# ---------------------------------------------------------------- bozucular (negatif testler)
def mut_s1a(cfg):   # muhurleme kaldir: start || KM1 -> start
    t = tanim(cfg, "HW.L15")
    t["ifade"] = [("HW.1B11A1" if (isinstance(x, list) and x[0] == "or") else x) for x in t["ifade"]]


def mut_s1b(cfg):   # donanim zincirinden stop + E-stop'u cikar
    t = tanim(cfg, "HW.L15")
    t["ifade"] = cikar(cikar(t["ifade"], "HW.ESTOP_OK"), "HW.1B12A")


def mut_s2a(cfg):   # olu zaman + NC kilit kaldir
    t = tanim(cfg, "HW.KM2")
    t["ifade"] = ton_ac(cikar(t["ifade"], ["not", "HW.KM3"]))


def mut_s2b(cfg):   # yildiz kontaktoru ucgen sonrasi da kalir, kilitler yok
    tanim(cfg, "HW.KM3")["ifade"] = ["and", "HW.L15"]
    t = tanim(cfg, "HW.KM2")
    t["ifade"] = ton_ac(cikar(t["ifade"], ["not", "HW.KM3"]))


def mut_s3a(cfg):
    t = tanim(cfg, "HW.S210A_bobin")
    t["ifade"] = cikar(t["ifade"], "HW.KA9")


def mut_s3b(cfg):   # kapi limitleri paralel kopru
    tanim(cfg, "HW.KA9")["ifade"] = ["or", "HW.ON_KAPI_L2", "HW.ARKA_KAPI_L2"]


def mut_s4a(cfg):
    tanim(cfg, "S.KAPI_UYUMSUZ")["muhur"] = False


def mut_s4b(cfg):
    t = tanim(cfg, "S.KAPI_UYUMSUZ")
    t["ifade"][-1] = 100


def mut_s5a(cfg):
    t = tanim(cfg, "S.ENJ_IZIN")
    t["ifade"] = cikar(t["ifade"], ["not", "S.DESARJ_ISTEGI"])


def mut_s5b(cfg):
    t = tanim(cfg, "S.DESARJ_ISTEGI")
    t["ifade"] = cikar(t["ifade"], "S.LOTO_MODU")


def mut_s6a(cfg):
    for ad, hedef in (("HW.KM4", "HW.KM5"), ("HW.KM5", "HW.KM4")):
        t = tanim(cfg, ad)
        t["ifade"] = cikar(t["ifade"], ["not", hedef])


def mut_s6b(cfg):
    for ad, hedef in (("HW.KM4", "HW.LS_KALIN_NC"), ("HW.KM5", "HW.LS_INCE_NC")):
        t = tanim(cfg, ad)
        t["ifade"] = cikar(t["ifade"], hedef)


def mut_s6c(cfg):   # PLC tarafinda da uc limit ve karsilikli kilit yok
    for ad, hedef, k in (("DO7.30", "DI5.06", ["not", "DO7.29"]), ("DO7.29", "DI5.05", ["not", "DO7.30"])):
        t = tanim(cfg, ad)
        t["ifade"] = cikar(cikar(t["ifade"], hedef), k)


def mut_s7(cfg):
    t = tanim(cfg, "DO7.31")
    t["ifade"] = cikar(t["ifade"], "DI5.13")


def mut_s8a(cfg):
    t = tanim(cfg, "S.AKU_BOS")
    t["ifade"][-1] = 1000


def mut_s8b(cfg):   # esik karsilastirmasi ters
    t = tanim(cfg, "S.AKU_BOS")
    t["ifade"][1][0] = "ge"


def _oto_hazirla(m):
    calistir(m)
    # eski senaryolar (S9..S15) sure tabanli yedek modda: ENC beslenmez (konum tabanli mod S16..S19'da)
    m.girdi.update({"DI4.09": 1, "DB68.PT2": 150, "P.VURUS_KONUMU_GIRILDI": 1, "P.ENC_BILDIRIM": 0})


def _cevrim(m, r, tur):
    """Bir tam OTO cevrimi surer; sureleri ve piston geri/yaglama davranisini dogrular."""
    m.girdi["HMI.OTO_BASLAT"] = 1
    adim(m, 30)
    r.kos(m.prev["S.OTO_ADIM"] == "KAPAMA", f"[{tur}] baslatma KAPAMA'ya gecmedi")
    m.girdi.update({"DI5.08": 1})
    adim(m, 30)
    r.kos(m.prev["S.OTO_ADIM"] == "ENJ", f"[{tur}] kalip kapali -> ENJ gecmedi")
    r.kos(m.prev["S.YAGLAMA_ZAMANI"] == 0, f"[{tur}] ENJ girisinde yaglama penceresi kapanmadi")
    return adim(m, 100)


def s9(m):
    r = Sonuc()
    _oto_hazirla(m)
    m.girdi["P.MAFSAL_YAGLAMA_SURE_ms"] = 0
    P = m.P
    yag_n = m.mk["zamanlar"]["yaglama_aralik_cevrim"]
    for tur in range(1, yag_n + 1):
        m.girdi["HMI.OTO_BASLAT"] = 1
        adim(m, 30)
        m.girdi["DI5.08"] = 1
        adim(m, 30)
        r.kos(m.prev["S.OTO_ADIM"] == "ENJ", f"tur {tur}: ENJ'ye gecmedi")
        if m.prev["S.OTO_ADIM"] != "ENJ":
            return r.hata
        r.kos(m.prev["S.FAZ1"] == 1, f"tur {tur}: FAZ1 baslamadi")
        adim(m, P["P.FAZ1_SURE_ms"] + 20)
        r.kos(m.prev["S.FAZ2"] == 1, f"tur {tur}: FAZ2'ye gecmedi")
        adim(m, P["P.FAZ2_SURE_ms"] + 20)
        r.kos(m.prev["S.FAZ3"] == 1, f"tur {tur}: FAZ3'e gecmedi")
        adim(m, P["P.FAZ3_SURE_ms"] + 20)
        r.kos(m.prev["S.OTO_ADIM"] == "ACMA" and m.prev["S.FAZ3_BITTI"] == 1, f"tur {tur}: ACMA/FAZ3_BITTI yok")
        r.kos(m.prev["S.OTO_PISTON_GERI"] == 0, f"tur {tur}: piston geri ACMA boyunca acildi (karar: ACMA bitisinden)")
        m.girdi.update({"DI5.08": 0, "AI10.1": P["P.ITICI_ACIKLIK_MIN_mm"] + 1})
        adim(m, 20)
        r.kos(m.prev["S.OTO_ADIM"] == "ITICI_ILERI" and m.prev["S.OTO_PISTON_GERI"] == 1,
              f"tur {tur}: ACMA bitisinde piston geri baslamadi")
        m.girdi["DI9.11"] = 1
        m.girdi["DI9.10"] = 0
        adim(m, 20)
        m.girdi.update({"DI9.11": 0, "DI9.10": 1})
        adim(m, 20)
        r.kos(m.prev["S.OTO_ADIM"] == "BOSTA" and m.prev["S.CEVRIM_SAYAC"] == tur, f"tur {tur}: cevrim sayaci artmadi")
        # piston geri bitmeden yeni cevrim yok
        r.kos(m.prev["S.OTO_PISTON_GERI"] == 1, f"tur {tur}: piston geri sure dolmadan bitti")
        m.girdi["HMI.OTO_BASLAT"] = 1
        adim(m, 100)
        r.kos(m.prev["S.OTO_ADIM"] == "BOSTA", f"tur {tur}: piston geri bitmeden yeni cevrim basladi")
        adim(m, P["P.PISTON_GERI_SURE_ms"])
        r.kos(m.prev["S.OTO_PISTON_GERI"] == 0, f"tur {tur}: piston geri sure sonunda kapanmadi")
        if tur < yag_n:
            r.kos(m.prev["S.YAGLAMA_ZAMANI"] == 0, f"tur {tur}: yaglama erken")
        m.girdi["HMI.OTO_BASLAT"] = 0
        m.girdi["DI5.08"] = 0
    # 10. cevrimde yaglama tetiklenmeli ve sureli bitmeli (sure 0 -> ayni taramada biter; ayri test asagida)
    return r.hata


def s9b(m):
    """Mafsal yaglama suresi: 10. cevrim sonunda yanar, P.MAFSAL_YAGLAMA_SURE_ms sonra soner."""
    r = Sonuc()
    _oto_hazirla(m)
    n = m.mk["zamanlar"]["yaglama_aralik_cevrim"]
    m.sq["cevrim"] = n - 1
    _cevrim(m, r, "yaglama")
    P = m.P
    m.girdi["DB68.PT2"] = 150
    adim(m, P["P.FAZ1_SURE_ms"] + P["P.FAZ2_SURE_ms"] + P["P.FAZ3_SURE_ms"] + 100)
    m.girdi.update({"DI5.08": 0, "AI10.1": P["P.ITICI_ACIKLIK_MIN_mm"] + 1})
    adim(m, 20)
    m.girdi["DI9.11"] = 1
    adim(m, 20)
    m.girdi.update({"DI9.11": 0, "DI9.10": 1})
    m.girdi["HMI.OTO_BASLAT"] = 0
    adim(m, 20)
    r.kos(m.prev["S.CEVRIM_SAYAC"] == n and m.prev["S.YAGLAMA_ZAMANI"] == 1, "N. cevrim sonunda yaglama yanmadi")
    sure = yukle()["mantik"]["ifade_dili"]["parametreler"]["P.MAFSAL_YAGLAMA_SURE_ms"]   # beklenen: JSON karari
    adim(m, sure - 500)
    r.kos(m.prev["S.YAGLAMA_ZAMANI"] == 1, "mafsal yaglama sure dolmadan sondu")
    adim(m, 700)
    r.kos(m.prev["S.YAGLAMA_ZAMANI"] == 0, "mafsal yaglama sure dolunca sonmedi (suresiz)")
    return r.hata


def s10(m):
    """A97 sayaci (baslangic = die_height_current, yon kurali), FKAP esigi, LOTO elle adimlar."""
    r = Sonuc()
    calistir(m)
    G, mm = m.G, m.P["P.mm_per_darbe"]
    adim(m, 20)
    r.kos(abs(m.prev["S.KY_SAYAC_MM"] - G["die_height_current"]) < 1e-9, "A97 sayaci die_height_current'tan baslamadi")
    for _ in range(3):                            # B=0: kalin (+)
        m.girdi.update({"DI9.01": 1, "DI9.02": 0})
        adim(m, 20)
        m.girdi["DI9.01"] = 0
        adim(m, 20)
    r.kos(abs(m.prev["S.KY_SAYAC_MM"] - (G["die_height_current"] + 3 * mm)) < 1e-9, "B=0 yonunde +3 darbe yanlis")
    m.girdi.update({"DI9.01": 1, "DI9.02": 1})    # B=1: ince (-)
    adim(m, 20)
    r.kos(abs(m.prev["S.KY_SAYAC_MM"] - (G["die_height_current"] + 2 * mm)) < 1e-9, "B=1 yonunde -1 darbe yanlis")
    # FKAP: sensor yokken DI5.08 yeterli; sensor varken > esik
    m.girdi["DI5.08"] = 1
    adim(m, 20)
    r.kos(m.prev["S.KILITLI_KUVVET_ALTINDA"] == 1, "sensor yok, DI5.08=1: kuvvet altinda 0")
    m.girdi.update({"P.KAPAMA_KUVVET_SENSORU_VAR": 1, "DB68.FKAP": 30})
    adim(m, 20)
    r.kos(m.prev["S.KILITLI_KUVVET_ALTINDA"] == 0, "sensor var, FKAP=30 kN (<50): kuvvet altinda 1")
    m.girdi["DB68.FKAP"] = 60
    adim(m, 20)
    r.kos(m.prev["S.KILITLI_KUVVET_ALTINDA"] == 1, "sensor var, FKAP=60 kN (>50): kuvvet altinda 0")
    # LOTO: 6-8 yalniz elle
    for no in (6, 7, 8):
        r.kos(m.loto_adim_dogrula(no) == 0, f"LOTO adim {no} elle onaysiz gecti")
        r.kos(m.loto_adim_dogrula(no, elle_onay=1) == 1, f"LOTO adim {no} elle onayla gecmedi")
    r.kos(m.loto_adim_dogrula(4, elle_onay=0) == 0, "LOTO adim 4 elle onay reddedilince gecti")
    return r.hata


def mut_s9a(cfg):      # piston geri ACMA boyunca
    for a in cfg["mantik"]["siralayici"]["adimlar"]:
        if a["ad"] == "ACMA":
            a["bitis"] = ["and", ["ge", "AI10.1", "P.ITICI_ACIKLIK_MIN_mm"], ["not", "DI5.08"]]
    cfg["mantik"]["siralayici"]["piston_geri"]["baslangic"] = "BOSTA"


def mut_s9b(cfg):      # yeni cevrim piston geri bitmeden baslayabilir
    k = cfg["mantik"]["siralayici"]["baslatma"]["kosul"]
    cfg["mantik"]["siralayici"]["baslatma"]["kosul"] = [k[0]] + [x for x in k[1:] if x != ["not", "S.OTO_PISTON_GERI"]]


def mut_s9c(cfg):      # yaglama suresiz
    cfg["mantik"]["ifade_dili"]["parametreler"]["P.MAFSAL_YAGLAMA_SURE_ms"] = 60000


def mut_s10a(cfg):
    cfg["mantik"]["siralayici"]["a97_sayac"]["yon_kurali"] = {"B_0": -1, "B_1": 1}


def mut_s10b(cfg):
    cfg["mantik"]["esikler"]["FKAP_kilitli_esik_kN"] = 0


# ---------------------------------------------------------------- maca (core) adimlari (Kademe 4 adim 1)
GIR = ["DO7.17", "DO7.19", "DO7.21", "DO7.23"]     # core1..4 in
CEK = ["DO7.18", "DO7.20", "DO7.22", "DO7.24"]     # core1..4 out
SEC = ["DI5.14", "DI5.15", "DI5.16", "DI5.17"]     # VARSAYIM: 1 = maca otomatik cevrimde kullanilir


def _maca_cikislar(v):
    return [v.get(k, 0) for k in GIR + CEK]


def _maca_hazirla(m, secili=(0, 2), kalip_acik=True):
    _oto_hazirla(m)
    m.girdi["P.MAFSAL_YAGLAMA_SURE_ms"] = 0
    for i in secili:
        m.girdi[SEC[i]] = 1
    m.girdi.update({"DI5.08": 0, "AI10.1": 100 if kalip_acik else 0, "DI9.10": 1, "DI9.11": 0})


def s12(m):
    """Tam cevrim sirasi: BOSTA -> MACA_GIR -> KAPAMA -> ENJ -> MACA_CEK -> ACMA; gir yalniz kalip acikken, cek kalip kapaliyken."""
    r = Sonuc()
    _maca_hazirla(m, secili=(0, 2), kalip_acik=False)
    P = m.P
    sure = P["P.MACA_SURE_ms"]
    m.girdi["HMI.OTO_BASLAT"] = 1
    adim(m, 100)
    r.kos(m.prev["S.OTO_ADIM"] == "MACA_GIR", "baslatma MACA_GIR'e gecmedi")
    r.kos(m.prev["DO7.17"] == 0 and m.prev["DO7.21"] == 0, "kalip KAPALI iken maca gir cikisi 1")
    m.girdi["AI10.1"] = 100
    adim(m, 30)
    v = m.prev
    r.kos(v["DO7.17"] == 1 and v["DO7.21"] == 1, "kalip acik: secili maca(lar) (1,3) gir cikisi yok")
    r.kos(v["DO7.19"] == 0 and v["DO7.23"] == 0, "secili olmayan maca (2,4) girdi")
    r.kos(all(v[k] == 0 for k in CEK), "MACA_GIR sirasinda cek cikisi 1")
    r.kos(m.bobin("DO7.17") == 1 and m.bobin("DO7.21") == 1 and m.bobin("DO7.19") == 0, "gir bobinleri (HW) yanlis")
    adim(m, sure - 250)
    r.kos(m.prev["S.OTO_ADIM"] == "MACA_GIR", "MACA_GIR P.MACA_SURE_ms dolmadan bitti")
    adim(m, 400)
    r.kos(m.prev["S.OTO_ADIM"] == "KAPAMA" and not any(_maca_cikislar(m.prev)), "sure sonunda KAPAMA'ya gecilmedi / maca cikisi acik kaldi")
    m.girdi["DI5.08"] = 1
    adim(m, 30)
    r.kos(m.prev["S.OTO_ADIM"] == "ENJ", "kalip kapali -> ENJ gecmedi")
    r.kos(not any(_maca_cikislar(m.prev)), "ENJ sirasinda maca cikisi 1")
    adim(m, P["P.FAZ1_SURE_ms"] + P["P.FAZ2_SURE_ms"] + P["P.FAZ3_SURE_ms"] + 60)
    v = m.prev
    r.kos(v["S.OTO_ADIM"] == "MACA_CEK" and v["S.FAZ3_BITTI"] == 1, "ENJ sonrasi MACA_CEK'e gecilmedi (ACMA'ya atladi?)")
    r.kos(v["DO7.18"] == 1 and v["DO7.22"] == 1 and v["DO7.20"] == 0 and all(v[k] == 0 for k in GIR), "MACA_CEK cikislari yanlis")
    r.kos(m.bobin("DO7.18") == 1 and m.bobin("DO7.17") == 0, "cek bobinleri (HW) yanlis")
    m.girdi["DI5.08"] = 0                      # kalip kapali degil -> cek cikisi kesilir
    adim(m, 30)
    r.kos(m.prev["DO7.18"] == 0 and m.prev["DO7.22"] == 0, "kalip KAPALI degilken maca cek cikisi 1")
    m.girdi["DI5.08"] = 1
    adim(m, 30)
    r.kos(m.prev["DO7.18"] == 1, "kalip tekrar kapali: cek cikisi donmedi")
    adim(m, sure - 250)
    r.kos(m.prev["S.OTO_ADIM"] == "MACA_CEK", "MACA_CEK sure dolmadan bitti (ACMA erken)")
    adim(m, 500)
    r.kos(m.prev["S.OTO_ADIM"] == "ACMA" and not any(_maca_cikislar(m.prev)), "MACA_CEK sonunda ACMA'ya gecilmedi / cikis acik kaldi")
    r.kos(m.prev["S.OTO_ACMA_ADIMI"] == 1, "ACMA adimi cikisi yok")
    return r.hata


def s13(m):
    """Secici (DI5.14..17) kapali: hic secili yok -> maca adimlari atlanir; yalniz secili maca hareket eder."""
    r = Sonuc()
    _maca_hazirla(m, secili=(), kalip_acik=True)
    m.girdi["HMI.OTO_BASLAT"] = 1
    adim(m, 30)
    r.kos(m.prev["S.OTO_ADIM"] in ("KAPAMA", "ENJ"), "secici hepsi kapali: MACA_GIR atlanmadi")
    r.kos(not any(_maca_cikislar(m.prev)), "secici kapali: maca cikisi 1")
    m2 = ElektrikMantik(cfg=m.cfg)      # ayni (varsa bozulmus) mantik
    _maca_hazirla(m2, secili=(1,), kalip_acik=True)
    m2.girdi["HMI.OTO_BASLAT"] = 1
    adim(m2, 100)
    v = m2.prev
    r.kos(v["S.OTO_ADIM"] == "MACA_GIR" and v["DO7.19"] == 1, "yalniz core2 secili: core2 gir yok")
    r.kos(v["DO7.17"] == 0 and v["DO7.21"] == 0 and v["DO7.23"] == 0, "secili olmayan maca (1,3,4) hareket etti")
    m2.girdi[SEC[1]] = 0      # secici cevrim ortasinda kapandi: adim biter, cikis kesilir
    adim(m2, 30)
    r.kos(m2.prev["DO7.19"] == 0, "secici kapaninca core2 cikisi kesilmedi")
    return r.hata


def s14(m):
    """Zaman asimi (sure*2) -> muhurlu alarm + BOSTA; LOTO/genel iptalde maca cikislari 0; resetle yeniden baslar."""
    r = Sonuc()
    _maca_hazirla(m, secili=(0,), kalip_acik=False)          # izin yok -> sure birikmez -> zaman asimi
    sure = m.P["P.MACA_SURE_ms"]
    m.girdi["HMI.OTO_BASLAT"] = 1
    adim(m, int(sure * 2) - 100)
    r.kos(m.prev["S.OTO_ADIM"] == "MACA_GIR" and m.prev["S.MACA_ALARM"] == 0, "zaman asimi erken (sure*2 dolmadan)")
    adim(m, 200)
    v = m.prev
    r.kos(v["S.MACA_ALARM"] == 1 and v["AL_MACA_ZAMAN_ASIMI"] == 1 and v["S.HERHANGI_ALARM"] == 1, "sure*2 sonrasi alarm yok")
    r.kos(v["S.OTO_ADIM"] == "BOSTA" and not any(_maca_cikislar(v)), "alarmda BOSTA'ya iptal / cikis 0 olmadi")
    adim(m, 200)
    r.kos(m.prev["S.OTO_ADIM"] == "BOSTA", "alarm silinmeden yeni cevrim basladi")
    m.girdi["AI10.1"] = 100
    m.girdi["HMI.RESET"] = 1
    adim(m, 20)
    m.girdi["HMI.RESET"] = 0
    adim(m, 50)
    r.kos(m.prev["S.MACA_ALARM"] == 0 and m.prev["S.OTO_ADIM"] == "MACA_GIR", "reset sonrasi alarm silinmedi / cevrim baslamadi")
    r.kos(m.prev["DO7.17"] == 1, "reset sonrasi maca gir cikisi yok")
    # LOTO: cikislar hemen 0 ve BOSTA
    m.girdi["HMI.LOTO_BASLAT"] = 1
    adim(m, 30)
    v = m.prev
    r.kos(not any(_maca_cikislar(v)) and v["S.OTO_ADIM"] == "BOSTA", "LOTO'da maca cikislari 0 / BOSTA olmadi")
    r.kos(all(m.bobin(k) == 0 for k in GIR + CEK), "LOTO'da maca bobini enerjili")
    # genel iptal: OTO modu kapandi
    m.girdi.update({"HMI.LOTO_BASLAT": 0, "HMI.LOTO_BITIR": 1})
    adim(m, 20)
    m.girdi["HMI.LOTO_BITIR"] = 0
    adim(m, 50)
    r.kos(m.prev["DO7.17"] == 1, "LOTO sonrasi cevrim tekrar baslamadi (test hazirligi)")
    m.girdi["DI4.09"] = 0
    adim(m, 30)
    r.kos(not any(_maca_cikislar(m.prev)) and m.prev["S.OTO_ADIM"] == "BOSTA", "oto modu kapaninca maca cikislari 0 olmadi")
    return r.hata


def s15(m):
    """Cift solenoid kilidi: in/out ayni anda 1 olamaz (PLC ifadesi ve HW bobini)."""
    r = Sonuc()
    _maca_hazirla(m, secili=(0,), kalip_acik=True)
    m.girdi["HMI.OTO_BASLAT"] = 1
    adim(m, 50)
    r.kos(m.prev["DO7.17"] == 1, "hazirlik: gir cikisi yok")
    # karsi cikis ariza ile 1 -> PLC gir'i keser
    m.zorla = {"DO7.18": 1}
    adim(m, 30)
    r.kos(m.prev["DO7.17"] == 0, "PLC: DO7.18=1 iken DO7.17 kesilmedi (in/out kilidi)")
    # PLC arizasi: ikisi birden zorla 1 -> HW bobinleri ikisi de 0
    m.zorla = {"DO7.17": 1, "DO7.18": 1}
    adim(m, 30)
    r.kos(m.bobin("DO7.17") == 0 and m.bobin("DO7.18") == 0, "HW: in+out birlikte 1 iken bobin enerjili (kilit yok)")
    # E-stop: valf beslemesi duser -> maca bobinleri 0
    m.zorla = {}
    adim(m, 30)
    m.girdi["HW.ST1_1"] = 0
    adim(m, 50)
    r.kos(all(m.bobin(k) == 0 for k in GIR + CEK), "E-stop'ta maca bobini enerjili")
    return r.hata


def _plc_tanim(cfg, id_):
    for e in cfg["mantik"]["plc"]:
        if e["id"] == id_:
            return e
    raise KeyError(id_)


def mut_s12a(cfg):     # ENJ sonrasi maca cek yok
    for a in cfg["mantik"]["siralayici"]["adimlar"]:
        if a["ad"] == "ENJ":
            a["sonraki"] = "ACMA"


def mut_s12b(cfg):     # maca gir kalip acik kosulu yok
    e = _plc_tanim(cfg, "S.MACA_GIR_IZIN")
    e["ifade"] = cikar(e["ifade"], "S.KALIP_ACIK")


def mut_s12c(cfg):     # maca cek kalip kapali kosulu yok
    e = _plc_tanim(cfg, "S.MACA_CEK_IZIN")
    e["ifade"] = cikar(e["ifade"], "S.KALIP_KAPALI")


def mut_s13a(cfg):     # core1 secicisi yok sayilir
    e = _plc_tanim(cfg, "DO7.19")
    e["ifade"] = cikar(e["ifade"], "DI5.15")
    e = _plc_tanim(cfg, "DO7.17")
    e["ifade"] = cikar(e["ifade"], "DI5.14")


def mut_s14a(cfg):     # zaman asimi carpani cok buyuk
    cfg["mantik"]["zamanlar"]["maca_zaman_asimi_carpan"] = 1000


def mut_s14b(cfg):     # LOTO/genel iptalde cikis kesilmez: izin LOTO'yu icermez, genel iptal LOTO'suz
    e = _plc_tanim(cfg, "S.MACA_IZIN_ORTAK")
    e["ifade"] = cikar(cikar(cikar(e["ifade"], ["not", "S.LOTO_MODU"]), "DI5.12"), ["not", "S.DESARJ_ISTEGI"])
    gi = cfg["mantik"]["siralayici"]["genel_iptal"]
    gi["kosul"] = cikar(gi["kosul"], "S.LOTO_MODU")


def mut_s14c(cfg):     # alarm silinmeden yeni cevrim
    k = cfg["mantik"]["siralayici"]["baslatma"]["kosul"]
    cfg["mantik"]["siralayici"]["baslatma"]["kosul"] = cikar(k, ["not", "S.MACA_ALARM"])


def mut_s15a(cfg):     # PLC in/out kilidi yok
    for i in GIR + CEK:
        e = _plc_tanim(cfg, i)
        e["ifade"] = [e["ifade"][0]] + [x for x in e["ifade"][1:] if not (isinstance(x, list) and x[0] == "not")]


def mut_s15b(cfg):     # HW bobininde karsi cikis kilidi yok
    for e in cfg["mantik"]["donanim"]:
        if e["id"].startswith("HW.MACA"):
            e["ifade"] = [x for x in e["ifade"] if not (isinstance(x, list) and x[0] == "not")]


# ---------------------------------------------------------------- kapali dongu (Kademe 4 adim 2)
def _kd(m, **kw):
    calistir(m)
    return KapaliDongu(m, **kw)


def _klon(m):
    """m ile ayni (mutasyonlu olabilir) konfigurasyonla yeni ornek."""
    return ElektrikMantik(cfg=copy.deepcopy(m.cfg))


def _faz_sureleri(k):
    g = k.gecis
    return g["ENJ.FAZ2"] - g["ENJ.FAZ1"], g["ENJ.FAZ3"] - g["ENJ.FAZ2"]


def s16(m):
    """Kapali dongu: DO -> hareket -> DI/ENC -> PLC; tam cevrim, faz gecisleri konumda, alarm yok."""
    r = Sonuc()
    k = _kd(m)
    sure = k.calistir_cevrim()
    v = m.prev
    r.kos(sure is not None, "kapali dongu cevrimi bitmedi (zaman asimi/alarm)")
    if sure is None:
        return r.hata
    r.kos(v["S.CEVRIM_SAYAC"] == 1 and v["S.OTO_ADIM"] == "BOSTA", "cevrim sayaci 1 / BOSTA degil")
    r.kos(not (v["S.ENJ_KONUM_ALARM"] or v["S.PISTON_GERI_ALARM"] or v["S.MACA_ALARM"] or v["S.HERHANGI_ALARM"]), "alarm var")
    sira = [o[1] for o in k.olay]
    r.kos(sira == ["MACA_GIR", "KAPAMA", "ENJ", "ENJ", "ENJ", "ENJ", "MACA_CEK", "ACMA", "ITICI_ILERI", "ITICI_GERI", "BOSTA"],
          f"adim sirasi beklenenden farkli: {sira}")
    G, D, P = k.gecis, k.gecis_durum, m.P
    # faz gecisleri HAREKET durumuna bagli (sure degil): FAZ2 girisinde plunger >= FAZ1 esigi, FAZ3 girisinde >= FAZ2 esigi
    r.kos(P["P.FAZ1_BITIS_mm"] <= D["ENJ.FAZ2"][0] <= P["P.FAZ1_BITIS_mm"] + 3, f"FAZ2 girisinde px={D['ENJ.FAZ2'][0]:.1f} (esik {P['P.FAZ1_BITIS_mm']})")
    r.kos(P["P.FAZ2_BITIS_mm"] <= D["ENJ.FAZ3"][0] <= P["P.FAZ2_BITIS_mm"] + 8, f"FAZ3 girisinde px={D['ENJ.FAZ3'][0]:.1f} (esik {P['P.FAZ2_BITIS_mm']})")
    r.kos(D["ENJ"][1] <= 0.002 and D["ENJ.FAZ1"][1] <= 0.002, "ENJ kalip kilitlenmeden basladi (s>0)")
    r.kos(all(x < 1e-6 for x in D["KAPAMA"][3]), "KAPAMA girisinde maca kavitede degil (ma=0 beklenir)")
    r.kos(all(x > 1 - 1e-6 for x in D["ACMA"][3]), "ACMA girisinde maca cekili degil")
    r.kos(abs(D["ITICI_ILERI"][1] * k.kurs_mafsal - k.kurs_mafsal * D["ITICI_ILERI"][1]) < 1e-9 and
          D["ITICI_ILERI"][1] * k.kurs_mafsal >= P["P.ITICI_ACIKLIK_MIN_mm"], "ITICI_ILERI acilik < minimum")
    r.kos(D["ITICI_GERI"][2] >= k.kurs_ej - 1, "ITICI_GERI girisinde itici ileri limitte degil")
    r.kos(D["BOSTA"][2] <= 1, "BOSTA'da itici geride degil")
    r.kos(k.px <= P["P.ENC_TOL_mm"], f"cevrim sonunda plunger geride degil (px={k.px:.1f})")
    r.kos(k.max_px > k.kurs_pl - 5, f"plunger strok sonuna ulasmadi (max {k.max_px:.0f})")
    r.kos(not k.ihlal, f"hareket kurali ihlali: {sorted(k.ihlal)}")
    return r.hata


def s17(m):
    """Konum tabanli: plunger yavaslayinca FAZ sureleri uzar (sure tabani degil); cok yavassa zaman asimi alarmi."""
    r = Sonuc()
    k0 = _kd(yeni())
    k0.calistir_cevrim()
    n1, n2 = _faz_sureleri(k0)
    k = _kd(m, hiz_olcek={"plunger": 0.5})
    sure = k.calistir_cevrim()
    r.kos(sure is not None, "plunger 0,5x: cevrim bitmedi (konum tabani yavas hizda da tamamlanmali)")
    if sure is None:
        return r.hata
    f1, f2 = _faz_sureleri(k)
    r.kos(1.8 * n1 <= f1 <= 2.2 * n1, f"FAZ1 suresi hiz ile olceklenmedi ({f1:.0f} ms, nominal {n1:.0f})")
    r.kos(1.8 * n2 <= f2 <= 2.2 * n2 + 6, f"FAZ2 suresi hiz ile olceklenmedi ({f2:.0f} ms, nominal {n2:.0f})")
    r.kos(k.gecis_durum["ENJ.FAZ2"][0] >= m.P["P.FAZ1_BITIS_mm"], "yavas plunger: FAZ2'ye 150 mm'den once gecildi (sure tabani)")
    r.kos(not k.ihlal, f"ihlal: {sorted(k.ihlal)}")
    # cok yavas: FAZ1 zaman asimi -> muhurlu alarm + BOSTA, resetsiz yeni cevrim yok
    m2 = _klon(m)
    k2 = _kd(m2, hiz_olcek={"plunger": 0.2})
    k2.calistir_cevrim()
    r.kos(m2.prev["S.ENJ_KONUM_ALARM"] == 1 and m2.prev["S.OTO_ADIM"] == "BOSTA", "yavas plunger: zaman asimi alarmi/BOSTA yok")
    r.kos(m2.prev["S.HERHANGI_ALARM"] == 1, "AL_ENJ_KONUM_ZAMAN_ASIMI S.HERHANGI_ALARM'a yansimadi")
    m2.girdi["HMI.OTO_BASLAT"] = 1
    adim(m2, 500)
    r.kos(m2.prev["S.OTO_ADIM"] == "BOSTA", "alarm silinmeden yeni cevrim basladi")
    m2.girdi["HMI.RESET"] = 1
    adim(m2, 20)
    m2.girdi["HMI.RESET"] = 0
    adim(m2, 100)
    r.kos(m2.prev["S.ENJ_KONUM_ALARM"] == 0 and m2.prev["S.OTO_ADIM"] != "BOSTA", "RESET sonrasi alarm silinmedi/cevrim baslamadi")
    # yedek mod: P.ENC_BILDIRIM=0 -> sure tabani (FAZ1 = P.FAZ1_SURE_ms, hizdan bagimsiz)
    m3 = _klon(m)
    k3 = _kd(m3, hiz_olcek={"plunger": 0.5})
    m3.girdi["P.ENC_BILDIRIM"] = 0
    k3.calistir_cevrim()
    g1, _ = _faz_sureleri(k3)
    r.kos(abs(g1 - m3.P["P.FAZ1_SURE_ms"]) <= 10, f"yedek sure modu: FAZ1 {g1:.0f} ms (beklenen {m3.P['P.FAZ1_SURE_ms']})")
    return r.hata


def s18(m):
    """Enkoder arizasi (ENC=0 sabit) -> FAZ1 zaman asimi; piston geri takilinca AL_PISTON_GERI_ZAMAN_ASIMI."""
    r = Sonuc()
    k = _kd(m, ariza={"enc_sabit": 0.0})
    k.calistir_cevrim()
    t = k.gecis.get("ENJ.FAZ1")
    r.kos(m.prev["S.ENJ_KONUM_ALARM"] == 1 and m.prev["S.OTO_ADIM"] == "BOSTA", "ENC=0: zaman asimi alarmi/BOSTA yok")
    r.kos(abs((m.t - t) - m.P["P.FAZ1_ZAMAN_ASIMI_ms"]) <= 20, f"FAZ1 zaman asimi {m.t - t:.0f} ms (beklenen {m.P['P.FAZ1_ZAMAN_ASIMI_ms']})")
    r.kos(m.prev["DO7.25"] == 0, "alarmdan sonra yavas enjeksiyon cikisi acik kaldi")
    # piston geri takilir (hiz 0,05x): 2500 ms icinde ENC geri konuma inmez
    m2 = _klon(m)
    k2 = _kd(m2, hiz_olcek={"plunger": 1.0})
    k2.olcek["plunger"] = 1.0
    orig = k2._v

    def v_yavas_geri(ad, a):
        return orig(ad, a) * (0.05 if a == "geri_mm_s" else 1.0)
    k2._v = v_yavas_geri
    k2.calistir_cevrim()
    r.kos(m2.prev["S.PISTON_GERI_ALARM"] == 1 and m2.prev["S.HERHANGI_ALARM"] == 1, "piston geri takildi: AL_PISTON_GERI_ZAMAN_ASIMI yok")
    r.kos(m2.prev["S.OTO_PISTON_GERI"] == 0, "piston geri alarminda cikis kapanmadi")
    m2.girdi["HMI.OTO_BASLAT"] = 1
    adim(m2, 300)
    r.kos(m2.prev["S.OTO_ADIM"] == "BOSTA", "piston geri alarmi silinmeden yeni cevrim basladi")
    return r.hata


def s19(m):
    """cevrim.py esleme: PLC adimlari <-> faz 1..16; esikler cevrim.ayarlar ile ayni; fark yalniz bilinen/etiketli."""
    import json as _j
    import cevrim
    r = Sonuc()
    k = _kd(m)
    k.calistir_cevrim()
    hm = m.mk["hareket_modeli"]
    PJ = _j.load(open(os.path.join(ROOT, "params", "params.json"), encoding="utf-8"))
    HJ = _j.load(open(os.path.join(ROOT, "params", "hidrolik.json"), encoding="utf-8"))
    c = cevrim.ayarlar(PJ, HJ)
    tab = {int(f[0].split()[0]): f[0] for f in cevrim.faz_tablosu(c)}
    P = m.P
    r.kos(P["P.FAZ1_BITIS_mm"] == c["slow"], f"FAZ1 esigi {P['P.FAZ1_BITIS_mm']} != cevrim slow {c['slow']}")
    r.kos(P["P.FAZ2_BITIS_mm"] == c["stroke"] - c["f3"], f"FAZ2 esigi {P['P.FAZ2_BITIS_mm']} != stroke-f3 {c['stroke'] - c['f3']}")
    r.kos(abs(k.kurs_pl - c["stroke"]) < 1e-9 and abs(k.kurs_ej - c["ej"]) < 1e-9 and abs(k.kurs_ma - c["ma"]) < 1e-9, "kurslar cevrim.ayarlar ile ayni degil")
    # esleme tablosu: faz numaralari cevrim.py'de var, farklar bilinen listede
    bil = set(hm["bilinen_fark"])
    gorulen_num = []
    for e in hm["cevrim_esleme"]:
        for tok in e["cevrim"].replace("/", "+").split("+"):
            n = int(tok.split()[0])
            r.kos(n in tab, f"esleme: cevrim faz {n} yok")
            r.kos(e["cevrim"].split("+")[0].split("/")[0].strip().split(" ", 1)[1][:6] == tab.get(int(e["cevrim"].split()[0]), " x")[len(str(int(e["cevrim"].split()[0]))) + 1:][:6]
                  if n == int(e["cevrim"].split()[0]) else True, f"esleme faz adi uyusmuyor: {e['cevrim']}")
        r.kos(e["fark"] is None or e["fark"] in bil, f"esleme farki bilinen listede degil: {e['fark']}")
        r.kos(e["fark"] is None or "VARSAYIM" in e.get("not", ""), f"fark VARSAYIM etiketsiz: {e['plc']}")
    # dinamik: gozlenen farklar tanimli listede ve beklenen ikisi gozleniyor
    r.kos(k.fark <= bil, f"etiketsiz fark: {sorted(k.fark - bil)}")
    r.kos(k.fark == {"FARK_SIRA_PISTON_GERI", "FARK_ACMA_300"}, f"gozlenen fark kumesi {sorted(k.fark)}")
    r.kos(not k.ihlal, f"ihlal: {sorted(k.ihlal)}")
    # sira: PLC adimlarinin cevrim faz numaralari azalmiyor, tek ters sira 'piston geri' (FARK_SIRA_PISTON_GERI)
    plc_sira = [("MACA_GIR", 3), ("KAPAMA", 4), ("ENJ.FAZ1", 7), ("ENJ.FAZ2", 8), ("ENJ.FAZ3", 9), ("MACA_CEK", 12),
                ("ACMA", 13), ("OTO_PISTON_GERI", 11), ("ITICI_ILERI", 14), ("ITICI_GERI", 16)]
    zaman = [(k.gecis[a], n, a) for a, n in plc_sira]
    zaman.sort()
    ters = [(a, n) for (t1, n1, a1), (t2, n2, a) in zip(zaman, zaman[1:]) for n in [n2] if n2 < n1]
    r.kos([a for a, _ in ters] == ["OTO_PISTON_GERI"], f"cevrim sirasina ters adimlar: {ters} (yalniz OTO_PISTON_GERI beklenir)")
    r.kos(all(e["fark"] == "FARK_SIRA_PISTON_GERI" for e in hm["cevrim_esleme"] if e["plc"] == "OTO_PISTON_GERI"), "piston geri esleme farki etiketsiz")
    # cevrim faz 10 katilasma = PLC FAZ3 sonu: sure tabanli, etiketli
    f3 = k.gecis["MACA_CEK"] - k.gecis["ENJ.FAZ3"]
    r.kos(abs(f3 - m.P["P.FAZ3_SURE_ms"]) <= 10, f"FAZ3 (katilasma) suresi {f3:.0f} != P.FAZ3_SURE_ms")
    r.kos(any(e["fark"] == "FARK_KATILASMA_SURE" for e in hm["cevrim_esleme"]), "katilasma farki etiketsiz")
    return r.hata


# ---------------------------------------------------------------- ariza enjeksiyonu (Kademe 4 adim 3)
def _s_ariza(ariza_id):
    def f(m):
        """Ariza enjekte -> PLC beklenen fazda/alarmla durmali; teshis kaydi alanlari dolu; guvenlik + LOTO 1..n sirali."""
        r = Sonuc()
        mod = next(x for x in m.cfg["mantik"]["ariza_enjeksiyon"]["modlar"] if x["id"] == ariza_id)
        calistir(m)
        t = teshis_kaydi(m, mod)
        b = mod["beklenen"]
        r.kos(t["faz"] == b["faz"], f"{ariza_id}: durus fazi {t['faz']} (beklenen {b['faz']})")
        r.kos(t["alarm"] == b["alarm"], f"{ariza_id}: alarm {t['alarm']} (beklenen {b['alarm']})")
        r.kos(t["tespit"] == ("alarm" if b["alarm"] else "sessiz_takilma"), f"{ariza_id}: tespit {t['tespit']}")
        r.kos(bool(t["bekleyen_kosul"]) and t["bekleyen_kosul"] != "-", f"{ariza_id}: bekleyen kosul bos")
        r.kos(len(t["sorumlu_ID"]) >= 2 and t["sorumlu_ID"][0] == (mod.get("hedef") or "DB68.ENC")
              and any(i.startswith("A") and i[1:].isdigit() for i in t["sorumlu_ID"]), f"{ariza_id}: sorumlu_ID (kanal + mekanik A##) eksik {t['sorumlu_ID']}")
        g = t["guvenlik_notu"]
        r.kos(len(g) > 100 and "akumulator" in g.lower() and "LOTO" in g and "kilit" in g.lower(), f"{ariza_id}: guvenlik notu eksik")
        no = [a["no"] for a in m.cfg["loto"]["adimlar"]]
        r.kos(t["loto_adimlar"] == list(range(1, len(no) + 1)) == no, f"{ariza_id}: LOTO adimlari 1..n sirali degil {t['loto_adimlar']}")
        r.kos(t["cikis_var_hareket_yok"] == (mod["tur"] == "bobin_yanik"), f"{ariza_id}: 'cikis var hareket yok' isareti {t['cikis_var_hareket_yok']}")
        r.kos(t["etiket"] == "DESIGN ASSUMPTION", f"{ariza_id}: DESIGN ASSUMPTION etiketi yok")
        return r.hata
    f.__name__ = f"s_ariza_{ariza_id}"
    f.__doc__ = f"Ariza {ariza_id}"
    return f


def s20(m):
    """Kontrol: arizasiz tam cevrim TAMAMLANDI, alarm yok; ariza listesi >= 8 mod ve tum turler kapsamda."""
    r = Sonuc()
    calistir(m)
    mods = m.cfg["mantik"]["ariza_enjeksiyon"]["modlar"]
    r.kos(len(mods) >= 8, f"ariza sayisi {len(mods)} < 8")
    turler = {x["tur"] for x in mods}
    for z in ("sensor_sikismis_0", "sensor_sikismis_1", "bobin_yanik", "valf_takili", "enkoder_darbe_kaybi", "enkoder_sabit", "kablo_kopuk"):
        r.kos(z in turler, f"ariza turu eksik: {z}")
    k = KapaliDongu(m)
    r.kos(k.calistir_cevrim() is not None and not m.prev["S.HERHANGI_ALARM"], "arizasiz cevrim bitmedi/alarm var")
    return r.hata


def _mut_param(ad, deger):
    def f(cfg):
        cfg["mantik"]["ifade_dili"]["parametreler"][ad] = deger
    f.__name__ = f"mut_param_{ad}"
    return f


def mut_s16b(cfg):     # PLC: konum modu kapali (sure tabani)
    cfg["mantik"]["ifade_dili"]["parametreler"]["P.ENC_BILDIRIM"] = 0


def mut_s16c(cfg):     # piston geri bitis toleransi cok genis -> plunger inmeden biter
    cfg["mantik"]["siralayici"]["piston_geri"]["tolerans"] = 600


def mut_s16d(cfg):     # alarmda yeni cevrim engeli kalkti
    b = cfg["mantik"]["siralayici"]["baslatma"]
    b["kosul"] = [x for x in b["kosul"] if x not in (["not", "S.ENJ_KONUM_ALARM"], ["not", "S.PISTON_GERI_ALARM"])]


def mut_s16e(cfg):     # FAZ1/FAZ2 zaman asimi sonsuz
    p = cfg["mantik"]["ifade_dili"]["parametreler"]
    p["P.FAZ1_ZAMAN_ASIMI_ms"] = p["P.FAZ2_ZAMAN_ASIMI_ms"] = 10 ** 9


mut_param_f1 = _mut_param("P.FAZ1_BITIS_mm", 600)


def mut_s19a(cfg):     # esikler cevrim.py ile uyumsuz
    cfg["mantik"]["ifade_dili"]["parametreler"]["P.FAZ2_BITIS_mm"] = 400



def mut_ariza_zaman_asimi_yok(cfg):     # FAZ1/FAZ2/piston geri zaman asimi sonsuz -> alarm beklenen testler yakalar
    p = cfg["mantik"]["ifade_dili"]["parametreler"]
    p["P.FAZ1_ZAMAN_ASIMI_ms"] = p["P.FAZ2_ZAMAN_ASIMI_ms"] = p["P.PISTON_GERI_SURE_ms"] = 10 ** 9


def mut_ariza_guvenlik_bos(cfg):
    cfg["mantik"]["ariza_enjeksiyon"]["guvenlik_ortak"] = ""
    cfg["mantik"]["ariza_enjeksiyon"]["guvenlik_tur"] = {k: "" for k in cfg["mantik"]["ariza_enjeksiyon"]["guvenlik_tur"]}


def mut_ariza_loto_sirasiz(cfg):
    a = cfg["loto"]["adimlar"]
    a[2]["no"], a[3]["no"] = a[3]["no"], a[2]["no"]


def mut_ariza_beklenen_kayik(cfg):
    for x in cfg["mantik"]["ariza_enjeksiyon"]["modlar"]:
        if x["id"] == "ARZ06":
            x["beklenen"]["faz"] = "ENJ.FAZ2"


SENARYOLAR = [
    (1, "Start birakilinca motor devam (muhur); stop ve E-stop durdurur", s1, [mut_s1a, mut_s1b]),
    (2, "KM2/KM3 asla birlikte 1 degil; KM3 dususunden >=50 ms sonra KM2", s2, [mut_s2a, mut_s2b]),
    (3, "Kapi aciksa DO7.05=1 olsa bile S210A bobini 0", s3, [mut_s3a, mut_s3b]),
    (4, "Limit1/limit2 uyumsuzlugu 500 ms sonra muhurlu alarm", s4, [mut_s4a, mut_s4b]),
    (5, "S121 istegi varken enjeksiyon izni 0", s5, [mut_s5a, mut_s5b]),
    (6, "KM4/KM5 asla birlikte 1 degil; uc limitte kontaktor duser", s6, [mut_s6a, mut_s6b, mut_s6c]),
    (7, "Yag seviye alarminda KA2 duser", s7, [mut_s7]),
    (8, "LOTO adim 4: S.AKU_BOS (PT2 < 2 bar, 10 s)", s8, [mut_s8a, mut_s8b]),
    (9, "OTO cevrim: faz sureleri, piston geri ACMA bitisinden sureli, yeni cevrim piston geri sonrasi", s9, [mut_s9a, mut_s9b]),
    (10, "Mafsal yaglama sureli (N. cevrimde)", s9b, [mut_s9c]),
    (11, "A97 sayaci die_height_current'tan, FKAP 50 kN esigi, LOTO 6-8 yalniz elle", s10, [mut_s10a, mut_s10b]),
    (12, "MACA tam cevrim: MACA_GIR (kalip acik) -> KAPAMA -> ENJ -> MACA_CEK (kalip kapali) -> ACMA", s12, [mut_s12a, mut_s12b, mut_s12c]),
    (13, "MACA secici DI5.14..17 kapali -> maca atlanir; yalniz secili maca hareket eder", s13, [mut_s13a]),
    (14, "MACA zaman asimi (sure*2) -> muhurlu alarm + BOSTA; LOTO/genel iptalde cikis 0", s14, [mut_s14a, mut_s14b, mut_s14c]),
    (15, "MACA in/out cift solenoid kilidi (PLC + HW bobin), E-stop'ta bobin 0", s15, [mut_s15a, mut_s15b]),
    (16, "Kapali dongu: DO -> hareket -> DI/DB68.ENC -> PLC; tam cevrim, FAZ gecisleri konumda", s16, [mut_s16b, mut_s16c, mut_param_f1]),
    (17, "Konum tabani: plunger yavaslayinca FAZ suresi uzar; cok yavassa zaman asimi alarmi + RESET; yedek sure modu", s17, [mut_s16b, mut_s16d, mut_s16e]),
    (18, "ENC arizasi (0 sabit) -> FAZ1 zaman asimi; piston geri takilirsa alarm", s18, [mut_s16e, mut_s16d]),
    (19, "cevrim.py esleme (faz 1..16): esikler/kurslar ayni, farklar etiketli (FARK_*), ihlal yok", s19, [mut_s19a]),
    (20, "Ariza enjeksiyonu: arizasiz cevrim TAMAM; >=8 ariza, tum turler kapsamda", s20, []),
    (21, "Ariza DI5.08 sikismis-0 -> KAPAMA'da sessiz takilma (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ01"), [mut_ariza_loto_sirasiz]),
    (22, "Ariza DI9.11 sikismis-0 -> ITICI_ILERI'de sessiz takilma (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ02"), []),
    (23, "Ariza DI9.11 sikismis-1 -> MACA_GIR izin yok, AL_MACA_ZAMAN_ASIMI (yanlis yonlendirme) (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ03"), []),
    (24, "Ariza DI9.10 kablo kopuk -> MACA_GIR izin yok, AL_MACA_ZAMAN_ASIMI (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ04"), []),
    (25, "Ariza DO7.05 bobin yanik -> KAPAMA takilir (cikis var hareket yok) (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ05"), []),
    (26, "Ariza DO7.25 bobin yanik -> FAZ1 AL_ENJ_KONUM_ZAMAN_ASIMI (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ06"), [mut_ariza_zaman_asimi_yok, mut_ariza_beklenen_kayik, mut_ariza_guvenlik_bos]),
    (27, "Ariza DO7.01 valf takili -> FAZ2 AL_ENJ_KONUM_ZAMAN_ASIMI (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ07"), [mut_ariza_zaman_asimi_yok]),
    (28, "Ariza ENC darbe kaybi %50 -> FAZ2 zaman asimi (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ08"), []),
    (29, "Ariza ENC sabit 0 -> FAZ1 zaman asimi (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ09"), [mut_ariza_zaman_asimi_yok]),
    (30, "Ariza ENC sabit 600 -> piston geri zaman asimi (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ10"), []),
    (31, "Ariza DO7.26 valf takili -> AL_PISTON_GERI_ZAMAN_ASIMI (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ11"), [mut_ariza_zaman_asimi_yok]),
    (32, "Ariza DO7.04 bobin yanik -> ACMA takilir (guvenlik + LOTO 1..n dolu)", _s_ariza("ARZ12"), []),
]


def main():
    log = []
    kalan = 0
    for no, ad, fn, muts in SENARYOLAR:
        try:
            hata = fn(yeni())
        except Exception as e:              # noqa
            hata = [f"istisna: {type(e).__name__}: {e}"]
        durum = "GECTI" if not hata else "KALDI"
        kalan += bool(hata)
        log.append(f"S{no} {durum}: {ad}")
        for h in hata:
            log.append(f"    - {h}")
        for mu in muts:
            try:
                nh = fn(yeni(mu))
            except Exception as e:          # noqa
                nh = [f"istisna: {type(e).__name__}: {e}"]
            yak = "YAKALANDI" if nh else "KACTI"
            if not nh:
                kalan += 1
            log.append(f"    negatif {mu.__name__}: {yak}" + (f"  ({nh[0]})" if nh else "  <-- bozuk mantik testi gecti!"))
    ozet = f"Toplam: {len(SENARYOLAR)} senaryo, {kalan} HATA"
    log.append(ozet)
    os.makedirs(os.path.join(ROOT, "out"), exist_ok=True)
    with open(os.path.join(ROOT, "out", "elektrik_testleri.txt"), "w", encoding="utf-8") as f:
        f.write("\n".join(log) + "\n")
    print("\n".join(log))
    return 1 if kalan else 0


if __name__ == "__main__":
    sys.exit(main())
