# Smart Campus Network Monitoring System (NMS Project)

A lightweight Python-based **Network Management System (NMS)** designed for campus infrastructure.  
It performs real-time monitoring of network devices using **ICMP and SNMP (real or simulated)**, supports automated remediation, configuration management, logging, and includes a modern **web dashboard with live charts**.

---

## 🌟 Key Features
### FCAPS
### 🟢 Fault Management
- ICMP ping-based device reachability
- UP/DOWN detection
- Fault tracking in logs
- Automated remediation after repeated failures

### 🟡 Performance Management
- Latency measurement
- CPU & Memory monitoring (SNMP or simulator)
- Live charts for latency & CPU trends
- Time-series history storage in CSV logs

### 🔵 Configuration Management
- Device inventory in `devices.json`
- Config backup & restore (`config_backup.py`)

### 🔴 Accounting Management
- CSV logs for device status, latency, CPU, mem, timestamp
- Separate remediation event logs

### 🟣 Optional Security Elements
- Backend API can be restricted or hosted locally
- Config & logs can be protected/access controlled

---

## 🖥 Frontend Dashboard (Updated UI + Live Charts!)

- Modern card-style UI
- Color-coded status badges
- Auto-refreshing every 5 seconds
- Latency graph using Chart.js
- CPU usage graph using Chart.js
- Works over REST API (`/api/devices`)
- No frameworks required (pure HTML/CSS/JS)

📌 Example Preview (not included but will look like card-style Grafana-style UI)

---

## 🏗 Project Structure

```

SmartCampusNMS/
│
├── code/
│   ├── nms_agent_v2.py     # Monitoring agent (multi-threaded)
│   ├── config_backup.py    # Config backup/restore
│   ├── web_app.py          # REST API + frontend hosting
│
├── frontend/
│   └── index.html          # UI + Chart.js dashboard (LIVE)
│
├── data/
│   ├── nms_log_v2.csv      # Monitoring log
│   ├── remediation_log.csv # Automated remediation log
│
├── backups/                # Auto-created config backups
│
├── devices.json            # Device inventory
├── topology.json           # Logical network model
│
├── screenshots/            # UI + terminal + charts screenshots
├── README.md
└── .gitignore

````

---

## ⚙️ Installation

### Install dependencies:

```bash
pip install flask pysnmp
````

(If pysnmp fails, the system will automatically simulate CPU/memory values)

---

## ▶️ Running the System

### 1. Start the monitoring agent:

```bash
python code/nms_agent_v2.py
```

### 2. Start the Flask backend + UI:

```bash
python code/web_app.py
```

### 3. Open dashboard:

```
http://localhost:5000
```

The UI will show:

* Device cards
* Real-time updates
* Live latency graph
* Live CPU graph

---

## 🔄 Config Backup

```bash
python code/config_backup.py
```

Options:

1. Backup config
2. List backups
3. Restore latest

---

## 📊 Data Outputs

* `nms_log_v2.csv`: timestamped monitoring data
* `remediation_log.csv`: remediation events
* Excel can be used for additional analysis

---

## 📌 FCAPS Coverage

| FCAPS             | Covered?                             |
| ----------------- | ------------------------------------ |
| F – Fault         | ✔ UP/DOWN, remediation               |
| C – Configuration | ✔ devices.json, backup/restore       |
| A – Accounting    | ✔ CSV historical logs                |
| P – Performance   | ✔ latency, CPU, memory + charts      |
| S – Security      | ◐ Basic (local access, isolated API) |

---

## 🚀 Future Enhancements

* Email/Telegram alerting
* SNMP trap receiver
* Database instead of CSV
* Web-based config editor
* Device authentication
* UI theme selector
* Role-based dashboard access

---

## 🧑‍💻 Author

**Yatheesh Chandra Maram**
BTech CSE (AI & DS) – REVA University (2022–2026)

---

## ⭐ Contribute

If you find this helpful, please ⭐ the repo!
