import pyvisa
import time
import csv
from datetime import datetime

class Multiplexer:
    def __init__(self, resource_address, simulate=False):
        self.simulate = simulate
        self.address = resource_address
        self.instrument = None

        if self.simulate:
            print(f"[SIMULATION] Virtuelles Gerät an {self.address}")
        else:
            try:
                rm = pyvisa.ResourceManager('@py') 
                self.instrument = rm.open_resource(self.address)
                self.instrument.timeout = 5000
                idn = self.instrument.query('*IDN?').strip()
                print(f"[ERFOLG] Verbunden mit: {idn}")
                self.instrument.write('*RST')
                self.instrument.write('*CLS')
            except Exception as e:
                print(f"[FEHLER] {e}")
                raise

    def send(self, command):
        if self.simulate:
            print(f"  [SIM TX] {command}")
        else:
            self.instrument.write(command)

    def query(self, command):
        if self.simulate:
            return "1.2345"
        else:
            return self.instrument.query(command).strip()

    def close_channel(self, channel_list):
        print(f"Schließe {channel_list}...")
        self.send(f"ROUT:CLOS ({channel_list})")

    def open_all(self):
        print("Öffne ALLE Kanäle...")
        self.send("ROUT:OPEN:ALL")

    def measure_dc_voltage(self, channel_list):
        return self.query(f"MEAS:VOLT:DC? ({channel_list})")

if __name__ == "__main__":
    VISA_ADDRESS = 'USB0::2391::1287::MY65320033::0::INSTR'
    SIMULATION = False 
    CSV_DATEI = "messungen.csv"

    # CSV-Header schreiben (überschreibt alte Datei gleichen Namens)
    with open(CSV_DATEI, mode='w', newline='') as file:
        writer = csv.writer(file)
        writer.writerow(["Zeitstempel", "Kanal", "Spannung_V"])

    mux = Multiplexer(VISA_ADDRESS, simulate=SIMULATION)

    try:
        mux.open_all()
        time.sleep(1)

        # Eine kleine Schleife, um 5 Messwerte im Abstand von 1 Sekunde aufzunehmen
        print("\nStarte Messreihe (5 Messungen)...")
        for i in range(5):
            spannung = mux.measure_dc_voltage('@1002')
            zeit = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Wert in die Konsole drucken
            print(f"[{zeit}] Wert {i+1}: {spannung} V")
            
            # Wert in die CSV-Datei anfügen (mode='a' für append)
            with open(CSV_DATEI, mode='a', newline='') as file:
                writer = csv.writer(file)
                writer.writerow([zeit, "@1002", spannung])
            
            time.sleep(1) # 1 Sekunde bis zur nächsten Messung warten

    finally:
        print("\nBeende Programm, setze Multiplexer zurück...")
        mux.open_all()
        print(f"Alle Daten wurden in '{CSV_DATEI}' gespeichert.")
