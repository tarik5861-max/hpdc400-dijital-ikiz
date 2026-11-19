"""
Kademe 3 Hidrolik Ağ Modeli ve Simülasyon Motoru (Genişletilmiş)
- ISO 1219 elemanları (Pompalar, Akümülatörler, Valfler, Silindirler)
- Akümülatör deşarj süresi ve basınç düşüm eğrisi simülasyonu
- Güvenlik zinciri / E-stop anında akümülatör deşarj testi (S121 / DV1)
"""

class HidrolikAgModeli:
    def __init__(self):
        self.sistem_basinci = 140.0  # bar
        self.akumulator_basinci = 140.0  # bar
        self.tank_basinci = 0.0  # bar
        self.akumulator_hacim_lt = 2.6  # 2 x 1.3L (A56 / ACC1)
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
            sonuc["akis_lpm"] = 120.0
            sonuc["aktif_valfler"] = ["Y2 (Mengene/Sistem)"]
        elif enjeksiyon_fazi == 2:
            sonuc["kaynak"] = "Pompa P1 + Akümülatör ACC1 (Hızlı vuruş)"
            sonuc["akis_lpm"] = 350.0
            sonuc["aktif_valfler"] = ["Y1 (Hızlı Vuruş Valfi)", "ACC1"]
        elif enjeksiyon_fazi == 3:
            sonuc["kaynak"] = "A55 Çarpan (Basınç Artırma, 2.04 oran)"
            sonuc["basinç_bar"] = self.sistem_basinci * 2.04
            sonuc["aktif_valfler"] = ["A55 (Multiplikatör Valfi)"]
        else:
            sonuc["kaynak"] = "Boşta / Bekleme"
            sonuc["akis_lpm"] = 0.0
            sonuc["aktif_valfler"] = ["DV1 (Güvenlik deşarjı kapalı)"]
        return sonuc
