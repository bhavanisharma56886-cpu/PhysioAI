import pandas as pd

file_path = r"C:\Users\hp\Desktop\AI-Physiotherapy\data\raw\squat\rehab246_squat_positions_standardized.csv"

df = pd.read_csv(file_path)

print("=" * 60)
print("SQUAT REPETITION / SUBJECT CHECK")
print("=" * 60)

# --------------------------------------------------
# 1. Number of subjects
# --------------------------------------------------

print("\n--- SUBJECTS ---")

subjects = df["subject_id"].unique()

print("Number of subjects:", len(subjects))
print("Subjects:", list(subjects))


# --------------------------------------------------
# 2. Number of repetitions
# --------------------------------------------------

print("\n--- REPETITIONS ---")

repetitions = df.groupby(
    ["subject_id", "repetition"]
).size()

print("Total subject-repetition groups:", len(repetitions))

print("\nFrames per repetition:")
print(repetitions.describe())


# --------------------------------------------------
# 3. Correct / incorrect repetitions
# --------------------------------------------------

print("\n--- REPETITION LABELS ---")

rep_labels = df.groupby(
    ["subject_id", "repetition"]
)["is_correct"].first()

print(rep_labels.value_counts())

print("\nCorrect repetitions:", (rep_labels == True).sum())
print("Incorrect repetitions:", (rep_labels == False).sum())


# --------------------------------------------------
# 4. Check whether a repetition has mixed labels
# --------------------------------------------------

print("\n--- LABEL CONSISTENCY ---")

label_counts = df.groupby(
    ["subject_id", "repetition"]
)["is_correct"].nunique()

mixed = label_counts[label_counts > 1]

if len(mixed) == 0:
    print("✅ Every repetition has one consistent label.")
else:
    print("⚠️ Some repetitions contain mixed labels:")
    print(mixed)


# --------------------------------------------------
# 5. Source files
# --------------------------------------------------

print("\n--- SOURCE FILES ---")

print("Number of source files:", df["source_file"].nunique())

print(df.groupby("source_file")["is_correct"].first().value_counts())


# --------------------------------------------------
# 6. Movement check
# --------------------------------------------------

print("\n--- MOVEMENT ---")

print(df["movement"].value_counts())


print("\n" + "=" * 60)
print("CHECK COMPLETE")
print("=" * 60)