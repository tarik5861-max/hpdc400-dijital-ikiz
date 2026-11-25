"""
Kademe 3 Hidrolik Ağ Modeli ve Simülasyon Motoru (Genişletilmiş)
- ISO 1219 elemanları (Pompalar, Akümülatörler, Valfler, Silindirler)
- Pompa debi/güç hesabı: params/hidrolik.json (P1/P2 deplasman, eta) + params/params.json (A120 devir, motor kW)
- Akümülatör deşarj süresi ve basınç düşüm eğrisi simülasyonu
- Güvenlik zinciri / E-stop anında akümülatör deşarj testi (S121 / DV1)
"""
import json
import math
import os

KOK = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))

# Faz 2 akümülatör debisi artık sabit değil: hizli_vurus_hesabi() hedef piston hızından (params/hidrolik.json
# hizli_vurus_tasarim, ikiz_tasarim varsayimi) ve ACC1 gaz yasasından (politropik n) türetilir.


def _oku(yol):
    with open(os.path.join(KOK, yol), encoding="utf-8") as f:
        return json.load(f)


def pompa_debi_lpm(deplasman_cm3_dev, devir_dpm, eta_v):
    """Sabit deplasmanlı pompa efektif debisi: Q = V * n * eta_v / 1000 [L/dk]."""
    return deplasman_cm3_dev * devir_dpm * eta_v / 1000.0


def hidrolik_guc_kw(basinc_bar, debi_lpm):
    """Hidrolik güç: P = p[bar] * Q[L/dk] / 600 [kW]."""
    return basinc_bar * debi_lpm / 600.0


def mil_gucu_kw(basinc_bar, deplasman_cm3_dev, devir_dpm, eta_hm):
    """Pompa mil (motor) gücü: P = p * V * n / (600000 * eta_hm) [kW] (teorik debi / mekanik-hidrolik verim)."""
    return basinc_bar * deplasman_cm3_dev * devir_dpm / (600000.0 * eta_hm)


def pompa_guc_kontrolu(hidrolik=None, params=None):
    """P1+P2 aynı milde (M1/A120). Hidrolik çıkış ve mil gücü motor gücüyle karşılaştırılır.
    Durum: OK (< %90), SINIRDA (%90..%105), YETERSIZ (> %105)."""
    hidrolik = hidrolik or _oku("params/hidrolik.json")
    params = params or _oku("params/params.json")
    motor = params["parts"]["A62"]["dims"]["motor"]
    n = float(motor["rpm"])
    p_motor = float(params["global"]["pump_motor_kW"])
    p_sis = float(params["global"]["system_pressure_bar"])
    sonuc = {"motor_kW": p_motor, "devir_dpm": n, "basinc_bar": p_sis, "pompalar": {}}
    top_hid = top_mil = 0.0
    for pm in hidrolik["elemanlar"]["pompalar"]:
        V = float(pm["deplasman_cm3_dev"])
        q = pompa_debi_lpm(V, n, float(pm["eta_v"]))
        ph = hidrolik_guc_kw(p_sis, q)
        pmil = mil_gucu_kw(p_sis, V, n, float(pm["eta_hm"]))
        sonuc["pompalar"][pm["id"]] = {"debi_lpm": round(q, 1), "hidrolik_kW": round(ph, 2), "mil_kW": round(pmil, 2)}
        top_hid += ph
        top_mil += pmil
    oran = top_mil / p_motor
    sonuc["toplam_hidrolik_kW"] = round(top_hid, 2)
    sonuc["toplam_mil_kW"] = round(top_mil, 2)
    sonuc["mil_yuk_orani"] = round(oran, 3)
    sonuc["durum"] = "OK" if oran < 0.90 else ("SINIRDA" if oran <= 1.05 else "YETERSIZ")
    return sonuc


def silindir_hizi_m_s(debi_lpm, bore_mm):
    """Piston hızı v = Q / A (piston tarafı)."""
    alan_m2 = math.pi * (bore_mm / 1000.0) ** 2 / 4.0
    return (debi_lpm / 60000.0) / alan_m2


# ---------------------------------------------------------------------------
# Akümülatör (gaz yayı) — kendi denklemlerimiz. Çapraz kontrol: OpenHydraulics/Hopsan gaz
# akümülatörü aynı ideal gaz politropik bağıntısını kullanır (p*V^n = sabit); kod kopyalanmadı.
# ---------------------------------------------------------------------------
def gaz_hacmi_l(V0_l, p0_bar, p_bar, n):
    """Ön dolum (V0, p0) noktasından politropik: V = V0 * (p0/p)^(1/n). Mutlak basınç kullanılır."""
    return V0_l * ((p0_bar + 1.0) / (p_bar + 1.0)) ** (1.0 / n)


def akumulator_faydali_hacim_l(V0_l, p0_bar, p1_bar, p2_bar, n):
    """p1 -> p2 deşarjında verilen yağ: dV = V0 * [(p0/p2)^(1/n) - (p0/p1)^(1/n)] (mutlak basınç)."""
    return gaz_hacmi_l(V0_l, p0_bar, p2_bar, n) - gaz_hacmi_l(V0_l, p0_bar, p1_bar, n)


def akumulator_son_basinc_bar(V0_l, p0_bar, p1_bar, dV_l, n):
    """p1'den dV çekilince son basınç: p2 = p1 * (V1/(V1+dV))^n (adyabatik/politropik)."""
    V1 = gaz_hacmi_l(V0_l, p0_bar, p1_bar, n)
    return (p1_bar + 1.0) * (V1 / (V1 + dV_l)) ** n - 1.0


def gerekli_V0_l(dV_l, p0_bar, p1_bar, p2_bar, n):
    """Ters hesap: dV verebilmek için gereken toplam gaz hacmi V0."""
    return dV_l / akumulator_faydali_hacim_l(1.0, p0_bar, p1_bar, p2_bar, n)


def tup_gaz_hacmi_l(a56_dims, et_mm):
    """A56 tüp iç hacmi (gaz). Silindir + 2 elipsoid uç (iç yükseklik = dome_height - et).
    İç boy = toplam boy - üst valf - ayak halkası - 2*et. ikiz_tasarim varsayimi: tüm iç hacim gaz (V0)."""
    od = float(a56_dims["od"])
    L = float(a56_dims["length"])
    di = (od - 2.0 * et_mm) / 1000.0
    L_ic = (L - float(a56_dims["top_valve"]["height"]) - float(a56_dims["foot_ring"]["height"]) - 2.0 * et_mm) / 1000.0
    h_dome = (float(a56_dims["dome_height"]) - et_mm) / 1000.0
    r = di / 2.0
    v_sil = math.pi * r ** 2 * (L_ic - 2.0 * h_dome)
    v_uc = 2.0 * (2.0 / 3.0) * math.pi * r ** 2 * h_dome
    return (v_sil + v_uc) * 1000.0, di * 1000.0, L_ic * 1000.0


def _boru_dp_bar(Q_lpm, D_mm, L_m, rho, nu_cst, rough_mm, K_ek=0.0):
    """fluids (MIT) ile düz boru + yerel kayıp: dP = (f*L/D + K) * rho*v^2/2."""
    from fluids import friction_factor
    from fluids.core import Reynolds
    D = D_mm / 1000.0
    A = math.pi * D ** 2 / 4.0
    v = Q_lpm / 60000.0 / A
    Re = Reynolds(V=v, D=D, nu=nu_cst * 1e-6)
    fd = friction_factor(Re=Re, eD=rough_mm / D_mm)
    dp = (fd * L_m / D + K_ek) * rho * v ** 2 / 2.0
    return dp / 1e5, v, Re, fd


def _dirsek_K(D_mm, rc_D, Re):
    from fluids.fittings import bend_rounded
    return bend_rounded(Di=D_mm / 1000.0, angle=90.0, rc=rc_D * D_mm / 1000.0, Re=Re)


def hat_kaybi_A64(Q_acc_lpm, prm, tas):
    """ACC1 -> A65 en uzun yol (A56_4, Y=+410): yükselen boru (Q/4) + toplayıcı (Q/4, Q/2) + ana hat (Q).
    Geometri params.json A64 dims'ten; vurus konumu global.shot_offset_z (seçili konum)."""
    d = prm["parts"]["A64"]["dims"]
    yag, hat = tas["yag"], tas["hat"]
    rho, nu, ru = yag["rho_kg_m3"], yag["nu_cSt"], hat["puruzluluk_mm"]
    et = float(hat["boru_et_mm"])                # params A64 capları DIS cap; hidrolik IC cap = dis - 2*et
    d = dict(d, riser_d=d["riser_d"] - 2 * et, header_d=d["header_d"] - 2 * et, main_d=d["main_d"] - 2 * et)
    ys = sorted(float(y) for y in d["risers_y"])
    y_main = float(d["main_run"]["y"])
    L_riser = (float(d["z_header"]) - float(d["z_riser_start"])) / 1000.0
    z_son = float(prm["global"]["shot_offset_z"]) + float(d["main_run"]["block_top_rel"])
    L_dikey = (float(d["z_header"]) - z_son) / 1000.0
    L_yatay = float(d["main_run"]["x_end_local"]) / 1000.0
    y_en, y_ic = ys[-1], ys[-2]
    L_h1 = abs(y_en - y_ic) / 1000.0           # yalnız uç tüp debisi (Q/4)
    L_h2 = abs(y_ic - y_main) / 1000.0         # iki tüp debisi (Q/2)
    parcalar = []
    q4 = Q_acc_lpm / 4.0
    dp, v, Re, f = _boru_dp_bar(q4, d["riser_d"], L_riser, rho, nu, ru, hat["K_giris"])
    Kd = _dirsek_K(d["riser_d"], hat["bend_rc_D"], Re)
    dp += Kd * rho * v ** 2 / 2.0 / 1e5
    parcalar.append(("riser Q/4", d["riser_d"], L_riser, v, dp))
    dp, v, Re, f = _boru_dp_bar(q4, d["header_d"], L_h1, rho, nu, ru)
    parcalar.append(("toplayici Q/4", d["header_d"], L_h1, v, dp))
    dp, v, Re, f = _boru_dp_bar(Q_acc_lpm / 2.0, d["header_d"], L_h2, rho, nu, ru, hat["K_tee_branch"])
    parcalar.append(("toplayici Q/2 + T", d["header_d"], L_h2, v, dp))
    dp, v, Re, f = _boru_dp_bar(Q_acc_lpm, d["main_d"], L_yatay + L_dikey, rho, nu, ru, hat["K_cikis"])
    Kd = _dirsek_K(d["main_d"], hat["bend_rc_D"], Re)
    dp += 2.0 * Kd * rho * v ** 2 / 2.0 / 1e5
    parcalar.append(("ana hat + 2 dirsek + cikis", d["main_d"], L_yatay + L_dikey, v, dp))
    toplam = sum(x[4] for x in parcalar)
    # ivmelenme (yağ sütunu ataleti): dp = rho * sum(L/A) * dQ/dt, rampa süresinde 0 -> Q
    dQdt = Q_acc_lpm / 60000.0 / (hat["ivme_rampa_ms"] / 1000.0)
    # her kesitin payı (L/A) * (kesit debisi / Q); tek riser ve uç toplayıcı Q/4, iç toplayıcı Q/2
    LA = (L_riser / (math.pi * (d["riser_d"] / 1000.0) ** 2 / 4.0) / 4.0
          + L_h1 / (math.pi * (d["header_d"] / 1000.0) ** 2 / 4.0) / 4.0
          + L_h2 / (math.pi * (d["header_d"] / 1000.0) ** 2 / 4.0) / 2.0
          + (L_yatay + L_dikey) / (math.pi * (d["main_d"] / 1000.0) ** 2 / 4.0))
    dp_ivme = rho * LA * dQdt / 1e5
    return {"parcalar": [{"ad": a, "D_mm": D, "L_m": round(L, 3), "v_m_s": round(v, 2), "dp_bar": round(p, 2)}
                         for a, D, L, v, p in parcalar],
            "dp_sabit_bar": round(toplam, 2), "dp_ivme_bar": round(dp_ivme, 2),
            "ana_hat_hiz_m_s": round(parcalar[-1][3], 2)}


def hizli_vurus_hesabi(hidrolik=None, params=None, elektrik=None):
    """Hedef piston hızından TERS hesap: Q = A54 * v -> vuruş hacmi -> ACC1 gerekli V0/p0 -> mevcut A56 grubu
    ile son basınç, faz 2 debisi, pompa katkısı, şarj süresi ve motor yükü. Tüm girdiler params/*.json."""
    hidrolik = hidrolik or _oku("params/hidrolik.json")
    params = params or _oku("params/params.json")
    elektrik = elektrik or _oku("params/elektrik.json")
    tas = hidrolik["hizli_vurus_tasarim"]
    g = params["global"]
    parts = params["parts"]
    p1 = float(g["system_pressure_bar"])
    n = float(tas["n_politropik"])
    bore = float(parts["A54"]["dims"]["barrel"]["bore"])
    A54 = math.pi * (bore / 1000.0) ** 2 / 4.0
    d_pl = float(g["plunger_d"])
    A_pl = math.pi * (d_pl / 1000.0) ** 2 / 4.0
    strok_top = float(parts["A52"]["dims"]["stroke"])
    a55 = parts["A55"]["dims"]["internal"]
    oran = (float(a55["piston_d"]) / float(a55["plunger_d"])) ** 2
    A55_big = math.pi * (float(a55["piston_d"]) / 1000.0) ** 2 / 4.0
    # PLC faz süreleri (elektrik.json salt okunur)
    pr = _bul_anahtar(elektrik, "P.FAZ2_SURE_ms")
    t2 = float(pr["P.FAZ2_SURE_ms"]) / 1000.0
    t1 = float(pr.get("P.FAZ1_SURE_ms", 0)) / 1000.0
    t3 = float(pr.get("P.FAZ3_SURE_ms", 0)) / 1000.0
    p1q = next(p for p in hidrolik["elemanlar"]["pompalar"] if p["id"] == "P1")
    Qp1 = float(p1q["nominal_debi_lpm"])
    v_hedef = float(tas["hedef_piston_hizi_m_s"])
    # 1) hedef debi ve vuruş hacmi
    Q_hedef = A54 * v_hedef * 60000.0
    s2 = v_hedef * t2                                  # hızlı faz stroku [m]
    V2 = A54 * s2 * 1000.0 * (1.0 + float(tas["kayip_orani"]))
    V3 = A55_big * float(tas["faz3_strok_mm"]) / 1000.0 * 1000.0
    V_pompa = Qp1 / 60.0 * t2
    dV_acc = V2 - V_pompa + V3
    # 2) basınçlar ve gereken V0
    p2_min = float(tas["p_min_oran"]) * p1
    p0 = float(tas["p0_oran"]) * p2_min
    V0_gerekli = gerekli_V0_l(dV_acc, p0, p1, p2_min, n)
    a56 = parts["A56"]
    adet = len(a56["instances"])
    v_tup, di, L_ic = tup_gaz_hacmi_l(a56["dims"], float(tas["tup_et_kalinligi_mm"]))
    V0 = adet * v_tup
    tup_min = math.ceil(V0_gerekli / v_tup)
    # 3) mevcut grupla deşarj (gaz yasası) -> faz 2 debisi
    kap = akumulator_faydali_hacim_l(V0, p0, p1, p2_min, n)    # p2_min'e kadar kapasite
    V2_acc_gercek = min(V2 - V_pompa, kap - V3)
    p2 = akumulator_son_basinc_bar(V0, p0, p1, V2_acc_gercek, n)
    p_faz3_bas = akumulator_son_basinc_bar(V0, p0, p1, V2_acc_gercek + V3, n)
    Q_acc_ort = V2_acc_gercek / t2 * 60.0
    Q_faz2 = (Q_acc_ort + Qp1) / (1.0 + float(tas["kayip_orani"]))   # pistona ulaşan
    v_faz2 = silindir_hizi_m_s(Q_faz2, bore)
    hat = hat_kaybi_A64(Q_acc_ort, params, tas)
    # 4) şarj ve motor
    V_sarj = V2_acc_gercek + V3
    t_sarj = V_sarj / (Qp1 / 60.0)
    guc = pompa_guc_kontrolu(hidrolik, params)
    p_motor = guc["motor_kW"]
    P1_mil = guc["pompalar"]["P1"]["mil_kW"]
    P2_mil = guc["pompalar"]["P2"]["mil_kW"]
    # şarj sırasında ortalama basınç (p_faz3_bas -> p1) ile P1 mil gücü, P2 tam yük kötü durum
    p_ort = (p_faz3_bas + p1) / 2.0
    P1_sarj = P1_mil * p_ort / p1
    tepe = (P1_sarj + P2_mil) / p_motor
    T = float(tas["cevrim_suresi_s"])
    # RMS: şarj süresince P1 tam + P2 sürekli tam (kötü durum), kalan sürede P1 boşaltmada ~%10 (VARSAYIM)
    P1_bos = 0.10 * P1_mil
    rms = math.sqrt(((P1_sarj + P2_mil) ** 2 * t_sarj + (P1_bos + P2_mil) ** 2 * (T - t_sarj)) / T) / p_motor
    durum_tepe = "OK" if tepe < 0.90 else ("SINIRDA" if tepe <= 1.05 else "YETERSIZ")
    durum_rms = "OK" if rms < 0.90 else ("SINIRDA" if rms <= 1.05 else "YETERSIZ")
    p_dogrudan_kW = hidrolik_guc_kw(p1, Q_hedef)
    # faz 3 statik çarpan basıncı (şarj faz 3 içinde biter -> besleme p1)
    p_carpan = p1 * oran
    F3 = p_carpan * 1e5 * A54 / 1000.0
    p_metal = F3 * 1000.0 / A_pl / 1e6
    return {
        "etiket": tas["etiket"],
        "hedef": {"v_m_s": v_hedef, "A54_bore_mm": bore, "A54_alan_cm2": round(A54 * 1e4, 2),
                  "Q_hedef_lpm": round(Q_hedef, 1), "plunger_d_mm": d_pl,
                  "metal_debi_L_s": round(A_pl * v_hedef * 1000.0, 2),
                  "faz2_sure_ms": t2 * 1000.0, "hizli_strok_mm": round(s2 * 1000.0, 1),
                  "faz1_strok_mm_sure_tabanli": round(silindir_hizi_m_s(Qp1, bore) * t1 * 1000.0, 1),
                  "toplam_strok_mm": strok_top,
                  "pompa_dogrudan_gerekli_kW": round(p_dogrudan_kW, 1)},
        "hacim": {"V_faz2_kayipli_l": round(V2, 3), "V_faz3_carpan_l": round(V3, 3),
                  "V_pompa_faz2_l": round(V_pompa, 3), "dV_acc_l": round(dV_acc, 3)},
        "akumulator": {"p1_bar": p1, "p2_min_bar": round(p2_min, 1), "p0_bar": round(p0, 1), "n": n,
                       "V0_gerekli_l": round(V0_gerekli, 1), "tup_ic_cap_mm": round(di, 1),
                       "tup_ic_boy_mm": round(L_ic, 1), "tup_gaz_hacmi_l": round(v_tup, 2),
                       "tup_adet": adet, "tup_min_adet": tup_min, "V0_mevcut_l": round(V0, 1),
                       "kapasite_p2min_l": round(kap, 2), "kapasite_orani": round(kap / dV_acc, 2),
                       "p2_gercek_bar": round(p2, 1), "p_faz3_baslangic_bar": round(p_faz3_bas, 1),
                       "p0_p1_oran": round(p0 / p1, 3), "p1_p0_oran": round(p1 / p0, 3),
                       "durum": "OK" if V0 >= V0_gerekli else "YETERSIZ"},
        "faz2": {"Q_acc_ort_lpm": round(Q_acc_ort, 1), "Q_P1_lpm": Qp1, "Q_piston_lpm": round(Q_faz2, 1),
                 "v_piston_m_s": round(v_faz2, 3), "hedefe_ulasti": v_faz2 >= v_hedef - 1e-6, "hat_A64": hat,
                 "basinc_dusumu_yuzde": round((p1 - p2) / p1 * 100.0, 1)},
        "faz3": {"carpan_orani": round(oran, 4), "p_carpan_bar": round(p_carpan, 2), "F_kN": round(F3, 1),
                 "p_metal_MPa": round(p_metal, 2), "params_injection_force_kN": g["injection_force_kN"]},
        "sarj": {"V_sarj_l": round(V_sarj, 3), "t_sarj_s": round(t_sarj, 2), "faz3_sure_s": t3,
                 "faz3_icinde_biter": t_sarj <= t3,
                 "P1_sarj_mil_kW": round(P1_sarj, 2), "P2_mil_kW": P2_mil,
                 "tepe_yuk_orani": round(tepe, 3), "tepe_durum": durum_tepe,
                 "cevrim_s": T, "rms_yuk_orani": round(rms, 3), "rms_durum": durum_rms},
    }


def orifis_dp_bar(Q_lpm, d_mm, Cd, rho):
    """Tam açık oturmalı kartuş / keskin orifis: dP = rho/2 * (Q / (Cd * A))^2 [bar] (A = pi d^2 / 4).
    Denklem OpenHydraulics/Hopsan orifis modeliyle aynı türden (Q = Cd A sqrt(2 dP / rho)); kod bağımsız."""
    A = math.pi * (d_mm / 1000.0) ** 2 / 4.0
    Q = Q_lpm / 60000.0
    return rho / 2.0 * (Q / (Cd * A)) ** 2 / 1e5


def kesit_hiz_m_s(Q_lpm, alan_mm2):
    return Q_lpm / 60000.0 / (alan_mm2 / 1e6)


def _daire_mm2(d_mm):
    return math.pi * d_mm ** 2 / 4.0


def _kanal_alan_mm2(k):
    """Kanal kesiti: {'d': ..} daire; {'b': genislik, 'l': boy} oval (stadyum) kesit."""
    if "d" in k:
        return _daire_mm2(float(k["d"])) * int(k.get("adet", 1))
    b, l = float(k["b"]), float(k["l"])
    return (b * (l - b) + _daire_mm2(b)) * int(k.get("adet", 1))


def a65_ic_devre_hesabi(hidrolik=None, params=None, hatlar=None, vurus=None):
    """A54 iç kanalları (A kapak / B kol) + A65 iç valfleri (Y1.1..Y1.11) faz bazlı debi, hız, dP.
    Fazlar: 0 boşta, 1 yavaş, 2 hızlı, 3 çarpan, 4 çarpan boşaltma (S118), 5 piston geri.
    Girdiler: params/hidrolik.json a65_ic_devre_tasarim (ikiz_tasarim varsayımı), params.json A54/A55/A65/A186,
    hatlar.json T hatları, hizli_vurus_hesabi() faz debileri. Geometri DEĞİŞTİRMEZ, yalnız kontrol eder."""
    hidrolik = hidrolik or _oku("params/hidrolik.json")
    params = params or _oku("params/params.json")
    hatlar = hatlar or _oku("params/hatlar.json")
    vurus = vurus or hizli_vurus_hesabi(hidrolik, params)
    tas = hidrolik["a65_ic_devre_tasarim"]
    yag = hidrolik["hizli_vurus_tasarim"]["yag"]
    rho, nu = float(yag["rho_kg_m3"]), float(yag["nu_cSt"])
    Cd = float(tas["Cd"])
    parts = params["parts"]
    g = params["global"]
    p1 = float(g["system_pressure_bar"])
    d54 = parts["A54"]["dims"]
    bore = float(d54["barrel"]["bore"])
    rod = float(parts["A186"]["dims"]["rod"]["d"])
    A_cap = _daire_mm2(bore)
    A_ann = A_cap - _daire_mm2(rod)
    oran_ba = A_ann / A_cap
    a55 = parts["A55"]["dims"]["internal"]
    A55_buyuk = _daire_mm2(float(a55["piston_d"]))
    A55_kucuk = _daire_mm2(float(a55["plunger_d"]))
    A55_halka = A55_buyuk - A55_kucuk
    Qp1 = next(p for p in hidrolik["elemanlar"]["pompalar"] if p["id"] == "P1")["nominal_debi_lpm"]
    f2 = vurus["faz2"]
    Q_S424 = f2["Q_acc_ort_lpm"]                      # ACC1 -> S424
    Q_A_faz2_valf = f2["Q_acc_ort_lpm"] + f2["Q_P1_lpm"]   # S424 + S120 -> A düğümü (kayıp dahil)
    Q_piston2 = f2["Q_piston_lpm"]
    Q_PA = float(tas["faz3"]["Q_PA_lpm"])
    v55 = kesit_hiz_m_s(Q_PA, A55_buyuk)              # A55 = A54 faz 3 piston hızı (A55 küçük = A54 çap)
    Q_halka55 = v55 * A55_halka * 60000.0 / 1e6
    Q_B3 = v55 * A_ann * 60000.0 / 1e6
    # faz 4 dekompresyon: kapak odası + A55 küçük taraf sıkışma hacmi (K_eff) -> PA tarafına geri
    # ölü boy: geri konumda piston arka yüzü - arka kafa dış yüzü (A55 plunger dinlenmede kafa dış yüzünde, VARSAYIM)
    L_olu = float(parts["A186"]["dims"]["piston"]["x_range"][0]) - float(d54["rear_head"]["local_x_range"][0])
    L_kap = float(d54["stroke"]) + L_olu
    V_kap_l = A_cap * L_kap / 1e6
    dp3 = vurus["faz3"]["p_carpan_bar"]
    dV_kap_l = V_kap_l * dp3 * 1e5 / float(tas["faz4"]["K_eff_Pa"])
    V_PA_geri_l = dV_kap_l * A55_buyuk / A55_kucuk
    Q_dek = V_PA_geri_l / (float(tas["faz4"]["t_dekompresyon_ms"]) / 1000.0) * 60.0
    # faz 5 geri: P1 -> B
    v_geri = kesit_hiz_m_s(Qp1, A_ann)
    Q_A5 = v_geri * A_cap * 60000.0 / 1e6
    Q_V55_geri = A55_halka * float(tas["faz3"]["A55_strok_mm"]) / 1e6 / (float(tas["faz5"]["A55_donus_s"])) * 60.0
    debi = {  # valf id -> {faz: Q L/dk}
        "Y1.1": {1: Qp1},
        "Y1.2": {2: f2["Q_P1_lpm"]},
        "Y1.3": {2: Q_S424},
        "Y1.4": {1: Qp1, 2: Q_A_faz2_valf},
        "Y1.5": {1: Qp1 * oran_ba, 2: Q_piston2 * oran_ba, 3: Q_B3},
        "Y1.6": {5: Qp1},
        "Y1.7": {5: Q_A5},
        "Y1.8": {3: Q_PA},
        "Y1.9": {4: Q_dek, 5: Q_V55_geri * A55_buyuk / A55_halka},   # A55 geri: büyük taraf -> T
        "Y1.10": {3: Q_halka55, 5: Q_V55_geri},
        "Y1.11": {},
    }
    valfler = {}
    for v in tas["valfler"]:
        ng = str(v["NG"])
        ngt = tas["ng_tablosu"][ng]
        dmax = {}
        for faz, Q in debi.get(v["id"], {}).items():
            dmax[faz] = {"Q_lpm": round(Q, 1), "dp_bar": round(orifis_dp_bar(Q, float(ngt["oturma_d_mm"]), Cd, rho), 2),
                         "v_oturma_m_s": round(kesit_hiz_m_s(Q, _daire_mm2(float(ngt["oturma_d_mm"]))), 2)}
        dpmax = max([x["dp_bar"] for x in dmax.values()], default=0.0)
        valfler[v["id"]] = {"NG": v["NG"], "acik_fazlar": v["acik_fazlar"], "fazlar": dmax, "dp_max_bar": dpmax,
                            "durum": "OK" if dpmax <= float(tas["valf_dp_sinir_bar"]) else "YUKSEK_DP"}
    # A54 iç kanalları
    kan = {}
    akis = {"A": {1: Qp1, 2: Q_A_faz2_valf, 5: Q_A5}, "B": {1: Qp1 * oran_ba, 2: Q_piston2 * oran_ba, 3: Q_B3, 5: Qp1}}
    for ad, k in tas["a54_ic_kanallar"].items():
        A = _kanal_alan_mm2(k["kanal"])
        Ap = _daire_mm2(float(k["port_d_mm"])) if "port_d_mm" in k else A
        Qm = max(akis[ad].values())
        v = kesit_hiz_m_s(Qm, A)
        dp = float(k["K_toplam"]) * rho * v ** 2 / 2.0 / 1e5
        kan[ad] = {"alan_mm2": round(A, 0), "Q_max_lpm": round(Qm, 1), "v_kanal_m_s": round(v, 2),
                   "v_port_m_s": round(kesit_hiz_m_s(Qm, Ap), 2), "dp_bar": round(dp, 2),
                   "durum": "OK" if v <= float(tas["kanal_hiz_sinir_m_s"]) else "HIZ_YUKSEK",
                   "fazlar": {f: round(q, 1) for f, q in akis[ad].items()}}
    # T karşı basıncı (faz 2, B -> Y1.5 -> T/T2 -> H20H/H20H2 -> H20R -> tank); RF1 hariç
    hl = {h["id"]: h for h in hatlar["hatlar"]}
    ru = float(hidrolik["hizli_vurus_tasarim"]["hat"]["puruzluluk_mm"])
    QB2 = Q_piston2 * oran_ba
    def _L(h):
        if "hortum_uzunluk_mm" in h:
            return h["hortum_uzunluk_mm"] / 1000.0
        pts = [h["guzergah"]["baslangic"]] + h["guzergah"]["ara_noktalar"] + [h["guzergah"]["bitis"]]
        return sum(sum(abs(a - b) for a, b in zip(p, q)) for p, q in zip(pts, pts[1:])) / 1000.0
    Kh = float(tas["t_hat"]["K_hortum_rakor"])
    dpH = max(_boru_dp_bar(QB2 / 2.0, hl[i].get("hortum", {}).get("ic_cap_mm", hl[i].get("ic_cap_mm")), _L(hl[i]),
                           rho, nu, ru, Kh)[0] for i in ("H20H", "H20H2"))
    dpR = _boru_dp_bar(QB2, hl["H20R"]["ic_cap_mm"], _L(hl["H20R"]), rho, nu, ru, float(tas["t_hat"]["K_H20R"]))[0]
    H60 = hatlar["hatlar_a183"]["H60"]
    dp60 = _boru_dp_bar(QB2, H60["ic_cap_mm"], H60["L_mm"] / 1000.0, rho, nu, ru, float(tas["t_hat"]["K_H60"]))[0]
    pB = kan["B"]["dp_bar"] + dp60 + valfler["Y1.5"]["fazlar"][2]["dp_bar"] + dpH + dpR
    # faz 2 basınç bütçesi (vuruş sonu, kararlı akış; ivme rampası ayrı)
    hat = f2["hat_A64"]
    p_acc2 = vurus["akumulator"]["p2_gercek_bar"]
    dpA = (hat["dp_sabit_bar"] + valfler["Y1.3"]["fazlar"][2]["dp_bar"] + valfler["Y1.4"]["fazlar"][2]["dp_bar"]
           + kan["A"]["dp_bar"])
    p_kap = p_acc2 - dpA
    p_net = p_kap - pB * oran_ba              # kapak eşdeğeri net (piston + metal direnci + sürtünme için)
    F_net = p_net * 1e5 * A_cap / 1e6 / 1000.0
    p_metal_esd = float(tas["faz2_metal_basinci_bar"]) * _daire_mm2(float(g["plunger_d"])) / A_cap
    pay = p_net - p_metal_esd
    # A65 yerleşim kontrolü (kartuş boşlukları ISO 7368 yaklaşık; geometri değişmez, yalnız rapor)
    blk = parts["A65"]["dims"]["block"]
    bx, by, bz = float(blk["len_x"]), float(blk["width_y"]), float(blk["z_range"][1] - blk["z_range"][0])
    kapak_top = sum(float(tas["ng_tablosu"][str(v["NG"])]["kapak_mm"]) ** 2 for v in tas["valfler"] if v.get("A65_icinde", True))
    derin_max = max(float(tas["ng_tablosu"][str(v["NG"])]["derinlik_mm"]) for v in tas["valfler"])
    sigan_eksen = [ad for ad, L in (("x", bx), ("y", by), ("z", bz)) if derin_max + float(tas["yerlesim"]["taban_et_mm"]) <= L]
    serbest = float(tas["yerlesim"]["serbest_yuz_mm2"])
    yer_durum = "OK" if (kapak_top * float(tas["yerlesim"]["paketleme"]) <= serbest and len(sigan_eksen) >= 2) else "YETERSIZ"
    # önerilen asgari zarf: tüm kartuşlar üst yüzden dikey (z), y genişliği korunur
    z_min = derin_max + float(tas["yerlesim"]["taban_et_mm"]) + float(tas["yerlesim"]["alt_kanal_katmani_mm"])
    x_min = (kapak_top * float(tas["yerlesim"]["paketleme"]) + float(tas["yerlesim"]["ust_yuz_dolu_mm2"])) / by
    return {
        "etiket": tas["etiket"],
        "alanlar_mm2": {"A54_kapak": round(A_cap, 0), "A54_halka": round(A_ann, 0), "halka_kapak_oran": round(oran_ba, 4),
                        "A55_buyuk": round(A55_buyuk, 0), "A55_kucuk": round(A55_kucuk, 0), "A55_halka": round(A55_halka, 0)},
        "a54_ic_kanallar": kan,
        "valfler": valfler,
        "faz3": {"v_A55_m_s": round(v55, 3), "Q_PA_lpm": Q_PA, "Q_A55_halka_lpm": round(Q_halka55, 1),
                 "Q_B_lpm": round(Q_B3, 1), "p_kapak_bar": dp3,
                 "Y1.4_kilit": "S116 (DO7.10) kapali tutar; kapak 285,7 bar > ACC ~135 bar geri akis yok"},
        "faz4": {"L_olu_mm": L_olu, "V_kapak_l": round(V_kap_l, 2), "dV_sikisma_l": round(dV_kap_l, 3), "V_PA_geri_l": round(V_PA_geri_l, 3),
                 "Q_dekompresyon_lpm": round(Q_dek, 1)},
        "faz5": {"v_geri_m_s": round(v_geri, 3), "t_geri_s": round(float(d54["stroke"]) / 1000.0 / v_geri, 2),
                 "Q_B_giris_lpm": Qp1, "Q_A_cikis_lpm": round(Q_A5, 1), "F_geri_kN": round(p1 * 1e5 * A_ann / 1e6 / 1000.0, 1)},
        "faz2_butce": {"p_acc_son_bar": p_acc2, "dp_A_yolu_bar": round(dpA, 2), "p_kapak_bar": round(p_kap, 1),
                       "Q_B_lpm": round(QB2, 1), "dp_B_kanal_H60_bar": round(kan["B"]["dp_bar"] + dp60, 2),
                       "dp_T_hortum_bar": round(dpH, 2), "dp_H20R_bar": round(dpR, 2), "p_B_bar": round(pB, 2),
                       "p_net_kapak_esd_bar": round(p_net, 1), "F_net_kN": round(F_net, 1),
                       "p_metal_esd_bar": round(p_metal_esd, 1), "kisma_payi_bar": round(pay, 1),
                       "dp_ivme_rampa_bar": hat["dp_ivme_bar"],
                       "durum": "OK" if pay - hat["dp_ivme_bar"] > 0 else "YETERSIZ",
                       "not": "RF1 donus filtresi dP haric (bypass acma basinci SAHA_DOGRULAMA); kisma payi S424 servo kontrol araligi"},
        "a65_yerlesim": {"blok_mm": [bx, by, bz], "kapak_alani_top_mm2": round(kapak_top, 0),
                         "gerekli_yuz_mm2": round(kapak_top * float(tas["yerlesim"]["paketleme"]), 0),
                         "serbest_yuz_mm2": serbest, "en_derin_bosluk_mm": derin_max, "sigan_eksenler": sigan_eksen,
                         "durum": yer_durum, "onerilen_asgari_zarf_mm": [round(x_min, -1), by, round(z_min, -1)]},
    }


def _bul_anahtar(d, anahtar):
    """İç içe dict/list içinde anahtarı taşıyan ilk dict'i döner."""
    if isinstance(d, dict):
        if anahtar in d:
            return d
        for v in d.values():
            r = _bul_anahtar(v, anahtar)
            if r is not None:
                return r
    elif isinstance(d, list):
        for v in d:
            r = _bul_anahtar(v, anahtar)
            if r is not None:
                return r
    return None


class HidrolikAgModeli:
    def __init__(self):
        self.sistem_basinci = 140.0  # bar
        self.akumulator_basinci = 140.0  # bar
        self.tank_basinci = 0.0  # bar
        hid = _oku("params/hidrolik.json")
        prm = _oku("params/params.json")
        self.sistem_basinci = float(prm["global"]["system_pressure_bar"])
        self.akumulator_basinci = self.sistem_basinci
        p1 = next(p for p in hid["elemanlar"]["pompalar"] if p["id"] == "P1")
        self.p1_debi_lpm = float(p1["nominal_debi_lpm"])
        self.a54_bore_mm = float(prm["parts"]["A54"]["dims"]["barrel"]["bore"])
        self.vurus = hizli_vurus_hesabi(hid, prm)
        self.akumulator_hacim_lt = self.vurus["akumulator"]["V0_mevcut_l"]  # A56 x4 gaz hacmi (V0)
        self.carpan_orani = self.vurus["faz3"]["carpan_orani"]
        self.valf_durumlari = {
            "Y1": False,  # Hızlı vuruş
            "Y2": False,  # Mengene
            "Y3": False,  # İtici
            "DV1": True,  # E-stop deşarj valfi (varsayılan kapalı, enerji kesilince açık)
            "A55": False  # Çarpan
        }

    def a65_valf_durumu(self, faz: int):
        """A65 iç valfleri (Y1.1..Y1.11) için faz bazlı açık/kapalı + debi (a65_ic_devre_hesabi).
        faz: 0 boşta, 1 yavaş, 2 hızlı, 3 çarpan, 4 çarpan boşaltma, 5 piston geri."""
        if not hasattr(self, "_a65"):
            self._a65 = a65_ic_devre_hesabi(vurus=self.vurus)
            self._a65_tas = {v["id"]: v for v in _oku("params/hidrolik.json")["a65_ic_devre_tasarim"]["valfler"]}
        acik = {}
        for vid, v in self._a65["valfler"].items():
            if faz in v["acik_fazlar"]:
                q = v["fazlar"].get(faz, {}).get("Q_lpm", v["fazlar"].get(str(faz), {}).get("Q_lpm", 0.0))
                acik[vid] = {"yol": self._a65_tas[vid]["yol"], "Q_lpm": q, "bobin": self._a65_tas[vid]["bobin"]}
        return acik

    def akumulator_desarj_simulasyonu(self, adim_saniye=0.5, sure_saniye=4.0):
        """E-stop veya duruş anında akümülatör basıncının deşarj vanası (DV1) üzerinden düşüşünü simüle eder."""
        zaman = 0.0
        basinc = self.akumulator_basinci
        egri = []

        # Deşarj zaman sabiti (daha hızlı deşarj için ayarlandı)
        tau = 0.8
        while zaman <= sure_saniye:
            basinc = self.akumulator_basinci * (2.71828 ** (-zaman / tau))
            if basinc < 1.0:
                basinc = 0.0
            egri.append((round(zaman, 2), round(basinc, 2)))
            zaman += adim_saniye
            if basinc == 0.0:
                break
        return egri

    def valf_ve_silindir_akis_kontrolu(self, enjeksiyon_fazi: int):
        """Enjeksiyon fazlarına (1: yavaş, 2: hızlı, 3: basınç artırma/çarpan) göre hidrolik besleme ve valf haritalaması."""
        sonuc = {"faz": enjeksiyon_fazi, "kaynak": "", "basinç_bar": self.sistem_basinci, "aktif_valfler": []}
        if enjeksiyon_fazi == 1:
            sonuc["kaynak"] = "Pompa P1 (Doğrudan besleme)"
            sonuc["akis_lpm"] = self.p1_debi_lpm
            sonuc["aktif_valfler"] = ["Y2 (Mengene/Sistem)"]
        elif enjeksiyon_fazi == 2:
            sonuc["kaynak"] = "Pompa P1 + Akümülatör ACC1 (Hızlı vuruş)"
            sonuc["akis_lpm"] = self.vurus["faz2"]["Q_piston_lpm"]   # gaz yasası + P1 (hizli_vurus_hesabi)
            sonuc["acc_debi_lpm"] = self.vurus["faz2"]["Q_acc_ort_lpm"]
            sonuc["acc_son_basinc_bar"] = self.vurus["akumulator"]["p2_gercek_bar"]
            sonuc["aktif_valfler"] = ["Y1 (Hızlı Vuruş Valfi)", "ACC1"]
        elif enjeksiyon_fazi == 3:
            sonuc["kaynak"] = f"A55 Çarpan (Basınç Artırma, {self.carpan_orani:.3f} oran = (Ø200/Ø140)^2)"
            sonuc["basinç_bar"] = round(self.sistem_basinci * self.carpan_orani, 2)
            sonuc["aktif_valfler"] = ["A55 (Multiplikatör Valfi)"]
        else:
            sonuc["kaynak"] = "Boşta / Bekleme"
            sonuc["akis_lpm"] = 0.0
            sonuc["aktif_valfler"] = ["DV1 (Güvenlik deşarjı kapalı)"]
        sonuc["a65_acik"] = sorted(self.a65_valf_durumu(enjeksiyon_fazi))
        if sonuc.get("akis_lpm"):
            sonuc["a54_hiz_m_s"] = round(silindir_hizi_m_s(sonuc["akis_lpm"], self.a54_bore_mm), 3)
        return sonuc


if __name__ == "__main__":
    print(json.dumps(pompa_guc_kontrolu(), ensure_ascii=False, indent=1))
    print(json.dumps(hizli_vurus_hesabi(), ensure_ascii=False, indent=1))
    print(json.dumps(a65_ic_devre_hesabi(), ensure_ascii=False, indent=1))
