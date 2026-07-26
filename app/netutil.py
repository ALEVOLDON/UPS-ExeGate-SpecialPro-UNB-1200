import socket
from app.config import DEFAULT_HOST, DEFAULT_PORT


def port_in_use(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> bool:
    """Return True if something already accepts TCP connections on host:port."""
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.settimeout(0.4)
        return sock.connect_ex((host, port)) == 0


def port_busy_message(host: str = DEFAULT_HOST, port: int = DEFAULT_PORT) -> str:
    return (
        f"Порт {port} уже занят (http://{host}:{port}).\n\n"
        "Закройте другую копию UPS Monitor (desktop_app / main.py / ярлык) "
        "и запустите снова."
    )
