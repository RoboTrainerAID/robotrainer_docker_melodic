import pandas as pd
import ast  # Für sichere Umwandlung von Strings zu Listen

# CSV einlesen
df = pd.read_csv("data/merged/1_2_green_line_force_right_40_2025-05-29-21-33-53.csv")

# Spalten, die du nutzen willst
columns = [
    "ang_x", "ang_y", "ang_z",
    "angle_increment", "angle_max", "angle_min",
    "bag_duration",
    "force_x", "force_y", "force_z",
    "front", "hr", "hrv", "left",
    "lin_x", "lin_y", "lin_z",
    "ppg_ch0", "ppg_ch1", "ppg_ch2", "ppg_ch3",
    "ppi",
    "range_max", "range_min", "right",
    "scan_time", "time_increment",
    "torque_x", "torque_y", "torque_z"
]

# Ergebnis-Vektor
flattened_values = []

for col in columns:
    if col not in df.columns:
        continue

    # Iteriere durch alle Zeilen einer Spalte
    for val in df[col].dropna():  # NaN überspringen
        val = str(val).strip()
        
        # Prüfen ob es eine Liste ist (z. B. "[1.0, 2.0]")
        if val.startswith("[") and val.endswith("]"):
            try:
                parsed_list = ast.literal_eval(val)
                flattened_values.extend(parsed_list)
            except:
                continue  # Falls ungültiges Format
        else:
            try:
                num = float(val)
                flattened_values.append(num)
            except:
                continue  # z. B. leere Strings ignorieren

# Ergebnis prüfen
print(flattened_values)
print(f"Gesamtlänge des Feature-Vektors: {len(flattened_values)}")
