"""
Kademe 3 Hidrolik Ağ Simülasyonu ve Güvenlik Testleri (Genişletilmiş)
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.hidrolik_ag_modeli import HidrolikAgModeli, pompa_guc_kontrolu

# Beklentiler elle hesaplandi (2026-11-19): 45VQ42 136 cm3/dev, 20VQ5 16.4 cm3/dev, A120 1480 d/dk,
# eta_v 0.95, eta_hm 0.92, 140 bar, A54 bore 140 mm, ACC1 faz-2 ek debi 230 L/dk (VARSAYIM).
BEKLENEN_P1_LPM = 191.2   # 136*1480*0.95/1000 = 191.22 (eski 120)
BEKLENEN_P2_LPM = 23.1    # 16.4*1480*0.95/1000 = 23.06 (eski 25)
BEKLENEN_FAZ2_LPM = 421.2 # 191.2 + 230 (eski 350)
BEKLENEN_V1 = 0.207       # 191.2/60000 / (pi*0.14^2/4) m/s
BEKLENEN_V2 = 0.456       # 421.2/60000 / (pi*0.14^2/4) m/s

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
        if faz == 3:
            assert abs(bilgi["basinç_bar"] - 285.6) < 0.05, bilgi
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

if __name__ == "__main__":
    test_desarj_guvenligi()
    test_enjeksiyon_fazlari()
    test_pompa_guc()
    print("Tüm Kademe 3 hidrolik ağ simülasyon testleri başarıyla tamamlandı.")
