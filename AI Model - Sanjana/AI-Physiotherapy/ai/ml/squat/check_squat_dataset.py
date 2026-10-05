import pandas as pd
import os

# Dataset path
file_path = r"C:\Users\hp\Desktop\AI-Physiotherapy\data\raw\squat\rehab246_squat_positions_standardized.csv"

print("=" * 60)
print("SQUAT DATASET CHECK")
print("=" * 60)

# Check whether file exists
if not os.path.exists(file_path):
    print("\n❌ ERROR: CSV file not found!")
    print("Check the file path.")
    exit()

print("\n✅ CSV file found!")

# Load dataset
df = pd.read_csv(file_path)

# Basic information
print("\n--- BASIC INFORMATION ---")
print("Rows:", len(df))
print("Columns:", len(df.columns))

# Column names
print("\n--- COLUMN NAMES ---")
for i, column in enumerate(df.columns, start=1):
    print(i, ":", column)

# First 5 rows
print("\n--- FIRST 5 ROWS ---")
print(df.head())

# Data types
print("\n--- DATA TYPES ---")
print(df.dtypes)

# Missing values
print("\n--- MISSING VALUES ---")
missing = df.isnull().sum()

if missing.sum() == 0:
    print("✅ No missing values!")
else:
    print(missing[missing > 0])

# Check is_correct column
print("\n--- LABEL CHECK ---")

if "is_correct" in df.columns:

    print("✅ 'is_correct' column found!")

    print("\nLabel counts:")
    print(df["is_correct"].value_counts())

    print("\nLabel percentages:")
    print(df["is_correct"].value_counts(normalize=True) * 100)

else:
    print("❌ 'is_correct' column NOT found!")

# Check duplicate rows
print("\n--- DUPLICATES ---")
duplicates = df.duplicated().sum()
print("Duplicate rows:", duplicates)

# Numerical columns
print("\n--- NUMERICAL FEATURES ---")
numeric_columns = df.select_dtypes(include="number").columns

print("Number of numerical columns:", len(numeric_columns))

for column in numeric_columns:
    print("-", column)

print("\n" + "=" * 60)
print("DATASET CHECK COMPLETE")
print("=" * 60)