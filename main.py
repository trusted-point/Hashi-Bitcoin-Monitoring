import signal
import threading

from typing import Callable

from prometheus_client import make_wsgi_app
from wsgiref.simple_server import (
    WSGIRequestHandler,
    WSGIServer,
    make_server,
)

from src.calls import BitcoinRPCClient
from src.collector import collect_metrics
from utils.config import config
from utils.logger import logger


shutdown_event = threading.Event()


class MetricsRequestHandler(WSGIRequestHandler):
    def log_message(self, format: str, *args) -> None:
        logger.debug(f"Metrics HTTP: {format % args}")


def handle_shutdown_signal(signum, _frame) -> None:
    if shutdown_event.is_set():
        return

    signal_name = signal.Signals(signum).name
    logger.info(f"🛑 Received {signal_name}. Shutting down...")

    shutdown_event.set()


def print_app_config() -> None:
    logger.info("🏇 Starting the app...")
    logger.info("-------------------------------------------------")
    logger.info(f"|   App Log level:        {config.app_log_level}")
    logger.info(f"|   Prometheus host:      {config.prometheus_host}:{config.prometheus_port}")
    logger.info(f"|   Bitcoin RPC URL:      {config.bitcoin_rpc_url}")
    logger.info(f"|   Bitcoin RPC timeout:  {config.bitcoin_rpc_timeout} seconds")
    logger.info(f"|   Collection interval:  {config.prometheus_collect_interval} seconds")
    logger.info("-------------------------------------------------")


def create_metrics_app() -> Callable:
    metrics_app = make_wsgi_app()

    def app(environ, start_response):
        if environ.get("PATH_INFO") == "/metrics":
            return metrics_app(environ, start_response)

        start_response(
            "404 Not Found",
            [
                ("Content-Type", "text/plain; charset=utf-8"),
                ("Content-Length", "10"),
            ],
        )

        return [b"Not Found\n"]

    return app


def start_metrics_server(
    host: str,
    port: int,
) -> tuple[WSGIServer, threading.Thread]:
    server = make_server(
        host,
        port,
        create_metrics_app(),
        handler_class=MetricsRequestHandler,
    )

    server_thread = threading.Thread(
        target=server.serve_forever,
        name="prometheus-http-server",
        daemon=True,
    )

    server_thread.start()

    return server, server_thread


def wait_for_next_collection(interval: float) -> None:
    shutdown_event.wait(interval)


def main() -> None:
    signal.signal(
        signal.SIGTERM,
        handle_shutdown_signal,
    )
    signal.signal(
        signal.SIGINT,
        handle_shutdown_signal,
    )

    print_app_config()

    rpc = BitcoinRPCClient(
        url=config.bitcoin_rpc_url,
        username=config.bitcoin_rpc_username,
        password=config.bitcoin_rpc_password,
        timeout=config.bitcoin_rpc_timeout,
    )

    metrics_server = None
    metrics_thread = None

    try:
        metrics_server, metrics_thread = start_metrics_server(
            host=config.prometheus_host,
            port=config.prometheus_port,
        )

        logger.info(
            f"📊 Metrics server started at "
            f"http://{config.prometheus_host}:"
            f"{config.prometheus_port}/metrics"
        )

        while not shutdown_event.is_set():
            collect_metrics(rpc)

            if shutdown_event.is_set():
                break

            wait_for_next_collection(
                config.prometheus_collect_interval
            )

    finally:
        rpc.close()
        logger.info("🔌 Bitcoin RPC session closed")

        if metrics_server is not None:
            metrics_server.shutdown()
            metrics_server.server_close()

        if metrics_thread is not None:
            metrics_thread.join(timeout=5)

        logger.info("📊 Metrics server stopped")


if __name__ == "__main__":
    main()