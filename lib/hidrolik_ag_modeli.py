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

# VARSAYIM: faz 2'de akümülatörün P1'e eklediği debi. Eski modelde örtük (350 - 120 = 230 L/dk);
# hız gereksinimi (Kademe 3 açık noktası) hesaplanınca akümülatör hacim/ön dolum hesabıyla değişecek.
ACC1_FAZ2_EK_DEBI_LPM = 230.0


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


class HidrolikAgModeli:
    def __init__(self):
        self.sistem_basinci = 140.0  # bar
        self.akumulator_basinci = 140.0  # bar
        self.tank_basinci = 0.0  # bar
        self.akumulator_hacim_lt = 2.6  # 2 x 1.3L (A56 / ACC1)
        hid = _oku("params/hidrolik.json")
        prm = _oku("params/params.json")
        self.sistem_basinci = float(prm["global"]["system_pressure_bar"])
        self.akumulator_basinci = self.sistem_basinci
        p1 = next(p for p in hid["elemanlar"]["pompalar"] if p["id"] == "P1")
        self.p1_debi_lpm = float(p1["nominal_debi_lpm"])
        self.a54_bore_mm = float(prm["parts"]["A54"]["dims"]["barrel"]["bore"])
        self.valf_durumlari = {
            "Y1": False,  # Hızlı vuruş
            "Y2": False,  # Mengene
            "Y3": False,  # İtici
            "DV1": True,  # E-stop deşarj valfi (varsayılan kapalı, enerji kesilince açık)
            "A55": False  # Çarpan
        }

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
            sonuc["akis_lpm"] = self.p1_debi_lpm + ACC1_FAZ2_EK_DEBI_LPM
            sonuc["aktif_valfler"] = ["Y1 (Hızlı Vuruş Valfi)", "ACC1"]
        elif enjeksiyon_fazi == 3:
            sonuc["kaynak"] = "A55 Çarpan (Basınç Artırma, 2.04 oran)"
            sonuc["basinç_bar"] = self.sistem_basinci * 2.04
            sonuc["aktif_valfler"] = ["A55 (Multiplikatör Valfi)"]
        else:
            sonuc["kaynak"] = "Boşta / Bekleme"
            sonuc["akis_lpm"] = 0.0
            sonuc["aktif_valfler"] = ["DV1 (Güvenlik deşarjı kapalı)"]
        if sonuc.get("akis_lpm"):
            sonuc["a54_hiz_m_s"] = round(silindir_hizi_m_s(sonuc["akis_lpm"], self.a54_bore_mm), 3)
        return sonuc


if __name__ == "__main__":
    print(json.dumps(pompa_guc_kontrolu(), ensure_ascii=False, indent=1))
