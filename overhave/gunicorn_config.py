import os
import pathlib

from overhave.base_settings import OVERHAVE_ENV_PREFIX

worker_class = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_WORKER_CLASS", "uvicorn.workers.UvicornWorker")
workers = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_WORKERS", 4)
threads = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_THREADS", 1)
worker_connections = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_CONNECTIONS", 1000)
timeout = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_TIMEOUT", 10)
max_requests = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_REQUESTS", 10000)
backlog = int(os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_BACKLOG", 2048))
max_requests_jitter = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_REQUESTS_JITTER", 100)
reuse_port = True

port = os.environ.get(OVERHAVE_ENV_PREFIX + "GUNICORN_PORT", 8000)
bind = f"0.0.0.0:{port}"

if pathlib.Path("/dev/shm").exists():
    worker_tmp_dir = "/dev/shm"

errorlog = "-"
accesslog = "-"
