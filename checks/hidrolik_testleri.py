"""
Kademe 3 Hidrolik Ağ Simülasyonu ve Güvenlik Testleri (Genişletilmiş)
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import math
from lib.hidrolik_ag_modeli import HidrolikAgModeli, pompa_guc_kontrolu, hizli_vurus_hesabi

# Beklentiler elle hesaplandi (2026-11-19): 45VQ42 136 cm3/dev, 20VQ5 16.4 cm3/dev, A120 1480 d/dk,
# eta_v 0.95, eta_hm 0.92, 140 bar, A54 bore 140 mm.
# Faz 2 (2026-11-19 rev): sabit 230 L/dk ACC1 ek debisi KALDIRILDI; hedef piston hizi 3.0 m/s
# (ikiz_tasarim varsayimi, params/hidrolik.json hizli_vurus_tasarim) -> ACC1 gaz yasasi.
BEKLENEN_P1_LPM = 191.2   # 136*1480*0.95/1000 = 191.22 (eski 120)
BEKLENEN_P2_LPM = 23.1    # 16.4*1480*0.95/1000 = 23.06 (eski 25)
A54_M2 = math.pi * 0.14 ** 2 / 4.0
BEKLENEN_FAZ2_LPM = 2770.9  # A54*3.0*60000 = 2770.88 (eski 421.2 = 191.2+230 sabit)
BEKLENEN_V1 = 0.207       # 191.2/60000 / (pi*0.14^2/4) m/s
BEKLENEN_V2 = 3.000       # hedef; eski 0.456 m/s (gercekci degildi, tipik 2-5 m/s)
BEKLENEN_FAZ3_BAR = 285.71  # 140*(200/140)^2 = 285.714 (eski 285.6 = 140*2.04 yuvarlak oran)

def test_desarj_guvenligi():
    print("Test 1: Akümülatör deşarj simülasyonu (E-stop / S121 / DV1)...")
    ag = HidrolikAgModeli()
    egri = ag.akumulator_desarj_simulasyonu(adim_saniye=0.5, sure_saniye=3.0)
    print("Deşarj eğrisi (Zaman, Basınç bar):", egri)
    son_basinc = egri[-1][1]
    assert son_basinc < 5.0, f"Akümülatör deşarjı yetersiz! Son basınç: {son_basinc} bar"
    print("✓ Akümülatör deşarj testi BAŞARILI.")

def test_enjeksiyon_fazlari():
    print("Test 2: Enjeksiyon fazları hidrolik akış, valf (Y1, Y2, Y3, DV1, A55) ve çarpan kontrolü...")
    ag = HidrolikAgModeli()
    for faz in [1, 2, 3, 0]:
        bilgi = ag.valf_ve_silindir_akis_kontrolu(faz)
        print(f"  Faz {faz}: {bilgi}")
        if faz == 1:
            assert abs(bilgi["akis_lpm"] - BEKLENEN_P1_LPM) < 0.05, bilgi
            assert abs(bilgi["a54_hiz_m_s"] - BEKLENEN_V1) < 0.001, bilgi
        if faz == 2:
            assert abs(bilgi["akis_lpm"] - BEKLENEN_FAZ2_LPM) < 0.05, bilgi
            assert abs(bilgi["a54_hiz_m_s"] - BEKLENEN_V2) < 0.001, bilgi
            assert bilgi["acc_son_basinc_bar"] >= 126.0, bilgi   # p2_min = 0.9*140
        if faz == 3:
            assert abs(bilgi["basinç_bar"] - BEKLENEN_FAZ3_BAR) < 0.01, bilgi
    print("✓ Enjeksiyon faz ve valf haritalama testleri BAŞARILI.")

def test_pompa_guc():
    print("Test 3: P1+P2 debi ve M1 (A120 55 kW) guc kontrolu...")
    g = pompa_guc_kontrolu()
    print("  ", g["pompalar"], "mil", g["toplam_mil_kW"], "kW", g["durum"])
    assert abs(g["pompalar"]["P1"]["debi_lpm"] - BEKLENEN_P1_LPM) < 0.05
    assert abs(g["pompalar"]["P2"]["debi_lpm"] - BEKLENEN_P2_LPM) < 0.05
    assert abs(g["toplam_hidrolik_kW"] - 50.0) < 0.05   # 140*(191.22+23.06)/600 = 50.00
    assert g["toplam_hidrolik_kW"] <= g["motor_kW"]
    assert abs(g["toplam_mil_kW"] - 57.21) < 0.05      # 140*1480*(136+16.4)/(600000*0.92)
    assert g["durum"] == "SINIRDA", g["durum"]          # %104: tam yukte motor sinirda
    print("✓ Pompa guc testi BAŞARILI (SINIRDA).")

def test_akumulator_ters_hesap():
    print("Test 4: ACC1 (A56 x4) ters hesap - hedef 3.0 m/s, gaz yasasi n=1.4...")
    r = hizli_vurus_hesabi()
    # bagimsiz el hesabi (mutlak basinc, bar+1)
    V2 = A54_M2 * (3.0 * 0.060) * 1.05 * 1000.0          # 180 mm hizli strok, %5 kayip = 2.909 L
    V3 = math.pi * 0.2 ** 2 / 4.0 * 0.010 * 1000.0        # A55 O200 x 10 mm = 0.314 L
    Vp = 191.22 / 60.0 * 0.060                            # P1 katkisi 60 ms = 0.191 L
    dV = V2 - Vp + V3                                     # 3.032 L
    p1, p2, p0, n = 141.0, 127.0, 114.4, 1.4              # 140/126/113.4 bar g
    k = (p0 / p2) ** (1 / n) - (p0 / p1) ** (1 / n)
    V0_ger = dV / k                                       # ~45.4 L
    r_ = 0.095; h = 0.045
    v_tup = (math.pi * r_ ** 2 * (1.170 - 2 * h) + 2 * (2 / 3) * math.pi * r_ ** 2 * h) * 1000.0  # 32.32 L
    V0 = 4 * v_tup
    V1 = V0 * (p0 / p1) ** (1 / n)
    p2_g = p1 * (V1 / (V1 + (V2 - Vp))) ** n - 1.0        # ~135.3 bar g
    a = r["akumulator"]
    print("  ", r["hacim"], a)
    assert abs(r["hacim"]["dV_acc_l"] - dV) < 0.005, (r["hacim"], dV)
    assert abs(a["V0_gerekli_l"] - V0_ger) < 0.1, (a["V0_gerekli_l"], V0_ger)
    assert abs(a["tup_gaz_hacmi_l"] - v_tup) < 0.01, (a["tup_gaz_hacmi_l"], v_tup)
    assert abs(a["p2_gercek_bar"] - p2_g) < 0.1, (a["p2_gercek_bar"], p2_g)
    assert a["tup_min_adet"] == 2 and a["tup_adet"] == 4 and a["durum"] == "OK"
    assert a["p2_gercek_bar"] >= a["p2_min_bar"] and a["p0_bar"] <= 0.9 * a["p2_min_bar"] + 1e-9
    assert r["faz2"]["hedefe_ulasti"]
    s = r["sarj"]
    assert s["faz3_icinde_biter"] and abs(s["t_sarj_s"] - dV / (191.22 / 60.0)) < 0.01
    assert s["tepe_durum"] == "SINIRDA", s                # sarj aninda P1+P2 ~%102
    assert s["rms_durum"] == "OK", s
    print("✓ ACC1 ters hesap testi BAŞARILI (4 tup yeterli, min 2).")

if __name__ == "__main__":
    test_desarj_guvenligi()
    test_enjeksiyon_fazlari()
    test_pompa_guc()
    test_akumulator_ters_hesap()
    print("Tüm Kademe 3 hidrolik ağ simülasyon testleri başarıyla tamamlandı.")
