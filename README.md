# Bitcoin-Fullnode-Prometheus-Exporter

Prometheus exporter for monitoring Bitcoin Core full nodes through RPC.

## Features
- Bitcoin Core blockchain and sync metrics
- Peer, network, mempool, RPC, index, fee, hash-rate, and memory metrics
- Support for `txindex`, `blockfilterindex`, and `peerblockfilters` status
- Prometheus metrics endpoint at `/metrics`
- Configuration through `.env` variables and CLI flags
- Docker and systemd deployment support

## Requirements
- Python 3.10+
- Bitcoin Core with RPC enabled
- Network access from the exporter to the Bitcoin Core RPC endpoint
- [Docker Engine with Docker Compose](https://docs.docker.com/engine/install/) for Docker deployment

## Configuration

#### Copy the example environment file and update it with your settings:
```bash
cp .env.example .env
nano .env
chmod 600 .env
```
CLI arguments override matching `.env` values. RPC username and password are environment-only.

## Systemd Setup

#### 1. Update and install required packages:
```bash
sudo apt update && sudo apt install python3 python3-venv git -y
```
#### 2. Clone the repository:
```bash
git clone https://github.com/trusted-point/Bitcoin-Fullnode-Prometheus-Exporter.git
cd Bitcoin-Fullnode-Prometheus-Exporter
```
#### 3. Activate virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate
```
#### 4. Install dependencies:
```bash
pip install -r requirements.txt
```
#### 5. View available flags:
```bash
python3 main.py --help
```
CLI arguments override matching `.env` values. RPC username and password are environment-only.

#### 6. Create `/etc/systemd/system/bitcoin-fullnode-exporter.service`:
```bash
sudo tee /etc/systemd/system/bitcoin-fullnode-exporter.service > /dev/null <<EOF
[Unit]
Description=Bitcoin Fullnode Prometheus Exporter
After=network-online.target
Wants=network-online.target

[Service]
Type=simple
User=$USER
WorkingDirectory=$HOME/Bitcoin-Fullnode-Prometheus-Exporter
EnvironmentFile=$HOME/Bitcoin-Fullnode-Prometheus-Exporter/.env
ExecStart=$HOME/Bitcoin-Fullnode-Prometheus-Exporter/venv/bin/python3 main.py
Restart=on-failure

[Install]
WantedBy=multi-user.target
EOF
```
#### 7. Enable and start the service:
```bash
sudo systemctl daemon-reload && \
sudo systemctl enable bitcoin-fullnode-exporter && \
sudo systemctl restart bitcoin-fullnode-exporter && \
sudo journalctl -u bitcoin-fullnode-exporter -f -o cat
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
[21:49:04] |   INFO    | |   Prometheus host:      127.0.0.1:9098
[21:49:04] |   INFO    | |   Bitcoin RPC URL:      http://127.0.0.1:38332
[21:49:04] |   INFO    | |   Bitcoin RPC timeout:  10.0 seconds
[21:49:04] |   INFO    | |   Collection interval:  15.0 seconds
[21:49:04] |   INFO    | -------------------------------------------------
[21:49:04] |   INFO    | 📊 Metrics server started at http://127.0.0.1:9098/metrics
[21:49:04] |   INFO    | Bitcoin metric collection completed. Successful groups: 14/14
```
### Metrics will be available at:
```bash
http://127.0.0.1:9091/metrics
```