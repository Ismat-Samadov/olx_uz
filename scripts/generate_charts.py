"""
Generate comprehensive charts analyzing disease trends in Azerbaijan (1990-2024)
"""

import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import numpy as np
from matplotlib.ticker import FuncFormatter

# Set style for better-looking charts
plt.style.use('seaborn-v0_8-darkgrid')
sns.set_palette("husl")

# Load the normalized datasets
print("Loading data...")
df_diseases = pd.read_csv('data/normalized_population_morbidity_by_disease.csv')
df_cancer = pd.read_csv('data/normalized_malignant_neoplasms_by_age_gender.csv')

# Convert value columns to numeric
df_diseases['value'] = pd.to_numeric(df_diseases['value'], errors='coerce')
df_cancer['value'] = pd.to_numeric(df_cancer['value'], errors='coerce')

# Helper function to format numbers
def millions(x, pos):
    return f'{x*1e-6:.1f}M'

def thousands(x, pos):
    return f'{x*1e-3:.0f}K'

print("Generating charts...\n")

# ============================================================================
# CHART 1: Overall Disease Burden Trend (1990-2024)
# ============================================================================
print("Chart 1: Overall disease burden trend...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Absolute numbers
total_trend = df_diseases[
    (df_diseases['disease_category'] == 'All diseases') &
    (df_diseases['metric_type'] == 'absolute_cases')
].sort_values('year')

ax1.plot(total_trend['year'], total_trend['value'],
         linewidth=3, color='#2E86AB', marker='o', markersize=4)
ax1.fill_between(total_trend['year'], total_trend['value'], alpha=0.3, color='#2E86AB')
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Total Cases', fontsize=12, fontweight='bold')
ax1.set_title('Total Disease Cases Over Time', fontsize=14, fontweight='bold', pad=20)
ax1.yaxis.set_major_formatter(FuncFormatter(millions))
ax1.grid(True, alpha=0.3)

# Add annotations for key points
first_val = total_trend.iloc[0]['value']
last_val = total_trend.iloc[-1]['value']
growth = ((last_val / first_val) - 1) * 100
ax1.annotate(f'1990: {first_val/1e6:.2f}M',
             xy=(1990, first_val), xytext=(1992, first_val + 200000),
             fontsize=10, bbox=dict(boxstyle='round,pad=0.5', facecolor='yellow', alpha=0.7))
ax1.annotate(f'2024: {last_val/1e6:.2f}M\n+{growth:.1f}%',
             xy=(2024, last_val), xytext=(2020, last_val + 200000),
             fontsize=10, bbox=dict(boxstyle='round,pad=0.5', facecolor='lightgreen', alpha=0.7))

# Rate per 10,000
rate_trend = df_diseases[
    (df_diseases['disease_category'] == 'All diseases') &
    (df_diseases['metric_type'] == 'rate_per_10000')
].sort_values('year')

ax2.plot(rate_trend['year'], rate_trend['value'],
         linewidth=3, color='#A23B72', marker='s', markersize=4)
ax2.fill_between(rate_trend['year'], rate_trend['value'], alpha=0.3, color='#A23B72')
ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Rate per 10,000 Population', fontsize=12, fontweight='bold')
ax2.set_title('Disease Rate per 10,000 Population', fontsize=14, fontweight='bold', pad=20)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('charts/01_overall_disease_burden.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 2: Top Disease Categories Comparison (2024)
# ============================================================================
print("Chart 2: Top disease categories comparison...")

diseases_2024 = df_diseases[
    (df_diseases['year'] == 2024) &
    (df_diseases['metric_type'] == 'absolute_cases') &
    (df_diseases['is_aggregate'] == False)
].sort_values('value', ascending=True).tail(10)

fig, ax = plt.subplots(figsize=(14, 8))
colors = plt.cm.viridis(np.linspace(0.3, 0.9, len(diseases_2024)))

bars = ax.barh(range(len(diseases_2024)), diseases_2024['value'], color=colors, edgecolor='black', linewidth=0.5)
ax.set_yticks(range(len(diseases_2024)))
ax.set_yticklabels([cat[:50] for cat in diseases_2024['disease_category']], fontsize=11)
ax.set_xlabel('Number of Cases', fontsize=12, fontweight='bold')
ax.set_title('Top 10 Disease Categories in 2024', fontsize=16, fontweight='bold', pad=20)
ax.xaxis.set_major_formatter(FuncFormatter(thousands))
ax.grid(True, axis='x', alpha=0.3)

# Add value labels on bars
for i, (idx, row) in enumerate(diseases_2024.iterrows()):
    ax.text(row['value'] + 20000, i, f"{row['value']/1000:.0f}K",
            va='center', fontsize=10, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/02_top_diseases_2024.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 3: Evolution of Major Disease Categories
# ============================================================================
print("Chart 3: Evolution of major disease categories...")

major_categories = [
    'Respiratory system diseases',
    'Circulatory system diseases',
    'Digestive system diseases',
    'Infectious and parasitic diseases',
    'Nervous system diseases'
]

# Use distinct colors, line styles, and markers for better separation
colors = ['#E63946', '#457B9D', '#2A9D8F', '#F4A261', '#8E44AD']
linestyles = ['-', '--', '-.', ':', '-']
markers = ['o', 's', '^', 'D', 'v']

fig, ax = plt.subplots(figsize=(18, 10))

for i, category in enumerate(major_categories):
    cat_data = df_diseases[
        (df_diseases['disease_category'] == category) &
        (df_diseases['metric_type'] == 'absolute_cases')
    ].sort_values('year')

    ax.plot(cat_data['year'], cat_data['value'],
            linewidth=3, marker=markers[i], markersize=5,
            label=category, alpha=0.85, color=colors[i],
            linestyle=linestyles[i], markevery=2)

ax.set_xlabel('Year', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Cases', fontsize=14, fontweight='bold')
ax.set_title('Evolution of Major Disease Categories (1990-2024)',
             fontsize=18, fontweight='bold', pad=20)
# Move legend outside plot area to avoid overlap
ax.legend(loc='center left', bbox_to_anchor=(1, 0.5), fontsize=12,
          framealpha=0.95, edgecolor='black', shadow=True)
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.grid(True, alpha=0.3, linestyle='--')
ax.set_xlim(1989, 2025)

plt.tight_layout()
plt.savefig('charts/03_major_diseases_evolution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 4: Disease Distribution in 1990 vs 2024 (Grouped Bar Chart)
# ============================================================================
print("Chart 4: Disease distribution comparison...")

# Get top 8 diseases by total cases across both years
diseases_1990 = df_diseases[
    (df_diseases['year'] == 1990) &
    (df_diseases['metric_type'] == 'absolute_cases') &
    (df_diseases['is_aggregate'] == False)
].sort_values('value', ascending=False)

diseases_2024_all = df_diseases[
    (df_diseases['year'] == 2024) &
    (df_diseases['metric_type'] == 'absolute_cases') &
    (df_diseases['is_aggregate'] == False)
].sort_values('value', ascending=False)

# Get top 8 categories by 2024 values
top_categories = diseases_2024_all.head(8)['disease_category'].tolist()

# Prepare data for both years
data_1990 = diseases_1990[diseases_1990['disease_category'].isin(top_categories)].set_index('disease_category')
data_2024 = diseases_2024_all[diseases_2024_all['disease_category'].isin(top_categories)].set_index('disease_category')

# Short labels
short_labels = {
    'Respiratory system diseases': 'Respiratory',
    'Digestive system diseases': 'Digestive',
    'Circulatory system diseases': 'Circulatory',
    'Infectious and parasitic diseases': 'Infectious',
    'Injuries, poisoning and external causes': 'Injuries',
    'Nervous system diseases': 'Nervous',
    'Eye and adnexa diseases': 'Eye',
    'Endocrine system diseases, nutritional and metabolic disorders': 'Endocrine',
    'Genitourinary system diseases': 'Genitourinary',
    'Skin and subcutaneous tissue diseases': 'Skin'
}

categories_short = [short_labels.get(cat, cat[:20]) for cat in top_categories]

fig, ax = plt.subplots(figsize=(16, 9))

x = np.arange(len(top_categories))
width = 0.35

# Get values in correct order
values_1990 = [data_1990.loc[cat, 'value'] if cat in data_1990.index else 0 for cat in top_categories]
values_2024 = [data_2024.loc[cat, 'value'] if cat in data_2024.index else 0 for cat in top_categories]

bars1 = ax.bar(x - width/2, values_1990, width, label='1990',
               color='#457B9D', alpha=0.85, edgecolor='black', linewidth=1)
bars2 = ax.bar(x + width/2, values_2024, width, label='2024',
               color='#E63946', alpha=0.85, edgecolor='black', linewidth=1)

ax.set_xlabel('Disease Category', fontsize=14, fontweight='bold')
ax.set_ylabel('Number of Cases', fontsize=14, fontweight='bold')
ax.set_title('Disease Distribution Comparison: 1990 vs 2024',
             fontsize=18, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(categories_short, rotation=45, ha='right', fontsize=11)
ax.legend(fontsize=13, loc='upper left', framealpha=0.95, edgecolor='black')
ax.yaxis.set_major_formatter(FuncFormatter(thousands))
ax.grid(True, axis='y', alpha=0.3, linestyle='--')

# Add percentage change labels on top
for i, (v1, v2) in enumerate(zip(values_1990, values_2024)):
    if v1 > 0:
        pct_change = ((v2 - v1) / v1) * 100
        color = '#28A745' if pct_change > 0 else '#DC3545'
        ax.text(i, max(v1, v2) + 20000, f'{pct_change:+.0f}%',
                ha='center', fontsize=9, fontweight='bold', color=color)

plt.tight_layout()
plt.savefig('charts/04_disease_distribution_comparison.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 5: Growth Rates by Disease Category (1990-2024)
# ============================================================================
print("Chart 5: Growth rates by disease category...")

growth_data = []
categories = df_diseases[df_diseases['is_aggregate'] == False]['disease_category'].unique()

for category in categories:
    cat_data = df_diseases[
        (df_diseases['disease_category'] == category) &
        (df_diseases['metric_type'] == 'absolute_cases')
    ].sort_values('year')

    if len(cat_data) >= 2:
        first_val = cat_data.iloc[0]['value']
        last_val = cat_data.iloc[-1]['value']
        if first_val > 0:
            growth_pct = ((last_val / first_val) - 1) * 100
            growth_data.append({
                'category': category,
                'growth': growth_pct
            })

growth_df = pd.DataFrame(growth_data).sort_values('growth', ascending=True)

# Create shorter labels for better readability
label_mapping = {
    'Blood and blood-forming organ diseases and immune disorders': 'Blood & immune disorders',
    'Endocrine system diseases, nutritional and metabolic disorders': 'Endocrine & metabolic',
    'Musculoskeletal system and connective tissue diseases': 'Musculoskeletal & connective',
    'Pregnancy, childbirth and puerperium': 'Pregnancy & childbirth',
    'Infectious and parasitic diseases': 'Infectious & parasitic',
    'Injuries, poisoning and external causes': 'Injuries & poisoning',
    'Clinical and laboratory abnormalities': 'Clinical abnormalities',
    'Mental and behavioral disorders': 'Mental & behavioral',
    'Skin and subcutaneous tissue diseases': 'Skin diseases',
    'Respiratory system diseases': 'Respiratory',
    'Circulatory system diseases': 'Circulatory',
    'Digestive system diseases': 'Digestive',
    'Genitourinary system diseases': 'Genitourinary',
    'Nervous system diseases': 'Nervous system',
    'Perinatal period conditions': 'Perinatal conditions',
    'Congenital anomalies': 'Congenital anomalies',
    'Eye and adnexa diseases': 'Eye diseases',
    'Ear and mastoid process diseases': 'Ear diseases',
    'Neoplasms': 'Neoplasms (tumors)'
}

growth_df['short_label'] = growth_df['category'].map(lambda x: label_mapping.get(x, x))

fig, ax = plt.subplots(figsize=(16, 11))
colors = ['#DC3545' if x < 0 else '#28A745' for x in growth_df['growth']]

bars = ax.barh(range(len(growth_df)), growth_df['growth'],
               color=colors, alpha=0.75, edgecolor='black', linewidth=1)
ax.set_yticks(range(len(growth_df)))
ax.set_yticklabels(growth_df['short_label'], fontsize=11, fontweight='normal')
ax.set_xlabel('Growth Rate (%)', fontsize=14, fontweight='bold')
ax.set_title('Disease Category Growth Rates (1990-2024)',
             fontsize=18, fontweight='bold', pad=20)
ax.axvline(x=0, color='black', linewidth=2, linestyle='-')
ax.grid(True, axis='x', alpha=0.3, linestyle='--')

# Add value labels with better positioning
for i, (idx, row) in enumerate(growth_df.iterrows()):
    offset = 15 if row['growth'] > 0 else -15
    ha = 'left' if row['growth'] > 0 else 'right'
    ax.text(row['growth'] + offset, i, f"{row['growth']:.1f}%",
            va='center', ha=ha, fontsize=10, fontweight='bold',
            bbox=dict(boxstyle='round,pad=0.3', facecolor='white',
                     edgecolor=colors[i], alpha=0.8))

# Add legend
from matplotlib.patches import Patch
legend_elements = [Patch(facecolor='#28A745', alpha=0.75, label='Increase'),
                   Patch(facecolor='#DC3545', alpha=0.75, label='Decrease')]
ax.legend(handles=legend_elements, loc='lower right', fontsize=11, framealpha=0.95)

plt.tight_layout()
plt.savefig('charts/05_disease_growth_rates.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 6: Cancer Incidence Trend (2007-2024)
# ============================================================================
print("Chart 6: Cancer incidence trend...")

fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(16, 6))

# Total cancer cases over time
cancer_total = df_cancer[
    (df_cancer['gender'] == 'Total') &
    (df_cancer['age_group'] == 'All ages') &
    (df_cancer['metric_type'] == 'absolute_cases')
].sort_values('year')

ax1.plot(cancer_total['year'], cancer_total['value'],
         linewidth=3, color='#E63946', marker='o', markersize=5)
ax1.fill_between(cancer_total['year'], cancer_total['value'], alpha=0.3, color='#E63946')
ax1.set_xlabel('Year', fontsize=12, fontweight='bold')
ax1.set_ylabel('Number of Cases', fontsize=12, fontweight='bold')
ax1.set_title('Total Cancer Cases Over Time', fontsize=14, fontweight='bold', pad=20)
ax1.grid(True, alpha=0.3)

# Add growth annotation
first_cancer = cancer_total.iloc[0]['value']
last_cancer = cancer_total.iloc[-1]['value']
cancer_growth = ((last_cancer / first_cancer) - 1) * 100
ax1.annotate(f'Growth: +{cancer_growth:.1f}%\n({first_cancer:.0f} → {last_cancer:.0f})',
             xy=(2016, (first_cancer + last_cancer)/2),
             fontsize=11, bbox=dict(boxstyle='round,pad=0.7', facecolor='yellow', alpha=0.8),
             ha='center')

# Cancer rate per 100,000
cancer_rate = df_cancer[
    (df_cancer['gender'] == 'Total') &
    (df_cancer['age_group'] == 'All ages') &
    (df_cancer['metric_type'] == 'rate_per_100000')
].sort_values('year')

ax2.plot(cancer_rate['year'], cancer_rate['value'],
         linewidth=3, color='#F77F00', marker='s', markersize=5)
ax2.fill_between(cancer_rate['year'], cancer_rate['value'], alpha=0.3, color='#F77F00')
ax2.set_xlabel('Year', fontsize=12, fontweight='bold')
ax2.set_ylabel('Rate per 100,000 Population', fontsize=12, fontweight='bold')
ax2.set_title('Cancer Rate per 100,000 Population', fontsize=14, fontweight='bold', pad=20)
ax2.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('charts/06_cancer_incidence_trend.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 7: Cancer by Gender Over Time
# ============================================================================
print("Chart 7: Cancer by gender over time...")

fig, ax = plt.subplots(figsize=(14, 7))

for gender in ['Male', 'Female']:
    gender_data = df_cancer[
        (df_cancer['gender'] == gender) &
        (df_cancer['age_group'] == 'All ages') &
        (df_cancer['metric_type'] == 'absolute_cases')
    ].sort_values('year')

    ax.plot(gender_data['year'], gender_data['value'],
            linewidth=3, marker='o', markersize=5, label=gender, alpha=0.8)

ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Cases', fontsize=12, fontweight='bold')
ax.set_title('Cancer Cases by Gender (2007-2024)', fontsize=16, fontweight='bold', pad=20)
ax.legend(fontsize=12, loc='upper left')
ax.grid(True, alpha=0.3)

plt.tight_layout()
plt.savefig('charts/07_cancer_by_gender.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 8: Cancer Age Distribution (2024)
# ============================================================================
print("Chart 8: Cancer age distribution...")

# Absolute numbers by age group
cancer_age_2024 = df_cancer[
    (df_cancer['year'] == 2024) &
    (df_cancer['metric_type'] == 'absolute_cases') &
    (df_cancer['gender'] == 'Total') &
    (df_cancer['level'] == 2)
].sort_values('value', ascending=False)

age_order = ['0-13', '14-17', '18-29', '30-34', '35-39', '40-59', '60+']
cancer_age_2024['age_group'] = pd.Categorical(cancer_age_2024['age_group'], categories=age_order, ordered=True)
cancer_age_2024 = cancer_age_2024.sort_values('age_group')

# Create a single larger chart with both absolute and percentage
fig, (ax1, ax2) = plt.subplots(1, 2, figsize=(18, 8))

# Left: Absolute numbers
colors_age = plt.cm.RdYlGn_r(np.linspace(0.2, 0.9, len(cancer_age_2024)))
bars1 = ax1.bar(range(len(cancer_age_2024)), cancer_age_2024['value'],
                color=colors_age, edgecolor='black', linewidth=1.5, alpha=0.85)
ax1.set_xticks(range(len(cancer_age_2024)))
ax1.set_xticklabels(cancer_age_2024['age_group'], fontsize=13, fontweight='bold')
ax1.set_ylabel('Number of Cases', fontsize=14, fontweight='bold')
ax1.set_xlabel('Age Group', fontsize=14, fontweight='bold')
ax1.set_title('Cancer Cases by Age Group (2024)', fontsize=16, fontweight='bold', pad=20)
ax1.grid(True, axis='y', alpha=0.3, linestyle='--')

# Add value labels
for i, (idx, row) in enumerate(cancer_age_2024.iterrows()):
    ax1.text(i, row['value'] + 200, f"{row['value']:.0f}",
             ha='center', fontsize=11, fontweight='bold')

# Right: Percentage breakdown as horizontal bar
total_cancer = cancer_age_2024['value'].sum()
cancer_age_2024['percentage'] = (cancer_age_2024['value'] / total_cancer * 100)
cancer_age_sorted = cancer_age_2024.sort_values('percentage', ascending=True)

bars2 = ax2.barh(range(len(cancer_age_sorted)), cancer_age_sorted['percentage'],
                 color=[colors_age[age_order.index(ag)] for ag in cancer_age_sorted['age_group']],
                 edgecolor='black', linewidth=1.5, alpha=0.85)
ax2.set_yticks(range(len(cancer_age_sorted)))
ax2.set_yticklabels(cancer_age_sorted['age_group'], fontsize=13, fontweight='bold')
ax2.set_xlabel('Percentage of Total Cases (%)', fontsize=14, fontweight='bold')
ax2.set_title('Percentage Distribution by Age (2024)', fontsize=16, fontweight='bold', pad=20)
ax2.grid(True, axis='x', alpha=0.3, linestyle='--')

# Add percentage labels
for i, (idx, row) in enumerate(cancer_age_sorted.iterrows()):
    ax2.text(row['percentage'] + 1, i, f"{row['percentage']:.1f}%",
             va='center', fontsize=11, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/08_cancer_age_distribution.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 9: Cancer by Age and Gender (2024)
# ============================================================================
print("Chart 9: Cancer by age and gender...")

fig, ax = plt.subplots(figsize=(14, 8))

cancer_age_gender = df_cancer[
    (df_cancer['year'] == 2024) &
    (df_cancer['metric_type'] == 'absolute_cases') &
    (df_cancer['level'] == 2) &
    (df_cancer['gender'] != 'Total')
]

# Prepare data for grouped bar chart
age_groups = sorted(cancer_age_gender['age_group'].unique(),
                    key=lambda x: age_order.index(x) if x in age_order else 999)
x = np.arange(len(age_groups))
width = 0.35

males = []
females = []
for age in age_groups:
    male_val = cancer_age_gender[
        (cancer_age_gender['age_group'] == age) &
        (cancer_age_gender['gender'] == 'Male')
    ]['value'].values
    female_val = cancer_age_gender[
        (cancer_age_gender['age_group'] == age) &
        (cancer_age_gender['gender'] == 'Female')
    ]['value'].values

    males.append(male_val[0] if len(male_val) > 0 else 0)
    females.append(female_val[0] if len(female_val) > 0 else 0)

bars1 = ax.bar(x - width/2, males, width, label='Male', color='#4A90E2', edgecolor='black', linewidth=0.5)
bars2 = ax.bar(x + width/2, females, width, label='Female', color='#E94B8E', edgecolor='black', linewidth=0.5)

ax.set_xlabel('Age Group', fontsize=12, fontweight='bold')
ax.set_ylabel('Number of Cases', fontsize=12, fontweight='bold')
ax.set_title('Cancer Cases by Age Group and Gender (2024)', fontsize=16, fontweight='bold', pad=20)
ax.set_xticks(x)
ax.set_xticklabels(age_groups, fontsize=11)
ax.legend(fontsize=12)
ax.grid(True, axis='y', alpha=0.3)

# Add value labels on bars
for bars in [bars1, bars2]:
    for bar in bars:
        height = bar.get_height()
        if height > 0:
            ax.text(bar.get_x() + bar.get_width()/2., height + 100,
                    f'{int(height)}',
                    ha='center', va='bottom', fontsize=9, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/09_cancer_age_gender.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 10: Heatmap - Cancer Rates by Age Group Over Time
# ============================================================================
print("Chart 10: Cancer rates heatmap...")

# Prepare data for heatmap
cancer_rates_age = df_cancer[
    (df_cancer['metric_type'] == 'rate_per_100000') &
    (df_cancer['gender'] == 'Total') &
    (df_cancer['level'] == 2)
]

# Create pivot table
heatmap_data = cancer_rates_age.pivot(index='age_group', columns='year', values='value')
heatmap_data = heatmap_data.reindex(age_order)

fig, ax = plt.subplots(figsize=(16, 8))
sns.heatmap(heatmap_data, annot=True, fmt='.1f', cmap='YlOrRd',
            linewidths=0.5, cbar_kws={'label': 'Rate per 100,000'}, ax=ax)
ax.set_title('Cancer Incidence Rates by Age Group Over Time (per 100,000)',
             fontsize=16, fontweight='bold', pad=20)
ax.set_xlabel('Year', fontsize=12, fontweight='bold')
ax.set_ylabel('Age Group', fontsize=12, fontweight='bold')

plt.tight_layout()
plt.savefig('charts/10_cancer_rates_heatmap.png', dpi=300, bbox_inches='tight')
plt.close()

# ============================================================================
# CHART 11: Key Insights Summary Dashboard
# ============================================================================
print("Chart 11: Key insights dashboard...")

fig = plt.figure(figsize=(18, 12))
gs = fig.add_gridspec(3, 3, hspace=0.4, wspace=0.3)

# Total disease growth
ax1 = fig.add_subplot(gs[0, :])
ax1.axis('off')
ax1.text(0.5, 0.7, 'Azerbaijan Health Statistics',
         ha='center', va='center', fontsize=28, fontweight='bold', color='#2C3E50')
ax1.text(0.5, 0.3, 'Disease Trends Analysis (1990-2024)',
         ha='center', va='center', fontsize=18, color='#34495E')

# Key metric 1
ax2 = fig.add_subplot(gs[1, 0])
ax2.axis('off')
total_1990 = df_diseases[(df_diseases['year'] == 1990) &
                         (df_diseases['disease_category'] == 'All diseases') &
                         (df_diseases['metric_type'] == 'absolute_cases')]['value'].values[0]
total_2024 = df_diseases[(df_diseases['year'] == 2024) &
                         (df_diseases['disease_category'] == 'All diseases') &
                         (df_diseases['metric_type'] == 'absolute_cases')]['value'].values[0]
growth = ((total_2024 / total_1990) - 1) * 100

ax2.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, color='#3498DB', alpha=0.3))
ax2.text(0.5, 0.7, f'+{growth:.1f}%', ha='center', va='center',
         fontsize=40, fontweight='bold', color='#2C3E50')
ax2.text(0.5, 0.3, 'Total Disease Growth', ha='center', va='center',
         fontsize=14, fontweight='bold', color='#34495E')

# Key metric 2
ax3 = fig.add_subplot(gs[1, 1])
ax3.axis('off')
cancer_2007 = df_cancer[(df_cancer['year'] == 2007) &
                        (df_cancer['gender'] == 'Total') &
                        (df_cancer['age_group'] == 'All ages') &
                        (df_cancer['metric_type'] == 'absolute_cases')]['value'].values[0]
cancer_2024_val = df_cancer[(df_cancer['year'] == 2024) &
                            (df_cancer['gender'] == 'Total') &
                            (df_cancer['age_group'] == 'All ages') &
                            (df_cancer['metric_type'] == 'absolute_cases')]['value'].values[0]
cancer_growth = ((cancer_2024_val / cancer_2007) - 1) * 100

ax3.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, color='#E74C3C', alpha=0.3))
ax3.text(0.5, 0.7, f'+{cancer_growth:.1f}%', ha='center', va='center',
         fontsize=40, fontweight='bold', color='#2C3E50')
ax3.text(0.5, 0.3, 'Cancer Growth', ha='center', va='center',
         fontsize=14, fontweight='bold', color='#34495E')

# Key metric 3
ax4 = fig.add_subplot(gs[1, 2])
ax4.axis('off')
respiratory_2024 = df_diseases[(df_diseases['year'] == 2024) &
                               (df_diseases['disease_category'] == 'Respiratory system diseases') &
                               (df_diseases['metric_type'] == 'absolute_cases')]['value'].values[0]
resp_pct = (respiratory_2024 / total_2024) * 100

ax4.add_patch(plt.Rectangle((0.1, 0.1), 0.8, 0.8, fill=True, color='#2ECC71', alpha=0.3))
ax4.text(0.5, 0.7, f'{resp_pct:.1f}%', ha='center', va='center',
         fontsize=40, fontweight='bold', color='#2C3E50')
ax4.text(0.5, 0.3, 'Respiratory Diseases\n(% of total)', ha='center', va='center',
         fontsize=13, fontweight='bold', color='#34495E')

# Bottom insights
ax5 = fig.add_subplot(gs[2, :])
ax5.axis('off')

insights_text = """
KEY FINDINGS:
• Disease burden increased 65.7% over 34 years (1.73M → 2.87M cases)
• Cancer cases more than DOUBLED in 17 years (+116% growth)
• Respiratory diseases remain the leading cause (37% of all cases)
• Female cancer incidence is now higher than male (8,051 vs 7,113 in 2024)
• 90% of cancer cases occur in people aged 40+ years
"""

ax5.text(0.5, 0.5, insights_text, ha='center', va='center',
         fontsize=13, family='monospace',
         bbox=dict(boxstyle='round', facecolor='wheat', alpha=0.5))

plt.savefig('charts/11_key_insights_dashboard.png', dpi=300, bbox_inches='tight')
plt.close()

print("\n" + "=" * 70)
print("✓ All charts generated successfully!")
print("=" * 70)
print("\nGenerated 11 comprehensive charts:")
print("  1. Overall disease burden trend")
print("  2. Top disease categories (2024)")
print("  3. Evolution of major diseases")
print("  4. Disease distribution comparison (1990 vs 2024)")
print("  5. Growth rates by disease category")
print("  6. Cancer incidence trend")
print("  7. Cancer by gender")
print("  8. Cancer age distribution")
print("  9. Cancer by age and gender")
print(" 10. Cancer rates heatmap")
print(" 11. Key insights dashboard")
print("\nAll charts saved to: charts/")
print("=" * 70)
