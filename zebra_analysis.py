import pandas as pd
import numpy as np
from pathlib import Path
from PIL import Image
from scipy.stats import ttest_ind
import matplotlib.pyplot as plt
import seaborn as sns
import re

# ---- Function to extract signal from TIFFs ----
def extract_signals(data_dir, treatments, cell_line_name):
    signal_data = []
    for tif_path in sorted(data_dir.glob("*.tif")):
        file_name = tif_path.name
        for treatment in treatments:
            if re.search(rf"\b{treatment}\b", file_name, flags=re.IGNORECASE):
                image = Image.open(tif_path)
                image_np = np.array(image)
                signal = image_np.sum()
                signal_data.append({
                    "file": file_name,
                    "treatment": treatment,
                    "signal_sum": signal,
                    "cell_line": cell_line_name
                })
                break
    return pd.DataFrame(signal_data)

# ---- Setup paths and treatment mappings ----
treatments = ["control", "LS", "RU", "VA", "VC", "VR"]
treatment_counts_nomo = dict(zip(treatments, [6, 3, 3, 3, 3, 3]))
treatment_counts_molm = dict(zip(treatments, [4, 3, 3, 3, 3, 3]))

data_dir_nomo = Path("/Volumes/Seagate Expansion Drive/ZebrafishPaper/Nikole/NOMO-2.7.24/second try/TIF")
data_dir_molm = Path("/Volumes/Seagate Expansion Drive/ZebrafishPaper/Nikole/MOLM-13-23.7.24/TIFF")

# ---- Extract signals ----
df_nomo = extract_signals(data_dir_nomo, treatments, "NOMO-1")
df_molm = extract_signals(data_dir_molm, treatments, "MOLM-13")

# ---- Combine and save raw data ----
df_all = pd.concat([df_nomo, df_molm], ignore_index=True)
df_all.to_csv("zebrafish_signal_data_combined.csv", index=False)

# ---- Set plot styling ----
treatment_order = treatments
custom_palette = {
    "control": "#F8766D",  # reddish
    "LS": "#E6AB02",       # yellow
    "RU": "#66A61E",       # green
    "VA": "#1E90FF",       # blue
    "VC": "#7570B3",       # purple
    "VR": "#E78AC3"        # pink
}

# ---- Perform t-tests and collect results ----
ttest_results = []

# ---- Plotting ----
fig, axes = plt.subplots(1, 2, figsize=(14, 6), sharey=True)

for i, (cell_line, df_sub) in enumerate(df_all.groupby("cell_line")):
    ax = axes[i]
    
    sns.boxplot(data=df_sub, x="treatment", y="signal_sum",
                order=treatment_order, palette=custom_palette, ax=ax)
    sns.stripplot(data=df_sub, x="treatment", y="signal_sum",
                  order=treatment_order, color='black', alpha=0.6, jitter=True, ax=ax)
    
    ax.set_title(cell_line)
    ax.set_xlabel("Drug")
    if i == 0:
        ax.set_ylabel("Signal (sum of pixel intensity)")
    else:
        ax.set_ylabel("")

    # Add p-value bars
    control_values = df_sub[df_sub["treatment"] == "control"]["signal_sum"]
    y_max = df_sub["signal_sum"].max()
    y_base = y_max * 1.05
    bar_height = y_max * 0.05

    for j, treatment in enumerate(treatment_order[1:], start=1):
        treatment_values = df_sub[df_sub["treatment"] == treatment]["signal_sum"]
        stat, pval = ttest_ind(control_values, treatment_values)

        # Significance stars
        #if pval < 0.001:
            #stars = "***"
        #elif pval < 0.01:
           # stars = "**"
        #elif pval < 0.05:
          #  stars = "*"
        #else:
         #   stars = "ns"
        stars = pval
        # Draw line and label
        x1, x2 = 0, j
        y = y_base + bar_height * (j - 1)
        ax.plot([x1, x1, x2, x2], [y, y + bar_height * 0.2, y + bar_height * 0.2, y], lw=1.3, c='black')
        ax.text((x1 + x2) / 2, y + bar_height * 0.25, f"{stars}\n(p={pval:.3g})",
                ha='center', va='bottom', fontsize=9)

        # Save results
        ttest_results.append({
            "cell_line": cell_line,
            "treatment": treatment,
            "p_value": pval,
            "significance": stars
        })

plt.suptitle("Fluorescence Signal in Zebrafish (NOMO-1 vs MOLM-13)", fontsize=14, y=1.05)
plt.tight_layout()
plt.savefig("zebrafish_signal_plot.png", dpi=300)
plt.show()

# ---- Save statistical results ----
df_stats = pd.DataFrame(ttest_results)
df_stats.to_csv("zebrafish_ttest_results.csv", index=False)
