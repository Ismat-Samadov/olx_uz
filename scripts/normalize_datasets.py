import pandas as pd

def normalize_dataset_1():
    """
    Normalize 001_2_1.xls - Population Morbidity by Disease Classification
    Hierarchy:
    - Level 0: Total (All diseases)
    - Level 1: Individual disease categories
    """
    df = pd.read_excel('data/001_2_1.xls', header=None)

    # Extract years from row 4 (index 4)
    years = []
    for col in range(2, 37):  # columns 2-36 contain years
        val = df.iloc[4, col]
        if pd.notna(val):
            # Handle both numeric years and year strings
            year_str = str(val).strip()
            # Remove footnotes like '1)' or '2)' - split first to handle '2012.02)' format
            if ')' in year_str:
                # Extract everything before the first ')'
                year_str = year_str.split(')')[0]
                # Remove any non-digit characters at the end (like '2')
                import re
                match = re.search(r'(\d{4})', year_str)
                if match:
                    year_str = match.group(1)
            try:
                year = int(float(year_str))
                # Sanity check: years should be between 1990 and 2030
                if 1990 <= year <= 2030:
                    years.append(year)
                else:
                    years.append(None)
            except:
                years.append(None)
        else:
            years.append(None)

    # Section 1: Absolute numbers (rows 6-26)
    absolute_data = []

    # Row 6: Total (Level 0)
    disease_name = "All diseases"
    for i, year in enumerate(years):
        if year:
            value = df.iloc[6, i + 2]
            if pd.notna(value):
                absolute_data.append({
                    'year': year,
                    'disease_category': disease_name,
                    'metric_type': 'absolute_cases',
                    'value': value,
                    'level': 0,
                    'is_aggregate': True
                })

    # Rows 8-26: Individual disease categories (Level 1)
    disease_rows = [
        (8, "Infectious and parasitic diseases"),
        (9, "Neoplasms"),
        (10, "Blood and blood-forming organ diseases and immune disorders"),
        (11, "Endocrine system diseases, nutritional and metabolic disorders"),
        (12, "Mental and behavioral disorders"),
        (13, "Nervous system diseases"),
        (14, "Eye and adnexa diseases"),
        (15, "Ear and mastoid process diseases"),
        (16, "Circulatory system diseases"),
        (17, "Respiratory system diseases"),
        (18, "Digestive system diseases"),
        (19, "Skin and subcutaneous tissue diseases"),
        (20, "Musculoskeletal system and connective tissue diseases"),
        (21, "Genitourinary system diseases"),
        (22, "Pregnancy, childbirth and puerperium"),
        (23, "Perinatal period conditions"),
        (24, "Congenital anomalies"),
        (25, "Clinical and laboratory abnormalities"),
        (26, "Injuries, poisoning and external causes")
    ]

    for row_idx, disease_name in disease_rows:
        for i, year in enumerate(years):
            if year:
                value = df.iloc[row_idx, i + 2]
                if pd.notna(value):
                    absolute_data.append({
                        'year': year,
                        'disease_category': disease_name,
                        'metric_type': 'absolute_cases',
                        'value': value,
                        'level': 1,
                        'is_aggregate': False
                    })

    # Section 2: Rates per 10,000 population (rows 28-48)
    rate_data = []

    # Row 28: Total rate (Level 0)
    disease_name = "All diseases"
    for i, year in enumerate(years):
        if year:
            value = df.iloc[28, i + 2]
            if pd.notna(value):
                rate_data.append({
                    'year': year,
                    'disease_category': disease_name,
                    'metric_type': 'rate_per_10000',
                    'value': value,
                    'level': 0,
                    'is_aggregate': True
                })

    # Rows 30-48: Individual disease category rates (Level 1)
    rate_disease_rows = [
        (30, "Infectious and parasitic diseases"),
        (31, "Neoplasms"),
        (32, "Blood and blood-forming organ diseases and immune disorders"),
        (33, "Endocrine system diseases, nutritional and metabolic disorders"),
        (34, "Mental and behavioral disorders"),
        (35, "Nervous system diseases"),
        (36, "Eye and adnexa diseases"),
        (37, "Ear and mastoid process diseases"),
        (38, "Circulatory system diseases"),
        (39, "Respiratory system diseases"),
        (40, "Digestive system diseases"),
        (41, "Skin and subcutaneous tissue diseases"),
        (42, "Musculoskeletal system and connective tissue diseases"),
        (43, "Genitourinary system diseases"),
        (44, "Pregnancy, childbirth and puerperium"),
        (45, "Perinatal period conditions"),
        (46, "Congenital anomalies"),
        (47, "Clinical and laboratory abnormalities"),
        (48, "Injuries, poisoning and external causes")
    ]

    for row_idx, disease_name in rate_disease_rows:
        for i, year in enumerate(years):
            if year:
                value = df.iloc[row_idx, i + 2]
                if pd.notna(value):
                    rate_data.append({
                        'year': year,
                        'disease_category': disease_name,
                        'metric_type': 'rate_per_10000',
                        'value': value,
                        'level': 1,
                        'is_aggregate': False
                    })

    # Combine all data
    all_data = absolute_data + rate_data

    # Create DataFrame
    normalized_df = pd.DataFrame(all_data)

    # Sort by year, metric_type, level, disease_category
    normalized_df = normalized_df.sort_values(['year', 'metric_type', 'level', 'disease_category'])

    # Save to CSV
    normalized_df.to_csv('data/normalized_population_morbidity_by_disease.csv', index=False)

    print(f"Dataset 1 normalized: {len(normalized_df)} records created")
    print(f"Years covered: {normalized_df['year'].min()} - {normalized_df['year'].max()}")
    print(f"Aggregate rows: {normalized_df['is_aggregate'].sum()}")
    print(f"Detail rows: {(~normalized_df['is_aggregate']).sum()}")

    return normalized_df


def normalize_dataset_2():
    """
    Normalize 001_2_8.xls - Malignant Neoplasms by Gender and Age Groups
    Hierarchy:
    - Level 0: Grand total
    - Level 1: Gender totals (Male/Female)
    - Level 2: Age group details by gender
    """
    df = pd.read_excel('data/001_2_8.xls', header=None)

    # Extract years from row 4 (index 4)
    years = []
    for col in range(2, 20):  # columns 2-19 contain years
        val = df.iloc[4, col]
        if pd.notna(val):
            year_str = str(val).strip()
            if ')' in year_str:
                year_str = year_str.split(')')[0]
                import re
                match = re.search(r'(\d{4})', year_str)
                if match:
                    year_str = match.group(1)
            try:
                year = int(float(year_str))
                if 1990 <= year <= 2030:
                    years.append(year)
                else:
                    years.append(None)
            except:
                years.append(None)
        else:
            years.append(None)

    all_data = []

    # Section 1: Absolute cases (rows 5-29)

    # Row 5: Grand total (Level 0)
    for i, year in enumerate(years):
        if year:
            value = df.iloc[5, i + 2]
            if pd.notna(value):
                all_data.append({
                    'year': year,
                    'gender': 'Total',
                    'age_group': 'All ages',
                    'metric_type': 'absolute_cases',
                    'value': value,
                    'level': 0,
                    'is_aggregate': True
                })

    # Row 6: Males total (Level 1)
    for i, year in enumerate(years):
        if year:
            value = df.iloc[6, i + 2]
            if pd.notna(value):
                all_data.append({
                    'year': year,
                    'gender': 'Male',
                    'age_group': 'All ages',
                    'metric_type': 'absolute_cases',
                    'value': value,
                    'level': 1,
                    'is_aggregate': True
                })

    # Row 7: Females total (Level 1)
    for i, year in enumerate(years):
        if year:
            value = df.iloc[7, i + 2]
            if pd.notna(value):
                all_data.append({
                    'year': year,
                    'gender': 'Female',
                    'age_group': 'All ages',
                    'metric_type': 'absolute_cases',
                    'value': value,
                    'level': 1,
                    'is_aggregate': True
                })

    # Age group details (Level 2)
    age_group_rows = [
        (9, 10, 11, "0-13"),
        (12, 13, 14, "14-17"),
        (15, 16, 17, "18-29"),
        (18, 19, 20, "30-34"),
        (21, 22, 23, "35-39"),
        (24, 25, 26, "40-59"),
        (27, 28, 29, "60+")
    ]

    for total_row, male_row, female_row, age_group in age_group_rows:
        # Total for age group
        for i, year in enumerate(years):
            if year:
                value = df.iloc[total_row, i + 2]
                if pd.notna(value):
                    all_data.append({
                        'year': year,
                        'gender': 'Total',
                        'age_group': age_group,
                        'metric_type': 'absolute_cases',
                        'value': value,
                        'level': 2,
                        'is_aggregate': True
                    })

        # Males for age group
        for i, year in enumerate(years):
            if year:
                value = df.iloc[male_row, i + 2]
                if pd.notna(value):
                    all_data.append({
                        'year': year,
                        'gender': 'Male',
                        'age_group': age_group,
                        'metric_type': 'absolute_cases',
                        'value': value,
                        'level': 2,
                        'is_aggregate': False
                    })

        # Females for age group
        for i, year in enumerate(years):
            if year:
                value = df.iloc[female_row, i + 2]
                if pd.notna(value):
                    all_data.append({
                        'year': year,
                        'gender': 'Female',
                        'age_group': age_group,
                        'metric_type': 'absolute_cases',
                        'value': value,
                        'level': 2,
                        'is_aggregate': False
                    })

    # Section 2: Rates per 100,000 population (rows 30-54)

    # Row 30: Grand total rate (Level 0)
    for i, year in enumerate(years):
        if year:
            value = df.iloc[30, i + 2]
            if pd.notna(value):
                all_data.append({
                    'year': year,
                    'gender': 'Total',
                    'age_group': 'All ages',
                    'metric_type': 'rate_per_100000',
                    'value': value,
                    'level': 0,
                    'is_aggregate': True
                })

    # Row 31: Males total rate (Level 1)
    for i, year in enumerate(years):
        if year:
            value = df.iloc[31, i + 2]
            if pd.notna(value):
                all_data.append({
                    'year': year,
                    'gender': 'Male',
                    'age_group': 'All ages',
                    'metric_type': 'rate_per_100000',
                    'value': value,
                    'level': 1,
                    'is_aggregate': True
                })

    # Row 32: Females total rate (Level 1)
    for i, year in enumerate(years):
        if year:
            value = df.iloc[32, i + 2]
            if pd.notna(value):
                all_data.append({
                    'year': year,
                    'gender': 'Female',
                    'age_group': 'All ages',
                    'metric_type': 'rate_per_100000',
                    'value': value,
                    'level': 1,
                    'is_aggregate': True
                })

    # Age group rate details (Level 2)
    age_group_rate_rows = [
        (34, 35, 36, "0-13"),
        (37, 38, 39, "14-17"),
        (40, 41, 42, "18-29"),
        (43, 44, 45, "30-34"),
        (46, 47, 48, "35-39"),
        (49, 50, 51, "40-59"),
        (52, 53, 54, "60+")
    ]

    for total_row, male_row, female_row, age_group in age_group_rate_rows:
        # Total rate for age group
        for i, year in enumerate(years):
            if year:
                value = df.iloc[total_row, i + 2]
                if pd.notna(value):
                    all_data.append({
                        'year': year,
                        'gender': 'Total',
                        'age_group': age_group,
                        'metric_type': 'rate_per_100000',
                        'value': value,
                        'level': 2,
                        'is_aggregate': True
                    })

        # Males rate for age group
        for i, year in enumerate(years):
            if year:
                value = df.iloc[male_row, i + 2]
                if pd.notna(value):
                    all_data.append({
                        'year': year,
                        'gender': 'Male',
                        'age_group': age_group,
                        'metric_type': 'rate_per_100000',
                        'value': value,
                        'level': 2,
                        'is_aggregate': False
                    })

        # Females rate for age group
        for i, year in enumerate(years):
            if year:
                value = df.iloc[female_row, i + 2]
                if pd.notna(value):
                    all_data.append({
                        'year': year,
                        'gender': 'Female',
                        'age_group': age_group,
                        'metric_type': 'rate_per_100000',
                        'value': value,
                        'level': 2,
                        'is_aggregate': False
                    })

    # Create DataFrame
    normalized_df = pd.DataFrame(all_data)

    # Sort by year, metric_type, level, gender, age_group
    normalized_df = normalized_df.sort_values(['year', 'metric_type', 'level', 'gender', 'age_group'])

    # Save to CSV
    normalized_df.to_csv('data/normalized_malignant_neoplasms_by_age_gender.csv', index=False)

    print(f"\nDataset 2 normalized: {len(normalized_df)} records created")
    print(f"Years covered: {normalized_df['year'].min()} - {normalized_df['year'].max()}")
    print(f"Aggregate rows: {normalized_df['is_aggregate'].sum()}")
    print(f"Detail rows: {(~normalized_df['is_aggregate']).sum()}")

    return normalized_df


if __name__ == "__main__":
    print("Normalizing Dataset 1: Population Morbidity by Disease Classification")
    print("=" * 70)
    df1 = normalize_dataset_1()

    print("\n" + "=" * 70)
    print("Normalizing Dataset 2: Malignant Neoplasms by Gender and Age Groups")
    print("=" * 70)
    df2 = normalize_dataset_2()

    print("\n" + "=" * 70)
    print("Normalization complete!")
    print(f"Files created:")
    print(f"  - data/normalized_population_morbidity_by_disease.csv")
    print(f"  - data/normalized_malignant_neoplasms_by_age_gender.csv")
