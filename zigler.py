# zignalyzer
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from scipy.stats import ttest_ind

# Load the data (replace with your actual path or DataFrame if already loaded)
df = pd.read_html("fishes.html")[0]

# Step 1: Normalize area by fish size
df["normalized_signal"] = df["area_max"] / df["li"]

# Step 2: Identify control and treatment groups
control_group = df[df["sample"] == "VC"]
treatment_groups = df[df["sample"] != "VC"]

# Step 3: Perform t-tests comparing each treatment to control
results = []
for treatment in treatment_groups["sample"].unique():
    treat_data = df[df["sample"] == treatment]["normalized_signal"]
    control_data = control_group["normalized_signal"]

    if len(treat_data) > 1 and len(control_data) > 1:
        t_stat, p_val = ttest_ind(control_data, treat_data, equal_var=False)
    else:
        t_stat, p_val = float('nan'), float('nan')

    results.append({
        "Treatment": treatment,
        "T-Statistic": t_stat,
        "P-Value": p_val
    })

t_test_df = pd.DataFrame(results)

# Step 4: Plotting
plt.figure(figsize=(10, 6))
sns.boxplot(data=df, x="sample", y="normalized_signal", palette="Set2")
sns.stripplot(data=df, x="sample", y="normalized_signal", color="black", size=6, jitter=True, alpha=0.7)
plt.title("Normalized Fluorescence Signal by Treatment")
plt.xlabel("Treatment Group")
plt.ylabel("Normalized Signal (area_max / fish length)")
plt.grid(True)
plt.tight_layout()
plt.show()

# Step 5: Show t-test results
print("T-Test Results:")
print(t_test_df)

