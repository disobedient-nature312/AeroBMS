import os
import glob
import pandas as pd
import numpy as np
from tqdm import tqdm

INPUT_DIR = "../data/cleaned_data"
OUTPUT_FILE = "../data/master_dataset.csv"


def process_battery_data(input_dir, output_file):
    all_files = sorted(glob.glob(os.path.join(input_dir, "*.csv")))

    if not all_files:
        print("❌ Error: No CSV files found. Please check the INPUT_DIR path.")
        return

    extracted_data = []
    print(f"🚀 Initializing extraction pipeline for {len(all_files)} files...")

    for file_path in tqdm(all_files, desc="Processing Cycles", unit="file"):
        df = pd.read_csv(file_path)

        df.columns = df.columns.str.strip()

        if 'Current_measured' not in df.columns:
            continue

        min_current = df['Current_measured'].min()
        if min_current > -0.5:
            continue

        cycle_id = int(os.path.basename(file_path).split('.')[0])
        max_temp = df['Temperature_measured'].max()
        avg_temp = df['Temperature_measured'].mean()
        min_voltage = df['Voltage_measured'].min()

        time_sec = df['Time'].values
        current_amps = np.abs(df['Current_measured'].values)

        capacity_Ah = np.trapezoid(current_amps, time_sec) / 3600.0

        extracted_data.append({
            'File_ID': cycle_id,
            'Max_Temp': max_temp,
            'Avg_Temp': avg_temp,
            'Avg_Discharge_Load': np.abs(min_current),
            'Cutoff_Voltage': min_voltage,
            'Capacity_Ah': capacity_Ah
        })

    if len(extracted_data) == 0:
        print("\n❌ Error: No valid discharge cycles were extracted.")
        return

    master_df = pd.DataFrame(extracted_data)
    master_df = master_df.sort_values('File_ID').reset_index(drop=True)

    battery_ids = []
    current_batt = 1

    for i in range(len(master_df)):
        if i == 0:
            battery_ids.append(current_batt)
            continue

        cap_prev = master_df.loc[i - 1, 'Capacity_Ah']
        cap_curr = master_df.loc[i, 'Capacity_Ah']

        if (cap_curr - cap_prev > 0.4) and (cap_curr > 1.75):
            current_batt += 1

        battery_ids.append(current_batt)

    master_df['Battery_ID'] = battery_ids

    master_df['Cycle_in_Battery'] = master_df.groupby('Battery_ID').cumcount() + 1
    max_cycles = master_df.groupby('Battery_ID')['Cycle_in_Battery'].transform('max')
    master_df['RUL'] = max_cycles - master_df['Cycle_in_Battery']

    os.makedirs(os.path.dirname(output_file), exist_ok=True)
    master_df.to_csv(output_file, index=False)

    print("\n" + "=" * 50)
    print(f"✅ True Master Dataset Generated Successfully!")
    print(f"🔋 Unique Physical Batteries Identified: {current_batt} (Should be around 34-40)")
    print("=" * 50)

if __name__ == "__main__":
    process_battery_data(INPUT_DIR, OUTPUT_FILE)