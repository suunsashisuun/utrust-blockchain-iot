import pandas as pd
import matplotlib.pyplot as plt
import os


# -----------------------------
# PATH SETUP
# -----------------------------
base_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(base_path, ".."))

results_path = os.path.join(root_path, "final_results.csv")
scalability_path = os.path.join(root_path, "scalability_results.csv")


# -----------------------------
# SAFETY CHECK
# -----------------------------
if not os.path.exists(results_path):
    raise FileNotFoundError(f"Missing file: {results_path}")

if not os.path.exists(scalability_path):
    raise FileNotFoundError(f"Missing file: {scalability_path}")


# -----------------------------
# LOAD DATA
# -----------------------------
results = pd.read_csv(results_path)
scalability = pd.read_csv(scalability_path)


# -----------------------------
# HANDLE COLUMN FORMAT (mean/std or single)
# -----------------------------
def get_col(df, base):
    if base + "_mean" in df.columns:
        return df[base + "_mean"], df.get(base + "_std", None)
    return df[base], None


latency_vals, latency_std = get_col(results, "latency")
throughput_vals, throughput_std = get_col(results, "throughput")
fairness_vals, fairness_std = get_col(results, "fairness")


# -----------------------------
# LABEL FUNCTION
# -----------------------------
def add_labels(values):
    for i, v in enumerate(values):
        plt.text(i, v, f"{v:.3f}", ha='center', va='bottom', fontsize=9)


# -----------------------------
# COLOR SCHEME
# -----------------------------
colors = ['#7f8c8d'] * len(results)

# highlight UTrust
for i, s in enumerate(results["strategy"]):
    if "UTrust" in s:
        colors[i] = "#2ecc71"


# -----------------------------
# IMPROVEMENT CALCULATION
# -----------------------------
try:
    baseline = results[results["strategy"] == "Random"].iloc[0]
    utrust = results[results["strategy"].str.contains("UTrust")].iloc[0]

    fairness_improve = ((utrust["fairness"] - baseline["fairness"]) / baseline["fairness"]) * 100
    latency_change = ((utrust["latency"] - baseline["latency"]) / baseline["latency"]) * 100

    print("\n===== KEY INSIGHTS =====")
    print(f"Fairness Improvement: {fairness_improve:.2f}%")
    print(f"Latency Change: {latency_change:.2f}%")

except:
    print("\n[Warning] Could not compute improvement (check strategy names)")


# -----------------------------
# LATENCY
# -----------------------------
plt.figure()
plt.bar(results["strategy"], latency_vals, yerr=latency_std, capsize=5, color=colors)
plt.title("Latency Comparison")
plt.xlabel("Strategy")
plt.ylabel("Latency")
plt.grid(axis='y', linestyle='--', alpha=0.6)
add_labels(latency_vals)
plt.tight_layout()
plt.savefig(os.path.join(base_path, "latency_comparison.png"))


# -----------------------------
# THROUGHPUT
# -----------------------------
plt.figure()
plt.bar(results["strategy"], throughput_vals, yerr=throughput_std, capsize=5, color=colors)
plt.title("Throughput Comparison")
plt.xlabel("Strategy")
plt.ylabel("Throughput")
plt.grid(axis='y', linestyle='--', alpha=0.6)
add_labels(throughput_vals)
plt.tight_layout()
plt.savefig(os.path.join(base_path, "throughput_comparison.png"))


# -----------------------------
# FAIRNESS
# -----------------------------
plt.figure()
plt.bar(results["strategy"], fairness_vals, yerr=fairness_std, capsize=5, color=colors)
plt.title("Fairness Comparison")
plt.xlabel("Strategy")
plt.ylabel("Fairness Index")
plt.grid(axis='y', linestyle='--', alpha=0.6)
add_labels(fairness_vals)
plt.tight_layout()
plt.savefig(os.path.join(base_path, "fairness_comparison.png"))


# -----------------------------
# SCALABILITY
# -----------------------------
plt.figure()
plt.plot(
    scalability["Validators"],
    scalability["AvgLatency"],
    marker='o'
)

for i in range(len(scalability)):
    plt.text(
        scalability["Validators"][i],
        scalability["AvgLatency"][i],
        f"{scalability['AvgLatency'][i]:.3f}",
        ha='center'
    )

plt.title("Scalability Analysis (Latency vs Validators)")
plt.xlabel("Number of Validators")
plt.ylabel("Average Latency")
plt.grid(linestyle='--', alpha=0.6)
plt.tight_layout()
plt.savefig(os.path.join(base_path, "scalability_plot.png"))


# -----------------------------
# SHOW
# -----------------------------
plt.show()
