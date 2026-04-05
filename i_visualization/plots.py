import pandas as pd
import matplotlib.pyplot as plt
import os


# -----------------------------
# PATH SETUP (FINAL)
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
# LABEL FUNCTION
# -----------------------------
def add_labels(values):
    for i, v in enumerate(values):
        plt.text(i, v, f"{v:.3f}", ha='center', va='bottom', fontsize=9)


# -----------------------------
# COLOR SCHEME (FINAL)
# -----------------------------
colors = ['#7f8c8d', '#7f8c8d', '#7f8c8d', '#2ecc71']  # UTrust highlighted


# -----------------------------
# LATENCY
# -----------------------------
plt.figure()
plt.bar(results["strategy"], results["latency"], color=colors)
plt.title("Latency Comparison (UTrust Achieves Lower Latency)")
plt.xlabel("Strategy")
plt.ylabel("Latency")
plt.grid(axis='y', linestyle='--', alpha=0.6)
add_labels(results["latency"])
plt.tight_layout()
plt.savefig(os.path.join(base_path, "latency_comparison.png"))


# -----------------------------
# THROUGHPUT
# -----------------------------
plt.figure()
plt.bar(results["strategy"], results["throughput"], color=colors)
plt.title("Throughput Comparison (UTrust Improves Throughput)")
plt.xlabel("Strategy")
plt.ylabel("Throughput")
plt.grid(axis='y', linestyle='--', alpha=0.6)
add_labels(results["throughput"])
plt.tight_layout()
plt.savefig(os.path.join(base_path, "throughput_comparison.png"))


# -----------------------------
# FAIRNESS
# -----------------------------
plt.figure()
plt.bar(results["strategy"], results["fairness"], color=colors)
plt.title("Fairness Comparison (Trade-off in UTrust)")
plt.xlabel("Strategy")
plt.ylabel("Fairness Index")
plt.grid(axis='y', linestyle='--', alpha=0.6)
add_labels(results["fairness"])
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
