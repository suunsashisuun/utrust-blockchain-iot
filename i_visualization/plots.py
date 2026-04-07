import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import os

# -----------------------------
# PATH SETUP
# -----------------------------
base_path = os.path.dirname(os.path.abspath(__file__))
root_path = os.path.abspath(os.path.join(base_path, ".."))

results_path = os.path.join(root_path, "final_results.csv")
scalability_path = os.path.join(root_path, "scalability_results.csv")
detailed_path = os.path.join(root_path, "detailed_runs.csv")

# -----------------------------
# LOAD DATA
# -----------------------------
results = pd.read_csv(results_path)
scalability = pd.read_csv(scalability_path)

if os.path.exists(detailed_path):
    detailed = pd.read_csv(detailed_path)
    detailed_available = True
else:
    detailed_available = False


label_map = {
    "FullParticipation": "Full",
    "GreedyTrust": "Greedy",
    "BalancedTrust": "Balanced",
    "RoundRobin": "RR",
    "Random": "Random",
    "NoUrgency": "NoUrg",
    "UTrust": "UTrust"
}

detailed["strategy_short"] = detailed["strategy"].map(label_map).fillna(results["strategy"])

results["strategy_short"] = results["strategy"].map(label_map).fillna(results["strategy"])

# -----------------------------
# COLORS
# -----------------------------
colors = ['#7f8c8d'] * len(results)
for i, s in enumerate(results["strategy_short"]):
    if "UTrust" in s:
        colors[i] = "#2ecc71"

# -----------------------------
# LABEL FUNCTION
# -----------------------------
def add_labels(values):
    for i, v in enumerate(values):
        plt.text(i, v, f"{v:.3f}", ha='center', va='bottom', fontsize=9)



# -----------------------------
# BASIC COMPARISON (3 CORE PLOTS)
# -----------------------------
for metric in ["latency", "throughput", "fairness"]:
    plt.figure()

    values = results[metric]
    std = results.get(metric + "_std", None)

    plt.bar(results["strategy_short"], values, yerr=std, capsize=5, color=colors)

    plt.title(f"{metric.capitalize()} Comparison")
    plt.xlabel("strategy_short")
    plt.ylabel(metric.capitalize())
    plt.grid(axis='y', linestyle='--', alpha=0.6)

    add_labels(values)

    plt.tight_layout()
    plt.savefig(os.path.join(base_path, f"{metric}_comparison.png"))

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

plt.title("Scalability (Latency vs Validators)")
plt.xlabel("Validators")
plt.ylabel("Latency")
plt.grid(linestyle='--', alpha=0.6)

plt.tight_layout()
plt.savefig(os.path.join(base_path, "scalability.png"))

# -----------------------------
# DISTRIBUTION (COMBINED)
# -----------------------------
if detailed_available:

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))
    metrics = ["latency", "throughput", "fairness"]

    for i, metric in enumerate(metrics):
        sns.violinplot(
            x="strategy_short",
            y=metric,
            data=detailed,
            ax=axes[i]
        )

        axes[i].set_title(metric.capitalize())
        axes[i].grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(base_path, "distribution_combined.png"))

# -----------------------------
# ERROR BAR (MEAN ± STD)
# -----------------------------
if detailed_available:

    grouped = detailed.groupby("strategy_short").agg({
        "latency": ["mean", "std"],
        "throughput": ["mean", "std"],
        "fairness": ["mean", "std"]
    })

    grouped.columns = ["_".join(col) for col in grouped.columns]
    grouped = grouped.reset_index()

    fig, axes = plt.subplots(1, 3, figsize=(15, 5))

    for i, metric in enumerate(["latency", "throughput", "fairness"]):

        means = grouped[f"{metric}_mean"]
        stds = grouped[f"{metric}_std"]

        axes[i].errorbar(
            grouped["strategy_short"],
            means,
            yerr=stds,
            fmt='o',
            capsize=5
        )

        axes[i].set_title(metric.capitalize())
        axes[i].grid(axis='y', linestyle='--', alpha=0.5)

    plt.tight_layout()
    plt.savefig(os.path.join(base_path, "error_combined.png"))

# -----------------------------
# RUN CONSISTENCY
# -----------------------------
if detailed_available:

    fig, axes = plt.subplots(3, 1, figsize=(8, 10), sharex=True)
    metrics = ["latency", "throughput", "fairness"]

    for i, metric in enumerate(metrics):

        for strategy_short in detailed["strategy_short"].unique():
            subset = detailed[detailed["strategy_short"] == strategy_short]

            axes[i].plot(
                subset["run"],
                subset[metric],
                marker='o',
                label=strategy_short
            )

        axes[i].set_title(metric.capitalize())
        axes[i].grid()

    axes[-1].set_xlabel("Run")

    handles, labels = axes[0].get_legend_handles_labels()
    fig.legend(handles, labels, loc='upper center', ncol=3)

    plt.tight_layout()
    plt.savefig(os.path.join(base_path, "run_consistency.png"))

# -----------------------------
# COST vs PERFORMANCE
# -----------------------------
if "validators_used" in results.columns:

    plt.figure()

    plt.scatter(results["validators_used"], results["throughput"], label="Throughput", s=100)
    plt.scatter(results["validators_used"], results["latency"], label="Latency", s=100)

    for i, txt in enumerate(results["strategy_short"]):
        plt.annotate(txt, (results["validators_used"][i], results["throughput"][i]))

    plt.legend()
    plt.xlabel("Validators Used")
    plt.ylabel("Metric Value")
    plt.title("Cost vs Performance")

    plt.grid()
    plt.tight_layout()
    plt.savefig(os.path.join(base_path, "cost_vs_performance.png"))

# -----------------------------
# VALIDATOR USAGE
# -----------------------------
if "validators_used" in results.columns:

    plt.figure()

    plt.bar(results["strategy_short"], results["validators_used"], color=colors)

    plt.title("Validator Participation Cost")
    plt.xlabel("Strategy")
    plt.ylabel("Validators Used")

    for i, v in enumerate(results["validators_used"]):
        plt.text(i, v, f"{v:.1f}", ha='center', va='bottom')

    plt.grid(axis='y', linestyle='--', alpha=0.6)
    plt.tight_layout()

    plt.savefig(os.path.join(base_path, "validator_usage.png"))


# -----------------------------
# COMBINED BOX PLOTS (FINAL — KEEP THIS)
# -----------------------------
if detailed_available:

    import matplotlib.pyplot as plt

    metrics = ["latency", "throughput", "fairness"]

    fig, axes = plt.subplots(1, 3, figsize=(15, 4))

    for i, metric in enumerate(metrics):
        detailed.boxplot(column=metric, by="strategy_short", ax=axes[i])

        axes[i].set_title(metric.capitalize())
        axes[i].set_xlabel("")
        axes[i].set_ylabel(metric.capitalize())
        axes[i].tick_params(axis='x', rotation=30)

    plt.suptitle("")  # remove default title
    plt.tight_layout()

    plt.savefig(os.path.join(base_path, "stability_boxplots.png"))


# -----------------------------
# SHOW
# -----------------------------
plt.show()
