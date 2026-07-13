import argparse
import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


def validate_log_level(value: str) -> str:
    levels = {
        "DEBUG",
        "INFO",
        "WARNING",
        "ERROR",
        "CRITICAL",
    }

    log_level = value.upper()

    if log_level not in levels:
        raise argparse.ArgumentTypeError(
            f"Invalid log level: {value}"
        )

    return log_level


def validate_port(value: str) -> int:
    try:
        port = int(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Port must be an integer"
        )

    if not 1 <= port <= 65535:
        raise argparse.ArgumentTypeError(
            "Port must be between 1 and 65535"
        )

    return port


def validate_positive_float(value: str) -> float:
    try:
        number = float(value)
    except ValueError:
        raise argparse.ArgumentTypeError(
            "Value must be a number"
        )

    if number <= 0:
        raise argparse.ArgumentTypeError(
            "Value must be greater than zero"
        )

    return number


def get_required_env(name: str) -> str:
    value = os.getenv(name)

    if value is None or not value.strip():
        raise argparse.ArgumentTypeError(
            f"Missing required environment variable: {name}. Check your .env"
        )

    return value.strip()


@dataclass(frozen=True)
class Config:
    bitcoin_rpc_username: str
    bitcoin_rpc_password: str
    bitcoin_rpc_ip: str
    bitcoin_rpc_port: int
    bitcoin_rpc_timeout: float

    prometheus_host: str
    prometheus_port: int
    prometheus_collect_interval: float

    app_log_level: str
    app_log_path: str | None

    @property
    def bitcoin_rpc_url(self) -> str:
        return (
            f"http://{self.bitcoin_rpc_ip}:"
            f"{self.bitcoin_rpc_port}"
        )


def parse_config() -> Config:
    parser = argparse.ArgumentParser(
        description="Bitcoin full node Prometheus exporter",
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
    )

    parser.add_argument(
        "--bitcoin-rpc-ip",
        default=os.getenv(
            "BITCOIN_RPC_IP",
            "127.0.0.1",
        ),
        help="Bitcoin RPC host",
    )

    parser.add_argument(
        "--bitcoin-rpc-port",
        type=validate_port,
        default=validate_port(
            os.getenv(
                "BITCOIN_RPC_PORT",
                "8332",
            )
        ),
        help="Bitcoin RPC port",
    )

    parser.add_argument(
        "--bitcoin-rpc-timeout",
        type=validate_positive_float,
        default=validate_positive_float(
            os.getenv(
                "BITCOIN_RPC_TIMEOUT",
                "10",
            )
        ),
        help="Bitcoin RPC response timeout in seconds",
    )

    parser.add_argument(
        "--prometheus-host",
        default=os.getenv(
            "PROMETHEUS_HOST",
            "127.0.0.1",
        ),
        help="Prometheus metrics bind host",
    )

    parser.add_argument(
        "--prometheus-port",
        type=validate_port,
        default=validate_port(
            os.getenv(
                "PROMETHEUS_PORT",
                "9091",
            )
        ),
        help="Prometheus metrics server port",
    )

    parser.add_argument(
        "--collect-interval",
        type=validate_positive_float,
        default=validate_positive_float(
            os.getenv(
                "PROMETHEUS_COLLECT_INTERVAL",
                "15",
            )
        ),
        help="Metrics collection interval in seconds",
    )

    parser.add_argument(
        "--app-log-level",
        type=validate_log_level,
        default=validate_log_level(
            os.getenv(
                "APP_LOG_LEVEL",
                "INFO",
            )
        ),
        help="Application log level",
    )

    parser.add_argument(
        "--app-log-path",
        default=None,
        help="Path to the application log file; disabled if not set",
    )

    args = parser.parse_args()

    try:
        bitcoin_rpc_username = get_required_env(
            "BITCOIN_RPC_USERNAME"
        )
        bitcoin_rpc_password = get_required_env(
            "BITCOIN_RPC_PASSWORD"
        )
    except argparse.ArgumentTypeError as error:
        parser.error(str(error))

    return Config(
        bitcoin_rpc_username=bitcoin_rpc_username,
        bitcoin_rpc_password=bitcoin_rpc_password,
        bitcoin_rpc_ip=args.bitcoin_rpc_ip,
        bitcoin_rpc_port=args.bitcoin_rpc_port,
        bitcoin_rpc_timeout=args.bitcoin_rpc_timeout,
        prometheus_host=args.prometheus_host,
        prometheus_port=args.prometheus_port,
        prometheus_collect_interval=args.collect_interval,
        app_log_level=args.app_log_level,
        app_log_path=args.app_log_path or os.getenv("APP_LOG_PATH"),
    )


config = parse_config()