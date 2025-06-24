import pandas as pd

# load the CSV file
df = pd.read_csv("clinical_scores.csv")
daten = df.iloc[1:, 2:]

# Convert all columns to numeric, coercing errors to NaN
daten = daten.apply(pd.to_numeric, errors='coerce')

matrix = daten.transpose().values.tolist()

print(matrix)
