from settings import settings

worker_class = "uvicorn.workers.UvicornWorker"
bind = "0.0.0.0:8080"

accesslog = settings.GUNICORN_ACCESS_LOG
errorlog = settings.GUNICORN_ERROR_LOG
workers = settings.GUNICORN_WORKERS
threads = settings.GUNICORN_THREADS
capture_output = True
loglevel = "info"
