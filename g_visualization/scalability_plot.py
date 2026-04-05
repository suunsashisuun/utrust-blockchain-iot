import pandas as pd
import matplotlib.pyplot as plt

df = pd.read_csv("scalability_results.csv")

plt.figure()
plt.plot(df["Validators"], df["AvgLatency"], marker='o')

plt.title("Scalability Analysis")
plt.xlabel("Number of Validators")
plt.ylabel("Average Latency")

plt.grid()

plt.savefig("scalability_plot.png")
plt.show()
