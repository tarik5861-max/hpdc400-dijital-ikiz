from dataclasses import dataclass, field
from typing import Dict, List, Optional
from enum import Enum

class VoltageLevel(Enum):
    AC_380V = "3N/PE AC380V 50Hz"
    AC_220V = "AC220V (TC1 630VA)"
    DC_24V_MAIN = "+24V (U1 S-500-24)"
    DC_24V_PLC = "024V / D24V (PS307)"
    DC_24V_SOLENOID = "S24V"
    GND = "0V / DCOM"

@dataclass
class Component:
    tag: str
    description: str
    page: str
    supply: VoltageLevel
    specs: str = ""
    connections: Dict[str, str] = field(default_factory=dict)

@dataclass
class PLCChannel:
    module: str
    slot: int
    address: str
    device_tag: str
    description: str
    is_active: bool = False

class DCC630ElectricalSystem:
    """
    L.K. Machinery International Ltd. - DCC630 (6217710010142301)
    Elektrik Şeması Dijital İkizi ve Mantık Simülatörü
    """
    def __init__(self):
        self.components: Dict[str, Component] = {}
        self.plc_io: Dict[str, PLCChannel] = {}
        self._build_power_and_control()
        self._build_plc_io_map()
        self._build_proportional_valves()

    def _build_power_and_control(self):
        # Sayfa 9-1 / 9-4: Ana Güç ve Motorlar
        self.components["MAIN_BREAKER"] = Component(
            tag="100A", description="Ana Giriş Şalteri", page="9-4",
            supply=VoltageLevel.AC_380V, specs="3N/PE AC380V 50Hz, 3x25mm2 BK + 25mm2 N"
        )
        self.components["M1"] = Component(
            tag="M1", description="Ana Hidrolik Yağ Pompası Motoru (Yıldız-Üçgen)", page="9-4",
            supply=VoltageLevel.AC_380V, specs="30kW, 380V, Termik FR1: 37-50A",
            connections={"Main": "KM1", "Delta": "KM2", "Star": "KM3"}
        )
        self.components["M4"] = Component(
            tag="M4", description="Ön Kapı Motoru (Front Door Motor)", page="9-4",
            supply=VoltageLevel.AC_380V, specs="0.75kW, 4P",
            connections={"Controller": "Front Door Motor Controller", "Encoder": "Revolve Encoder"}
        )
        self.components["CZ1"] = Component(
            tag="CZ1", description="Pano Kliması ve 220V Priz", page="9-4",
            supply=VoltageLevel.AC_220V, specs="QF2 10A / QF4 10A, 2.5mm2"
        )

        # Sayfa 9-2: İzolasyon Trafosu, PS307 ve Pompa Başlatma Röleleri
        self.components["TC1"] = Component(
            tag="TC1", description="İzolasyon Trafosu", page="9-2",
            supply=VoltageLevel.AC_380V, specs="630VA, AC380V -> AC220V, Sigorta FU11: AG10-6A"
        )
        self.components["PS307"] = Component(
            tag="PS307", description="Siemens PLC Güç Modülü", page="9-2",
            supply=VoltageLevel.AC_220V, specs="Çıkış: D24V / DCOM"
        )
        self.components["M10"] = Component(
            tag="M10", description="Yağlama Pompası (Lubrication Pump)", page="9-2",
            supply=VoltageLevel.AC_220V, specs="75W (Manual / Auto)"
        )
        self.components["FAN1"] = Component(
            tag="FAN1", description="Elektrik Pano Soğutma Fanı", page="9-2",
            supply=VoltageLevel.AC_220V, specs="17W"
        )

        # Sayfa 9-3: DC Güç Kaynağı ve Güvenlik Rölesi
        self.components["U1"] = Component(
            tag="U1", description="Ana 24VDC Güç Kaynağı", page="9-3",
            supply=VoltageLevel.AC_220V, specs="Model: S-500-24, FU10(4A) -> +24V, FU12(16A) -> 024V"
        )
        self.components["KA9"] = Component(
            tag="KA9", description="Kalıp Kapama Güvenlik Rölesi (Die Close Safety Control)", page="9-3",
            supply=VoltageLevel.DC_24V_MAIN,
            connections={"Interlocks": "Front Door Limit 2 + Back Door Limit 2 + Safety Switch"}
        )
        self.components["M11"] = Component(
            tag="M11", description="Gres Pompası (Grease Pump)", page="9-3",
            supply=VoltageLevel.DC_24V_MAIN, connections={"Control": "KA41"}
        )

        # Sayfa 9-8: Endüstriyel PC ve Haberleşme
        self.components["PC577"] = Component(
            tag="PC577", description="Operatör Paneli / Endüstriyel PC", page="9-8",
            supply=VoltageLevel.AC_220V, specs="UPS K1000 (1000W) beslemeli, CP5613, IM153-1/2"
        )

    def _build_plc_io_map(self):
        # Sayfa 9-4 (Slot 4 - SM323 DI16/DO16), 9-5 (Slot 6 - SM321 DI32 & Slot 7 - SM322 DO32), 9-7 (Slot 9 & 10)
        io_definitions = [
            # Dijital Girişler (Örnek Kritik Adresler)
            ("SM323-DI", 4, "I0.0", "1B0", "Kalıp Kapama Butonu 1 (Die Close Button 1)"),
            ("SM323-DI", 4, "I0.1", "1B1", "Kalıp Açma Butonu (Die Open Button)"),
            ("SM323-DI", 4, "I0.2", "1B2", "Enjeksiyon Butonu (Injection Button)"),
            ("SM323-DI", 4, "I0.7", "1B7-1", "Manuel Mod Seçici (Manual Switch)"),
            ("SM323-DI", 4, "I1.0", "1B7-2", "Otomatik Mod Seçici (Auto Switch)"),
            ("SM323-DI", 4, "I1.2", "1B10", "Motor Start Butonu"),
            ("SM323-DI", 4, "I1.3", "1B11A-2", "Motor Stop Butonu"),
            ("SM321-DI", 6, "I2.0", "2LS1", "Ön Kapı Kapalı Limiti 2"),
            ("SM321-DI", 6, "I2.2", "2LS3", "Arka Kapı Kapalı Limiti 2"),
            ("SM321-DI", 6, "I2.7", "2LS8", "Kalıp Kapalı Onay Switch (Die Closed Confirm LS)"),
            ("SM321-DI", 6, "I3.3", "E-STOP", "Acil Durdurma Switch (E-Stop)"),
            ("SM321-DI", 6, "I3.4", "TANK_LVL", "Hidrolik Tank Yağ Seviyesi"),
            
            # Dijital Çıkışlar (Slot 7 - SM322 DO32)
            ("SM322-DO", 7, "Q0.0", "S113", "Enjeksiyon Valfi / U16 Tetikleme"),
            ("SM322-DO", 7, "Q0.1", "S120", "Kalıp Kapama Kontrolü (Die Close Control)"),
            ("SM322-DO", 7, "Q0.2", "S180", "Kalıp Açma Kontrolü (Die Open Control)"),
            ("SM322-DO", 7, "Q0.4", "S210A", "Stop Valfi (KA9 Güvenlik Kontağı Üzerinden)"),
            ("SM322-DO", 7, "Q0.5", "S605", "Birleştirme Valfi (Confluence Valve)"),
            ("SM322-DO", 7, "Q0.6", "S208", "Hızlı Boşaltma Valfi (Fast Discharge)"),
            ("SM322-DO", 7, "Q1.3", "S126", "Çoğaltıcı (Intensifier) Kontrolü -> U17"),
            ("SM322-DO", 7, "Q1.4", "S301", "İtici İleri (Ejector FWD)"),
            ("SM322-DO", 7, "Q1.5", "S302", "İtici Geri (Ejector BWD)"),
            ("SM322-DO", 7, "Q2.0", "S401", "Yavaş Enjeksiyon (Slow Injection)"),
            ("SM322-DO", 7, "Q2.6", "KM_DELTA", "Pompa Motoru Üçgen Kontrolü"),
            ("SM322-DO", 7, "Q2.7", "KM_STAR", "Pompa Motoru Yıldız Kontrolü"),
            ("SM322-DO", 7, "Q3.6", "KA2", "Yağlama Pompası Kontrolü"),
            ("SM322-DO", 7, "Q3.7", "KA1", "Pompa Motoru Ana Kontrolü"),
        ]
        for mod, slot, addr, tag, desc in io_definitions:
            self.plc_io[addr] = PLCChannel(mod, slot, addr, tag, desc)

    def _build_proportional_valves(self):
        # Sayfa 9-9 & 9-7: Analog Çıkışlar ve Oransal Valf Sürücüleri
        self.components["U16"] = Component(
            tag="U16", description="Enjeksiyon Servo Valf Sürücüsü (TDP050EH)", page="9-9",
            supply=VoltageLevel.DC_24V_MAIN,
            connections={"AO": "DB68 (A09+/A09-)", "Enable": "Q0.0 (S113)", "Valve": "S424"}
        )
        self.components["U17"] = Component(
            tag="U17", description="Çoğaltıcı (Intensifier) Oransal Valf Sürücüsü", page="9-9",
            supply=VoltageLevel.DC_24V_MAIN,
            connections={"AO": "AO1 Slot11 (A05+/A05-)", "Enable": "Q1.3 (S126)"}
        )
        self.components["U18"] = Component(
            tag="U18", description="2. Faz Hız Oransal Valf Sürücüsü", page="9-9",
            supply=VoltageLevel.DC_24V_MAIN,
            connections={"AO": "AO1 Slot11 (A06+/A06-)", "Enable": "S419"}
        )
        self.components["U12"] = Component(
            tag="U12", description="Basınç ve Akış Oransal Amplifikatör Kartı (LKPP-03)", page="9-7",
            supply=VoltageLevel.DC_24V_SOLENOID,
            connections={"Pressure_AO": "AI/AO Slot10 (AO1)", "Flow_AO": "AI/AO Slot10 (AO2)",
                         "Pressure_Valve": "S103", "Flow_Valve": "S102"}
        )

    # --- DONANIM KİLİTLEME (INTERLOCK) VE DEVRE MANTIĞI ---
    def check_emergency_chain(self, e_stops_ok: bool, fr1_ok: bool) -> bool:
        """Sayfa 9-2: Acil stop zinciri (1B1-1 -> 1B2-1 -> 1B3-1 -> 1B4-1) ve Termik FR1 kontrolü"""
        return e_stops_ok and fr1_ok

    def simulate_pump_motor_start(self, e_stops_ok: bool, fr1_ok: bool, start_btn: bool, star_timer_done: bool) -> dict:
        """Sayfa 9-2: Hidrolik Pompa Motoru (M1) Yıldız-Üçgen (KM1, KM2, KM3) Yol Verme Mantığı"""
        if not self.check_emergency_chain(e_stops_ok, fr1_ok):
            return {"KM1": False, "KM2_Delta": False, "KM3_Star": False, "Status": "HATA: Acil Stop veya Termik (FR1) Açık!"}
        
        if start_btn:
            if not star_timer_done:
                # KT1 süresi dolana kadar KM1 + KM3 (Yıldız) aktif, KM2 (Üçgen) elektriksel kilitli
                return {"KM1": True, "KM2_Delta": False, "KM3_Star": True, "Status": "Yıldız (Star) Kalkış Aktif"}
            else:
                # KT1 süresi doldu: KM3 düşer, KM1 + KM2 (Üçgen) devreye girer
                return {"KM1": True, "KM2_Delta": True, "KM3_Star": False, "Status": "Üçgen (Delta) Normal Çalışma"}
        return {"KM1": False, "KM2_Delta": False, "KM3_Star": False, "Status": "Motor Duruyor"}

    def check_die_close_safety(self, front_door_closed: bool, back_door_closed: bool, safety_switch_ok: bool) -> bool:
        """Sayfa 9-3: KA9 Kalıp Kapama Güvenlik Rölesi ve Q0.4 (S210A) izni"""
        ka9_energized = front_door_closed and back_door_closed and safety_switch_ok
        self.components["KA9"].connections["State"] = "ENERJİLİ" if ka9_energized else "KESİK"
        return ka9_energized

    def trace_signal(self, query: str) -> List[str]:
        """Şema üzerindeki herhangi bir bileşen, valf veya PLC adresini sorgular"""
        results = []
        q = query.upper()
        for tag, comp in self.components.items():
            if q in tag.upper() or q in comp.description.upper() or q in str(comp.connections).upper():
                results.append(f"[Bileşen - Sayfa {comp.page}] {comp.tag}: {comp.description} | Besleme: {comp.supply.value} | Bağlantı: {comp.connections}")
        for addr, io in self.plc_io.items():
            if q in addr.upper() or q in io.device_tag.upper() or q in io.description.upper():
                results.append(f"[PLC Slot {io.slot} ({io.module})] {io.address} -> {io.device_tag}: {io.description}")
        return results


# --- ÖRNEK KULLANIM ---
if __name__ == "__main__":
    machine = DCC630ElectricalSystem()

    print("1. Hidrolik Pompa Motoru Testi:")
    print("  Kalkış anı:", machine.simulate_pump_motor_start(True, True, True, star_timer_done=False))
    print("  5 sn sonra:", machine.simulate_pump_motor_start(True, True, True, star_timer_done=True))

    print("\n2. Kalıp Kapama Güvenlik Zinciri (KA9):")
    izin = machine.check_die_close_safety(front_door_closed=True, back_door_closed=False, safety_switch_ok=True)
    print(f"  Arka kapı açıkken kalıp kapama izni (KA9): {izin}")

    print("\n3. Şema Üzerinde Sinyal / Valf Takibi ('U16' ve 'S120'):")
    for line in machine.trace_signal("U16") + machine.trace_signal("S120"):
        print(" ", line)