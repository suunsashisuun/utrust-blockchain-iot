import pandas as pd
import matplotlib.pyplot as plt

# load results
df = pd.read_csv("final_results.csv")

strategies = df["strategy"]

# ---------------------------
# LATENCY GRAPH
# ---------------------------
plt.figure()
plt.bar(strategies, df["latency"])
plt.title("Average Latency Comparison")
plt.xlabel("Strategy")
plt.ylabel("Latency (seconds)")
plt.grid()

plt.savefig("latency_comparison.png")
plt.show()

# ---------------------------
# THROUGHPUT GRAPH
# ---------------------------
plt.figure()
plt.bar(strategies, df["throughput"])
plt.title("Throughput Comparison")
plt.xlabel("Strategy")
plt.ylabel("Transactions per unit time")
plt.grid()

plt.savefig("throughput_comparison.png")
plt.show()

# ---------------------------
# FAIRNESS GRAPH
# ---------------------------
plt.figure()
plt.bar(strategies, df["fairness"])
plt.title("Fairness Index Comparison")
plt.xlabel("Strategy")
plt.ylabel("Fairness (0 to 1)")
plt.ylim(0, 1)
plt.grid()

plt.savefig("fairness_comparison.png")
plt.show()
