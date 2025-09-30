import pandas as pd
import os

class CsvTrimmer:
    """Trim merged CSV per (user, path) based on force_input_raw_x and reference_topic change."""

    def __init__(self, csv_path, force_col="force_input_raw_x",
                 ref_cols=("front", "left", "right"), out_folder="data/cut"):
        self.csv_path = csv_path
        self.force_col = force_col
        self.ref_cols = ref_cols
        self.out_folder = out_folder

        if not os.path.exists(out_folder):
            os.makedirs(out_folder)
            print("[INIT] Created output folder:", out_folder)

    def find_trim_index(self, df):
        """Find index of first trim condition: force!=0 then reference_topic changes."""
        force_nonzero_seen = False
        prev_triplet = None

        for idx, row in df.iterrows():
            # Condition 1: force != 0
            if not force_nonzero_seen and abs(float(row[self.force_col])) > 1e-6:
                force_nonzero_seen = True
                print(f"[SCAN] Force nonzero at time={row['time']:.3f}, user={row['user']}, path={row['path']}")

            # Condition 2: reference change after force!=0
            if force_nonzero_seen:
                triplet = tuple(row[c] for c in self.ref_cols)
                if prev_triplet is None:
                    prev_triplet = triplet
                    continue
                if triplet != prev_triplet:
                    print(f"[SCAN] Reference change {prev_triplet} → {triplet} "
                          f"at time={row['time']:.3f}, user={row['user']}, path={row['path']}")
                    return idx
                prev_triplet = triplet

        print("[SCAN] No trim condition found for this group.")
        return None

    def trim_group(self, df_group):
        """Trim a single (user, path) group."""
        idx = self.find_trim_index(df_group)
        if idx is None:
            return df_group  # keep full if no trim condition
        return df_group.loc[idx:].reset_index(drop=True)

    def process(self, out_csv="trimmed_dataset.csv"):
        df = pd.read_csv(self.csv_path)

        trimmed_groups = []
        for (user, path), group in df.groupby(["user", "path"]):
            print(f"[PROCESS] Trimming user={user}, path={path}")
            group_sorted = group.sort_values("time").reset_index(drop=True)
            trimmed = self.trim_group(group_sorted)
            trimmed_groups.append(trimmed)

        df_trimmed = pd.concat(trimmed_groups, ignore_index=True)

        out_path = os.path.join(self.out_folder, out_csv)
        df_trimmed.to_csv(out_path, index=False)
        print("[DONE] Trimmed CSV saved to:", out_path)
        return out_path
