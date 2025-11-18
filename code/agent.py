"""
Smart Campus Network Monitoring System (NMS Project)
Monitors devices using ICMP ping (Fault + Performance Management)
"""

import os
import time
import csv
from datetime import datetime

# List of network devices to monitor (use real IPs if you have them)
NETWORK_DEVICES = [
    {"name": "Core Router", "ip": "8.8.8.8"},
    {"name": "WiFi Controller", "ip": "8.8.4.4"},
    {"name": "Lab Switch", "ip": "1.1.1.1"},
]

LOG_FILE = os.path.join("data", "nms_log.csv")
POLL_INTERVAL = 10  # seconds


def ping(ip: str):
    # For Windows. If you're on Linux/Mac, change -n to -c
    command = f"ping -n 1 {ip}"
    result = os.popen(command).read()

    if "TTL=" in result or "ttl=" in result:
        latency_ms = None
        for part in result.split():
            if "time" in part.lower():
                digits = ''.join(c for c in part if c.isdigit())
                if digits:
                    latency_ms = float(digits)
        return True, latency_ms

    return False, None


def ensure_log_file():
    # Create CSV with header if not present
    if not os.path.exists(LOG_FILE):
        os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "device", "ip", "status", "latency_ms"])


def write_log(device_name, ip, status, latency_ms):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            device_name,
            ip,
            status,
            latency_ms
        ])


def start_nms_agent():
    ensure_log_file()
    print("=== Smart Campus NMS Agent Started ===")
    print(f"Logging to: {LOG_FILE}")
    print("Press Ctrl + C to stop.\n")

    try:
        while True:
            for dev in NETWORK_DEVICES:
                name, ip = dev["name"], dev["ip"]
                print(f"Pinging {name} ({ip}) ... ", end="")
                is_up, latency = ping(ip)
                status = "UP" if is_up else "DOWN"
                write_log(name, ip, status, latency)
                if is_up:
                    print(f"{status} | latency = {latency} ms")
                else:
                    print("DOWN")
            print("-" * 40)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping NMS agent. Bye!")


if __name__ == "__main__":
    start_nms_agent()

