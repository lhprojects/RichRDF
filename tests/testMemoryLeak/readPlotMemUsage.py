import time
import matplotlib.pyplot as plt
import psutil
import sys

pid = int(sys.argv[1]) # Replace with your actual PID
filename = sys.argv[2]
process = psutil.Process(pid)

timestamps = []
rss_values = []

try:
    while True:
        mem_info = process.memory_info()
        rss = mem_info.rss / (1024 * 1024)  # Convert to MB
        timestamps.append(time.monotonic())
        rss_values.append(rss)
        print(f"RSS: {time.monotonic() - timestamps[0]} {rss:.2f} MB")
        time.sleep(1) 
except Exception:
    pass

# Convert timestamps to elapsed seconds
start_time = timestamps[0]
elapsed_time = [t - start_time for t in timestamps]

# Plotting
plt.figure(figsize=(5, 5))
plt.plot(elapsed_time, rss_values)
plt.xlabel("Time (s)")
plt.ylabel("Memory Usage (MB)")
plt.title("Memory Usage Over Time")
plt.grid(True)
plt.tight_layout()
plt.savefig(filename)
plt.show()


