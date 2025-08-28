# -*- coding: utf-8 -*-
import ConfigParser
import rosbag
import pandas as pd
import os, glob, re

def parse_config(path="src/config.ini"):
    cfg = ConfigParser.ConfigParser()
    if not cfg.read(path):
        raise IOError("Config file not found: %s" % path)

    bin_size = int(cfg.get("SETTINGS", "bin_size"))
    specs = {}
    for col, v in cfg.items("TOPICS"):
        if "|" not in v:
            raise ValueError("Topic entry must contain 'topic|field': %s" % v)
        topic, field = v.split("|", 1)
        specs[col] = (topic.strip(), field.strip())
    return bin_size, specs


def extract_field(msg, field_path):
    """Passes a path such as ‘wrench.force.x’ through the ROS message object."""
    try:
        obj = msg
        for part in field_path.split("."):
            obj = getattr(obj, part)
        # Falls Array: nimm erstes Element  (Muss noch angepasst werden!)
        if isinstance(obj, (list, tuple)):
            return obj[0] if obj else ""
        return obj
    except Exception:
        return ""



def process_bag(bag_path, specs, bin_size_hz):
    """Reads Bag, extracts values, averages in time bins according to bin_size_hz."""
    rows = []

    with rosbag.Bag(bag_path) as bag:
        for topic, msg, t in bag.read_messages(topics=set(tp for tp, _ in specs.values())):
            ts = t.to_sec()
            row = {"time": ts}
            for col, (tp, field) in specs.items():
                if tp == topic:
                    row[col] = extract_field(msg, field)
            rows.append(row)

    if not rows:
        return pd.DataFrame()

    # Build DataFrame
    df = pd.DataFrame(rows).sort_values("time")

    # Determine bin length in seconds
    bin_size_sec = 1.0 / float(bin_size_hz)

    # Create time bins
    bins = pd.interval_range(
        start=df["time"].min(),
        end=df["time"].max(),
        freq=bin_size_sec,
        closed="left"
    )
    df["time_bin"] = pd.cut(df["time"], bins)

    # Calculate average value per time bin
    df_grouped = df.groupby("time_bin").mean(numeric_only=True).reset_index(drop=True)

    # Set time interval = Start of bins
    df_grouped["time"] = [iv.left for iv in bins[:len(df_grouped)]]

    return df_grouped


def parse_user_path(filename):
    """Extrahiert User-Nummer und Path-Nummer aus Bag-Dateiname."""
    # z. B. KATE_AA_U001_1_...
    match = re.search(r'U(\d+)_([0-9]+)_', filename)
    if match:
        user = match.group(1)
        path = match.group(2)
        return user, path
    else:
        return "", ""



def main():
    bin_size, specs = parse_config("src/config.ini")
    print("⏬ Downsample:", bin_size)
    print("🎯 Columns:", specs)

    bag_files = glob.glob("data/KATE*.bag")
    if not bag_files:
        raise IOError("No bag files found")
    
    all_dfs = []

    for bag_path in bag_files:
        base = os.path.splitext(os.path.basename(bag_path))[0]

        # Extract user and path
        user, path = parse_user_path(base)

        df = process_bag(bag_path, specs, bin_size)

        # Force all columns, even if empty
        cols = ["time"] + list(specs.keys())
        for col in cols:
            if col not in df.columns:
                df[col] = ""

        # Add user and path columns
        df["user"] = user
        df["path"] = path

        df = df[["time"] + list(specs.keys()) + ["user", "path"]]   # Fix order
        
        all_dfs.append(df)

    # Join all bags together
    df_all = pd.concat(all_dfs, ignore_index=True)
    out_csv = "data/KATE_AA_dataset_{}Hz.csv".format(bin_size)
    df_all.to_csv(out_csv, index=False)
    print("✅ Alle Bags in einer CSV gespeichert:", out_csv)


if __name__ == "__main__":
    main()
