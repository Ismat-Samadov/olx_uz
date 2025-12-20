"""
Example analysis scripts demonstrating how to use the normalized datasets
"""

import pandas as pd
import matplotlib.pyplot as plt

# Load the normalized datasets
df_diseases = pd.read_csv('data/normalized_population_morbidity_by_disease.csv')
df_cancer = pd.read_csv('data/normalized_malignant_neoplasms_by_age_gender.csv')

# Convert value columns to numeric (they may have been read as strings)
df_diseases['value'] = pd.to_numeric(df_diseases['value'], errors='coerce')
df_cancer['value'] = pd.to_numeric(df_cancer['value'], errors='coerce')

print("=" * 70)
print("EXAMPLE 1: Total Disease Burden Trend (1990-2024)")
print("=" * 70)

# Get total disease cases over time
total_trend = df_diseases[
    (df_diseases['disease_category'] == 'All diseases') &
    (df_diseases['metric_type'] == 'absolute_cases')
].sort_values('year')

print(f"Total disease cases in 1990: {total_trend.iloc[0]['value']:,.0f}")
print(f"Total disease cases in 2024: {total_trend.iloc[-1]['value']:,.0f}")
print(f"Growth: {((total_trend.iloc[-1]['value'] / total_trend.iloc[0]['value'] - 1) * 100):.1f}%")
print()

print("=" * 70)
print("EXAMPLE 2: Top 5 Disease Categories in 2024")
print("=" * 70)

# Get individual disease categories for 2024
diseases_2024 = df_diseases[
    (df_diseases['year'] == 2024) &
    (df_diseases['metric_type'] == 'absolute_cases') &
    (df_diseases['is_aggregate'] == False)  # Exclude the total
].sort_values('value', ascending=False)

print("Top 5 disease categories by absolute cases:")
for idx, row in diseases_2024.head(5).iterrows():
    print(f"  {row['disease_category']:60s} {row['value']:>12,.0f}")
print()

print("=" * 70)
print("EXAMPLE 3: Cancer Incidence by Gender (2007 vs 2024)")
print("=" * 70)

# Get gender breakdown for first and last year
cancer_gender = df_cancer[
    (df_cancer['age_group'] == 'All ages') &
    (df_cancer['metric_type'] == 'absolute_cases') &
    (df_cancer['level'] == 1)  # Gender totals only
]

cancer_2007 = cancer_gender[cancer_gender['year'] == 2007]
cancer_2024 = cancer_gender[cancer_gender['year'] == 2024]

print("2007:")
for _, row in cancer_2007.iterrows():
    print(f"  {row['gender']:8s}: {row['value']:>8,.0f} cases")

print("\n2024:")
for _, row in cancer_2024.iterrows():
    print(f"  {row['gender']:8s}: {row['value']:>8,.0f} cases")

# Calculate growth
male_2007 = cancer_2007[cancer_2007['gender'] == 'Male']['value'].values[0]
male_2024 = cancer_2024[cancer_2024['gender'] == 'Male']['value'].values[0]
female_2007 = cancer_2007[cancer_2007['gender'] == 'Female']['value'].values[0]
female_2024 = cancer_2024[cancer_2024['gender'] == 'Female']['value'].values[0]

print(f"\nMale growth: {((male_2024/male_2007 - 1) * 100):.1f}%")
print(f"Female growth: {((female_2024/female_2007 - 1) * 100):.1f}%")
print()

print("=" * 70)
print("EXAMPLE 4: Cancer Incidence by Age Group in 2024")
print("=" * 70)

# Get age distribution for 2024
cancer_age_2024 = df_cancer[
    (df_cancer['year'] == 2024) &
    (df_cancer['metric_type'] == 'absolute_cases') &
    (df_cancer['gender'] == 'Total') &
    (df_cancer['level'] == 2)  # Age group details
].sort_values('value', ascending=False)

print("Cancer cases by age group (2024):")
total_cases = cancer_age_2024['value'].sum()
for _, row in cancer_age_2024.iterrows():
    percentage = (row['value'] / total_cases) * 100
    print(f"  {row['age_group']:8s}: {row['value']:>8,.0f} cases ({percentage:>5.1f}%)")
print(f"  {'Total':8s}: {total_cases:>8,.0f} cases")
print()

print("=" * 70)
print("EXAMPLE 5: Respiratory Disease Rates Over Time")
print("=" * 70)

# Get respiratory disease rates
respiratory = df_diseases[
    (df_diseases['disease_category'] == 'Respiratory system diseases') &
    (df_diseases['metric_type'] == 'rate_per_10000')
].sort_values('year')

print("Year    Rate per 10,000 population")
print("-" * 35)
for _, row in respiratory.iterrows():
    if row['year'] % 5 == 0 or row['year'] == 2024:  # Show every 5 years + 2024
        print(f"{row['year']:4.0f}    {row['value']:>10.1f}")
print()

print("=" * 70)
print("EXAMPLE 6: Filter Detail Rows Only")
print("=" * 70)

# Example of filtering to get only non-aggregate data
detail_diseases = df_diseases[df_diseases['is_aggregate'] == False]
detail_cancer = df_cancer[
    (df_cancer['level'] == 2) &
    (df_cancer['gender'] != 'Total')
]

print(f"Disease dataset:")
print(f"  Total rows: {len(df_diseases)}")
print(f"  Detail rows (non-aggregates): {len(detail_diseases)}")
print(f"  Aggregate rows: {len(df_diseases) - len(detail_diseases)}")

print(f"\nCancer dataset:")
print(f"  Total rows: {len(df_cancer)}")
print(f"  Detail rows (gender-specific age groups): {len(detail_cancer)}")
print(f"  Aggregate rows: {len(df_cancer) - len(detail_cancer)}")
print()

print("=" * 70)
print("Analysis complete! Check the CSV files for the full normalized data.")
print("=" * 70)
