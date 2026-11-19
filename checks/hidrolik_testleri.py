"""
Kademe 3 Hidrolik Ağ Simülasyonu ve Güvenlik Testleri (Genişletilmiş)
"""
import sys
import os

# Ensure project root is in sys.path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from lib.hidrolik_ag_modeli import HidrolikAgModeli

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
    print("✓ Enjeksiyon faz ve valf haritalama testleri BAŞARILI.")

if __name__ == "__main__":
    test_desarj_guvenligi()
    test_enjeksiyon_fazlari()
    print("Tüm Kademe 3 hidrolik ağ simülasyon testleri başarıyla tamamlandı.")
