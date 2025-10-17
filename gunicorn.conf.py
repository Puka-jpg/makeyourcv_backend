from settings import settings

worker_class = "uvicorn.workers.UvicornWorker"
wsgi_app = "main:app"
bind = "127.0.0.1:8080"

accesslog = settings.GUNICORN_ACCESS_LOG
errorlog = settings.GUNICORN_ERROR_LOG
workers = settings.GUNICORN_WORKERS
threads = settings.GUNICORN_THREADS
capture_output = True
loglevel = "info"
