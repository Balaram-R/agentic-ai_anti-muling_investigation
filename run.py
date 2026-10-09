import os
import subprocess
import sys
import time
import requests
from pathlib import Path

ROOT = Path(__file__).resolve().parent

API_URL = os.getenv(
    "API_BASE_URL",
    "http://127.0.0.1:8000",
)

HOST = os.getenv(
    "APP_HOST",
    "127.0.0.1",
)

PORT = int(
    os.getenv(
        "APP_PORT",
        "8000",
    )
)


def ready(seconds=20):
    end = time.time() + seconds

    while time.time() < end:
        try:
            response = requests.get(
                API_URL + "/health",
                timeout=1,
            )

            if response.status_code == 200:
                return True

        except requests.RequestException:
            pass

        time.sleep(0.25)

    return False


def db_ok():
    try:
        import psycopg

        from app.core.config import get_settings

        db_url = get_settings().database_url.replace(
            "postgresql+psycopg://",
            "postgresql://",
        )

        with psycopg.connect(
            db_url,
            connect_timeout=2,
        ):
            return True

    except Exception as e:
        print(f"Database connection failed: {e}")
        return False


def main():
    import tkinter as tk

    from app.gui.client import ApiClient
    from app.gui.sender import SenderWindow
    from app.gui.receiver import ReceiverWindow
    from app.gui.human_review_workspace import (
        HumanReviewWorkspace,
    )

    if not ready(1):
        if not db_ok():
            raise SystemExit(
                "PostgreSQL is unavailable. "
                "Start it with: docker compose up -d postgres"
            )

        subprocess.run(
            [
                sys.executable,
                "-m",
                "alembic",
                "upgrade",
                "head",
            ],
            cwd=ROOT,
            check=True,
        )

        subprocess.run(
            [
                sys.executable,
                "-m",
                "app.db.seed_cli",
            ],
            cwd=ROOT,
            check=True,
        )

        proc = subprocess.Popen(
            [
                sys.executable,
                "-m",
                "uvicorn",
                "app.main:app",
                "--host",
                HOST,
                "--port",
                str(PORT),
            ],
            cwd=ROOT,
        )

        if not ready():
            proc.terminate()
            raise SystemExit(
                "FastAPI failed readiness check; "
                "inspect the API process output."
            )
    else:
        proc = None

    api = ApiClient(API_URL)

    sender_root = tk.Tk()
    receiver_root = tk.Tk()
    investigator_root = tk.Tk()

    SenderWindow(
        sender_root,
        api,
    )

    ReceiverWindow(
        receiver_root,
        api,
    )

    HumanReviewWorkspace(
        investigator_root,
        api,
        investigation_id=None,
    )

    sender_root.geometry(
        "760x620+30+50"
    )

    receiver_root.geometry(
        "980x620+820+50"
    )

    investigator_root.geometry(
        "1350x900+300+40"
    )

    def close():
        try:
            sender_root.destroy()
        except tk.TclError:
            pass

        try:
            receiver_root.destroy()
        except tk.TclError:
            pass

        try:
            investigator_root.destroy()
        except tk.TclError:
            pass

        if proc:
            proc.terminate()

    sender_root.protocol(
        "WM_DELETE_WINDOW",
        close,
    )

    receiver_root.protocol(
        "WM_DELETE_WINDOW",
        close,
    )

    investigator_root.protocol(
        "WM_DELETE_WINDOW",
        close,
    )

    investigator_root.mainloop()


if __name__ == "__main__":
    main()
