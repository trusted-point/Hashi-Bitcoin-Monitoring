![Hashi & Bitcoin Monitoring](assets/banner.png)

# 🔥 Hashi & Bitcoin Monitoring 🔥
Prometheus and Grafana monitoring stack for Hashi nodes, with optional extended monitoring for the connected Bitcoin Core Fullnode.

The repository includes:
- A **Grafana dashboard** for Hashi node monitoring
- **Prometheus configuration** examples for Hashi metrics
- An optional **Bitcoin Prometheus Exporter** for additional visibility

The **Bitcoin Metrics Exporter** is not required to monitor Hashi. Hashi itself already exposes several Bitcoin-related metrics, including Kyoto light-client, peer connectivity, sync status, fee rate, deposits, withdrawals, and UTXO pool metrics.

Deploy it for deeper visibility into the underlying Bitcoin Core Fullnode. See the [Bitcoin Fullnode Metrics Exporter](#-bitcoin-core-fullnode-exporter-) section.

## Prometheus Configuration
```yaml
- job_name: "Hashi-Node"
  static_configs:
    - targets: ["127.0.0.1:9180"]
      labels:
        alias: "testnet"

# Optional: extended Bitcoin Fullnode monitoring
- job_name: "Bitcoin-Fullnode"
  static_configs:
    - targets: ["127.0.0.1:9097"]
      labels:
        alias: "signet"
#     - targets: ["127.0.0.1:9098"]
#       labels:
#         alias: "mainnet"

# Multiple targets can be added under each job to monitor several Hashi and Bitcoin. Use a unique alias for every target so it can be selected separately in Grafana.
```

## Grafana Dashboard & Variables

Grafana dashboard JSON files are located in the [`dashboards`](dashboards) directory.

Download the required `.json` file and import it into Grafana.

**Dashboards --> New --> Import --> Upload dashboard JSON file**

| Variable | Source |
|---|---|
| `datasource="$datasource"` | Grafana variable of type `Data source` with data source type `Prometheus` |
| `hashi_alias="$hashi_alias"` | Auto-populated from `label_values(hashi_epoch, alias)` |
| `bitcoin_alias="$bitcoin_alias"` | Auto-populated from `label_values(bitcoin_node_info, alias)` |

## 📂 Bitcoin Fullnode Metrics Exporter 📂
### Features
- Blockchain and sync metrics
- Peer, network, mempool, RPC, index, fee, hash-rate, and memory metrics
- Support for `txindex`, `blockfilterindex`, and `peerblockfilters` status
- Prometheus metrics endpoint at `/metrics`
- Configuration through `.env` variables or CLI flags
- Docker and systemd deployment support
### Requirements
- Python 3.10+
- Bitcoin Core with RPC enabled
- Network access from the exporter to the Bitcoin Core RPC endpoint
- [Docker Engine with Docker Compose](https://docs.docker.com/engine/install/) for Docker deployment

### Configuration

#### 1. Clone the repository:
```bash
cd $HOME
git clone https://github.com/trusted-point/Hashi-Bitcoin-Monitoring.git
cd Hashi-Bitcoin-Monitoring
```
#### 2. Copy the `.env.example` file and update it with your settings:
```bash
cp .env.example .env
nano .env
chmod 600 .env
```
- Config priority: CLI flags --> environment/.env --> built-in defaults

- The Bitcoin RPC credentials are available only through environment variables or the .env file.
## Systemd Setup

#### 1. Update and install required packages:
```bash
sudo apt update && sudo apt install python3 python3-venv git -y
```
#### 2. Create and activate the virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
#### 3. Install dependencies:
```bash
pip install -r requirements.txt
```
#### 4. View available flags:
```bash
python3 main.py --help
```
#### 5. Create `/etc/systemd/system/bitcoin-fullnode-exporter.service`:
```bash
sudo tee /etc/systemd/system/bitcoin-fullnode-exporter.service > /dev/null <<EOF
[Unit]
Description=Bitcoin Fullnode Prometheus Exporter
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/Hashi-Bitcoin-Monitoring
EnvironmentFile=$HOME/Hashi-Bitcoin-Monitoring/.env
ExecStart=$HOME/Hashi-Bitcoin-Monitoring/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```
#### 6. Enable and start the service:
```bash
sudo systemctl daemon-reload && \
sudo systemctl enable bitcoin-fullnode-exporter && \
sudo systemctl restart bitcoin-fullnode-exporter
```
#### 7. View service logs:
```bash
journalctl -u bitcoin-fullnode-exporter -f -o cat
```
## Docker setup

#### 1. Build and start:
```bash
docker compose up -d --build
```
#### 2. View logs:
```bash
docker compose logs -f bitcoin-fullnode-exporter
```
### Expected startup logs:
```bash
[21:49:04] |   INFO    | 🏇 Starting the app...
[21:49:04] |   INFO    | -------------------------------------------------
[21:49:04] |   INFO    | |   App Log level:        INFO
[21:49:04] |   INFO    | |   Prometheus host:      127.0.0.1:9097
[21:49:04] |   INFO    | |   Bitcoin RPC URL:      http://127.0.0.1:38332
[21:49:04] |   INFO    | |   Bitcoin RPC timeout:  10.0 seconds
[21:49:04] |   INFO    | |   Collection interval:  15.0 seconds
[21:49:04] |   INFO    | -------------------------------------------------
[21:49:04] |   INFO    | 📊 Metrics server started at http://127.0.0.1:9097/metrics
[21:49:04] |   INFO    | Bitcoin metric collection completed. Successful groups: 14/14
```
### Metrics will be available at:
```bash
curl http://127.0.0.1:9097/metrics
```