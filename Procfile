worker-default: celery -A tasks worker --loglevel=DEBUG -n deployed_worker
worker-beat: celery -A tasks beat
web: ./launch.sh
