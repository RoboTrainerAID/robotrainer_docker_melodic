# -*- coding: utf-8 -*-
import pandas as pd

class CSVMerger:
    """Merge two CSV files based on user, path, and time."""

    def __init__(self, base_csv, gait_csv, output_csv, tolerance=0.05):
        self.base_csv = base_csv
        self.gait_csv = gait_csv
        self.output_csv = output_csv
        self.tolerance = tolerance

    def merge(self):
        """Merge base_csv and gait_csv based on user, path, and nearest time within tolerance."""
        df1 = pd.read_csv(self.base_csv)
        df2 = pd.read_csv(self.gait_csv)

        df1["time"] = df1["time"].astype(float)
        df2["time"] = df2["time"].astype(float)

        df1 = df1.sort_values("time")
        df2 = df2.sort_values("time")

        merged = []
        for (user, path), group1 in df1.groupby(["user", "path"]):
            group2 = df2[(df2["user"] == user) & (df2["path"] == path)]

            if group2.empty:
                merged.append(group1)
                continue

            merged_group = pd.merge_asof(
                group1.sort_values("time"),
                group2.sort_values("time"),
                on="time",
                by=["user", "path"],
                direction="nearest",
                tolerance=self.tolerance
            )
            merged.append(merged_group)

        df_merged = pd.concat(merged, ignore_index=True)
        df_merged.to_csv(self.output_csv, index=False)