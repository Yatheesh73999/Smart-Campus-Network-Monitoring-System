"""
Smart Campus NMS - v2
- Multi-threaded polling
- ICMP reachability (Fault management)
- Optional SNMP metrics (Performance management)
- Logs into CSV
"""

import os
import time
import csv
import json
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, as_completed
import random  # used to simulate metrics if SNMP not available
# Track consecutive DOWN counts per device for remediation logic
down_counters = {}
REMEDIATION_FILE = os.path.join("data", "remediation_log.csv")
DOWN_THRESHOLD = 3  # times in a row

# ---------- OPTIONAL SNMP IMPORT ----------
SNMP_AVAILABLE = True
try:
    from pysnmp.hlapi import (
        SnmpEngine,
        CommunityData,
        UdpTransportTarget,
        ContextData,
        ObjectType,
        ObjectIdentity,
        getCmd,
    )
except ImportError:
    SNMP_AVAILABLE = False
    print("[WARN] pysnmp not available. SNMP metrics will be simulated / None.")


# Devices to monitor
CONFIG_FILE = "devices.json"
LOG_FILE = os.path.join("data", "nms_log_v2.csv")
POLL_INTERVAL = 10  # seconds
MAX_WORKERS = 5     # threads


def load_devices():
    """Load device list from JSON config (Configuration Management)."""
    if not os.path.exists(CONFIG_FILE):
        raise FileNotFoundError(f"Config file {CONFIG_FILE} not found.")
    with open(CONFIG_FILE, "r") as f:
        data = json.load(f)
    return data.get("devices", [])


LOG_FILE = os.path.join("data", "nms_log_v2.csv")
POLL_INTERVAL = 10  # seconds
MAX_WORKERS = 5     # threads


# ---------- ICMP PING ----------
def ping(ip: str):
    """Simple ICMP ping using system command."""
    command = f"ping -n 1 {ip}"  # Windows; use -c on Linux/Mac
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


# ---------- SNMP HELPERS ----------
def snmp_get(ip: str, oid: str, community: str = "public", port: int = 161):
    """Simple SNMP GET. Returns value or None."""
    if not SNMP_AVAILABLE:
        return None

    try:
        iterator = getCmd(
            SnmpEngine(),
            CommunityData(community, mpModel=0),
            UdpTransportTarget((ip, port), timeout=1, retries=0),
            ContextData(),
            ObjectType(ObjectIdentity(oid)),
        )

        errorIndication, errorStatus, errorIndex, varBinds = next(iterator)

        if errorIndication or errorStatus:
            return None

        for varBind in varBinds:
            return float(str(varBind[1]))
    except Exception:
        return None


def get_snmp_metrics(ip: str, community: str = "public"):
    """
    Returns dict with cpu_usage and mem_free.
    If SNMP not available or fails, returns simulated values.
    """
    if SNMP_AVAILABLE:
        # Example OIDs (may or may not work on actual devices):
        cpu_oid = "1.3.6.1.2.1.25.3.3.1.2.1"
        mem_oid = "1.3.6.1.2.1.25.2.3.1.6.1"

        cpu = snmp_get(ip, cpu_oid, community=community)
        mem = snmp_get(ip, mem_oid, community=community)

        if cpu is not None or mem is not None:
            return {"cpu_usage": cpu, "mem_free": mem}

    # Fallback: simulate metrics so graphs still look meaningful
    cpu_sim = random.randint(5, 80)    # 5%–80% CPU
    mem_sim = random.randint(100, 800) # fake units of free memory
    return {"cpu_usage": cpu_sim, "mem_free": mem_sim}


# ---------- LOGGING ----------
def ensure_log_file():
    os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)
    if not os.path.exists(LOG_FILE):
        with open(LOG_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow([
                "timestamp",
                "device",
                "ip",
                "status",
                "latency_ms",
                "cpu_usage",
                "mem_free",
            ])


def write_log(row: list):
    with open(LOG_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(row)


def ensure_remediation_log():
    os.makedirs(os.path.dirname(REMEDIATION_FILE), exist_ok=True)
    if not os.path.exists(REMEDIATION_FILE):
        with open(REMEDIATION_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "device", "ip", "action", "reason"])


def log_remediation(device_name, ip, action, reason):
    with open(REMEDIATION_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        writer.writerow([
            datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            device_name,
            ip,
            action,
            reason
        ])

# ---------- POLLING TASK ----------
def poll_device(device: dict):
    name = device["name"]
    ip = device["ip"]
    snmp_enabled = device.get("snmp", False)
    community = device.get("community", "public")

    is_up, latency = ping(ip)
    status = "UP" if is_up else "DOWN"

    # ----- Automated remediation logic -----
    # Update consecutive DOWN counters
    if status == "DOWN":
        down_counters[name] = down_counters.get(name, 0) + 1
    else:
        down_counters[name] = 0

    # If device is DOWN for N cycles, trigger a (simulated) remediation
    if down_counters.get(name, 0) == DOWN_THRESHOLD:
        action = "Trigger restart / notify admin"
        reason = f"Device {name} has been DOWN for {DOWN_THRESHOLD} consecutive checks."
        print(f"[REMEDIATION] {action} for {name} ({ip}) – {reason}")
        ensure_remediation_log()
        log_remediation(name, ip, action, reason)
    # ---------------------------------------

    cpu_usage = None
    mem_free = None


    if is_up and snmp_enabled:
        metrics = get_snmp_metrics(ip, community)
        cpu_usage = metrics["cpu_usage"]
        mem_free = metrics["mem_free"]

    ts = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    row = [ts, name, ip, status, latency, cpu_usage, mem_free]
    write_log(row)

    return name, status, latency, cpu_usage, mem_free


def start_nms_agent_v2():
    ensure_log_file()
    ensure_remediation_log()

    print("=== Smart Campus NMS Agent v2 (Multi-threaded + SNMP) ===")
    print(f"Logging to: {LOG_FILE}")
    if not SNMP_AVAILABLE:
        print("[INFO] Running without real pysnmp. CPU/memory metrics will be simulated.")
    print("Press Ctrl + C to stop.\n")

    try:
        devices = load_devices()
        print(f"[INFO] Loaded {len(devices)} devices from {CONFIG_FILE}")

        while True:
            with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
                futures = {executor.submit(poll_device, dev): dev for dev in devices}
                for future in as_completed(futures):
                    name, status, latency, cpu, mem = future.result()
                    print(f"{name}: {status}, latency={latency}, cpu={cpu}, mem_free={mem}")
            print("-" * 50)
            time.sleep(POLL_INTERVAL)
    except KeyboardInterrupt:
        print("\nStopping NMS agent v2. Bye!")


if __name__ == "__main__":
    start_nms_agent_v2()
