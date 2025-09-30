import pandas as pd
import os, glob

class CsvMerger:
    """Merge multiple CSV files on user, path, time, and total_duration."""

    def __init__(self, folder="data", pattern=None):
        self.folder = folder
        self.pattern = pattern  # optional, nur wenn du glob nutzen willst

    def load_csvs(self):
        if self.pattern:
            csv_files = glob.glob(os.path.join(self.folder, self.pattern))
        else:
            csv_files = []
        if not csv_files:
            raise IOError("No CSV files found with pattern: {}".format(self.pattern))
        print("[INIT] Found CSVs:", csv_files)
        return csv_files

    def merge_csvs(self, csv_files):
        merged_df = None

        for i, file in enumerate(csv_files):
            print("[PROCESS] Reading:", file)
            df = pd.read_csv(file)

            if merged_df is None:
                merged_df = df
            else:
                merged_df = pd.merge(
                    merged_df, df,
                    on=["user", "path", "time", "total_duration"],
                    how="outer"   # falls minimale Unterschiede bestehen
                )

        return merged_df

    def process(self, out_csv="merged_dataset.csv", csv_files=None):
        if csv_files is None:
            csv_files = self.load_csvs()
        else:
            csv_files = [os.path.join(self.folder, f) if not os.path.isabs(f) else f
                         for f in csv_files]

        df_merged = self.merge_csvs(csv_files)

        out_path = os.path.join(self.folder, out_csv)
        df_merged.to_csv(out_path, index=False)
        print("[DONE] Merged CSV saved to:", out_path)
        return out_path
