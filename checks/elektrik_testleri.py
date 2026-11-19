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
from elektrik_mantik import ElektrikMantik, yukle   # noqa

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
    m3 = yeni()
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
    m.girdi.update({"DI4.09": 1, "DB68.PT2": 150, "P.VURUS_KONUMU_GIRILDI": 1})


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
