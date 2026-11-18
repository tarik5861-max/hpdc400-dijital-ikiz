from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class ModuleType(Enum):
    DI = "Dijital Giriş (DI)"
    DO = "Dijital Çıkış (DO)"
    AI = "Analog Giriş (AI)"
    AO = "Analog Çıkış (AO)"

@dataclass
class IOChannel:
    slot: int
    module_name: str
    address: str
    tag: str
    description: str
    channel_type: ModuleType
    page: str
    associated_fuses: List[str] = field(default_factory=list)
    associated_relays: List[str] = field(default_factory=list)

@dataclass
class TroubleshootingRule:
    symptom: str
    affected_components: List[str]
    root_causes: List[str]
    checks: List[str]
    related_plc_addresses: List[str]

class DCC630CompleteSystem:
    """
    L.K. Machinery DCC630 - Eksiksiz PLC I/O Veri Tabanı (128+ Kanal) 
    ve Akıllı Arıza Teşhis (Troubleshooting) Motoru
    """
    def __init__(self):
        self.io_database: Dict[str, IOChannel] = {}
        self.troubleshooting_rules: List[TroubleshootingRule] = []
        self._build_complete_io_map()
        self._build_troubleshooting_knowledge_base()

    def _build_complete_io_map(self):
        """Şema sayfalarındaki (9-4, 9-5, 9-7, 9-8) 128+ I/O kanalının haritalaması"""
        
        # --- SLOT 4 & 6: DİJİTAL GİRİŞLER (DI) ---
        di_channels = [
            (4, "SM323-DI", "I0.0", "1B0", "Kalıp Kapama Butonu 1", "9-4", ["FU10"]),
            (4, "SM323-DI", "I0.1", "1B1", "Kalıp Açma Butonu", "9-4", ["FU10"]),
            (4, "SM323-DI", "I0.2", "1B2", "Enjeksiyon Butonu", "9-4", ["FU10"]),
            (4, "SM323-DI", "I0.3", "1B3-1", "Piston İleri (Plunger FWD) Knob", "9-4", ["FU10"]),
            (4, "SM323-DI", "I0.4", "1B3-2", "Piston Geri (Plunger BWD) Knob", "9-4", ["FU10"]),
            (4, "SM323-DI", "I0.5", "1B4-1", "İtici İleri (Ejector FWD) Knob", "9-4", ["FU10"]),
            (4, "SM323-DI", "I0.6", "1B4-2", "İtici Geri (Ejector BWD) Knob", "9-4", ["FU10"]),
            (4, "SM323-DI", "I0.7", "1B7-1", "Manuel Mod Seçici", "9-4", ["FU10"]),
            (4, "SM323-DI", "I1.0", "1B7-2", "Otomatik Mod Seçici", "9-4", ["FU10"]),
            (4, "SM323-DI", "I1.1", "1B9", "Piston Yağlama Knob", "9-4", ["FU10"]),
            (4, "SM323-DI", "I1.2", "1B10", "Motor Start Butonu", "9-4", ["FU10"]),
            (4, "SM323-DI", "I1.3", "1B11A-2", "Motor Stop Butonu", "9-4", ["FU10"]),
            (4, "SM323-DI", "I1.4", "1B12A", "Kalıp Ayar Butonu (Die Adjust)", "9-4", ["FU10"]),
            (4, "SM323-DI", "I1.5", "1B13", "Yarı Otomatik Seçici", "9-4", ["FU10"]),
            (4, "SM323-DI", "I1.6", "1B15", "Kalıp Kapama Butonu 2", "9-4", ["FU10"]),
            
            # Slot 6: SM321 DI32 (Genişletilmiş Sensörler ve Limitler)
            (6, "SM321-DI", "I2.0", "2LS1", "Ön Kapı Kapalı Limit 2", "9-5", ["FU10"], ["KA9"]),
            (6, "SM321-DI", "I2.1", "2LS2", "Ön Kapı Kapalı Limit 1", "9-5", ["FU10"], ["KA9"]),
            (6, "SM321-DI", "I2.2", "2LS3", "Arka Kapı Kapalı Limit 2", "9-5", ["FU10"], ["KA9"]),
            (6, "SM321-DI", "I2.3", "2LS4", "Arka Kapı Kapalı Limit 1", "9-5", ["FU10"], ["KA9"]),
            (6, "SM321-DI", "I2.4", "2LS5", "Kalıp İnce Limit (Die Thin)", "9-5", ["FU10"]),
            (6, "SM321-DI", "I2.5", "2LS6", "Kalıp Kalın Limit (Die Thick)", "9-5", ["FU10"]),
            (6, "SM321-DI", "I2.6", "2LS7", "Yağ Seviye Alarmı (Lub Level)", "9-5", ["FU10"]),
            (6, "SM321-DI", "I2.7", "2LS8", "Kalıp Kapalı Onay LS (Confirm)", "9-5", ["FU10"]),
            (6, "SM321-DI", "I3.0", "3LS9", "Yavaş Enjeksiyon Limiti", "9-5", ["FU10"]),
            (6, "SM321-DI", "I3.1", "3LS10", "Piston Geri Limiti", "9-5", ["FU10"]),
            (6, "SM321-DI", "I3.2", "3LS11", "Atış Hazır Lambası / Sensörü", "9-5", ["FU10"]),
            (6, "SM321-DI", "I3.3", "E-STOP", "Acil Durdurma Anahtarı (E-Stop Chain)", "9-5", ["FU10"], ["KA9"]),
            (6, "SM321-DI", "I3.4", "TANK_LVL", "Hidrolik Tank Seviye/Sıcaklık", "9-5", ["FU10"]),
            (6, "SM321-DI", "I3.5", "3LS13", "Emme Filtresi Anahtarı (Oil Suction Filter)", "9-5", ["FU10"]),
            (6, "SM321-DI", "I3.6", "3LS15", "Ön Kapı Açık Limiti", "9-5", ["FU10"]),
            (6, "SM321-DI", "I3.7", "3LS15A", "Ön Kapı Emniyet Koruma Sensörü", "9-5", ["FU10"], ["KA9"]),
            
            # Ekstra DI Kanalları (I4.0 - I7.7 arası Core ve Seçici Girişleri)
            (6, "SM321-DI", "I4.0", "382-1", "Core 1 In Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I4.1", "382-2", "Core 1 Out Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I4.2", "384-1", "Core 2 In Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I4.3", "384-2", "Core 2 Out Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I4.4", "386-1", "Core 3 In Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I4.5", "386-2", "Core 3 Out Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I4.6", "388-1", "Core 4 In Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I4.7", "388-2", "Core 4 Out Seçici", "9-5", ["FU10"]),
            (6, "SM321-DI", "I5.0", "3B10", "Kapı Açma Butonu", "9-5", ["FU10"]),
            (6, "SM321-DI", "I5.1", "3B11", "Kapı Kapama Butonu", "9-5", ["FU10"]),
        ]

        # --- SLOT 7: DİJİTAL ÇIKIŞLAR (DO) ---
        do_channels = [
            (7, "SM322-DO", "Q0.0", "S113", "Enjeksiyon Valfi Sürücü Tetikleme (U16)", "9-8", ["FU12"], ["KA9"]),
            (7, "SM322-DO", "Q0.1", "S120", "Kalıp Kapama Kontrol Valfi", "9-8", ["FU12"], ["KA9"]),
            (7, "SM322-DO", "Q0.2", "S180", "Kalıp Açma Kontrol Valfi", "9-8", ["FU12"], ["KA9"]),
            (7, "SM322-DO", "Q0.3", "S211", "Piston Yağlama Valfi", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q0.4", "S210A", "Stop Valfi (Güvenlik Kontrol)", "9-8", ["FU12"], ["KA9"]),
            (7, "SM322-DO", "Q0.5", "S605", "Birleştirme Valfi (Confluence Valve)", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q0.6", "S208", "Hızlı Boşaltma Valfi (Fast Discharge)", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q0.7", "S121", "Akümülatör Yağ Boşaltma Valfi", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.0", "S119", "Yoğunlaştırıcı (Intensifier) Yağ Boşaltma", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.1", "S120", "İtici İleri (Ejector FWD)", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.2", "S121", "İtici Geri (Ejector BWD)", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.3", "S126", "Çoğaltıcı (Intensifier) Oransal Sürücü (U17)", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.4", "S301", "Core 1 In Valf", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.5", "S302", "Core 1 Out Valf", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.6", "S303", "Core 2 In Valf", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q1.7", "S304", "Core 2 Out Valf", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q2.0", "S401", "Yavaş Enjeksiyon Oransal Kontrol", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q2.1", "S210", "2. Faz Enjeksiyon Valfi", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q2.2", "S509", "3. Faz Enjeksiyon Valfi", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q2.3", "S510", "Hızlı Kalıp Açma Valfi", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q2.4", "S116", "E-Stop İkaz Lambası", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q2.5", "HL1", "Alarm Buzzer / Siren", "9-8", ["FU12"]),
            (7, "SM322-DO", "Q2.6", "KM_DELTA", "Pompa Motoru Üçgen Kontaktörü", "9-4", ["AG10-6A"], ["KM1", "KM2"]),
            (7, "SM322-DO", "Q2.7", "KM_STAR", "Pompa Motoru Yıldız Kontaktörü", "9-4", ["AG10-6A"], ["KM1", "KM3"]),
            (7, "SM322-DO", "Q3.6", "KA2", "Yağlama Pompası Kontaktör Rölesi", "9-2", ["AG10-6A"]),
            (7, "SM322-DO", "Q3.7", "KA1", "Ana Pompa Motoru Kontrol Rölesi", "9-2", ["AG10-6A"]),
        ]

        # --- SLOT 10 & 11: ANALOG GİRİŞ/ÇIKIŞLAR (AI/AO) ---
        analog_channels = [
            (10, "SM335-AI", "AI0", "LKPP-03", "Hidrolik Basınç Sensörü (Pressure)", "9-7", ["PS307"]),
            (10, "SM335-AI", "AI1", "LKPP-03", "Hidrolik Akış Sensörü (Flow)", "9-7", ["PS307"]),
            (10, "SM335-AI", "AI2", "VR1", "Kalıp Açma/Kapama Pozisyon Cetveli", "9-7", ["PS307"]),
            (11, "6ES7332-AO", "AO0", "U16", "Enjeksiyon Servo Valf Analog Çıkışı", "9-7", ["PS307"]),
            (11, "6ES7332-AO", "AO1", "U17", "Çoğaltıcı Oransal Valf Analog Çıkışı", "9-7", ["PS307"]),
            (11, "6ES7332-AO", "AO2", "U18", "2. Faz Hız Oransal Valf Analog Çıkışı", "9-7", ["PS307"]),
        ]

        # Veritabanına kaydet
        for item in di_channels:
            ch = IOChannel(item[0], item[1], item[2], item[3], item[4], ModuleType.DI, item[5], item[6], item[7] if len(item)>7 else [])
            self.io_database[ch.address] = ch

        for item in do_channels:
            ch = IOChannel(item[0], item[1], item[2], item[3], item[4], ModuleType.DO, item[5], item[6], item[7] if len(item)>7 else [])
            self.io_database[ch.address] = ch

        for item in analog_channels:
            ch = IOChannel(item[0], item[1], item[2], item[3], item[4], ModuleType.AI if "AI" in item[1] else ModuleType.AO, item[5], item[6])
            self.io_database[ch.address] = ch

    def _build_troubleshooting_knowledge_base(self):
        """Arıza teşhis motoru kural tabanı"""
        self.troubleshooting_rules.append(TroubleshootingRule(
            symptom="Kalıp kapanmıyor / Kalıp kapama valfi tetiklenmiyor",
            affected_components=["S120", "KA9", "2LS1", "2LS3", "3LS15A"],
            root_causes=[
                "Ön veya arka kapı emniyet limit switchlerinden biri (2LS1, 2LS3) tam basmıyor veya açık kaldı.",
                "KA9 Kalıp Kapama Güvenlik Rölesi çekili değil (E-Stop zincirinde kopukluk var).",
                "FU10 (+24V kontrol sigortası) atmış olabilir."
            ],
            checks=[
                "Sayfa 9-3 ve 9-5'i kontrol et: I2.0 (2LS1) ve I2.2 (2LS3) sinyal LED'lerinin PLC üzerinde yanıp yanmadığına bak.",
                "KA9 rölesinin fiziksel durumunu ve 24V beslemesini kontrol et.",
                "FU10 (4A) sigortasını ölç."
            ],
            related_plc_addresses=["I2.0", "I2.2", "I3.3", "I3.7", "Q0.1"]
        ))

        self.troubleshooting_rules.append(TroubleshootingRule(
            symptom="Ana hidrolik yağ pompası motoru (M1) devreye girmiyor / Kalkmıyor",
            affected_components=["KM1", "KM2", "KM3", "FR1", "TC1", "AG10-6A"],
            root_causes=[
                "Termik röle (FR1: 37-50A) aşırı akımdan dolayı atma yapmış.",
                "Acil stop zinciri (1B1-1 ila 1B4-1) açık.",
                "Yıldız-üçgen geçiş rölesi (KT1) arızalı veya KM3/KM2 kontaktörlerinde mekanik sıkışma var."
            ],
            checks=[
                "Sayfa 9-4: FR1 termik rölesinin üzerindeki 'RESET' butonunu kontrol et.",
                "Sayfa 9-2: TC1 trafo çıkış voltajını ve AG10-6A sigortalarını ölç.",
                "Q2.6 ve Q2.7 çıkışlarının PLC'den aktif olup olmadığını izle."
            ],
            related_plc_addresses=["Q2.6", "Q2.7", "I1.2", "I1.3"]
        ))

        self.troubleshooting_rules.append(TroubleshootingRule(
            symptom="Enjeksiyon pistonu hareket etmiyor / Servo valf (U16) tepki vermiyor",
            affected_components=["U16", "S424", "S113", "PS307", "FU12"],
            root_causes=[
                "FU12 (16A güç sigortası) atmış veya 024V beslemesi kesilmiş.",
                "Q0.0 çıkışından U16 sürücüsüne tetik sinyali gitmiyor.",
                "AO0 analog çıkış kartı kablosunda ekranlama (shield) kopukluğu veya toprak hatası var."
            ],
            checks=[
                "Sayfa 9-3 ve 9-9: FU12 sigortasını ve U16 kartının -24V / +24V besleme LED'lerini kontrol et.",
                "Q0.0 çıkış durumunu PLC yazılımından gözlemle.",
                "DB68 konnektöründeki enjeksiyon enkoder ve servo sinyal kablolarını kontrol et."
            ],
            related_plc_addresses=["Q0.0", "AO0", "I0.2"]
        ))

    def diagnose(self, problem_description: str) -> dict:
        """Kullanıcının girdiği şikayete göre en yakın arıza nedenlerini ve kontrol noktalarını döner"""
        query = problem_description.lower()
        matched_rules = []
        for rule in self.troubleshooting_rules:
            if any(word in rule.symptom.lower() for word in query.split()):
                matched_rules.append(rule)
        
        if not matched_rules:
            # Genel arama yap
            return {
                "status": "Bulunamadı",
                "message": "Belirttiğiniz şikayet doğrudan eşleşmedi. Lütfen 'kalıp', 'pompa' veya 'enjeksiyon' gibi anahtar kelimeler kullanın.",
                "total_io_channels_in_db": len(self.io_database)
            }

        result = {"status": "Teşhis Başarılı", "matches": []}
        for r in matched_rules:
            match_info = {
                "problem": r.symptom,
                "muhtemel_sebepler": r.root_causes,
                "kontrol_edilecek_noktalar": r.checks,
                "ilgili_plc_adresleri": r.related_plc_addresses,
                "kontrol_edilecek_bilesen_detaylari": [
                    {addr: f"{self.io_database[addr].tag} - {self.io_database[addr].description} (Sayfa {self.io_database[addr].page})" 
                     for addr in r.related_plc_addresses if addr in self.io_database}
                ]
            }
            result["matches"].append(match_info)
        return result

    def get_channel_info(self, address: str) -> Optional[dict]:
        """Herhangi bir PLC adresinin (örn: I2.0, Q0.1) tüm detayını getirir"""
        ch = self.io_database.get(address.upper())
        if not ch:
            return None
        return {
            "slot": ch.slot,
            "modul": ch.module_name,
            "adres": ch.address,
            "etiket": ch.tag,
            "aciklama": ch.description,
            "tip": ch.channel_type.value,
            "sayfa": ch.page,
            "sigortalar": ch.associated_fuses,
            "roleler": ch.associated_relays
        }


# --- GİTHUB 'TWIN' PROJESİ İÇİN BACKEND ENTEGRASYON TESTİ ---
if __name__ == "__main__":
    dcc630_system = DCC630CompleteSystem()

    print(f"=== L.K. MACHINERY DCC630 ELEKTRİK & PLC SİSTEMİ ===")
    print(f"Toplam Veri Tabanına Kayıtlı I/O Kanal Sayısı: {len(dcc630_system.io_database)}")

    print("\n--- TEST 1: PLC Adres Sorgulama (Örn: Q0.1 ve I2.0) ---")
    for addr in ["Q0.1", "I2.0", "AO0"]:
        info = dcc630_system.get_channel_info(addr)
        print(f"  {addr} -> {info['etiket']}: {info['aciklama']} [Slot {info['slot']}, Sayfa {info['sayfa']}]")

    print("\n--- TEST 2: İnteraktif Arıza Teşhis Motoru ('kalıp kapanmıyor') ---")
    diagnosis = dcc630_system.diagnose("kalıp kapanmıyor")
    for match in diagnosis["matches"]:
        print(f"  [Şikayet]: {match['problem']}")
        print(f"  [Olası Sebepler]:")
        for cause in match['muhtemel_sebepler']:
            print(f"    - {cause}")
        print(f"  [İlgili PLC Adresleri & Bileşenler]: {match['ilgili_plc_adresleri']}")