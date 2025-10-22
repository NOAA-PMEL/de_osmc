worker-beat: celery -A tasks beat
worker-default: celery -A tasks worker --loglevel=DEBUG -n deployed_worker
web: gunicorn app:server --workers 4
